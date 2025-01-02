import os
import json
import numpy as np
import matplotlib.pyplot as plt
from itertools import islice

def fast_non_dominated_sort(solutions):
    """
    针对2维目标的快速帕累托前沿查找 (time, distance)
    :param solutions: shape (N, 2)，第一列 time，第二列 distance
    :return: 帕累托前沿解
    """
    # 按 time 升序排序
    sorted_data = solutions[solutions[:, 0].argsort()]
    # 扫描寻找 distance 的最优值
    pareto_front = []
    min_dist = float('inf')
    for point in sorted_data:
        if point[1] < min_dist:
            pareto_front.append(point)
            min_dist = point[1]
    return np.array(pareto_front)

def load_and_get_pareto(json_file):
    """
    从指定的JSONL文件读取解集并返回对应的帕累托前沿
    """
    solutions = []
    with open(json_file, 'r', encoding='utf-8') as f:
        while True:
            lines = list(islice(f, 1000))
            if not lines:
                break
            batch = [(json.loads(line)["time"], json.loads(line)["distance"]) for line in lines]

            batch_arr = [(time, distance) for time, distance in batch if 1e-1 <= time < 1e6]
            for p in batch_arr:
                solutions.append(p)
    solutions = np.array(solutions)
    if len(solutions) == 0:
        return None
    pareto_front = fast_non_dominated_sort(solutions)
    pareto_front = pareto_front[pareto_front[:, 0].argsort()]
    return pareto_front

def plot_all_methods_pareto22(parent_folder, save_path):
    """
    遍历所有方法的 JSONL 文件，计算帕累托前沿后，全都绘制在一张图上
    """
    # 定义颜色与标记列表
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'cyan', 'magenta', 'black']
    markers = ['o', 's', '^', 'D', 'v', 'P', 'X', '*']
    
    method_pareto = {}
    
    for root, _, files in os.walk(parent_folder):
        method = os.path.basename(root)
        # 收集本方法下的所有解
        all_solutions = []
        for file in files:
            if file.endswith(".jsonl") and "3.95" in file:
                json_file = os.path.join(root, file)
                pf = load_and_get_pareto(json_file)
                if pf is not None:
                    all_solutions.append(pf)
        # 合并所有解并生成最终帕累托前沿
        if all_solutions:
            merged_solutions = np.vstack(all_solutions)
            final_pf = fast_non_dominated_sort(merged_solutions)
            final_pf = final_pf[final_pf[:, 0].argsort()]
            method_pareto[method] = final_pf
    
    # 绘图
    plt.figure(figsize=(10, 8))
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['mathtext.fontset'] = 'stix'
    
    # 针对每个方法绘制帕累托前沿
    for i, (m, pf) in enumerate(method_pareto.items()):
        c = colors[i % len(colors)]
        mk = markers[i % len(markers)]
        plt.scatter(pf[:, 0], pf[:, 1], label=m, c=c, marker=mk, s=50)
        plt.plot(pf[:, 0], pf[:, 1], c=c, linestyle='--')
    
    plt.xlabel('Time', fontsize=20, fontweight='bold')
    plt.ylabel('Distance', fontsize=20, fontweight='bold')
    plt.tick_params(axis='both', labelsize=16)
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.legend(fontsize=14)
    
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved overall figure to {save_path}")


def plot_all_methods_pareto(parent_folder, save_path, 
                          xlabel='Time', ylabel='Distance',
                          xscale='linear', yscale='linear',
                          xlim=None, ylim=None):
    """
    遍历所有方法的JSONL文件并绘制帕累托前沿
    
    参数:
        parent_folder: 父文件夹路径
        save_path: 保存路径
        xlabel, ylabel: 坐标轴标签
        xscale, yscale: 坐标类型 ('linear','log','symlog')
        xlim, ylim: 坐标轴范围 (tuple)
    """
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'cyan', 'magenta', 'black']
    markers = ['o', 's', '^', 'D', 'v', 'P', 'X', '*']
    
    method_pareto = {}
    
    for root, _, files in os.walk(parent_folder):
        method = os.path.basename(root)
        # 收集本方法下的所有解
        all_solutions = []
        for file in files:
            if file.endswith(".jsonl") and "3.95" in file:
                json_file = os.path.join(root, file)
                pf = load_and_get_pareto(json_file)
                if pf is not None:
                    all_solutions.append(pf)
        # 合并所有解并生成最终帕累托前沿
        if all_solutions:
            merged_solutions = np.vstack(all_solutions)
            final_pf = fast_non_dominated_sort(merged_solutions)
            final_pf = final_pf[final_pf[:, 0].argsort()]
            method_pareto[method] = final_pf
    
    plt.figure(figsize=(10, 8))
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['mathtext.fontset'] = 'stix'
    
    # 设置坐标轴类型
    plt.xscale(xscale)
    plt.yscale(yscale)
    
    # 绘制帕累托前沿
    for i, (m, pf) in enumerate(method_pareto.items()):
        c = colors[i % len(colors)]
        mk = markers[i % len(markers)]
        plt.scatter(pf[:, 0], pf[:, 1], label=m, c=c, marker=mk, s=50)
        plt.plot(pf[:, 0], pf[:, 1], c=c, linestyle='--')
    
    # 设置坐标轴
    plt.xlabel(xlabel, fontsize=20, fontweight='bold')
    plt.ylabel(ylabel, fontsize=20, fontweight='bold')
    if xlim: plt.xlim(xlim)
    if ylim: plt.ylim(ylim)
    
    plt.tick_params(axis='both', labelsize=16)
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.legend(fontsize=14)
    
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()
    plt.close()
    print(f"Saved overall figure to {save_path}")

if __name__ == "__main__":
    parent_folder = "./plot_data"
    save_path = "./fig_pareto/all_methods_pareto.pdf"
    
    # 使用示例:
    # plot_all_methods_pareto(
    #     parent_folder, 
    #     save_path,
    #     xscale='log',  # 对数坐标
    #     yscale='linear',  # 线性坐标
    #     xlim=(1e-3, 1e3),  # x轴范围
    #     ylim=(0, 1000)  # y轴范围
    # )

    plot_all_methods_pareto(
        parent_folder, 
        save_path,
        xscale='linear',  # 对数坐标
        yscale='linear',  # 线性坐标
    )