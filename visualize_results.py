#!/usr/bin/env python3
"""
MPDA结果可视化工具
用于绘制多无人机任务分配的路径图和结果分析
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
from utils.mpdaInstance import MPDAInstance
from matplotlib.legend_handler import HandlerLine2D

class ArrowLineHandler(HandlerLine2D):
    """自定义图例处理器，在路径线上添加箭头"""
    def create_artists(self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans):
        line, = super().create_artists(legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans)
        arrow = plt.arrow(xdescent + width*0.6, ydescent + height/2, width*0.3, 0,
                         head_width=height*0.3, head_length=width*0.2, 
                         fc=line.get_color(), ec=line.get_color())
        return [line, arrow]


def load_best_scheme(json_file, max_market="d"):
    """
    从JSONL文件中加载每个解的时间、距离、方案，然后按时间或距离排序，
    返回最短距离或最短时间的方案。

    :param json_file: JSONL 文件路径
    :param max_market: 优先排序的目标 ('t' 表示时间, 'd' 表示距离)
    :return: 最优或次优方案
    """
    solutions = []

    # 加载所有方案到列表
    with open(json_file, 'r', encoding='utf-8') as file:
        for line in file:
            data = json.loads(line.strip())
            solutions.append((data["time"], data["distance"], data["scheme"]))

    # 按时间或距离排序
    if max_market == "d":
        # 按距离排序
        solutions.sort(key=lambda x: x[1])
    else:
        # 按时间排1
        solutions.sort(key=lambda x: x[0])

    # 选择最优方案
    best_scheme = solutions[0][2]  # 最优方案

    return best_scheme

def plot_robot_paths(ins_file, scheme, save_path=None, arrow_interval=1500):
    """
    根据 ins 文件和 scheme 绘制机器人路径图，并在路径上间隔一定距离绘制箭头。
    
    :param ins_file: ins 文件路径
    :param scheme: 每个机器人执行的任务方案
    :param save_path: 保存绘图的路径
    :param arrow_interval: 箭头间隔距离
    """
    # 加载 ins 文件
    ins = MPDAInstance()
    ins.loadCfg(fileName=ins_file)
    
    # 提取任务点坐标和机器人起始位置
    task_positions = [(ins._task_x_lst[i], ins._task_y_lst[i]) for i in range(len(ins._task_x_lst))]
    robot_positions = [(ins._rob_x_lst[i], ins._rob_y_lst[i]) for i in range(len(ins._rob_x_lst))]
    # 位置全部-=50
    task_positions = [(100*(x-50), 100*(y-50)) for x, y in task_positions]
    robot_positions = [(100*(x-50), 100*(y-50)) for x, y in robot_positions]
    
    # 绘制任务点
    task_x, task_y = zip(*task_positions)


    bobot_x, bobot_y = zip(*robot_positions)
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['mathtext.fontset'] = 'stix'  # 数学字体也使用 Times New Roman

    # plt.scatter(task_x, task_y, c='g', marker='s', label="Task", s=10)  # 蓝色正方形表示任务点
    # plt.scatter(bobot_x, bobot_y, c='gray', marker='o', label="Start", s=100)  # 红色圆形表示机器人起始位置

    plt.scatter(task_x, task_y, c='g', marker='s', label="Task", s=10)
    plt.scatter(bobot_x, bobot_y, c='gray', marker='o', label="Start", s=100)



    markers = ['o', 'v', '^', '<', '>', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X']
    # 为每个机器人分配不同颜色
    # colors = plt.colormaps["tab10"]
    colors = ['#FF0000', '#0000FF', '#00FF00', '#FFD700', '#000000', '#FF1493', '#00FFFF', '#FF8C00', '#8A2BE2', '#006400']
    
    # 绘制机器人路径
    robot_id_set = set()
    
    for i, robot_data in enumerate(scheme):
        robot_id = robot_data['robot']
        if robot_id in robot_id_set:
            continue

        robot_id_set.add(robot_id)
        tasks = robot_data['task']
        # color = colors(robot_id / len(scheme))  # 分配颜色
        color = colors[i % len(colors)]
        marker = markers[i % len(markers)]  # 循环使用标记样式
        
        # 获取机器人路径的坐标
        path_positions = [robot_positions[robot_id]] + [task_positions[task] for task in tasks]
        path_x, path_y = zip(*path_positions)
        path_x = np.array(path_x) + np.random.uniform(-0.1, 0.1, len(path_x))
        path_y = np.array(path_y) + np.random.uniform(-0.1, 0.1, len(path_y))
        
        # 绘制路径的线条
        # plt.plot(path_x, path_y, '-', color=color, label=f'Robot {robot_id}')
        line = plt.plot(path_x, path_y, '-', color=color, label=f'Robot {robot_id}')[0]
           
        
        # 绘制间隔箭头
        total_length = 0
        for j in range(len(path_x) - 1):
            # 计算线段的长度
            dx = path_x[j + 1] - path_x[j]
            dy = path_y[j + 1] - path_y[j]
            segment_length = (dx**2 + dy**2)**0.5
            
            # 在这段线段上按间隔距离绘制箭头
            while total_length < segment_length:
                # 算出箭头的绘制位置
                arrow_x = path_x[j] + dx * (total_length / segment_length)
                arrow_y = path_y[j] + dy * (total_length / segment_length)
                plt.arrow(
                    arrow_x, arrow_y, dx * 0.1, dy * 0.1,  # 箭头方向
                    head_width=200, head_length=225,
                    fc=color, ec=color, length_includes_head=True
                )
                total_length += arrow_interval  # 增加累计长度
            total_length -= segment_length  # 减去线段长度，更新为下一个段的起点
            
        # 绘制路径点
        # plt.scatter(path_x, path_y, c=[color] * len(path_x), marker=marker, s=50)
    
    # 图例和标题
    # plt.scatter(task_x, task_y, c='blue', marker='s', s=20)  # 蓝色正方形表示任务点
    # plt.scatter(bobot_x, bobot_y, c='red', marker='o', label="Start", s=20)  # 红色圆形表示机器人起始位置
    plt.legend(handler_map={plt.Line2D: ArrowLineHandler()},loc='center left', bbox_to_anchor=(1, 0.5), fontsize = 16)
    # plt.title('Robot Paths with Spaced Arrows')
    plt.xlabel('x coordinate', fontsize=20)
    plt.ylabel('y coordinate', fontsize=20)
    plt.tick_params(axis='both', labelsize=16)
    plt.grid(False)
    if save_path is not None:
        # 保存高清图片
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    # plt.show()
    plt.close()

def process_all_json_files(parent_folder, ins_folder, save_folder):
    """
    遍历父文件夹中的所有子文件夹，读取 JSONL 文件，并绘制机器人路径图。
    
    :param parent_folder: 包含 JSONL 文件的父文件夹
    :param ins_folder: 包含 .txt ins 文件的文件夹
    :param save_folder: 保存绘图的目标文件夹
    """
    # 如果目标文件夹不存在，则创建
    os.makedirs(save_folder, exist_ok=True)

    for root, _, files in os.walk(parent_folder):
        for file in files:
            # if file.endswith(".jsonl"):
            if file.endswith(".jsonl") and "3.95" in file:
                json_file = os.path.join(root, file)
                
                # 提取文件名（如 "L_20_60_1.51"）作为实例名
                instance_name = os.path.splitext(file)[0]
                ins_file = os.path.join(ins_folder, f"{instance_name}.txt")
                
                # 检查 ins 文件是否存在
                if not os.path.exists(ins_file):
                    print(f"Warning: {ins_file} does not exist. Skipping...")
                    continue

                # 保存绘图文件路径
                method = os.path.basename(parent_folder)
                method_save_folder = os.path.join(save_folder, method)
                os.makedirs(method_save_folder, exist_ok=True)
                save_path = os.path.join(method_save_folder, f"{instance_name}.pdf")
                
                # 加载最优方案并绘制
                scheme = load_best_scheme(json_file)
                if scheme:
                    print(f"Processing {json_file}...")
                    plot_robot_paths(ins_file, scheme, save_path=save_path)
                else:
                    print(f"No valid scheme found in {json_file}. Skipping...")


if __name__ == "__main__":
    # 示例路径（请替换为实际路径）
    parent_folder = "./plot_data/DEGA"  # 包含 JSONL 文件的父文件夹
    ins_folder = "./AllInstance"  # 包含 .txt ins 文件的文件夹
    save_folder = "./fig"  # 保存绘图的目标文件夹

    # name = "M_15_30_2.16"
    # ins_file = f"./AllInstance/{name}.txt"
    # json_file = f"./plot_data/{method}/{name}.jsonl"
    # base_save_path = f"./fig"

    # 调用函数处理所有 JSON 文件
    process_all_json_files(parent_folder, ins_folder, save_folder)