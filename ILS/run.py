import os
import time
import numpy as np
import random
import copy
from pymoo.indicators.hv import HV
from tqdm import tqdm
from deap import tools  # 用于帕累托前沿的计算
from ILS.evalute import evaluate, save_scheme_data, Individual


class ILS:
    def __init__(self, ins, args):
        self.args = args
        self.method = 'ILS'  # 使用ILS替换GA
        self.benchmarkName = args.benchmarkName
        self.rdSeed = args.rdSeed
        self._ins = ins
        self.robot_num = ins._robNum  # 机器人数量
        self.task_num = ins._taskNum  # 任务数量
        self._gen = args.generations  # 迭代次数
        self._pop_size = self.robot_num * self.task_num  # 种群大小
        self._local_search_num = int(0.1 * (self.task_num ** 2) * self.robot_num)  # 局部搜索次数
        self._best_solution = None
        self._eval_pop = None
        self._route_best = None
        self._save_path = args.save_path
        self.shape = None
        self.eval_counter = 0  # 引入评估计数器
        self.max_evaluations = self._pop_size * self._gen  # 最大评估次数

        # 添加时间限制
        self.time_limit = self.robot_num * self.task_num * max(self.robot_num, self.task_num) / 10  # 秒

        # 用于保存所有评估过的个体
        self.all_solutions = []

    def _init_population(self):
        """ 初始化初始解 """
        
        pop = []
        for i in range(self._pop_size):
            random_gene = {
                'R': np.random.permutation(self.task_num),  # 随机生成任务顺序
                'X': self.gene_fix(np.random.randint(0, 2, size=(self.robot_num, self.task_num)))  # 随机分配任务
            }
            pop.append(Individual(random_gene))
        # print(f"Initialized population with {len(pop)} individuals.")
        return pop

    def gene_fix(self, mat):
        """ 修复生成的基因以满足约束 """
        for i in range(self.task_num):
            need_task = max(self._ins._taskRateLst[i], 1e-6)
            rob_lst = np.array([j for j in range(self.robot_num) if mat[j][i] == 1])
            aby = 0. if len(rob_lst) == 0 else np.sum(np.array(self._ins._robAbiLst)[rob_lst])
            remain_rob = [j for j in range(self.robot_num) if mat[j][i] == 0]
            while aby < need_task:
                rob_no_tsk = [j for j in remain_rob if np.sum(mat[j, :]) == 0]
                if len(rob_no_tsk) > 0:
                    rob_idx = random.choice(rob_no_tsk)
                else:
                    rob_idx = random.choice(remain_rob)

                mat[rob_idx][i] = 1
                aby += self._ins._robAbiLst[rob_idx]
                remain_rob.remove(rob_idx)
        rob_no_tsk = [j for j in range(self.robot_num) if np.sum(mat[j, :]) == 0]
        for i in rob_no_tsk:
            tsk = random.choice(range(self.task_num))
            mat[i][tsk] = 1
        for i in range(self.task_num):
            if np.sum(mat[:, i]) == 0:
                print(f"Task {i} has no robot!")
                raise ValueError('Invalid gene in gene_fix function.')

        return mat

    def local_search(self, solution):
        """ 局部搜索：改进解 """
        best_solution = copy.deepcopy(solution)
        best_cost = self._evaluate(best_solution)

        improved = True
        while improved and self.eval_counter < self.max_evaluations:
            improved = False
            neighbors = self.get_neighbors(best_solution)
            # print(f"Generated {len(neighbors)} neighbors.")
            for neighbor in neighbors:
                cost = self._evaluate(neighbor)
                if self.dominates(cost, best_cost):
                    # print(f"Found better neighbor with cost {cost}.")
                    best_solution = neighbor
                    best_cost = cost
                    improved = True
                    break  # 可选择找到更好解后立即跳出，以加速搜索
                if self.eval_counter >= self.max_evaluations:
                    # print("Reached maximum evaluations during local search.")
                    break
            # if not improved:
                # print("No improvement found in local search.")
        return best_solution, best_cost

    def perturb(self, solution):
        """ 扰动操作：通过随机交换打破局部最优 """
        perturbed_solution = copy.deepcopy(solution)
        task_order = perturbed_solution.genome['R']
        try:
            i, j = np.random.choice(len(task_order), 2, replace=False)
            task_order[i], task_order[j] = task_order[j], task_order[i]
            # print(f"Perturbed solution by swapping tasks {i} and {j}.")
        except Exception as e:
            print(f"Error during perturbation: {e}")
            raise e
        return perturbed_solution

    def accept_solution(self, current_cost, new_cost):
        """ 接受准则：如果新解支配当前解，或者以一定概率接受非支配解 """
        if self.dominates(new_cost, current_cost):
            # print(f"Accepting new solution with better cost {new_cost}.")
            return True
        else:
            # 使用模拟退火的接受概率（可调整策略）
            delta = sum(np.array(new_cost) - np.array(current_cost))
            probability = np.exp(-delta / 100.0)
            rand_val = np.random.rand()
            if rand_val < probability:
                # print(f"Accepting worse solution with cost {new_cost} due to probability {probability:.4f}.")
                return True
            else:
                # print(f"Rejecting worse solution with cost {new_cost}.")
                return False
    
    def _evaluate(self, individual):
        total_time, total_distance, scheme = evaluate(individual, self._ins)
        save_path = os.path.join(self._save_path, f"{self.args.sample_id}_{self.benchmarkName}")
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        
        save_scheme_data(total_time, total_distance, scheme, save_path, f"{self.benchmarkName}")
        return total_time, total_distance

    def local_mutate_X(self, allocate_lst: np.ndarray) -> np.ndarray:
        """ 修改任务分配矩阵 """
        new_allocate = allocate_lst.copy()
        operator_space = [1, 2, 3]
        op_lst = random.choices(operator_space, k=1)
        for i in op_lst:
            if i == 1:
                # 随机选择两个机器人，交换他们的任务分配
                rob1, rob2 = random.sample(range(self.robot_num), 2)
                new_allocate[rob1], new_allocate[rob2] = new_allocate[rob2].copy(), new_allocate[rob1].copy()
            elif i == 2:
                tsk_idx = random.randint(0, self.task_num - 1)
                rob_no_tsk = [j for j in range(self.robot_num) if new_allocate[j, tsk_idx] == 0]
                rob_do_tsk = [j for j in range(self.robot_num) if new_allocate[j, tsk_idx] == 1]
                if len(rob_no_tsk) == 0:
                    rob_idx = random.choice(rob_do_tsk)
                    new_allocate[rob_idx][tsk_idx] = 0
                elif len(rob_do_tsk) == 0:
                    rob_idx = random.choice(rob_no_tsk)
                    new_allocate[rob_idx][tsk_idx] = 1
                else:
                    rob_do_idx = random.choice(rob_do_tsk)
                    rob_no_idx = random.choice(rob_no_tsk)
                    new_allocate[rob_do_idx][tsk_idx] = 0
                    new_allocate[rob_no_idx][tsk_idx] = 1
            elif i == 3:
                rob_idx = random.randint(0, self.robot_num - 1)
                tsk_do_lst = [j for j in range(self.task_num) if new_allocate[rob_idx, j] == 1]
                tsk_no_lst = [j for j in range(self.task_num) if new_allocate[rob_idx, j] == 0]
                if len(tsk_no_lst) == 0:
                    tsk_idx = random.choice(tsk_do_lst)
                    new_allocate[rob_idx][tsk_idx] = 0
                elif len(tsk_do_lst) == 0:
                    tsk_idx = random.choice(tsk_no_lst)
                    new_allocate[rob_idx][tsk_idx] = 1
                else:
                    tsk_do_idx = random.choice(tsk_do_lst)
                    tsk_no_idx = random.choice(tsk_no_lst)
                    new_allocate[rob_idx][tsk_do_idx] = 0
                    new_allocate[rob_idx][tsk_no_idx] = 1
        new_allocate = self.gene_fix(new_allocate)
        return new_allocate

    def get_neighbors(self, solution):
        """ 获取邻居解，通过交换任务顺序和改变任务分配矩阵生成邻居 """
        neighbors = []
        task_order = solution.genome['R']
        allocate_matrix = solution.genome['X']

        # 生成通过交换任务顺序的邻居
        for j in range(len(task_order)):
            for k in range(j + 1, len(task_order)):
                neighbor = copy.deepcopy(solution)
                neighbor.genome['R'][j], neighbor.genome['R'][k] = neighbor.genome['R'][k], neighbor.genome['R'][j]
                neighbors.append(neighbor)

        # 生成通过修改任务分配矩阵的邻居
        for _ in range(self.task_num):  # 生成一定数量的邻居
            neighbor = copy.deepcopy(solution)
            neighbor.genome['X'] = self.local_mutate_X(neighbor.genome['X'])
            neighbors.append(neighbor)

        # 生成同时修改任务顺序和任务分配矩阵的邻居
        for _ in range(self.task_num):  # 限制组合数量
            neighbor = copy.deepcopy(solution)
            # 交换任务顺序中的两个任务
            i, j = np.random.choice(len(task_order), 2, replace=False)
            neighbor.genome['R'][i], neighbor.genome['R'][j] = neighbor.genome['R'][j], neighbor.genome['R'][i]
            # 应用任务分配矩阵的变异
            neighbor.genome['X'] = self.local_mutate_X(neighbor.genome['X'])
            neighbors.append(neighbor)

        # print(f"Generated {len(neighbors)} neighbors in get_neighbors.")
        return neighbors

    def run(self):
        """ ILS的主循环 """
        pop = self._init_population()
        current_solution = pop[0]
        current_cost = self._evaluate(current_solution)

        best_solution = current_solution
        best_cost = current_cost

        start_time = time.time()
        pbar = tqdm(total=self.max_evaluations, desc='Evaluations')  # 初始化tqdm进度条
        while self.eval_counter < self.max_evaluations and (time.time() - start_time) < self.time_limit:
            # 局部搜索
            # print("Starting local search...")
            new_solution, new_cost = self.local_search(current_solution)

            # 扰动并再次局部搜索
            # print("Applying perturbation...")
            perturbed_solution = self.perturb(new_solution)
            # print("Starting local search after perturbation...")
            perturbed_solution, perturbed_cost = self.local_search(perturbed_solution)

            # 接受解
            if self.accept_solution(current_cost, perturbed_cost):
                current_solution = perturbed_solution
                current_cost = perturbed_cost

            # 更新最优解
            if self.dominates(current_cost, best_cost):
                # print(f"New best solution found with cost {current_cost}.")
                best_solution = current_solution
                best_cost = current_cost

            pbar.update(self.eval_counter - pbar.n)  # 更新进度条
            pbar.set_postfix({'Best Time': f'{best_cost[0]:.4f}', 'Best Distance': f'{best_cost[1]:.4f}'})  # 更新显示信息

            # 检查时间限制
            elapsed_time = time.time() - start_time
            if elapsed_time >= self.time_limit:
                print(f"Time limit reached: {elapsed_time:.2f}s")
                break

        pbar.close()
        print(f"Finished ILS loop. Best cost found: {best_cost}.")

        # 在运行结束后，评估所有解，找到帕累托前沿，保存本地
        self.save_pareto_front()
        print(f"Finished ILS run.")

        return best_solution, best_cost


    def save_pareto_front(self):
        """ 保存所有找到的解的帕累托前沿为本地的 NumPy 数组 """
        if not self.all_solutions:
            print("Warning: No solutions found. Cannot compute Pareto front.")
            return

        print(f"Total solutions evaluated: {len(self.all_solutions)}")

        # 提取所有解的目标值
        fitnesses = np.array([ind.fitness for ind in self.all_solutions])

        # 使用 DEAP 的工具函数找到帕累托前沿
        print("Finding Pareto front...")
        pareto_front = tools.sortNondominated(self.all_solutions, len(self.all_solutions), first_front_only=True)

        if not pareto_front or len(pareto_front[0]) == 0:
            print("Warning: Pareto front is empty. No solutions to save.")
            return
        print(f"Found {len(pareto_front[0])} solutions in Pareto front.")

        # 提取帕累托前沿的目标值
        pareto_fitnesses = np.array([ind.fitness.values for ind in pareto_front[0]])
        # 保存帕累托前沿的目标值到本地文件
        save_path = os.path.join(self._save_path, f'ILS_{self.args.sample_id}_{self.benchmarkName}.npy')
        np.save(save_path, pareto_fitnesses)
        print(f"Pareto front saved to {save_path}")

    def dominates(self, cost1, cost2):
        """ 检查 cost1 是否支配 cost2 """
        return (all(c1 <= c2 for c1, c2 in zip(cost1, cost2)) and any(c1 < c2 for c1, c2 in zip(cost1, cost2)))
