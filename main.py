#!/usr/bin/env python3
"""
Multi-UAV Multi-Task Assignment (MPDA) System
基于双编码遗传算法的多无人机多任务协调分配系统

支持的算法:
- DEGA: 双编码遗传算法 (主要算法)
- ILS: 迭代局部搜索
- MSGA: 多目标遗传算法
- CACS: 协作蚁群系统 (需要参考原论文作者代码)
- MSDE_SPEA2: 多目标差分进化算法

作者: 基于论文 "A Dual-Encoding-based Genetic Algorithm for Multi-Objective Multi-UAV Scheduling in Firefighting Scenarios"
"""

import copy
import datetime
import multiprocessing as mp
import argparse
import os
import time
import numpy as np
from utils.mpdaInstance import MPDAInstance

# 导入算法模块
from DEGA.run import DEGA
from ILS.run import ILS
from MSGA.run import MSGA

# 尝试导入其他算法（如果可用）
try:
    from CACS.run import CACS
    CACS_AVAILABLE = True
except ImportError:
    CACS_AVAILABLE = False
    print("注意: CACS算法不可用，请参考原论文作者的代码实现")

try:
    from MSDE_SPEA2.run import MSDE_SPEA2
    MSDE_SPEA2_AVAILABLE = True
except ImportError:
    MSDE_SPEA2_AVAILABLE = False


def get_available_methods():
    """获取可用的算法方法"""
    methods = ['DEGA', 'ILS', 'MSGA']
    if CACS_AVAILABLE:
        methods.append('CACS')
    if MSDE_SPEA2_AVAILABLE:
        methods.append('MSDE_SPEA2')
    return methods


def run_single_instance(benchmark_name, args):
    """运行单个测试实例"""
    print(f"正在运行实例: {benchmark_name} 使用算法: {args.method}")
    
    # 加载实例
    ins_file = os.path.join(args.instance_dir, f"{benchmark_name}.txt")
    if not os.path.exists(ins_file):
        print(f"错误: 实例文件 {ins_file} 不存在")
        return None
        
    ins = MPDAInstance()
    ins.loadCfg(fileName=ins_file)
    
    # 选择算法
    if args.method == 'DEGA':
        optimizer = DEGA(ins=ins, args=args)
    elif args.method == 'ILS':
        optimizer = ILS(ins=ins, args=args)
    elif args.method == 'MSGA':
        optimizer = MSGA(ins=ins, args=args)
    elif args.method == 'CACS' and CACS_AVAILABLE:
        optimizer = CACS(ins=ins, args=args)
    elif args.method == 'MSDE_SPEA2' and MSDE_SPEA2_AVAILABLE:
        optimizer = MSDE_SPEA2(ins=ins, args=args)
    else:
        print(f"错误: 算法 {args.method} 不可用")
        return None
    
    # 运行优化
    start_time = time.time()
    best_solution = optimizer.run()
    end_time = time.time()
    
    print(f"完成实例 {benchmark_name}: 时间={end_time-start_time:.2f}s")
    return best_solution


def get_benchmark_instances():
    """获取所有基准测试实例"""
    # 小规模实例 (S_*)
    small_instances = [
        'S_3_10_1.51', 'S_3_15_5.03', 'S_5_4_0.39', 'S_5_10_0.93', 'S_5_10_3.67', 
        'S_5_20_4.36', 'S_5_40_3.95', 'S_10_5_1.39', 'S_10_10_3.79', 'S_10_15_1.3',
        'S_15_10_1.17', 'S_15_20_0.67', 'S_17_23_1.71', 'S_20_10_0.47', 'S_20_10_0.94',
        'S_30_10_0.65', 'S_30_10_1.34'
    ]
    
    # 中规模实例 (M_*)
    medium_instances = [
        'M_15_30_2.16', 'M_20_20_0.58', 'M_20_20_0.967', 'M_20_20_0.97',
        'M_30_30_1.04', 'M_30_30_1.94', 'M_40_10_0.67', 'M_40_15_0.67'
    ]
    
    # 大规模实例 (L_*)
    large_instances = [
        'L_20_60_1.51', 'L_80_15_0.76', 'L_80_20_0.7', 'L_80_20_1.12'
    ]
    
    return {
        'small': small_instances,
        'medium': medium_instances,
        'large': large_instances,
        'all': small_instances + medium_instances + large_instances
    }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='多无人机多任务协调分配系统 (MPDA)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py --method DEGA --instance S_5_4_0.39 --generations 100
  python main.py --method ILS --scale small --num_runs 5
  python main.py --method MSGA --scale all --parallel
        """
    )
    
    # 算法选择
    available_methods = get_available_methods()
    parser.add_argument('--method', type=str, default='DEGA', 
                       choices=available_methods,
                       help='选择优化算法')
    
    # 实例选择
    parser.add_argument('--instance', type=str, default=None,
                       help='指定单个测试实例 (例如: S_5_4_0.39)')
    parser.add_argument('--scale', type=str, default='small',
                       choices=['small', 'medium', 'large', 'all'],
                       help='选择实例规模')
    
    # 算法参数
    parser.add_argument('--generations', type=int, default=200,
                       help='进化代数 (默认: 200)')
    parser.add_argument('--pop_size', type=int, default=100,
                       help='种群大小 (默认: 100)')
    parser.add_argument('--cross_rate', type=float, default=0.9,
                       help='交叉概率 (默认: 0.9)')
    parser.add_argument('--mutate_rate', type=float, default=0.1,
                       help='变异概率 (默认: 0.1)')
    
    # 运行参数
    parser.add_argument('--num_runs', type=int, default=1,
                       help='每个实例运行次数 (默认: 1)')
    parser.add_argument('--parallel', action='store_true',
                       help='启用并行计算')
    parser.add_argument('--seed', type=int, default=123,
                       help='随机种子 (默认: 123)')
    
    # 输出参数
    parser.add_argument('--output_dir', type=str, default='./results',
                       help='结果输出目录 (默认: ./results)')
    parser.add_argument('--instance_dir', type=str, default='./AllInstance',
                       help='实例文件目录 (默认: ./AllInstance)')
    
    args = parser.parse_args()
    
    # 显示配置信息
    print("=" * 60)
    print("多无人机多任务协调分配系统 (MPDA)")
    print("=" * 60)
    print(f"算法: {args.method}")
    print(f"可用算法: {', '.join(available_methods)}")
    
    # 确定要运行的实例
    benchmark_instances = get_benchmark_instances()
    if args.instance:
        instances_to_run = [args.instance]
        print(f"运行单个实例: {args.instance}")
    else:
        instances_to_run = benchmark_instances[args.scale]
        print(f"运行 {args.scale} 规模实例: {len(instances_to_run)} 个")
    
    print(f"每个实例运行次数: {args.num_runs}")
    print(f"进化代数: {args.generations}")
    print(f"种群大小: {args.pop_size}")
    print("-" * 60)
    
    # 创建输出目录
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(args.output_dir, f"{args.method}_{timestamp}")
    os.makedirs(output_path, exist_ok=True)
    args.save_path = output_path
    
    # 准备运行任务
    tasks = []
    for instance in instances_to_run:
        for run_id in range(args.num_runs):
            task_args = copy.deepcopy(args)
            task_args.benchmarkName = instance
            task_args.sample_id = len(tasks)
            task_args.rdSeed = args.seed + len(tasks)
            tasks.append((instance, task_args))
    
    print(f"总共 {len(tasks)} 个任务")
    
    # 运行任务
    results = []
    if args.parallel and len(tasks) > 1:
        # 并行运行
        cpu_count = mp.cpu_count()
        process_count = min(cpu_count - 1, len(tasks))
        print(f"使用 {process_count} 个进程并行运行")
        
        with mp.Pool(processes=process_count) as pool:
            results = pool.starmap(run_single_instance, tasks)
    else:
        # 串行运行
        print("串行运行模式")
        for instance, task_args in tasks:
            result = run_single_instance(instance, task_args)
            results.append(result)
    
    # 统计结果
    successful_runs = [r for r in results if r is not None]
    print("=" * 60)
    print(f"运行完成: {len(successful_runs)}/{len(tasks)} 个任务成功")
    print(f"结果保存在: {output_path}")
    print("=" * 60)


if __name__ == '__main__':
    main()
