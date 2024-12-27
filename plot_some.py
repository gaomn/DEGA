import matplotlib.pyplot as plt
import json
import os
from utils.mpdaInstance import MPDAInstance


def load_best_scheme(json_file):
    """
    从 JSONL 文件中读取最优方案。
    
    :param json_file: JSONL 文件路径
    :return: 最短 distance 的 scheme
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


def plot_robot_paths(ins_file, scheme, save_path=None):
    """
    根据 ins 文件和 scheme 绘制机器人路径图。
    
    :param ins_file: ins 文件路径
    :param scheme: 每个机器人执行的任务方案
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
    
    # 为每个机器人分配不同颜色
    colors = plt.colormaps["tab10"]  # 替换为新的 colormap 调用方式
    
    # 绘制机器人路径
    for robot_data in scheme:
        robot_id = robot_data['robot']
        tasks = robot_data['task']
        color = colors(robot_id / len(scheme))  # 分配颜色
        
        # 获取机器人路径的坐标
        path_positions = [robot_positions[robot_id]] + [task_positions[task] for task in tasks]
        path_x, path_y = zip(*path_positions)
        
        # 绘制路径
        plt.plot(path_x, path_y, '-o', label=f'Robot {robot_id}', color=color)
    
    # 图例和标题
    plt.legend()
    plt.title('Robot Paths')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.grid(True)
    if save_path is not None:
        # 保存高清图片
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()


def main(ins_file, json_file, save_path=None):
    """
    主函数，加载 ins 文件和 JSON 文件，并绘制机器人路径图。
    
    :param ins_file: ins 文件路径
    :param json_file: JSON 文件路径
    """
    # 加载最优方案
    scheme = load_best_scheme(json_file)
    # scheme = load_best_scheme_time(json_file)
    
    if not scheme:
        print("Error: No valid scheme found in the JSON file.")
        return
    
    # 绘制机器人路径图
    plot_robot_paths(ins_file, scheme, save_path)


if __name__ == "__main__":
    # 示例文件路径（请替换为实际路径）
    method = "ILS"
    # name = "S_3_10_1.51"
    name = "M_15_30_2.16"
    ins_file = f"./AllInstance/{name}.txt"
    json_file = f"./plot_data/{method}/{name}.jsonl"
    base_save_path = f"./fig"
    os.makedirs(base_save_path, exist_ok=True)
    save_path = os.path.join(base_save_path, f"{method}")
    os.makedirs(save_path, exist_ok=True)
    save_file = os.path.join(save_path, f"{name}.png")
    
    # 调用主函数
    main(ins_file, json_file, save_path=save_file)