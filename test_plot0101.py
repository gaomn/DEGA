import os
import json
import numpy as np
import matplotlib.pyplot as plt
from itertools import islice
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
from matplotlib.patches import ConnectionPatch

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
                          xlabel='Time(s)', ylabel='Distance(m)',
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
    
    plt.figure(figsize=(12, 8))
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
        # plt.plot(pf[:, 0], pf[:, 1], c=c, linestyle='--')
    
    # 设置坐标轴
    plt.xlabel(xlabel, fontsize=20, fontweight='bold')
    plt.ylabel(ylabel, fontsize=20, fontweight='bold')
    if xlim: plt.xlim(xlim)
    if ylim: plt.ylim(ylim)
    
    plt.tick_params(axis='both', labelsize=16)
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.legend(fontsize=14)
    
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.savefig(save_path.replace(".pdf", ".png"), dpi=300, bbox_inches='tight')
    plt.show()
    plt.close()
    print(f"Saved overall figure to {save_path}")


def plot_all_methods_pareto_inset2(parent_folder, save_path, 
                          xlabel='Time(s)', ylabel='Distance(m)',
                          xscale='linear', yscale='linear',
                          xlim=None, ylim=None,
                          inset_xlim=(0, 50000), inset_ylim=(1000, 3000)):
    """
    遍历所有方法的JSONL文件并绘制帕累托前沿，并添加局部放大的子图。
    
    参数:
        parent_folder: 父文件夹路径
        save_path: 保存路径
        xlabel, ylabel: 坐标轴标签
        xscale, yscale: 坐标类型 ('linear','log','symlog')
        xlim, ylim: 坐标轴范围 (tuple)
        inset_xlim, inset_ylim: 子图的坐标范围
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
    
    fig, ax = plt.subplots(figsize=(12, 8))
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['mathtext.fontset'] = 'stix'
    
    # 设置坐标轴类型
    ax.set_xscale(xscale)
    ax.set_yscale(yscale)
    
    # 绘制帕累托前沿
    for i, (m, pf) in enumerate(method_pareto.items()):
        c = colors[i % len(colors)]
        mk = markers[i % len(markers)]
        ax.scatter(pf[:, 0], pf[:, 1], label=m, c=c, marker=mk, s=50)
    
    # 设置坐标轴
    ax.set_xlabel(xlabel, fontsize=20, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=20, fontweight='bold')
    if xlim: ax.set_xlim(xlim)
    if ylim: ax.set_ylim(ylim)
    
    ax.tick_params(axis='both', labelsize=16)
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.legend(fontsize=14)
    
    # 添加子图
    ax_inset = inset_axes(ax, width="40%", height="40%", loc='upper right')
    for i, (m, pf) in enumerate(method_pareto.items()):
        c = colors[i % len(colors)]
        mk = markers[i % len(markers)]
        ax_inset.scatter(pf[:, 0], pf[:, 1], c=c, marker=mk, s=20)
    
    ax_inset.set_xlim(inset_xlim)
    ax_inset.set_ylim(inset_ylim)
    ax_inset.set_xscale(xscale)
    ax_inset.set_yscale(yscale)
    ax_inset.tick_params(axis='both', labelsize=12)
    ax_inset.grid(True, linestyle='--', alpha=0.3)
    
    # 添加矩形框
    rect = Rectangle((inset_xlim[0], inset_ylim[0]), 
                     inset_xlim[1] - inset_xlim[0], 
                     inset_ylim[1] - inset_ylim[0],
                     linewidth=1.5, edgecolor='black', facecolor='none', linestyle='--')
    ax.add_patch(rect)
    
    # 子图角点位置
    inset_bbox = ax_inset.get_position()
    fig_x, fig_y = fig.transFigure.transform((inset_bbox.x0, inset_bbox.y0))
    inset_width, inset_height = fig.transFigure.transform((inset_bbox.width, inset_bbox.height))
    inset_top_left = (fig_x, fig_y + inset_height)
    inset_bottom_left = (fig_x, fig_y)

    # 矩形框角点
    main_rect_top_left = (inset_xlim[0], inset_ylim[1])
    main_rect_bottom_left = (inset_xlim[0], inset_ylim[0])

    # 添加连接线条
    ax.plot(
        [main_rect_top_left[0], inset_top_left[0]],
        [main_rect_top_left[1], inset_top_left[1]],
        linestyle='--', color='black'
    )
    ax.plot(
        [main_rect_bottom_left[0], inset_bottom_left[0]],
        [main_rect_bottom_left[1], inset_bottom_left[1]],
        linestyle='--', color='black'
    )
    
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.savefig(save_path.replace(".pdf", ".png"), dpi=300, bbox_inches='tight')
    plt.show()
    plt.close()
    print(f"Saved overall figure to {save_path}")




def plot_all_methods_pareto_inset(parent_folder, save_path, 
                          xlabel='Time(s)', ylabel='Distance(m)',
                          xscale='linear', yscale='linear',
                          xlim=None, ylim=None,
                          inset_xlim=(0, 50000), inset_ylim=(1000, 3500)):
    """
    Plot Pareto fronts for all methods with an inset zoom plot.
    
    Parameters:
        parent_folder: Parent folder path
        save_path: Save path
        xlabel, ylabel: Axis labels
        xscale, yscale: Scale type ('linear','log','symlog')
        xlim, ylim: Axis limits (tuple)
        inset_xlim, inset_ylim: Inset plot axis limits
    """
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'cyan', 'magenta', 'black']
    markers = ['o', 's', '^', 'D', 'v', 'P', 'X', '*']
    
    method_pareto = {}
    
    # Load and process data (same as original)
    for root, _, files in os.walk(parent_folder):
        method = os.path.basename(root)
        all_solutions = []
        for file in files:
            if file.endswith(".jsonl") and "3.95" in file:
                json_file = os.path.join(root, file)
                pf = load_and_get_pareto(json_file)
                if pf is not None:
                    all_solutions.append(pf)
        if all_solutions:
            merged_solutions = np.vstack(all_solutions)
            final_pf = fast_non_dominated_sort(merged_solutions)
            final_pf = final_pf[final_pf[:, 0].argsort()]
            method_pareto[method] = final_pf
    
    # Create main figure
    fig, ax = plt.subplots(figsize=(12, 8))
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['mathtext.fontset'] = 'stix'
    
    # Set scale type
    ax.set_xscale(xscale)
    ax.set_yscale(yscale)
    
    # Plot Pareto fronts in main plot
    legend_elements = []
    for i, (m, pf) in enumerate(method_pareto.items()):
        c = colors[i % len(colors)]
        mk = markers[i % len(markers)]
        ax.scatter(pf[:, 0], pf[:, 1], c=c, marker=mk, s=50)
        # Create legend element
        legend_elements.append(Line2D([0], [0], marker=mk, color=c, 
                                    label=m, markersize=8, linestyle='None'))
    
    # Set axis labels and limits
    ax.set_xlabel(xlabel, fontsize=20, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=20, fontweight='bold')
    if xlim: ax.set_xlim(xlim)
    if ylim: ax.set_ylim(ylim)
    
    ax.tick_params(axis='both', labelsize=16)
    ax.grid(True, linestyle='--', alpha=0.3)
    
    # Add legend with enhanced visibility
    ax.legend(handles=legend_elements, fontsize=14, 
             bbox_to_anchor=(1.15, 1), loc='upper right',
             borderaxespad=0.)
    
    # Create inset axes
    ax_inset = inset_axes(ax, width="40%", height="40%", 
                         loc='upper right', borderpad=2)
    
    # Plot Pareto fronts in inset
    for i, (m, pf) in enumerate(method_pareto.items()):
        c = colors[i % len(colors)]
        mk = markers[i % len(markers)]
        ax_inset.scatter(pf[:, 0], pf[:, 1], c=c, marker=mk, s=20)
    
    # Configure inset
    ax_inset.set_xlim(inset_xlim)
    ax_inset.set_ylim(inset_ylim)
    ax_inset.set_xscale(xscale)
    ax_inset.set_yscale(yscale)
    ax_inset.tick_params(axis='both', labelsize=12)
    ax_inset.grid(True, linestyle='--', alpha=0.3)
    
    # Add rectangle in main plot to show zoomed region
    rect = Rectangle((inset_xlim[0], inset_ylim[0]), 
                    inset_xlim[1] - inset_xlim[0], 
                    inset_ylim[1] - inset_ylim[0],
                    linewidth=1.5, edgecolor='black', 
                    facecolor='none', linestyle='--')
    ax.add_patch(rect)
    rect_top_left = (inset_xlim[0], inset_ylim[1])
    rect_bottom_left = (inset_xlim[0], inset_ylim[0])
    rect_top_right = (inset_xlim[1], inset_ylim[1])
    rect_bottom_right = (inset_xlim[1], inset_ylim[0])
    # Get inset position for connecting lines
    inset_bbox = ax_inset.get_position()
    figure_to_data = fig.transFigure.inverted().transform
    inset_corners_data = fig.transFigure.inverted().transform([
        fig.transFigure.transform((inset_bbox.x0, inset_bbox.y1)),  # 左上
        fig.transFigure.transform((inset_bbox.x1, inset_bbox.y1)),  # 右上
        fig.transFigure.transform((inset_bbox.x1, inset_bbox.y0)),  # 右下
        fig.transFigure.transform((inset_bbox.x0, inset_bbox.y0))   # 左下
    ])
    con_top = ConnectionPatch(xyA=rect_top_right, coordsA=ax.transData,
                             xyB=(0, 1), coordsB=ax_inset.transAxes,
                             arrowstyle="->", linewidth=1, color='black', linestyle='--')
    
    con_bottom = ConnectionPatch(xyA=rect_bottom_right, coordsA=ax.transData,
                                xyB=(0, 0), coordsB=ax_inset.transAxes,
                                arrowstyle="->", linewidth=1, color='black', linestyle='--')
    
    ax.add_artist(con_top)
    ax.add_artist(con_bottom)


    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.savefig(save_path.replace(".pdf", ".png"), dpi=300, bbox_inches='tight')
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

    plot_all_methods_pareto_inset(
        parent_folder, 
        save_path,
        xscale='linear',  # 对数坐标
        yscale='linear',  # 线性坐标
    )