import copy
import datetime
import multiprocessing as mp
import argparse
import os
import time
import numpy as np
from utils.mpdaInstance import MPDAInstance
from DEGA.run import DEGA
from ILS.run import ILS
from MSGA.run import MSGA


def run_one(benchmarkName, args):
    # benchmarkName, insFileName, id, time_name
    insConfDir = args.insConfDir
    insFileName = insConfDir + benchmarkName + '.txt'
    ins = MPDAInstance()
    ins.loadCfg(fileName=insFileName)
    if args.method == 'ILS':
        optimiser = ILS(ins=ins, args=args)
    elif args.method == 'MSGA':
        optimiser = MSGA(ins=ins, args=args)
    else:
        optimiser = DEGA(ins=ins, args=args)
    best_solution = optimiser.run()

def main_loop(args):
    all_n = args.all_n
    this_n = args.this_n
    date_str = args.date_str
    args.insConfDir = './/AllInstance//'
    b_lst = ['L_20_60_1.51', 'L_80_15_0.76', 'L_80_20_0.7', 'L_80_20_1.12', 'M_15_30_2.16', 'M_20_20_0.58', 'M_20_20_0.967', 'M_20_20_0.97',
             'M_30_30_1.04', 'M_30_30_1.94', 'M_40_10_0.67', 'M_40_15_0.67', 'S_10_10_3.79', 'S_10_15_1.3', 'S_10_5_1.39', 'S_15_10_1.17',
             'S_15_20_0.67', 'S_17_23_1.71', 'S_20_10_0.47', 'S_20_10_0.94', 'S_30_10_0.65', 'S_30_10_1.34', 'S_3_10_1.51', 'S_3_15_5.03',
             'S_5_10_0.93', 'S_5_10_3.67', 'S_5_40_3.95', 'S_5_4_0.39']

    id = 0
    args_n = []
    b_l = b_lst[:all_n]
    b_sm = b_lst[all_n:]

    b_re_lst = []
    if len(b_sm) % 2 == 1:
        b_re_lst.append(b_sm[-1])
        b_sm.pop()
    for i in range(len(b_sm) // 2):
        b_re_lst.append(b_sm[i])
        b_re_lst.append(b_sm[-i-1])

    if all_n != 1:
        part_n = int(np.ceil(len(b_re_lst) // all_n))
        start_n = int((this_n - 1) * part_n)
        if this_n == all_n:
            b_re_lst = b_re_lst[start_n:]
            if b_l[-1] not in b_re_lst:
                b_re_lst.append(b_l[-1])
        else:
            b_re_lst = b_re_lst[start_n:start_n + part_n] + [b_l[int(this_n - 1)]]
    else:
        start_n = 0
        b_re_lst = b_lst

    # # b_re_lst = ['M_15_30_2.16']
    b_re_lst = ['S_5_40_3.95']
    print("使用测试案例:", b_re_lst)
    print(f'This process will run {len(b_re_lst)} benchmarks, start from {start_n}, end at {start_n + len(b_re_lst)}')

    path1 = f'./data_run'
    if not os.path.exists(path1):
        os.makedirs(path1)
    path2 = path1 + f'/{date_str}'
    if not os.path.exists(path2):
        os.makedirs(path2)

    for bn, benchmarkName in enumerate(b_re_lst):
        for i in range(args.num_runs):
            path3 = path2 + f'/{benchmarkName}'
            if not os.path.exists(path3):
                os.makedirs(path3)

            args.benchmarkName = benchmarkName
            args.sample_id = id
            args.rdSeed = int('1234' + str(bn) + str(i))
            args.save_path = path3
            args_n.append((benchmarkName, copy.deepcopy(args)))
            id += 1
    # 查看电脑有几个cpu核心
    cpu_num = mp.cpu_count()
    cn = cpu_num - 2
    print(f'There are {cpu_num} cpu cores, we will use {cn} cores to run the task ACO')
    # 创建一个进程池
    with mp.Pool(processes=cn) as pool:
        # 使用 starmap 传递多个参数
        results = pool.starmap(run_one, args_n)

    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_runs', type=int, default=1)
    parser.add_argument('--all_n', type=int, default=1)
    parser.add_argument('--this_n', type=int, default=1)
    parser.add_argument('--generations', type=int, default=500)
    parser.add_argument('--pop_size', type=int, default=100)
    parser.add_argument('--cross_rate', type=float, default=0.8)
    parser.add_argument('--mutate_rate', type=float, default=0.05)
    parser.add_argument('--rdSeed', type=int, default=123)
    parser.add_argument('--method', type=str, default='DEGA', choices=['DEGA', 'ILS', 'MSGA'])
    args = parser.parse_args()

    date_str = str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    args.date_str = date_str
    main_loop(args)
