import random
import numpy as np
import math
import time
from deap import base, creator, tools
import copy
from tqdm import tqdm
import heapq
import os
import json

# 定义GA类
class MSGA:
    def __init__(self, ins, args):
        self.args = args
        self.method = args.method if args.method is not None else 'MSGA'
        self.benchmarkName = args.benchmarkName
        self.rdSeed = args.rdSeed
        self._ins = ins
        self.robot_num = ins._robNum
        self.task_num = ins._taskNum
        self._gen = args.generations
        self._cross_rate = args.cross_rate
        self._mutate_rate = args.mutate_rate
        self._pop_size = int(1.1 * self.robot_num * self.task_num)

        # 多目标优化，最小化时间和距离
        creator.create("FitnessMin", base.Fitness, weights=(-1.0, -1.0))  # 同时最小化两个目标
        creator.create("Individual", np.ndarray, fitness=creator.FitnessMin)

        # 将任务分为有优先级和无优先级的两部分
        # 为简化，假设前一半任务有优先级
        self.priority_tasks = list(range(0, self.task_num // 2))
        self.other_tasks = list(range(self.task_num // 2, self.task_num))

        # 优先级任务的数量
        self.I = len(self.priority_tasks)

        # 初始化一些变量
        self.beta = np.array(self._ins._taskStateLst)    # 任务的初始需求量
        self.task_rate = np.array(self._ins._taskRateLst) # 任务的增长速率
        self.vk = np.array(self._ins._robAbiLst)         # 机器人的能力
        self.all_pop = []  # 存储所有个体的列表

    def _init_population(self):
        pop = []
        for i in range(self._pop_size):
            # 生成初始个体
            individual = np.zeros((self.robot_num, self.task_num + 1), dtype=int)
            # 第一列为全1，表示每个机器人从仓库出发
            individual[:, 0] = 1

            # 按任务增长速率从低到高排序分配任务，提高分配成功率
            tasks_sorted_by_rate = sorted(self.priority_tasks, key=lambda t: self.task_rate[t])

            # 分配优先级任务（阶段I）
            for task in tasks_sorted_by_rate:
                xri = np.zeros(self.robot_num, dtype=int)
                total_ability = np.sum(xri * self.vk)
                attempts = 0
                max_attempts = 100  # 最大尝试次数限制
                while total_ability < self.task_rate[task] and attempts < max_attempts:
                    # 随机将一个未分配该任务的机器人分配给该任务
                    unassigned_robots = np.where(xri == 0)[0]
                    if len(unassigned_robots) == 0:
                        break  # 所有机器人都已分配任务
                    r = np.random.choice(unassigned_robots)
                    xri[r] = 1
                    total_ability = np.sum(xri * self.vk)
                    attempts += 1
                if total_ability < self.task_rate[task]:
                    # 如果无法分配，则进行修复操作
                    individual = self._fix_individual(individual, task)
                else:
                    individual[:, task + 1] = xri

            # 分配其他任务（阶段II）
            for task in self.other_tasks:
                xri = np.zeros(self.robot_num, dtype=int)
                total_ability = np.sum(xri * self.vk)
                attempts = 0
                max_attempts = 100  # 最大尝试次数限制
                while total_ability < self.task_rate[task] and attempts < max_attempts:
                    # 随机将一个未分配该任务的机器人分配给该任务
                    unassigned_robots = np.where(xri == 0)[0]
                    if len(unassigned_robots) == 0:
                        break  # 所有机器人都已分配任务
                    r = np.random.choice(unassigned_robots)
                    xri[r] = 1
                    total_ability = np.sum(xri * self.vk)
                    attempts += 1
                if total_ability < self.task_rate[task]:
                    # 如果无法分配，则进行修复操作
                    individual = self._fix_individual(individual, task)
                else:
                    individual[:, task + 1] = xri

            # 创建个体
            ind = creator.Individual(individual)
            pop.append(ind)

        return pop

    def _fix_individual(self, individual, task):
        """
        修复个体中的特定任务，使其满足约束条件。
        """
        individual[individual < 0.5] = 0
        individual[individual >= 0.5] = 1

        total_ability = np.sum(individual[:, task + 1] * self.vk)
        unassigned_robots = np.where(individual[:, task + 1] == 0)[0]
        while total_ability < self.task_rate[task]:
            if len(unassigned_robots) == 0:
                print(f"Error: Unable to fix task {task}. No more unassigned robots available.")
                # 标记个体为不可行
                individual.invalid = True
                break
            # 随机选择一个未分配该任务的机器人进行分配
            r = np.random.choice(unassigned_robots)
            individual[r, task + 1] = 1
            total_ability += self.vk[r]
            # 更新未分配机器人列表
            unassigned_robots = np.where(individual[:, task + 1] == 0)[0]
        return individual

    def gene_fix(self, individual):
        # 全面修复操作，将所有任务逐个修复
        for task in range(self.task_num):
            total_ability = np.sum(individual[:, task + 1] * self.vk)
            if total_ability < self.task_rate[task]:
                individual = self._fix_individual(individual, task)
                if hasattr(individual, 'invalid') and individual.invalid:
                    break  # 无法修复，跳出循环
        return individual

    def _crossover(self, parent1, parent2):
        # 随机选择一个交叉算子
        operator = random.choice([1, 2, 3])
        if operator == 1:
            # 交叉算子1：矩阵加法
            offspring = parent1 + parent2
        elif operator == 2:
            # 交叉算子2：矩阵减法
            offspring = parent1 - parent2
        else:
            # 交叉算子3：对应元素乘法
            offspring = parent1 * parent2
        # 修复并创建子代个体
        offspring = self.gene_fix(offspring)
        child = creator.Individual(offspring)
        return child

    def _mutate(self, individual):
        # 变异操作：0-1互换
        for i in range(self.robot_num):
            for j in range(1, self.task_num+1):
                if random.random() < self._mutate_rate:
                    individual[i, j] = 1 - individual[i, j]
        # 修复并创建变异后的个体
        return self.gene_fix(individual)

    def _evaluate(self, individual):
        robot_task_sequences = [[] for _ in range(self.robot_num)]
        real_robot_task_sequences = [[] for _ in range(self.robot_num)]
        for r in range(self.robot_num):
            tasks_assigned = np.where(individual[r, 1:] == 1)[0]
            # 按任务增长速率从高到低排序（可根据需要调整）
            tasks_assigned = sorted(tasks_assigned, key=lambda t: self.task_rate[t], reverse=True)
            robot_task_sequences[r] = tasks_assigned

        if hasattr(individual, 'invalid') and individual.invalid:
            return float('inf'), float('inf')

        total_distance = 0.0
        task_status = self.beta.copy()  # 初始火势
        task_last_update_time = np.zeros(self.task_num)  # 任务上次状态更新的时间
        task_completion_time = np.full(self.task_num, np.inf)  # 初始化为无穷大

        # 初始化机器人任务序列
        robot_task_sequences = [[] for _ in range(self.robot_num)]
        for r in range(self.robot_num):
            tasks_assigned = np.where(individual[r, 1:] == 1)[0]
            # 按任务增长速率从高到低排序（可根据需要调整）
            tasks_assigned = sorted(tasks_assigned, key=lambda t: self.task_rate[t], reverse=True)
            robot_task_sequences[r] = tasks_assigned

        # 初始化事件队列
        event_queue = []
        # 机器人状态：[当前位置，当前时间]
        robots_state = [{'task': -1, 'time': 0.0} for _ in range(self.robot_num)]
        # 任务被机器人占用的记录，记录正在处理该任务的机器人ID
        task_robots = [[] for _ in range(self.task_num)]

        # 初始化机器人到达第一个任务的事件
        for r in range(self.robot_num):
            if robot_task_sequences[r]:
                next_task = robot_task_sequences[r][0]
                # 计算从起点到任务的时间
                travel_time = self._ins._rob2taskDisMat[r][next_task] / self._ins._robVelLst[r]
                arrival_time = robots_state[r]['time'] + travel_time
                total_distance += self._ins._rob2taskDisMat[r][next_task]
                # 将事件加入队列
                heapq.heappush(event_queue, (arrival_time, 'arrive', r, next_task))
                robots_state[r]['time'] = arrival_time
                robots_state[r]['task'] = next_task
                real_robot_task_sequences[r].append(next_task)

        # 全局时间
        current_time = 0.0

        # 定义一个函数来更新任务状态并安排完成事件
        def update_task_status_and_schedule_finish(task_id, current_time):
            # 更新任务状态
            delta_time = current_time - task_last_update_time[task_id]
            if task_status[task_id] > 0:
                net_rate = self.task_rate[task_id] - sum(self.vk[r] for r in task_robots[task_id])
                task_status[task_id] += net_rate * delta_time
                if task_status[task_id] <= 0:
                    task_status[task_id] = 0
                    task_completion_time[task_id] = current_time
                    # 移除任务的完成事件
                    event_queue[:] = [evt for evt in event_queue if not (evt[1] == 'finish' and evt[3] == task_id)]
                task_last_update_time[task_id] = current_time

            # 重新计算净速率
            net_rate = self.task_rate[task_id] - sum(self.vk[r] for r in task_robots[task_id])

            # 如果任务未完成且净速率小于0，安排完成事件
            if task_status[task_id] > 0 and net_rate < 0:
                extinguish_time = task_status[task_id] / (-net_rate)
                finish_time = current_time + extinguish_time
                # 移除已有的完成事件
                event_queue[:] = [evt for evt in event_queue if not (evt[1] == 'finish' and evt[3] == task_id)]
                heapq.heappush(event_queue, (finish_time, 'finish', None, task_id))

        while event_queue:
            # 取出下一个事件
            event = heapq.heappop(event_queue)
            event_time, event_type, robot_id, task_id = event
            time_diff = event_time - current_time
            current_time = event_time

            # 更新所有任务的状态
            for t in range(self.task_num):
                if t == task_id:
                    continue  # 当前任务将在后续单独更新
                delta_time = current_time - task_last_update_time[t]
                if task_status[t] <= 0:
                    continue
                # 计算状态变化
                # 当前有机器人在处理该任务
                if task_robots[t]:
                    total_ability = sum(self.vk[r] for r in task_robots[t])
                    net_rate = self.task_rate[t] - total_ability
                    delta = net_rate * delta_time
                else:
                    delta = self.task_rate[t] * delta_time
                task_status[t] += delta
                if task_status[t] <= 0:
                    task_status[t] = 0
                    task_completion_time[t] = current_time
                    # 移除任务的完成事件
                    event_queue[:] = [evt for evt in event_queue if not (evt[1] == 'finish' and evt[3] == t)]
                task_last_update_time[t] = current_time

            if event_type == 'arrive':
                # 添加机器人到任务
                task_robots[task_id].append(robot_id)
                update_task_status_and_schedule_finish(task_id, current_time)
            elif event_type == 'finish':
                # 任务完成，更新状态
                task_status[task_id] = 0
                task_completion_time[task_id] = current_time
                # 所有在该任务的机器人前往下一个任务
                for r in task_robots[task_id]:
                    next_task_index = robot_task_sequences[r].index(task_id) + 1
                    if next_task_index < len(robot_task_sequences[r]):
                        next_task = robot_task_sequences[r][next_task_index]
                        # 计算从当前任务到下一个任务的时间
                        travel_time = self._ins._taskDisMat[task_id][next_task] / self._ins._robVelLst[r]
                        arrival_time = current_time + travel_time
                        total_distance += self._ins._taskDisMat[task_id][next_task]
                        heapq.heappush(event_queue, (arrival_time, 'arrive', r, next_task))
                        robots_state[r]['time'] = arrival_time
                        robots_state[r]['task'] = next_task
                        real_robot_task_sequences[r].append(next_task)
                    else:
                        # 没有任务了
                        robots_state[r]['task'] = -1
                # 清空任务的机器人列表
                task_robots[task_id] = []
                task_last_update_time[task_id] = current_time

        # 所有机器人完成任务后的最大时间
        total_time = max(robot['time'] for robot in robots_state)

        # 检查任务是否全部完成
        if any(status > 0 for status in task_status):
            # 有任务未完成
            total_time = float('inf')
            total_distance = float('inf')

        # 检查优先级约束
        priority_ok = True
        for i in range(len(self.priority_tasks) - 1):
            task_i = self.priority_tasks[i]
            task_j = self.priority_tasks[i + 1]
            if task_completion_time[task_i] > task_completion_time[task_j]:
                priority_ok = False
                break
        save_dir = os.path.join(self.args.save_path, f"MSGA_{self.args.sample_id}_{self.benchmarkName}")
        os.makedirs(save_dir, exist_ok=True)
        save_scheme_data(total_time, total_distance, real_robot_task_sequences, save_dir, self.benchmarkName)
        return total_time, total_distance

    # 使用DEAP库实现MSGA算法
    def run(self):
        pop = self._init_population()
        max_gen = self._gen
        pop = self.ga_process(pop, max_gen, if_print=False, if_show=True)
        # 保存最优个体（可选）
        self._best_solution = pop[0]
        # 返回帕累托前沿种群
        pareto_front = self._get_pareto_front()
        self.save_pareto_front(pareto_front)
        return pareto_front

    def ga_process(self, pop, generation, if_print=False, if_show=True):
        start_time = time.time()
        toolbox = base.Toolbox()
        toolbox.register("select", tools.selTournament, tournsize=3)
        toolbox.register("evaluate", self._evaluate)

        # 评估初始种群
        invalid_ind = [ind for ind in pop if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # 进化过程
        if if_show:
            t = tqdm(range(generation))
        else:
            t = range(generation)
        for gen in t:
            offspring = []
            while len(offspring) < len(pop):
                parent1, parent2 = random.sample(pop, 2)
                if random.random() < self._cross_rate:
                    child = self._crossover(parent1, parent2)
                    if random.random() < self._mutate_rate:
                        child = self._mutate(child)
                    offspring.append(child)
                else:
                    offspring.append(copy.deepcopy(parent1))
            # 评估子代
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
            # 选择下一代
            pop = toolbox.select(pop + offspring, self._pop_size)
            self._updata_pop(pop=pop)
        # 返回最优个体
        top_individuals = self._updata_pop()
        return top_individuals

    def _updata_pop(self, ind=None, pop=None):
        # 确保 ind 和 pop 中的所有个体都符合 creator.Individual 的定义
        if ind is not None:
            # 检查 ind 是否为 creator.Individual，如果不是则转换
            if not isinstance(ind, creator.Individual):
                ind = creator.Individual(ind)
            self.all_pop.append(ind)

        if pop is not None:
            # 确保 pop 中的所有个体都是 creator.Individual 类型
            for individual in pop:
                if not isinstance(individual, creator.Individual):
                    individual = creator.Individual(individual)
                self.all_pop.append(individual)

        # 检查 self.all_pop 中所有个体的 fitness 是否有效
        self.all_pop = [ind for ind in self.all_pop if ind.fitness.valid]

        # 保持种群数量在合理范围内
        if len(self.all_pop) >= 200:
            # 对个体进行非支配排序，只保留帕累托前沿
            pareto_front = tools.sortNondominated(self.all_pop, len(self.all_pop), first_front_only=True)[0]
            self.all_pop = pareto_front
        return self.all_pop

    def _get_pareto_front(self):
        # 获取当前所有个体的帕累托前沿
        pareto_front = tools.sortNondominated(self.all_pop, len(self.all_pop), first_front_only=True)[0]
        return pareto_front

    def save_pareto_front(self, pareto_front):
        # 将帕累托前沿的个体保存为numpy数组
        fitnesses = np.array([ind.fitness.values for ind in pareto_front])
        save_path = os.path.join(self.args.save_path, f'MSGA_{self.args.sample_id}_{self.benchmarkName}.npy')
        np.save(save_path, fitnesses)
        # print(f"Pareto front saved to {save_path}")
        # print(f"Benchmark: {self.benchmarkName} | Min Fitness: (time: {fitnesses[:, 0].min():.2E}, distance: {fitnesses[:, 1].min():.2E})\n")
    
def save_scheme_data(time_val, distance_val, robot_task_sequences, save_dir, filename_prefix="scheme"):
    """
    将仿真结果(时间、距离、hv以及各机器人分配的任务序列)存入指定文件夹。
    使用 JSON Lines 格式，每行一个 JSON 对象，便于追加。
    """
    # 构建最终要保存的数据结构
    scheme_data = {
        "time": time_val,
        "distance": distance_val,
        "scheme": [
            {"robot": int(r), "task": [int(t) for t in tasks]} for r, tasks in enumerate(robot_task_sequences)
        ]
    }

    # 确保目录存在
    os.makedirs(save_dir, exist_ok=True)
    # 文件名可根据需要调整，使用 JSON Lines 格式
    save_path = os.path.join(save_dir, f"{filename_prefix}.jsonl")

    with open(save_path, 'a', encoding='utf-8') as f:
        json_line = json.dumps(scheme_data, ensure_ascii=False)
        f.write(json_line + '\n')  # 追加一行