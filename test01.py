import os
import json
import matplotlib.pyplot as plt
from utils.mpdaInstance import MPDAInstance
import numpy as np


def load_best_scheme(json_file):
    """
    从 JSONL 文件中读取最优方案（根据最短距离）。
    """
    shortest_distance = float('inf')
    best_scheme = None

    with open(json_file, 'r', encoding='utf-8') as file:
        for line in file:
            data = json.loads(line.strip())
            if data["distance"] < shortest_distance:
                shortest_distance = data["distance"]
                best_scheme = data["scheme"]
    
    return best_scheme

def load_best_scheme_time(json_file):
    shortest_time = float('inf')
    best_scheme = None

    with open(json_file, 'r', encoding='utf-8') as file:
        for line in file:
            data = json.loads(line.strip())
            if data["time"] < shortest_time:
                shortest_time = data["time"]
                best_scheme = data["scheme"]
    
    return best_scheme

def plot_robot_paths_old(ins_file, scheme, save_path=None):
    """
    根据 ins 文件和 scheme 绘制机器人路径图。
    
    :param ins_file: ins 文件路径
    :param scheme: 每个机器人执行的任务方案
    :param save_path: 保存绘图的路径
    """
    # 加载 ins 文件
    ins = MPDAInstance()
    ins.loadCfg(fileName=ins_file)
    
    # 提取任务点坐标和机器人起始位置
    task_positions = [(ins._task_x_lst[i], ins._task_y_lst[i]) for i in range(len(ins._task_x_lst))]
    robot_positions = [(ins._rob_x_lst[i], ins._rob_y_lst[i]) for i in range(len(ins._rob_x_lst))]
    
    # 绘制任务点
    task_x, task_y = zip(*task_positions)
    plt.scatter(task_x, task_y, c='blue', marker='s', label='Tasks', s=50)  # 蓝色正方形表示任务点
    markers = ['o', 'v', '^', '<', '>', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X']
    # 为每个机器人分配不同颜色
    colors = plt.colormaps["tab10"]
    
    # 绘制机器人路径
    task_labes = {"label": [], "color": []}
    robot_id_set = set()
    # for robot_data in scheme:
    for i, robot_data in enumerate(scheme):
        robot_id = robot_data['robot']
        if robot_id in robot_id_set:
            continue

        robot_id_set.add(robot_id)
        tasks = robot_data['task']
        color = colors(robot_id / len(scheme))  # 分配颜色
        marker = markers[i % len(markers)]  # 循环使用标记样式
        
        # 获取机器人路径的坐标
        # path_positions = [robot_positions[robot_id]] + [task_positions[task] for task in tasks]
        # path_x, path_y = zip(*path_positions)
        path_positions = [robot_positions[robot_id]] + [task_positions[task] for task in tasks]
        path_x, path_y = zip(*path_positions)
        path_x = np.array(path_x) + np.random.uniform(-0.1, 0.1, len(path_x))
        path_y = np.array(path_y) + np.random.uniform(-0.1, 0.1, len(path_y))
        
        # 构造标签，限制任务字符串长度
        task_str = f"Robot {robot_id}"
        if len(task_labes["label"]) < 10:
            task_labes["label"].append(task_str)
            task_labes["color"].append(color)
            # plt.plot(path_x, path_y, '-o', label=task_str, color=color)
            plt.plot(path_x, path_y, '-', color=color, label=f'Robot {robot_id}')
            plt.scatter(path_x, path_y, c=[color] * len(path_x), marker=marker, s=50)  # 绘制任务点
        elif len(task_labes["label"]) == 10:
            task_labes["label"].append("...")
            task_labes["color"].append(color)
            # plt.plot(path_x, path_y, '-o', label="...", color=color)
            plt.plot(path_x, path_y, '-', color=color, label=f'...')
            plt.scatter(path_x, path_y, c=[color] * len(path_x), marker=marker, s=50)  # 绘制任务点
        else:
            plt.plot(path_x, path_y, '-', color=color)
            plt.scatter(path_x, path_y, c=[color] * len(path_x), marker=marker, s=50)  # 绘制任务点
    
    # 图例和标题
    plt.legend()
    plt.title('Robot Paths')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.grid(True)
    if save_path is not None:
        # 保存高清图片
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    # plt.show()
    plt.close()

def plot_robot_paths(ins_file, scheme, save_path=None, arrow_interval=100):
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
    
    # 绘制任务点
    task_x, task_y = zip(*task_positions)
    robot_x, robot_y = zip(*robot_positions)
    plt.scatter(task_x, task_y, c='blue', marker='s', label='Tasks', s=30)  # 蓝色正方形表示任务点
    plt.scatter(robot_x, robot_y, c='red', marker='o', label='Start', s=50)  # 红色圆圈表示机器人起始位置
    markers = ['o', 'v', '^', '<', '>', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X']
    linestyles = ['-', '--', '-.', ':', (0, (5, 10)), (0, (3, 5, 1, 5)), (0, (3, 1, 1, 1))]  # 添加更多线条样式

    # 为每个机器人分配不同颜色
    colors = plt.colormaps["tab10"]
    
    # 绘制机器人路径
    robot_id_set = set()
    
    for i, robot_data in enumerate(scheme):
        robot_id = robot_data['robot']
        if robot_id in robot_id_set:
            continue

        robot_id_set.add(robot_id)
        tasks = robot_data['task']
        color = colors(robot_id / len(scheme))  # 分配颜色
        marker = markers[i % len(markers)]  # 循环使用标记样式
        # linestyle = linestyles[i % len(linestyles)]  # 循环使用线条样式
        linestyle = '-'  # 线条样式
        
        # 获取机器人路径的坐标
        path_positions = [robot_positions[robot_id]] + [task_positions[task] for task in tasks]
        path_x, path_y = zip(*path_positions)
        path_x = np.array(path_x) + np.random.uniform(-0.1, 0.1, len(path_x))
        path_y = np.array(path_y) + np.random.uniform(-0.1, 0.1, len(path_y))
        
        # 绘制路径的线条
        plt.plot(path_x, path_y, linestyle=linestyle, color=color, label=f'Robot {robot_id}')
        
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
                    head_width=2, head_length=1.5,
                    fc=color, ec=color, length_includes_head=True
                )
                total_length += arrow_interval  # 增加累计长度
            total_length -= segment_length  # 减去线段长度，更新为下一个段的起点
            
        # 绘制路径点
        plt.scatter(path_x, path_y, c=[color] * len(path_x), marker=marker, s=50)
    
    # 图例和标题
    plt.legend()
    plt.title('Robot Paths with Spaced Arrows')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.grid(True)
    if save_path is not None:
        # 保存高清图片
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()
    plt.close()

def process_all_json_files(parent_folder, ins_folder, save_folder):
    """
    遍历父文件夹中的所有子文件夹，读取 JSONL 文件，并绘制机器人路径图。
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
                save_path = os.path.join(method_save_folder, f"{instance_name}.png")
                
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

    # 调用函数处理所有 JSON 文件
    process_all_json_files(parent_folder, ins_folder, save_folder)