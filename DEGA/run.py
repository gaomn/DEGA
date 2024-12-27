import os
import time
import copy
import random
import numpy as np
from tqdm import tqdm
from pymoo.indicators.hv import HV
from deap import base, tools, creator
from DEGA.utils import Individual, evaluate, save_data_to_npy, save_scheme_data

class DEGA:
    def __init__(self, ins, args):
        self.args = args
        self.method = args.method if args.method is not None else 'GA'
        self.benchmarkName = args.benchmarkName
        self.rdSeed = args.rdSeed
        self._ins = ins
        self.robot_num = ins._robNum
        self.task_num = ins._taskNum
        self._gen = args.generations
        self._cross_rate = args.cross_rate
        self._mutate_rate = args.mutate_rate
        self._pop_size = self.robot_num * self.task_num + int(0.1 * (self.task_num**2) * self.robot_num)
        self._local_search_num = int(0.1 * (self.task_num**2) * self.robot_num)
        self._best_solution = None
        self._eval_pop = None
        self._route_best = None
        self._save_path = args.save_path
        self.time_limit = self.robot_num * self.task_num * max(self.robot_num, self.task_num) / 10  # 秒

        self.time_max = None
        self.shape = None

    def _init_population(self):
        pop = []
        for i in range(self._pop_size - len(pop)):
            random_gene = {'R': np.random.permutation(self.task_num),
                           'X': self.gene_fix(np.random.randint(0, 2, size=(self.robot_num, self.task_num)))}
            pop.append(Individual(random_gene))
        return pop

    def gene_fix(self, mat):
        for i in range(self.task_num):
            need_task = max(self._ins._taskRateLst[i],  1e-6)
            rob_lst = np.array([j for j in range(self.robot_num) if mat[j][i] == 1])
            aby = 0. if len(rob_lst) == 0 else np.sum(np.array(self._ins._robAbiLst)[rob_lst])
            remain_rob = [j for j in range(self.robot_num) if mat[j][i] == 0]
            count = 0
            max_count = 100
            while aby < need_task:
                if count >= max_count or len(remain_rob) == 0:
                    break
                count += 1
                rob_no_tsk = [j for j in remain_rob if np.sum(mat[j, :]) == 0]
                if len(rob_no_tsk) > 0:
                    rob_idx = random.choice(rob_no_tsk)
                else:
                    rob_idx = random.choice(remain_rob)

                mat[rob_idx][i] = 1
                aby += self._ins._robAbiLst[rob_idx]
                del remain_rob[remain_rob.index(rob_idx)]
        rob_no_tsk = [j for j in range(self.robot_num) if np.sum(mat[j, :]) == 0]
        for i in rob_no_tsk:
            tsk = random.choice(range(self.task_num))
            mat[i][tsk] = 1
        for i in range(self.task_num):
            if np.sum(mat[:, i]) == 0:
                print(f"Task {i} has no robot!")
                raise ValueError('Invalid gene in gene_fix function.')

        return mat

    def _crossover_R(self, ind1, ind2):
        size = ind1.shape[0]
        # Choose crossover points
        cx_point1 = random.randint(0, size - 1)
        cx_point2 = random.randint(0, size - 1)

        if cx_point1 > cx_point2:
            cx_point1, cx_point2 = cx_point2, cx_point1

        offspring1 = np.zeros(size, dtype=int) - 1
        offspring2 = np.zeros(size, dtype=int) - 1

        offspring1[cx_point1:cx_point2 + 1] = ind1[cx_point1:cx_point2 + 1]
        offspring2[cx_point1:cx_point2 + 1] = ind2[cx_point1:cx_point2 + 1]

        # Fill in the remaining positions in the offspring
        for i in range(size):
            if ind2[i] not in offspring1:
                for j in range(size):
                    if offspring1[j] == -1:
                        offspring1[j] = ind2[i]
                        break
            if ind1[i] not in offspring2:
                for j in range(size):
                    if offspring2[j] == -1:
                        offspring2[j] = ind1[i]
                        break

        return [offspring1, offspring2]

    def _crossover_x(self, ind1, ind2, op=None):
        operator = ['+', '-', '*']
        # 随机选择两种操作符
        if op is None:
            op1, op2 = random.sample(operator, 2)
            opt = [op1, op2]
        else:
            # print(f'Using operator {op} in {operator}')
            opt = [operator[op-1]]
        # 随机选择一个机器人和一个任务
        for i in opt:
            if i == '+':
                cross_gene = np.clip(np.array(ind1) + np.array(ind2), 0, 1)
            elif i == '-':
                cross_gene = np.abs(np.array(ind1) - np.array(ind2))
            elif i == '*':
                cross_gene = np.clip(np.array(ind1) * np.array(ind2), 0, 1)
            else:
                raise ValueError('Invalid operator in mate_x function.')
            cross_gene = self.gene_fix(cross_gene)
        return cross_gene

    def _crossover(self, ind1, ind2):
        all_op = {1: ['o1', 'o2'], 2: ['o1', 'm1'], 3: ['o1', 'm2'], 4: ['o1', 'm3'],
                  5: ['o2', 'o1'], 6: ['o2', 'm1'], 7: ['o2', 'm2'], 8: ['o2', 'm3'],
                  9: ['m3', 'o1'], 10: ['m3', 'o2'], 11: ['m3', 'm1'], 12: ['m3', 'm2'], 13: ['m3', 'm3'],
                  14: ['m4', 'o1'], 15: ['m4', 'o2'], 16: ['m4', 'm1'], 17: ['m4', 'm2'], 18: ['m4', 'm3'], }
        # 随机选择两个操作符交叉方式
        op1, op2, op3, op4 = random.sample(range(1, 19), 4)
        route_lst = [ind1.genome['R'], ind2.genome['R']] + self._crossover_R(ind1.genome['R'], ind2.genome['R'])

        child_lst = []
        for opt in [op1, op2, op3, op4]:
            if all_op[opt][1][0] == 'o':
                allocate = ind1.genome['X'].copy() if all_op[opt][1][1] == '1' else ind2.genome['X'].copy()
            else:
                allocate = self._crossover_x(ind1.genome['X'], ind2.genome['X'], op=int(all_op[opt][1][1]))
            child_lst.append(Individual({'R': route_lst[int(all_op[opt][0][1]) - 1].copy(), 'X': allocate}))

        return child_lst

    def _mutate_R(self, individual):
        new_individual = individual.copy()
        size = individual.shape[0]
        for i in range(size):
            if random.random() < self._mutate_rate:
                swap_with = random.randint(0, size - 1)
                # print("Swapping", i, "with", swap_with)
                new_individual[i], new_individual[swap_with] = new_individual[swap_with], new_individual[i]
        return new_individual

    def _mutate_x(self, gene):
        new_gene = np.array(gene).copy()
        rob_n, tsk_n = random.randint(1, self.robot_num - 1), random.randint(1, self.task_num - 1)
        rob_idx = np.random.choice(self.robot_num, rob_n, replace=False)
        tsk_idx = np.random.choice(self.task_num, tsk_n, replace=False)
        new_gene[rob_idx[:, np.newaxis], tsk_idx] = 1 - new_gene[rob_idx[:, np.newaxis], tsk_idx]
        new_gene = self.gene_fix(new_gene)
        return new_gene

    def _mutate(self, individual):
        all_op = {1: ['m', 'm'], 2: ['o', 'm'], 3: ['m', 'o']}
        # 随机选择一个操作符
        op = random.sample(range(1, 4), 1)[0]
        route_this = individual.genome['R'].copy()
        allocate_this = individual.genome['X'].copy()

        route_this = self._mutate_R(route_this) if all_op[op][0] == 'm' else route_this
        allocate_this = self._mutate_x(allocate_this) if all_op[op][1] == 'm' else allocate_this

        return Individual({'R': route_this, 'X': allocate_this})

    def _evaluate(self, individual: Individual) -> tuple:
        '''
        def save_scheme_data(time_val, distance_val, hv, robot_task_sequences, save_dir, filename_prefix="scheme"):
            """
            将仿真结果(时间、距离、hv以及各机器人分配的任务序列)存入指定文件夹。
            使用 JSON Lines 格式，每行一个 JSON 对象，便于追加。
            """
        '''
        total_time, total_distance, scheme = evaluate(individual, self._ins)
        save_path = os.path.join(self._save_path, f"{self.args.sample_id}_{self.benchmarkName}")
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        
        save_scheme_data(total_time, total_distance, scheme, save_path, f"{self.benchmarkName}")
        return total_time, total_distance
        # return evaluate(individual, self._ins)

    def _local_search_X(self, individual: Individual) -> Individual:
        route_lst = individual.genome['R'][:]  # Copy of the route genome
        allocate_lst = copy.deepcopy(individual.genome['X'])  # Deep copy of the allocation genome
        res_lst = []  # Store results that improve the individual
        fits = [individual.fitness.values[0], individual.fitness.values[1]]  # Store current fitness

        for i in range(self._local_search_num):
            new_allocate_lst = self.local_mutate_X(allocate_lst)  # Perform mutation on allocation
            new_ind = Individual({'R': route_lst.copy(), 'X': new_allocate_lst})  # Create a new individual
            new_fit = self._evaluate(new_ind)  # Evaluate the fitness of the new individual
            new_ind.fitness.values = new_fit  # Update the fitness of the new individual

            if new_fit[0] < fits[0] or new_fit[1] < fits[1]:
                res_lst.append(new_ind)  # Append the new individual if it improves

            # Update the best fitness and allocation if an improvement is found
            if new_fit[0] <= fits[0] and new_fit[1] < fits[1]:
                fits = [new_fit[0], new_fit[1]]  # Update best fitness
                allocate_lst = new_allocate_lst  # Update the allocation genome

        return res_lst  # Return the list of improved individuals

    def local_mutate_X(self, allocate_lst: np.ndarray) -> np.ndarray:
        new_allocate = allocate_lst.copy()
        operator_space = [1, 2, 3]
        op_lst = random.choices(operator_space, k=1)
        for i in op_lst:
            if i == 1:
                # 随机选择两个机器人，交换两个机器人的任务
                rob1, rob2 = random.sample(range(self.robot_num), 2)
                new_allocate[rob1], new_allocate[rob2] = new_allocate[rob2], new_allocate[rob1]
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

    def _local_search_R(self, individual: Individual) -> Individual:
        route_lst = individual.genome['R'][:]  # Copy of the route genome
        allocate_lst = individual.genome['X']  # Reference to the allocation genome
        res_lst = []  # Store results that improve the individual
        fits = [individual.fitness.values[0], individual.fitness.values[1]]  # Store current fitness

        for i in range(self._local_search_num):
            new_route_lst = self.local_mutate_R(route_lst)  # Perform mutation on route
            new_ind = Individual({'R': new_route_lst, 'X': allocate_lst})  # Create a new individual
            new_fit = self._evaluate(new_ind)  # Evaluate the fitness of the new individual
            new_ind.fitness.values = new_fit  # Update the fitness of the new individual

            if new_fit[0] < fits[0] or new_fit[1] < fits[1]:
                res_lst.append(new_ind)  # Append the new individual if it improves

            if new_fit[0] <= fits[0] and new_fit[1] < fits[1]:
                fits = [new_fit[0], new_fit[1]]  # Update best fitness
                route_lst = new_route_lst  # Update the route genome

        return res_lst  # Return the list of improved individual


    def local_mutate_R(self, route_lst: np.ndarray):
        new_route = route_lst.copy()
        # exchange_num = random.randint(1, int(self.task_num * 0.5))
        exchange_num = 1
        tsk_idx = random.sample(range(self.task_num), exchange_num)
        tsk_exchange = random.sample(range(self.task_num), exchange_num)
        for i, j in zip(tsk_idx, tsk_exchange):
            if random.random() < 0.5:
                new_route[i:j + 1] = np.hstack((new_route[j], new_route[i:j]))
            else:
                new_route[i], new_route[j] = new_route[j], new_route[i]
        return new_route

    def run(self):
        pop = self._init_population()
        max_gen = self._gen
        pop = self.ga_process(pop, max_gen, if_print=False, if_show=True)
        save_data_to_npy(pop, self.args.save_path, self.args.benchmarkName, self.args.sample_id, ifprint=False)
        self._best_solution = pop[int(np.argmin([i.fitness.values[1] for i in pop]))]
        return self._best_solution

    def ga_process(self, pop, generation, if_print=False, if_show=True):
        toolbox = base.Toolbox()
        toolbox.register("select", tools.selNSGA2)
        toolbox.register("evaluate", self._evaluate)

        invalid_ind = [ind for ind in pop if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # 编译统计
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean, axis=0)
        stats.register("min", np.min, axis=0)
        stats.register("max", np.max, axis=0)

        # 进化算法主体
        all_pop = copy.deepcopy(pop[:])
        # 使用tqdm库显示进度条
        if if_show:
            t = tqdm(range(generation))
        else:
            t = range(generation)
        for gen in t:

            # 选择下一代个体
            offspring = []
            fit_pro = [1 / ind.fitness.values[0] for ind in pop]
            fit_pro = [1e-1 if (i is None or i is np.nan) else i for i in fit_pro]
            fit_pro = np.nan_to_num(fit_pro)
            fit_pro = np.array(fit_pro) / np.sum(fit_pro)

            # 根据fit_pro概率，优选可能性大的进行交叉、变异
            for _ in range(len(pop) // 2):
                try:
                    i, j = np.random.choice(len(pop), 2, replace=False, p=fit_pro)
                except:
                    i, j = np.random.choice(len(pop), 2,)
                    # print(f"there is no valid individual in offspring, i={i}, j={j}")
                ch_lst = self._crossover(pop[i], pop[j])
                offspring += ch_lst

            # 根据fit_pro概率，优选可能性大的进行变异
            for _ in range(len(offspring)):
                if random.random() < self._mutate_rate:
                    # i = int(np.random.choice(len(offspring), 1, replace=False, p=fit_pro))
                    try:
                        i = random.choices(range(len(offspring)), weights=fit_pro)[0]
                    except:
                        i = random.choice(range(len(offspring)))
                        # print(f"there is no valid individual in offspring, i={i}")
                    ch = self._mutate(offspring[i])
                    offspring.append(ch)

            # 评估新个体的适应度
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(toolbox.evaluate, invalid_ind)

            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
            min_f0_index = np.argmin([ind.fitness.values[0] for ind in offspring])
            ind = offspring[min_f0_index]
            ind_lst = self._local_search_R(ind)
            offspring += ind_lst
            ind_lst = self._local_search_X(ind)
            offspring += ind_lst

            # 更新种群
            pop = toolbox.select(pop + offspring, self._pop_size)
            all_pop += copy.deepcopy(pop[:])

            # 当最后一代时，可以打印统计信息，看进化过程
            if if_print:
                record = stats.compile(pop)
                print(f"Generation {gen}: {record}      -    loss_value, time, distance")

        top_individuals = tools.sortNondominated(pop, len(pop), first_front_only=True)[0]
        self.plot_pareto_front(pop)
        return top_individuals
    
    def plot_pareto_front(self, pop):
        """
        绘制帕累托前沿。
        
        :param pop: 种群列表，其中每个个体具有两个目标值 (time, distance)。
        """
        import matplotlib.pyplot as plt

        # 提取所有个体的目标值
        objectives = np.array([ind.fitness.values for ind in pop])
        time_values = objectives[:, 0]  # 第一个目标：时间
        distance_values = objectives[:, 1]  # 第二个目标：距离

        # 找到帕累托前沿
        pareto_front = tools.sortNondominated(pop, len(pop), first_front_only=True)[0]
        pareto_objectives = np.array([ind.fitness.values for ind in pareto_front])
        pareto_time = pareto_objectives[:, 0]
        pareto_distance = pareto_objectives[:, 1]

        # 绘制散点图
        plt.figure(figsize=(8, 6))
        plt.scatter(time_values, distance_values, label="Population", alpha=0.5, color='gray')
        plt.scatter(pareto_time, pareto_distance, label="Pareto Front", color='red', marker='o')
        
        # 图形设置
        plt.title("Pareto Front Visualization")
        plt.xlabel("Time (Objective 1)")
        plt.ylabel("Distance (Objective 2)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        # 显示图形
        plt.show()






