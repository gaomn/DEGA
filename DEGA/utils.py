import heapq
import os
import json
import numpy as np
from deap import base
from deap import creator

creator.create("Fitness", base.Fitness, weights=(-1.0, -1.0))  # 假设您有2个目标是最小化
creator.create("Individual", np.ndarray, fitness=creator.Fitness)


class Individual:
    def __init__(self, genome, fitness=None):
        if fitness is None:
            fitness = creator.Fitness()
        self.genome = genome
        self.fitness = fitness


def evaluate(individual, ins):
    """
    进行仿真，返回 (总时间, 总距离)。
    同时，也会在函数内部构建 robot_task_sequences。
    """
    genome = individual.genome
    R = genome['R']  # Global task sequence
    X = genome['X']  #
    robot_num = ins._robNum
    task_num = ins._taskNum

    # Access necessary data from the instance (assuming these are defined)
    task_growth_rates = ins._taskRateLst  # Fire growth rates for tasks
    task_initial_states = ins._taskStateLst  # Initial fire levels
    robot_velocities = ins._robVelLst  # Robot movement speeds
    robot_abilities = ins._robAbiLst  # Robot firefighting abilities
    robot_positions = [(ins._rob_x_lst[i], ins._rob_y_lst[i]) for i in range(robot_num)]  # Starting positions
    task_positions = [(ins._task_x_lst[i], ins._task_y_lst[i]) for i in range(task_num)]  # Task positions
    rob2task_dis_mat = ins._rob2taskDisMat  # Precomputed distances from robots to tasks
    task_dis_mat = ins._taskDisMat  # Precomputed distances between tasks

    # Build robot task sequences based on assignment and global task order
    robot_task_sequences = [[] for _ in range(robot_num)]
    for robot in range(robot_num):
        # Tasks assigned to this robot
        tasks_assigned = [j for j in range(task_num) if X[robot][j] == 1]
        # Order tasks according to R
        tasks_ordered = [task for task in R if task in tasks_assigned]
        robot_task_sequences[robot] = tasks_ordered
    real_robot_task_sequences = [[] for _ in range(robot_num)]

    # Initialize variables
    task_status = task_initial_states.copy()  # 当前每个任务的火势
    task_last_update_time = [0.0] * task_num
    task_robots = [[] for _ in range(task_num)]  # 每个任务当前有哪些机器人在执行
    task_completion_times = [float('inf')] * task_num

    robot_states = [{'time': 0.0, 'position': robot_positions[r], 'task_index': 0} for r in range(robot_num)]
    total_distance = 0.0

    # 事件队列，用来做离散事件仿真
    event_queue = []

    # 初始化：把所有机器人的首个任务事件压入 event_queue
    for r in range(robot_num):
        sequence = robot_task_sequences[r]
        if sequence:
            first_task = sequence[0]
            real_robot_task_sequences[r] = [first_task]
            # 距离 = 机器人到第一个任务的距离
            distance = rob2task_dis_mat[r][first_task]
            travel_time = distance / robot_velocities[r]
            arrival_time = robot_states[r]['time'] + travel_time
            heapq.heappush(event_queue, (arrival_time, 'arrival', r, first_task))
            # 更新机器人状态
            robot_states[r]['time'] = arrival_time
            robot_states[r]['position'] = task_positions[first_task]
            total_distance += distance

    current_time = 0.0  # 全局仿真时间

    def update_task_statuses(time_increment):
        """在每次事件发生前，统一更新所有任务的火势。"""
        nonlocal current_time
        for t in range(task_num):
            if task_status[t] > 0:
                # 当前任务的总灭火能力
                total_ability = sum(robot_abilities[r] for r in task_robots[t])
                net_rate = task_growth_rates[t] - total_ability
                # 更新火势
                task_status[t] += net_rate * time_increment
                if task_status[t] <= 0:
                    task_status[t] = 0
                    task_completion_times[t] = current_time
        # 更新最后一次火势刷新时间
        for t in range(task_num):
            task_last_update_time[t] = current_time

    # 开始事件循环
    while event_queue:
        event = heapq.heappop(event_queue)
        event_time, event_type, robot_id, task_id = event
        time_increment = event_time - current_time
        current_time = event_time

        # 每次弹出一个事件时，先同步更新任务火势
        update_task_statuses(time_increment)

        if event_type == 'arrival':
            # 机器人到达任务
            task_robots[task_id].append(robot_id)
            # 如果任务已经被灭完了，则直接寻找下一个任务
            if task_status[task_id] <= 0:
                next_task_index = robot_states[robot_id]['task_index'] + 1
                sequence = robot_task_sequences[robot_id]
                if next_task_index < len(sequence):
                    next_task = sequence[next_task_index]
                    real_robot_task_sequences[robot_id].append(next_task)
                    distance = task_dis_mat[task_id][next_task]
                    travel_time = distance / robot_velocities[robot_id]
                    arrival_time = current_time + travel_time
                    heapq.heappush(event_queue, (arrival_time, 'arrival', robot_id, next_task))
                    # 更新机器人状态
                    robot_states[robot_id]['time'] = arrival_time
                    robot_states[robot_id]['position'] = task_positions[next_task]
                    robot_states[robot_id]['task_index'] = next_task_index
                    total_distance += distance
            else:
                # 该任务尚未完成
                total_ability = sum(robot_abilities[r] for r in task_robots[task_id])
                net_rate = task_growth_rates[task_id] - total_ability
                if net_rate < 0:
                    # 可以灭火，预计完成时间
                    remaining_fire = task_status[task_id]
                    extinguish_time = -remaining_fire / net_rate
                    completion_time = current_time + extinguish_time
                    # 若没有同一个task_id的灭火完成事件，则创建一个
                    existing_completion_events = [
                        e for e in event_queue if (e[1] == 'completion' and e[3] == task_id)
                    ]
                    if not existing_completion_events:
                        heapq.heappush(event_queue, (completion_time, 'completion', None, task_id))

        elif event_type == 'completion':
            # 任务完成
            task_status[task_id] = 0
            task_completion_times[task_id] = current_time
            # 此任务上的所有机器人去下一个任务
            for r in task_robots[task_id]:
                next_task_index = robot_states[r]['task_index'] + 1
                sequence = robot_task_sequences[r]
                if next_task_index < len(sequence):
                    next_task = sequence[next_task_index]
                    real_robot_task_sequences[r].append(next_task)
                    distance = task_dis_mat[task_id][next_task]
                    travel_time = distance / robot_velocities[r]
                    arrival_time = current_time + travel_time
                    heapq.heappush(event_queue, (arrival_time, 'arrival', r, next_task))
                    # 更新机器人状态
                    robot_states[r]['time'] = arrival_time
                    robot_states[r]['position'] = task_positions[next_task]
                    robot_states[r]['task_index'] = next_task_index
                    total_distance += distance
            # 清空任务上的机器人列表
            task_robots[task_id].clear()

    # 所有事件处理完毕后，计算完成时间（makespan）
    total_time = max(robot_states[r]['time'] for r in range(robot_num))

    # 检查是否所有任务都已完成
    if any(task_status[t] > 0 for t in range(task_num)):
        # 如果还有任务火势大于0，说明没完成
        total_time = float('inf')
        total_distance = float('inf')

    # 这里返回的是总时间和总距离，以及机器人任务序列
    return total_time, total_distance, real_robot_task_sequences


def save_data_to_npy(datas, save_path, name, sample_id, ifprint=False):
    """
    保存多次迭代后种群中个体的 fitness 到 npy 文件。
    """
    top_fitnesses = np.array([ind.fitness.values for ind in datas])
    save_path = os.path.join(save_path, f'GA_{sample_id}_{name}.npy')
    np.save(save_path, top_fitnesses)
    if ifprint:
        print(
            f"Benchmark: {name} | Min Fitness: ("
            f"time: {min([ind.fitness.values[0] for ind in datas]):.2E}, "
            f"distance: {min([ind.fitness.values[1] for ind in datas]):.2E})\n"
        )


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

