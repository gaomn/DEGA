# -*- coding: UTF-8 -*-
# @Date    :2024/4/23 15:42
# @Author  :高猛
# @Project :GA_test 
# @File    :utils.py
# @IDE     :PyCharm

import heapq
import os
import json
import numpy as np
from deap import base
from deap import creator

# 假设您有2个目标需要最小化,如果已经被创建，则不需要再次创建
if not creator.Fitness.weights:
    creator.create("Fitness", base.Fitness, weights=(-1.0, -1.0))
if not creator.Individual.fitness:
    creator.create("Individual", list, fitness=creator.FitnessMin)


# creator.create("Fitness", base.Fitness, weights=(-1.0, -1.0))
# creator.create("Individual", np.ndarray, fitness=creator.Fitness)


class Individual:
    def __init__(self, genome, fitness=None):
        if fitness is None:
            fitness = creator.Fitness()
        self.genome = genome
        self.fitness = fitness


def evaluate(individual, ins):
    """
    评估函数：
    1) 使用新的编码：genome = {'paths': [...]}，
       其中 paths[robot] 表示第 robot 个机器人的任务序列（列表）。
    2) 通过事件模拟，计算在本次分配/调度方案下所有火点被扑灭的总时间以及总移动距离。
    """
    # 从个体中获取新的编码
    genome = individual.genome
    # "paths" 是一个列表，长度为机器人数量，每个元素是一条任务路径
    paths = genome['paths']

    # 基础信息
    robot_num = ins._robNum
    task_num = ins._taskNum

    # 火势相关参数
    task_growth_rates = ins._taskRateLst  # 每个任务的火势自然增长率
    task_initial_states = ins._taskStateLst  # 每个任务的初始火势
    # 机器人相关参数
    robot_velocities = ins._robVelLst     # 机器人移动速度
    robot_abilities = ins._robAbiLst      # 机器人灭火能力
    # 位置相关
    robot_positions = [
        (ins._rob_x_lst[i], ins._rob_y_lst[i]) for i in range(robot_num)
    ]  # 机器人初始位置
    task_positions = [
        (ins._task_x_lst[i], ins._task_y_lst[i]) for i in range(task_num)
    ]  # 火点位置

    # 距离矩阵
    rob2task_dis_mat = ins._rob2taskDisMat  # 机器人到任务的距离
    task_dis_mat = ins._taskDisMat         # 任务之间的距离

    # 根据新的编码 "paths" 构建各机器人要访问的任务序列
    robot_task_sequences = [[] for _ in range(robot_num)]
    for r in range(robot_num):
        # 直接使用传进来的路径
        robot_task_sequences[r] = paths[r]

    # ======== 初始化模拟所需变量 ========
    task_status = task_initial_states.copy()       # 当前火势
    task_last_update_time = [0.0] * task_num       # 记录每个任务上次更新时刻
    task_robots = [[] for _ in range(task_num)]    # 正在执行该任务的机器人列表
    task_completion_times = [float('inf')] * task_num  # 任务完成时间
    real_robot_task_sequences = [[] for _ in range(robot_num)]  # 真实的任务序列

    # 机器人状态：当前时间、当前位置、正在访问的任务下标
    robot_states = [
        {'time': 0.0, 'position': robot_positions[r], 'task_index': 0}
        for r in range(robot_num)
    ]
    total_distance = 0.0

    # 事件队列：(事件发生时间, 事件类型, 机器人id, 任务id)
    event_queue = []

    # 让每个机器人前往其序列中的第一个任务
    for r in range(robot_num):
        sequence = robot_task_sequences[r]
        if len(sequence) > 0:
            first_task = sequence[0]
            # 从机器人的初始位置到第一个任务的距离
            distance = rob2task_dis_mat[r][first_task]
            travel_time = distance / robot_velocities[r]
            arrival_time = robot_states[r]['time'] + travel_time
            # 推入事件队列
            heapq.heappush(event_queue, (arrival_time, 'arrival', r, first_task))
            # 更新机器人状态
            robot_states[r]['time'] = arrival_time
            robot_states[r]['position'] = task_positions[first_task]
            total_distance += distance
            real_robot_task_sequences[r] = [first_task]

    current_time = 0.0  # 全局模拟时间

    # 工具函数：更新火势到当前时间
    def update_task_statuses(time_increment):
        nonlocal current_time
        for t in range(task_num):
            if task_status[t] > 0:
                # 当前在此任务上的机器人总能力
                total_ability = sum(robot_abilities[r] for r in task_robots[t])
                net_rate = task_growth_rates[t] - total_ability
                # 火势随时间演化
                task_status[t] += net_rate * time_increment
                # 不允许火势降到0以下
                if task_status[t] <= 0:
                    task_status[t] = 0
                    task_completion_times[t] = current_time
        # 更新最近一次刷新时间
        for t in range(task_num):
            task_last_update_time[t] = current_time

    # ========= 事件处理循环 =========
    while event_queue:
        event = heapq.heappop(event_queue)
        event_time, event_type, robot_id, task_id = event
        # 计算距离上次事件的时间增量
        time_increment = event_time - current_time
        current_time = event_time

        # 更新所有任务火势到当前时刻
        update_task_statuses(time_increment)

        if event_type == 'arrival':
            # 机器人到达任务点
            task_robots[task_id].append(robot_id)

            # 若此时任务已完成（火势为0），则直接去下一任务
            if task_status[task_id] <= 0:
                next_task_index = robot_states[robot_id]['task_index'] + 1
                seq = robot_task_sequences[robot_id]
                if next_task_index < len(seq):
                    next_task = seq[next_task_index]
                    dist = task_dis_mat[task_id][next_task]
                    travel_time = dist / robot_velocities[robot_id]
                    arrival_time = current_time + travel_time
                    heapq.heappush(event_queue,
                                   (arrival_time, 'arrival', robot_id, next_task))
                    robot_states[robot_id]['time'] = arrival_time
                    robot_states[robot_id]['position'] = task_positions[next_task]
                    robot_states[robot_id]['task_index'] = next_task_index
                    total_distance += dist
                    real_robot_task_sequences[robot_id].append(next_task)
                # 如果没有后续任务，机器人空闲
            else:
                # 计算净灭火率
                total_ability = sum(robot_abilities[r] for r in task_robots[task_id])
                net_rate = task_growth_rates[task_id] - total_ability
                if net_rate >= 0:
                    # 火势无法被扑灭，需要等待更多机器人或火势继续增长
                    pass
                else:
                    # 估算剩余灭火时间
                    remaining_fire = task_status[task_id]
                    extinguish_time = -remaining_fire / net_rate
                    completion_time = current_time + extinguish_time

                    # 如果还没调度过此任务的完成事件，则创建
                    existing_completion_events = [
                        e for e in event_queue
                        if (e[1] == 'completion' and e[3] == task_id)
                    ]
                    if not existing_completion_events:
                        heapq.heappush(event_queue,
                                       (completion_time, 'completion', None, task_id))

        elif event_type == 'completion':
            # 当前任务火势置0，更新完成时间
            task_status[task_id] = 0
            task_completion_times[task_id] = current_time

            # 让在该任务上的所有机器人前往各自的下一个任务
            for r in task_robots[task_id]:
                next_task_index = robot_states[r]['task_index'] + 1
                seq = robot_task_sequences[r]
                if next_task_index < len(seq):
                    next_task = seq[next_task_index]
                    dist = task_dis_mat[task_id][next_task]
                    travel_time = dist / robot_velocities[r]
                    arrival_time = current_time + travel_time
                    heapq.heappush(event_queue,
                                   (arrival_time, 'arrival', r, next_task))
                    robot_states[r]['time'] = arrival_time
                    robot_states[r]['position'] = task_positions[next_task]
                    robot_states[r]['task_index'] = next_task_index
                    total_distance += dist
                    real_robot_task_sequences[r].append(next_task)
                # 若没有后续任务，则该机器人已完成所有任务

            # 清空此任务上机器人记录
            task_robots[task_id].clear()

    # 所有事件处理完后，计算最大完成时间（makespan）
    total_time = max(robot_states[r]['time'] for r in range(robot_num))

    # 检查是否还有未完成的任务
    if any(task_status[t] > 0 for t in range(task_num)):
        # 如果依旧有火势大于0，说明无法完成任务
        total_time = float('inf')
        total_distance = float('inf')

    # 返回（总时间， 总移动距离）
    return total_time, total_distance, real_robot_task_sequences


def save_data_to_npy(datas, save_path, name, sample_id, ifprint=False):
    top_fitnesses = np.array([ind.fitness.values for ind in datas])
    save_path = os.path.join(save_path, f'GA_{sample_id}_{name}.npy')
    np.save(save_path, top_fitnesses)
    if ifprint:
        print(f"Benchmark: {name} | Min Fitness: ("
              f"time: {min([ind.fitness.values[0] for ind in datas]):.2E}, "
              f"distance: {min([ind.fitness.values[1] for ind in datas]):.2E})\n")
        
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