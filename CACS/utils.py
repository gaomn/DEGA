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

# ======== 1. 保持这部分不变：定义多目标适应度 ========
creator.create("Fitness", base.Fitness, weights=(-1.0, -1.0))  # 两个目标，皆需最小化
creator.create("Individual", np.ndarray, fitness=creator.Fitness)

# ======== 2. 将Individual改为存储“任务-联盟”编码 ========
class Individual:
    def __init__(self, genome, fitness=None):
        """
        genome示例结构:
        genome = {
            'task_alliance_list': [
                {'task_id': t0, 'alliance': [r1, r2, ...]},
                {'task_id': t1, 'alliance': [r0, r3, ...]},
                ...
            ]
        }
        """
        if fitness is None:
            fitness = creator.Fitness()
        self.genome = genome
        self.fitness = fitness


def evaluate(individual, ins):
    """
    使用事件驱动的方式对个体的调度方案进行仿真，并计算:
    1) total_time: 所有火点被灭火的完成时间(最大结束时间)
    2) total_distance: 所有机器人移动总距离
    """
    # ======== 3. 读取基因中的“任务-联盟”编码 ========
    # 形如: [{'task_id': 0, 'alliance': [0, 2]}, {'task_id': 1, 'alliance': [1]}, ...]
    task_alliance_list = individual.genome['task_alliance_list']

    # ======== 4. 从问题实例 ins 中获取必要信息 ========
    robot_num = ins._robNum
    task_num = ins._taskNum
    
    # 火势增长相关
    task_growth_rates = ins._taskRateLst      # 每个着火点的火势增长率 G_i
    task_initial_states = ins._taskStateLst   # 每个着火点的初始火势 F_i(0)
    
    # 机器人属性
    robot_velocities = ins._robVelLst         # 机器人移动速度
    robot_abilities = ins._robAbiLst          # 机器人灭火能力
    robot_positions = [(ins._rob_x_lst[i], ins._rob_y_lst[i]) for i in range(robot_num)]  # 机器人起始坐标
    
    # 任务坐标
    task_positions = [(ins._task_x_lst[i], ins._task_y_lst[i]) for i in range(task_num)]
    
    # 距离矩阵(预先计算好)
    rob2task_dis_mat = ins._rob2taskDisMat    # 机器人到任务的距离矩阵
    task_dis_mat = ins._taskDisMat           # 任务之间的距离矩阵
    
    # ======== 5. 根据“任务-联盟”结构，反向构建每个机器人的任务执行序列 ========
    #    robot_task_sequences[r] = [t1, t5, t2, ...] 表示第 r 个机器人依次要做的任务
    #    由于无先序约束，这里只是将同一个 task 放进所有参加该 task 的机器人队列里
    #    这样后续事件驱动中，每个机器人按先后顺序执行自己的任务队列。
    robot_task_sequences = [[] for _ in range(robot_num)]
    real_robot_task_alliance_list = [[] for _ in range(robot_num)]
    
    # 为避免同一个机器人在“理论并行”时出现冲突，这里默认按照 task_alliance_list 的顺序依次加入
    # 如果确有并行需求，事件驱动逻辑会自动处理是否需要等待。
    for item in task_alliance_list:
        t_id = item['task_id']
        alliance = item['alliance']  # 参与该任务的机器人列表
        for r in alliance:
            robot_task_sequences[r].append(t_id)
            real_robot_task_alliance_list[r].append(t_id)
    # print(real_robot_task_alliance_list)
    # ======== 6. 初始化仿真变量 ========
    # 任务状态: 当前火势
    task_status = task_initial_states.copy()
    # 记录任务上一次更新火势的时间
    task_last_update_time = [0.0] * task_num
    # 当前正在灭火的机器人集合
    task_robots = [[] for _ in range(task_num)]
    # 记录任务完成时间
    task_completion_times = [float('inf')] * task_num

    # 机器人状态 (time: 当前时间, position: 当前位置, task_index: 当前已执行到的任务序号下标)
    robot_states = [{'time': 0.0, 'position': robot_positions[r], 'task_index': 0} for r in range(robot_num)]
    
    # 移动总距离
    total_distance = 0.0
    
    # 事件优先队列 (time, event_type, robot_id, task_id)
    event_queue = []
    
    # ======== 7. 为每个机器人调度第一个任务的“到达事件” ========
    for r in range(robot_num):
        seq = robot_task_sequences[r]
        if seq:
            first_task = seq[0]
            distance = rob2task_dis_mat[r][first_task]
            travel_time = distance / robot_velocities[r]
            arrival_time = robot_states[r]['time'] + travel_time
            
            # 将到达事件推入优先队列
            heapq.heappush(event_queue, (arrival_time, 'arrival', r, first_task))
            
            # 更新机器人状态
            robot_states[r]['time'] = arrival_time
            robot_states[r]['position'] = task_positions[first_task]
            total_distance += distance
    
    current_time = 0.0  # 全局仿真时钟

    # ======== 8. 辅助函数：更新所有任务的火势状态到当前时刻 ========
    def update_task_statuses(time_increment):
        nonlocal current_time
        for t in range(task_num):
            if task_status[t] > 0:
                # 当前在t任务上的机器人能力总和
                total_ability = sum(robot_abilities[r] for r in task_robots[t])
                # 净增长率 = 火势增长率 - 机器人总能力
                net_rate = task_growth_rates[t] - total_ability
                # 更新火势
                task_status[t] += net_rate * time_increment
                # 火势不得低于0
                if task_status[t] <= 0:
                    task_status[t] = 0
                    task_completion_times[t] = current_time
        # 同步更新上一次火势更新时间
        for t in range(task_num):
            task_last_update_time[t] = current_time

    # ======== 9. 核心事件循环 ========
    while event_queue:
        event = heapq.heappop(event_queue)
        event_time, event_type, robot_id, task_id = event
        
        time_increment = event_time - current_time
        current_time = event_time
        
        # 先把火势状态更新到这个时间点
        update_task_statuses(time_increment)
        
        if event_type == 'arrival':
            # 机器人到达任务点
            task_robots[task_id].append(robot_id)
            
            if task_status[task_id] <= 0:
                # 如果到达时火已经被扑灭了，直接调度下一任务
                next_task_index = robot_states[robot_id]['task_index'] + 1
                seq = robot_task_sequences[robot_id]
                if next_task_index < len(seq):
                    next_task = seq[next_task_index]
                    distance = task_dis_mat[task_id][next_task]
                    travel_time = distance / robot_velocities[robot_id]
                    arrival_time = current_time + travel_time
                    
                    heapq.heappush(event_queue, (arrival_time, 'arrival', robot_id, next_task))
                    
                    # 更新机器人状态
                    robot_states[robot_id]['time'] = arrival_time
                    robot_states[robot_id]['position'] = task_positions[next_task]
                    robot_states[robot_id]['task_index'] = next_task_index
                    total_distance += distance
                # 若没下一个任务，该机器人就结束了
            else:
                # 如果火势还在，则计算是否可以扑灭
                total_ability = sum(robot_abilities[r] for r in task_robots[task_id])
                net_rate = task_growth_rates[task_id] - total_ability
                if net_rate >= 0:
                    # 火势无法下降，需要等待更多机器人或持续增长
                    pass
                else:
                    # 可以灭火，则根据剩余火势安排完成事件
                    remaining_fire = task_status[task_id]
                    extinguish_time = -remaining_fire / net_rate
                    completion_time = current_time + extinguish_time
                    
                    # 检查是否已有完成事件在队列
                    existing_completion = [e for e in event_queue if e[1] == 'completion' and e[3] == task_id]
                    if not existing_completion:
                        heapq.heappush(event_queue, (completion_time, 'completion', None, task_id))
        
        elif event_type == 'completion':
            # 任务完成时，把火势置0
            task_status[task_id] = 0
            task_completion_times[task_id] = current_time
            
            # 让在此任务上的机器人去下一个任务
            for r in task_robots[task_id]:
                next_task_index = robot_states[r]['task_index'] + 1
                seq = robot_task_sequences[r]
                if next_task_index < len(seq):
                    next_task = seq[next_task_index]
                    distance = task_dis_mat[task_id][next_task]
                    travel_time = distance / robot_velocities[r]
                    arrival_time = current_time + travel_time
                    
                    heapq.heappush(event_queue, (arrival_time, 'arrival', r, next_task))
                    
                    # 更新机器人状态
                    robot_states[r]['time'] = arrival_time
                    robot_states[r]['position'] = task_positions[next_task]
                    robot_states[r]['task_index'] = next_task_index
                    total_distance += distance
            
            # 清空此任务上的机器人
            task_robots[task_id].clear()

    # ======== 10. 仿真结束后，计算总体完工时间(所有机器人最后的时间) ========
    total_time = max(robot_states[r]['time'] for r in range(robot_num))

    # 检查是否所有任务均被灭
    if any(task_status[t] > 0 for t in range(task_num)):
        total_time = float('inf')
        total_distance = float('inf')

    # 返回两个目标: 完成时间 与 移动距离
    return total_time, total_distance, robot_task_sequences


def save_data_to_npy(datas, save_path, name, sample_id, ifprint=False):
    """
    用于保存结果的函数，可保持不变
    """
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
