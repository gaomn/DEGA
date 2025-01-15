import os
import time
import copy
import random
import numpy as np
from tqdm import tqdm
from pymoo.indicators.hv import HV
from deap import tools

# 假设从 CACS.utils 中导入:
#   Individual, evaluate, save_data_to_npy
from MSDE_SPEA2 .utils import Individual, evaluate, save_data_to_npy, save_scheme_data

class MSDE_SPEA2:
    def __init__(self, ins, args):
        self.args = args
        self.method = args.method if args.method is not None else 'GA'
        self.benchmarkName = args.benchmarkName
        self.rdSeed = args.rdSeed
        self._ins = ins
        self.robot_num = ins._robNum      # 机器人数量
        self.task_num = ins._taskNum      # 任务数量
        self._gen = args.generations      # 最大迭代次数
        self._cross_rate = args.cross_rate
        self._mutate_rate = args.mutate_rate

        # 种群大小(可根据论文/实验需要自行确定)
        self._pop_size = (
            self.robot_num * self.task_num
            + int(0.1 * (self.task_num ** 2) * self.robot_num)
        )

        # 外部非支配解集的最大容量 W
        self._W = self._pop_size

        # 局部搜索次数(如有需要)
        self._local_search_num = int(0.1 * (self.task_num ** 2) * self.robot_num)

        self._best_solution = None
        self._eval_pop = None
        self._route_best = None

        self._save_path = args.save_path
        self.time_limit = (
            self.robot_num * self.task_num * max(self.robot_num, self.task_num) / 10
        )  # 秒

        self.time_max = None
        self.shape = None

    def _init_population(self):
        """
        Step 1: 初始化种群 S (随机解)，然后对每个个体调用 gene_fix。
        """
        pop = []
        for _ in range(self._pop_size):
            genome = self._random_genome()
            # 修正基因，保证资源约束
            self.gene_fix(genome)
            ind = Individual(genome)
            pop.append(ind)
        return pop

    def _random_genome(self):
        """
        随机生成一个 genome, 这里示例为 {'paths': [list_of_tasks_for_robot0, ..., robotN]}
        允许同一个任务出现在多个机器人的列表中 => 多机器人并行扑火
        """
        genome = {'paths': [[] for _ in range(self.robot_num)]}
        # 简单随机: 每个任务都随机丢给1~2个机器人
        for t in range(self.task_num):
            # 保证至少给一个机器人
            r1 = random.randint(0, self.robot_num - 1)
            genome['paths'][r1].append(t)
            # 再随机决定是否额外给第二个机器人
            if random.random() < 0.3 and self.robot_num > 1:
                r2 = random.randint(0, self.robot_num - 1)
                while r2 == r1 and self.robot_num > 1:
                    r2 = random.randint(0, self.robot_num - 1)
                genome['paths'][r2].append(t)
        return genome

    def gene_fix(self, genome):
        """
        修正基因, 确保对每个任务, 分配的机器人能力总和 > 该任务的火势增长率.
        如果不满足, 则随机选择一个或多个空闲(或少任务)机器人分配上去, 直到满足.
        """
        # 获取机器人灭火能力(从 ins)
        robot_abilities = self._ins._robAbiLst   # [能力0, 能力1, ...]
        task_growth = self._ins._taskRateLst     # [火势增长率0, 火势增长率1, ...]
        paths = genome['paths']                   # paths[r] = 机器人 r 的任务列表

        # 首先统计: 每个任务分配给了哪些机器人
        task_to_robots = [[] for _ in range(self.task_num)]
        for r_idx, task_list in enumerate(paths):
            for t in task_list:
                task_to_robots[t].append(r_idx)

        # 对每个任务, 检查总能力是否 > 火势增长率, 如果不够则修正
        for t_id in range(self.task_num):
            needed = task_growth[t_id]
            # 计算已分配机器人的能力之和
            sum_ability = sum(robot_abilities[r] for r in task_to_robots[t_id])
            if sum_ability < needed:
                # 随机添加机器人, 直到 sum_ability >= needed
                # 优先找“无任务”的机器人 (演示)
                available_robots = list(range(self.robot_num))
                random.shuffle(available_robots)  # 打乱, 以模拟随机
                # 先挑选无任务的机器人
                no_task_robots = [
                    r for r in available_robots if len(paths[r]) == 0
                ]
                # 然后再考虑其他机器人
                full_list = no_task_robots + [
                    r for r in available_robots if r not in no_task_robots
                ]

                for r in full_list:
                    # 如果还不满足就把任务 t_id 分配给机器人 r
                    if sum_ability >= needed:
                        break
                    if r not in task_to_robots[t_id]:
                        task_to_robots[t_id].append(r)
                        paths[r].append(t_id)
                        sum_ability += robot_abilities[r]

        # 最终, 保证所有任务的能力和都 > 火势增长率

    def _evaluate(self, individual: Individual) -> tuple:
        """
        调用已有的 evaluate() 函数
        """
        # return evaluate(individual, self._ins)
        total_time, total_distance, scheme = evaluate(individual, self._ins)
        save_path = os.path.join(self._save_path, f"base_scheme")
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        
        save_scheme_data(total_time, total_distance, scheme, save_path, f"{self.benchmarkName}")
        return total_time, total_distance

    ########################################################################
    # k-邻域聚类 + MSDE剪枝 (示例)
    ########################################################################
    def msde_prune(self, Sprime):
        # 此部分与前例相同
        dist_matrix = self._calc_distance_matrix(Sprime)
        k = 2
        clusters = self._knn_clustering(Sprime, dist_matrix, k)
        for ind in Sprime:
            self._shifting(ind)
        density_list = self._msde_density(Sprime, dist_matrix)
        sorted_solutions = sorted(
            zip(Sprime, density_list), key=lambda x: x[1], reverse=True
        )
        selected = [item[0] for item in sorted_solutions[: self._W]]
        Sprime[:] = selected

    def _calc_distance_matrix(self, solutions):
        size = len(solutions)
        dist_matrix = np.zeros((size, size), dtype=float)
        for i in range(size):
            for j in range(i + 1, size):
                f_i = solutions[i].fitness.values
                f_j = solutions[j].fitness.values
                dist = np.sqrt((f_i[0] - f_j[0])**2 + (f_i[1] - f_j[1])**2)
                dist_matrix[i, j] = dist
                dist_matrix[j, i] = dist
        return dist_matrix

    def _knn_clustering(self, solutions, dist_matrix, k):
        clusters = []
        size = len(solutions)
        for i in range(size):
            row = dist_matrix[i]
            indices = np.argsort(row)
            neigh = []
            cnt = 0
            for idx in indices:
                if idx == i:
                    continue
                neigh.append(idx)
                cnt += 1
                if cnt >= k:
                    break
            clusters.append((i, neigh))
        return clusters

    def _shifting(self, individual):
        # 简单示例
        if 'paths' in individual.genome:
            r_idx = random.randint(0, len(individual.genome['paths']) - 1)
            path = individual.genome['paths'][r_idx]
            if path:
                chosen = random.choice(path)
                path.append(chosen)

    def _msde_density(self, solutions, dist_matrix):
        size = len(solutions)
        density = []
        for i in range(size):
            row = dist_matrix[i]
            row_sorted = np.sort(row[row > 0])
            if len(row_sorted) == 0:
                d = 1e5
            else:
                d = row_sorted[0]
            density.append(1.0 / (d + 1e-9))
        return density

    ########################################################################
    # 交叉 & 变异 (示例)
    ########################################################################
    def crossover_old(self, ind1, ind2):
        """
        演示：多路径随机交换部分任务
        交叉后需要 gene_fix 以确保资源约束
        """
        r_idx = random.randint(0, len(ind1.genome['paths']) - 1)
        path_a = ind1.genome['paths'][r_idx]
        path_b = ind2.genome['paths'][r_idx]
        if path_a and path_b:
            cut = random.randint(1, min(len(path_a), len(path_b)) - 1)
            new_a = path_a[:cut] + path_b[cut:]
            new_b = path_b[:cut] + path_a[cut:]
            ind1.genome['paths'][r_idx] = new_a
            ind2.genome['paths'][r_idx] = new_b

        # 补充“缺失调度”之类的逻辑(若需要)
        self.gene_fix(ind1.genome)
        self.gene_fix(ind2.genome)

    def crossover(self, ind1, ind2):
        """
        演示：多路径随机交换部分任务
        交叉后需要 gene_fix 以确保资源约束
        """
        r_idx = random.randint(0, len(ind1.genome['paths']) - 1)
        path_a = ind1.genome['paths'][r_idx]
        path_b = ind2.genome['paths'][r_idx]

        # 增加长度检查
        if len(path_a) >= 2 and len(path_b) >= 2: # 只有当两个路径长度都大于等于2时才进行交叉
            cut = random.randint(1, min(len(path_a), len(path_b)) - 1)
            new_a = path_a[:cut] + path_b[cut:]
            new_b = path_b[:cut] + path_a[cut:]
            ind1.genome['paths'][r_idx] = new_a
            ind2.genome['paths'][r_idx] = new_b
        else:
        # 新的追加逻辑
            if len(path_a) > 0 and len(path_b) == 0:
                ind2.genome['paths'][r_idx] = path_a[:] # 深拷贝，避免修改原路径
            elif len(path_b) > 0 and len(path_a) == 0:
                ind1.genome['paths'][r_idx] = path_b[:] # 深拷贝，避免修改原路径
            elif len(path_a) == 1 and len(path_b) > 1:
                task_to_add = path_a[0]
                if task_to_add not in path_b:
                    ind2.genome['paths'][r_idx].append(task_to_add)
                    ind1.genome['paths'][r_idx] = path_b[:] # 深拷贝，避免修改原路径
            elif len(path_b) == 1 and len(path_a) > 1:
                task_to_add = path_b[0]
                if task_to_add not in path_a:
                    ind1.genome['paths'][r_idx].append(task_to_add)
                    ind2.genome['paths'][r_idx] = path_a[:] # 深拷贝，避免修改原路径
            elif len(path_a)==1 and len(path_b)==1:
                if path_a[0]!=path_b[0]:
                    ind2.genome['paths'][r_idx].append(path_a[0])
                    ind1.genome['paths'][r_idx].append(path_b[0])
                    
        self.gene_fix(ind1.genome)
        self.gene_fix(ind2.genome)

    def mutate(self, ind):
        """
        演示：随机增删某个机器人的任务
        变异后也需 gene_fix
        """
        if 'paths' in ind.genome:
            r_idx = random.randint(0, len(ind.genome['paths']) - 1)
            path = ind.genome['paths'][r_idx]
            if random.random() < 0.5 and len(path) > 0:
                # 删除一个任务
                pos = random.randint(0, len(path) - 1)
                path.pop(pos)
            else:
                # 新增一个任务
                new_t = random.randint(0, self.task_num - 1)
                pos = random.randint(0, len(path))
                path.insert(pos, new_t)

        self.gene_fix(ind.genome)

    ########################################################################
    # 二元锦标赛 & 主进化循环
    ########################################################################
    def binary_tournament(self, a, b):
        """
        简单比较(a.fitness, b.fitness)，也可用非支配关系
        """
        if a.fitness.values < b.fitness.values:
            return a
        else:
            return b

    def cacs_process(self, pop, generation, if_print=False, if_show=True):
        """
        MSDE-SPEA2 主循环，结合资源约束(通过 gene_fix 保证)，
        k-邻域聚类 + MSDE剪枝，双目标等。
        """
        # 初始化: 先评估
        for ind in pop:
            ind.fitness.values = self._evaluate(ind)

        # 外部非支配解集 S'
        Sprime = []

        for gen in range(generation):
            # 2~3. 非支配排序
            union = pop + Sprime
            fronts = tools.sortNondominated(union, len(union))
            Sprime = fronts[0]

            # 4. 若 S' 超过 W, 则剪枝
            while len(Sprime) > self._W:
                self.msde_prune(Sprime)

            # 5. 再次评估(如基因修正后需要)
            for ind in pop:
                if not ind.fitness.valid:
                    ind.fitness.values = self._evaluate(ind)
            for ind in Sprime:
                if not ind.fitness.valid:
                    ind.fitness.values = self._evaluate(ind)

            # 6. 从 pop + S' 中二元锦标赛选交配池
            union = pop + Sprime
            offspring = []
            while len(offspring) < len(pop):
                a, b = random.sample(union, 2)
                winner = self.binary_tournament(a, b)
                offspring.append(copy.deepcopy(winner))

            # 7. 交叉 & 变异
            for i in range(0, len(offspring), 2):
                if i + 1 < len(offspring) and random.random() < self._cross_rate:
                    self.crossover(offspring[i], offspring[i+1])

                if random.random() < self._mutate_rate:
                    self.mutate(offspring[i])
                if i + 1 < len(offspring) and random.random() < self._mutate_rate:
                    self.mutate(offspring[i+1])

            # 8. 评估
            for ind in offspring:
                ind.fitness.values = self._evaluate(ind)

            pop = offspring

            if if_print:
                print(f"Gen {gen} => Pop={len(pop)}, S'={len(Sprime)}")

        return Sprime

    def run(self):
        """
        主入口：初始化 + cacs_process + 保存结果
        """
        pop = self._init_population()
        max_gen = self._gen

        pop = self.cacs_process(pop, max_gen, if_print=False, if_show=True)

        save_data_to_npy(
            pop, self.args.save_path, self.args.benchmarkName, self.args.sample_id, ifprint=False
        )

        # 选一个最优解（示例：以第二目标最小者）
        self._best_solution = pop[int(np.argmin([i.fitness.values[1] for i in pop]))]
        return self._best_solution