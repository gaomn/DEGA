# -*- coding: UTF-8 -*-
# @Date    : 2024/4/23
# @Author  : 高猛 + ChatGPT
# @Project : CACS_Implementation
# @File    : cacs_main.py
# @IDE     : PyCharm

import random
import copy
import numpy as np
from deap import tools

# 假设同级目录下有 utils.py，包含以下内容：
#  - Individual类
#  - evaluate函数
#  - save_data_to_npy函数
#  - 其它辅助方法
from CACS.utils import Individual, evaluate, save_data_to_npy


class CACS:
    """
    基于论文描述的合作蚁群系统（CACS）多目标算法。
    """
    def __init__(self, ins, args):
        """
        :param ins:    问题实例对象，需要至少包含下列属性:
                       - _robNum: 机器人数量
                       - _taskNum: 任务数量
                       - _taskRateLst: 每个任务的火势增长率
                       - _robAbiLst: 每个机器人的灭火能力
                       - 其它用于evaluate()的必要数据
        :param args:   超参数及运行设置，包含:
                       - number_of_colonies: 蚁群数量
                       - popsize_per_colony: 每个蚁群的规模(蚂蚁数量)
                       - max_iter: 最大迭代次数
                       - alpha, beta: 费洛蒙重要性、启发式重要性
                       - q0: 状态转移规则的阈值
                       - rho_l, rho_g: 局部与全局费洛蒙挥发率
                       - cross_rate, mutation_rate: 交叉与变异率
                       - ...
        """
        self.ins = ins
        self.args = args

        # 问题规模
        self.robot_num = ins._robNum
        self.task_num = ins._taskNum

        # 多蚁群相关参数
        self.num_colonies = args.number_of_colonies
        self.popsize_per_colony = args.popsize_per_colony
        self.max_iter = args.generations

        # 费洛蒙和启发式参数
        self.alpha = args.alpha
        self.beta = args.beta
        self.q0 = args.q0
        self.rho_l = args.rho_l
        self.rho_g = args.rho_g

        # 交叉、变异率
        self.cross_rate = args.cross_rate
        self.mutation_rate = args.mutate_rate

        # 档案(Archive)，存放非支配解（示例中用一个list表示）
        self.archive = []

        # 1) 初始化费洛蒙矩阵
        #   - tau1: 任务-任务 费洛蒙矩阵 (含起点 0)
        #   - tau2: 任务-机器人 费洛蒙矩阵
        # 2) 初始化启发式信息
        self.tau1, self.tau2 = self.initialize_pheromone()
        self.eta1, self.eta2 = self.initialize_heuristic_info()

        # 保存路径
        self.save_path = getattr(args, 'save_path', './results')
        self.sample_id = getattr(args, 'sample_id', 'demo')
        self.benchmarkName = getattr(args, 'benchmarkName', 'TestCase')

    # ---------------------------------------------------------------------
    # 1. 初始化费洛蒙矩阵
    # ---------------------------------------------------------------------
    def initialize_pheromone(self):
        """
        根据论文描述：需要初始化 tau^1 (任务-任务) 和 tau^2 (任务-机器人)，
        示例：初始值可统一设为 1 或者根据贪婪解 X_r 来计算。
        这里提供一个简单实现：全部设为 1.0
        """
        m = self.task_num
        n = self.robot_num

        # tau^1: (m+1) x (m+1) 矩阵 (0号表示仓库或起点)
        tau1 = [[1.0 for _ in range(m+1)] for _ in range(m+1)]

        # tau^2: m x n 矩阵
        tau2 = [[1.0 for _ in range(n)] for _ in range(m)]

        return tau1, tau2

    # ---------------------------------------------------------------------
    # 2. 初始化启发式信息
    # ---------------------------------------------------------------------
    def initialize_heuristic_info(self):
        """
        论文中:
        - eta^1 用于任务选择: eta_{w,o}^1 = 1 / dist(...)  (示例)
        - eta^2 用于联盟构建: eta_{t,u}^{2,c} = 1 / (Δ f_c + 1)  (示例)
        这里使用“距离”与“能力增量”的方式简单实现一下。
        """
        m = self.task_num
        # 这里简单地设置距离 = 1，或者从 ins 中获取预先计算好的任务距离矩阵
        # 以 dist(tw, to) = 1 => eta^1 = 1
        # 实际应根据论文进行真实计算
        eta1 = [[1.0 for _ in range(m+1)] for _ in range(m+1)]

        # eta^2: 针对任务 t 与机器人 r，每个目标 c 的增量
        # 此示例仅针对 c=1 (时间) or c=2 (距离) 做简化
        # 实际可根据论文对多个目标分别计算
        eta2 = [[1.0 for _ in range(self.robot_num)] for _ in range(m)]

        return eta1, eta2

    # ---------------------------------------------------------------------
    # 3. 生成初始解 X_r 
    # ---------------------------------------------------------------------
    def generate_initial_solution(self):
        """
        论文中描述：使用贪婪策略生成初始解 X_r，并由此计算初始费洛蒙 tau^{0,c}。
        这里仅做示例：随机生成一个解决方案。
        若要严格与论文一致，请根据火势增长、能力需求等贪婪构造。
        """
        genome = {'task_alliance_list': []}
        for t in range(self.task_num):
            # 随机选些机器人，保证能力 > 火势增长
            alliance = self.random_valid_alliance(t)
            genome['task_alliance_list'].append({'task_id': t, 'alliance': alliance})

        ind = Individual(genome)
        ind.fitness.values = evaluate(ind, self.ins)
        return ind

    def random_valid_alliance(self, task_id):
        """
        为任务 task_id 随机挑选一个联盟(机器人集合)，使得 sum(能力) > 任务火势增长。
        """
        req_rate = self.ins._taskRateLst[task_id]
        abilities = self.ins._robAbiLst
        trial = 0
        while True:
            trial += 1
            size = random.randint(1, self.robot_num)
            chosen = random.sample(range(self.robot_num), size)
            total_abi = sum(abilities[r] for r in chosen)
            if total_abi > req_rate:
                return chosen
            if trial > 50:
                # 多次失败就返回所有机器人
                return list(range(self.robot_num))

    # ---------------------------------------------------------------------
    # 4. 主算法
    # ---------------------------------------------------------------------
    def run(self):
        """
        CACS 主流程:
        1) 初始化档案
        2) 生成初始解 X_r (可选)，并据此初始化费洛蒙 (此处仅做示例)
        3) 循环迭代:
           - 对每个蚁群 c:
             a) 对 popsize_per_colony 只蚂蚁，每只蚂蚁构建解 X_{c,e}
             b) 对解进行局部费洛蒙更新
             c) 把解存到档案
           - 局部搜索
           - 全局费洛蒙更新
        4) 返回非支配解
        """
        # (可选) 用一个初始解来设定初始费洛蒙
        init_sol = self.generate_initial_solution()
        # 在论文中，还有 tau^{0,c} = 1/(m * f_c(X_r)) 的计算，可以在此替换
        # 这里仅作演示，不做实际替换

        # 初始化档案
        self.archive = []
        self.archive.append(init_sol)

        # 开始迭代
        for iteration in range(1, self.max_iter + 1):
            # --- 对每个蚁群 c ---
            for c in range(self.num_colonies):
                population_c = []  # 当前蚁群产生的解
                for e in range(self.popsize_per_colony):
                    # 构建解
                    new_sol = self.construct_solution(colony=c)
                    # 局部费洛蒙更新
                    self.locally_update_pheromone(new_sol, c)
                    # 存到 population_c
                    population_c.append(new_sol)

                # 将当前蚁群生成的解并入全局档案
                self.archive.extend(population_c)

            # 局部搜索(交叉+变异)
            self.archive = self.local_search(self.archive)

            # 全局费洛蒙更新
            self.globally_update_pheromone(self.archive)

            # (可选) 如果论文提到需要每次迭代更新非支配档案，可在此筛选
            self.archive = self.environment_selection(self.archive)

            # 打印或可视化
            # if iteration % 5 == 0:
            #     print(f"Iteration {iteration}: Archive size = {len(self.archive)}")

        # 结束后返回非支配解
        nd_solutions = self.environment_selection(self.archive, only_first_front=True)
        # 同时可将结果保存
        save_data_to_npy(nd_solutions, self.save_path, self.benchmarkName, self.sample_id, ifprint=True)
        return nd_solutions

    # ---------------------------------------------------------------------
    # 5. 解的构建
    # ---------------------------------------------------------------------
    def construct_solution(self, colony=0):
        """
        根据论文描述:
        - 首先进行任务选择(基于 tau^1 和 eta^1)
        - 然后进行联盟构建(基于 tau^2 和 eta^2)
        - 无先序约束时，任务顺序可随意。若有先决条件则要依规则选择。
        * 这里我们示例：随机顺序遍历所有任务, 并用"状态转移规则"来选联盟。
        """
        tasks = list(range(self.task_num))
        random.shuffle(tasks)  # 若无先序约束，可以随机顺序

        genome = {'task_alliance_list': []}

        for idx, t in enumerate(tasks):
            # 简化：直接调用 "基于 tau^2, eta^2 的状态转移" 来选联盟
            alliance = self.select_alliance_for_task(t, colony)
            genome['task_alliance_list'].append({
                'task_id': t,
                'alliance': alliance
            })

        ind = Individual(genome)
        # 评估
        ind.fitness.values = evaluate(ind, self.ins)
        return ind

    def select_alliance_for_task(self, task_id, colony):
        """
        状态转移规则 (示例):
          r_j = argmax_{r_u in R'} { [tau2[task_id][r_u]]^alpha * [eta2[task_id][r_u]]^beta }, 若 q <= q0
          否则基于概率选择
        此处为了简化: 直接把"所有使能力>火势增长率"的机器人作为候选，然后从中选1~N个。
        但若想更贴近论文，可像其描述的那样"逐个选择机器人"直到满足需求。
        """
        # 逐个选择机器人
        chosen = []
        req_rate = self.ins._taskRateLst[task_id]
        total_abi = 0.0
        available = list(range(self.robot_num))
        random.shuffle(available)

        while total_abi <= req_rate and available:
            q = random.random()
            if q <= self.q0:
                # 直接选择置信度最高的
                best_r = max(available, key=lambda r: (
                    (self.tau2[task_id][r] ** self.alpha) *
                    (self.eta2[task_id][r] ** self.beta)
                ))
                chosen.append(best_r)
                available.remove(best_r)
                total_abi = sum(self.ins._robAbiLst[x] for x in chosen)
            else:
                # 基于概率
                weights = []
                for r in available:
                    w = ((self.tau2[task_id][r] ** self.alpha) *
                         (self.eta2[task_id][r] ** self.beta))
                    weights.append(w)
                # 归一化
                s = sum(weights)
                if s <= 1e-10:
                    best_r = random.choice(available)
                else:
                    probs = [w / s for w in weights]
                    best_r = random.choices(available, weights=probs, k=1)[0]
                chosen.append(best_r)
                available.remove(best_r)
                total_abi = sum(self.ins._robAbiLst[x] for x in chosen)

        return chosen

    # ---------------------------------------------------------------------
    # 6. 局部费洛蒙更新
    # ---------------------------------------------------------------------
    def locally_update_pheromone(self, solution, colony):
        """
        论文：在每次构建解后进行局部费洛蒙更新:
        tau_{i,j}^{s,c} = (1 - rho_l)*tau_{i,j}^{s,c} + rho_l * tau^{0,c}, 若 (i,j) 属于解 X_{c,e}
        这里做简化：将 (task,robot) 在 tau2 上做局部更新
        """
        # 假设 tau^{0,c} 统一 = 1.0 (也可按论文设为 1/(m*f_c(X_r)) )
        tau0 = 1.0
        for item in solution.genome['task_alliance_list']:
            t = item['task_id']
            for r in item['alliance']:
                self.tau2[t][r] = (1 - self.rho_l) * self.tau2[t][r] + self.rho_l * tau0

    # ---------------------------------------------------------------------
    # 7. 局部搜索 (交叉 + 变异)
    # ---------------------------------------------------------------------
    def local_search(self, archive):
        """
        论文：局部搜索包括交叉和变异操作。
        - 这里直接对 archive 中的部分解进行操作。
        - 并重新评估、更新档案。
        """
        # 选出若干解
        # 示例：随机选 popsize_per_colony 个解
        if len(archive) <= self.popsize_per_colony:
            selected = archive
        else:
            selected = random.sample(archive, self.popsize_per_colony)

        new_solutions = []
        for _ in range(self.popsize_per_colony // 2):
            if len(selected) < 2:
                break
            p1, p2 = random.sample(selected, 2)

            child1, child2 = self.crossover(p1, p2, self.cross_rate)
            self.mutation(child1, self.mutation_rate)
            self.mutation(child2, self.mutation_rate)

            # 评估
            child1.fitness.values = evaluate(child1, self.ins)
            child2.fitness.values = evaluate(child2, self.ins)

            new_solutions.extend([child1, child2])

        # 更新 archive (将新解加入)
        archive.extend(new_solutions)
        return archive

    def crossover(self, parent1, parent2, cross_rate):
        """
        交叉操作：
        论文示例：随机选择切割点进行交换，然后修复先决条件(若有)。
        这里仅演示对 'task_alliance_list' 做片段交换。
        """
        c1 = copy.deepcopy(parent1)
        c2 = copy.deepcopy(parent2)

        if random.random() < cross_rate:
            # 交叉
            size = len(c1.genome['task_alliance_list'])
            if size < 2:
                return c1, c2
            pos1 = random.randint(0, size - 1)
            pos2 = random.randint(pos1, size - 1)

            seg1 = c1.genome['task_alliance_list'][pos1:pos2+1]
            seg2 = c2.genome['task_alliance_list'][pos1:pos2+1]
            c1.genome['task_alliance_list'][pos1:pos2+1] = seg2
            c2.genome['task_alliance_list'][pos1:pos2+1] = seg1

        return c1, c2

    def mutation(self, individual, mutation_rate):
        """
        变异操作：
        论文中示例：随机翻转联盟的二进制表示等。
        这里用一个简单方式：随机在 task_alliance_list 里，对部分任务做增/删机器人。
        """
        if random.random() < mutation_rate:
            tlist = individual.genome['task_alliance_list']
            if not tlist:
                return

            t_index = random.randint(0, len(tlist) - 1)
            alliance = tlist[t_index]['alliance']
            # 50% 概率增加机器人 / 删除机器人
            if alliance and random.random() < 0.5:
                # 删除
                alliance.remove(random.choice(alliance))
            else:
                # 增加
                candidates = list(set(range(self.robot_num)) - set(alliance))
                if candidates:
                    alliance.append(random.choice(candidates))
            tlist[t_index]['alliance'] = alliance

    # ---------------------------------------------------------------------
    # 8. 全局费洛蒙更新
    # ---------------------------------------------------------------------
    def globally_update_pheromone(self, archive):
        """
        论文：全局费洛蒙更新在每次迭代结束时进行，以强化优质解
        tau_{i,j}^{s,c} = (1 - rho_g)*tau_{i,j}^{s,c} + rho_g * Δ tau_c,  如果 (i,j) 在 X_{c,b} 中
        否则 (1 - rho_g)*tau_{i,j}^{s,c}
        这里示例：对目标1(时间)最优、目标2(距离)最优都进行一次更新(可扩展为非支配前沿里的若干解)。
        Δ tau_c = 1/f_c(X_{c,b}) 仅作示例
        """
        # 先筛选非支配解
        nd_archive = self.environment_selection(archive, only_first_front=True)

        # 选出对目标 time 最优的个体
        best_time_ind = min(nd_archive, key=lambda x: x.fitness.values[0])
        # 选出对目标 distance 最优的个体
        best_dist_ind = min(nd_archive, key=lambda x: x.fitness.values[1])

        self._global_update_for_solution(best_time_ind, idx_obj=0)
        self._global_update_for_solution(best_dist_ind, idx_obj=1)

    def _global_update_for_solution(self, solution, idx_obj=0):
        """
        对单个解 solution 做全局费洛蒙更新
        Δ tau_c = 1 / f_c(X_{c,b})
        """
        fc = solution.fitness.values[idx_obj]
        if fc <= 1e-12:
            d_tau = 1.0
        else:
            d_tau = 1.0 / fc

        for item in solution.genome['task_alliance_list']:
            t = item['task_id']
            for r in item['alliance']:
                old_val = self.tau2[t][r]
                new_val = (1 - self.rho_g)*old_val + self.rho_g * d_tau
                self.tau2[t][r] = new_val

    # ---------------------------------------------------------------------
    # 9. 环境选择(非支配筛选)
    # ---------------------------------------------------------------------
    def environment_selection(self, archive, only_first_front=False):
        """
        调用 DEAP 的 sortNondominated，
        若 only_first_front=True，只保留第一前沿，否则按前沿分层。
        """
        ndsort = tools.sortNondominated(archive, len(archive), first_front_only=only_first_front)
        if only_first_front:
            return ndsort[0]
        else:
            # 将所有前沿 flatten
            result = []
            for front in ndsort:
                result.extend(front)
            return result


#---------------------------- 使用示例 (可放到单独的 main 中) ----------------------------
# if __name__ == "__main__":
#     # 仅作示例：构造一个简单 ins
#     class InsExample:
#         def __init__(self):
#             self._robNum = 3
#             self._taskNum = 5
#             self._taskRateLst = [2, 3, 4, 1, 2]   # 火势增长率
#             self._robAbiLst  = [2, 2, 3]         # 机器人能力
#             # 其它如距离矩阵可在 evaluate 中自行处理

#     class Args:
#         def __init__(self):
#             self.number_of_colonies = 2
#             self.popsize_per_colony = 5
#             self.max_iter = 30
#             self.alpha = 1
#             self.beta = 2
#             self.q0 = 0.9
#             self.rho_l = 0.1
#             self.rho_g = 0.1
#             self.cross_rate = 0.8
#             self.mutation_rate = 0.2

#             self.save_path = './results'
#             self.sample_id = 'demo'
#             self.benchmarkName = 'FireTest'

#     ins = InsExample()
#     args = Args()

#     solver = CACS(ins, args)
#     final_solutions = solver.run()
#     print(f"非支配解数量: {len(final_solutions)}")
#     for sol in final_solutions:
#         print(sol.genome, sol.fitness.values)