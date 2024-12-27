import os
import sys

import numpy as np
import pandas as pd
import multiprocessing
import time
import copy
import datetime
from mpdaACO import MPDA_Task_ACO
from mpdaInstance import MPDAInstance


def pareto_frontier(points):
    """
    计算给定点的帕累托前沿

    :param points: List of tuples, 每个元素是一个包含k个float元素的元组，表示每个个体的k个适应值
    :return: 帕累托前沿的列表，包含所有不可支配的个体
    """
    pareto_front = []

    for point in points:
        dominated = False
        to_remove = []

        for front_point in pareto_front:
            if dominates(front_point, point):
                dominated = True
                break
            elif dominates(point, front_point):
                to_remove.append(front_point)

        if not dominated:
            pareto_front.append(point)
            for remove_point in to_remove:
                pareto_front.remove(remove_point)

    return pareto_front

def dominates(a, b):
    return all(x >= y for x, y in zip(a, b)) and any(x > y for x, y in zip(a, b))


def run_one(benchmarkName, id, random_seed, insConfDir='.//staticMpdaBenchmarkSet//',date_str='data'):
    print(f'begin to run task ACACO in {benchmarkName}, id={id}, random_seed={random_seed}, date_str={date_str}')
    ins = MPDAInstance()

    maxRunTime = 200
    sampleRate = 100
    decay = 95
    heuristicRule = '_Dis'
    heuristicRule = '_Pdis'
    heuristicRule = '_LPdis'
    # heuristicRule = '_Gta'
    # heuristicRule = '_Dvis'
    # heuristicRule = '_None'
    # heuristicRule = '_Syn'
    eliteRule = '_Gbt'
    localSearch = '_None'
    updatingMechanism = '_Trad'
    # updatingMechanism = '_Prob'
    updatingMechanism = '_ACS'
    # updatingMechanism = '_Eset'
    selectedMechanism = '_Limit'
    selectedMechanism = '_Trad'
    localSearchMechanism = '_AllTri'
    localSearchMechanism = '_Trad'
    fixMechanism = '_Trad'
    localSearchIndNum = 1
    localSearchRowNum = 2


    ins.loadCfg(fileName=insConfDir + benchmarkName + '.txt')
    mpda_as = MPDA_Task_ACO(ins, benchmarkName=benchmarkName,
                            decay=decay, sampleRate=sampleRate,
                            rdSeed=random_seed,
                            maxRunTime=maxRunTime,
                            heuristicRule=heuristicRule,
                            eliteRule=eliteRule,
                            localSearchMechanism=localSearchMechanism,
                            localSearchIndNum=localSearchIndNum,
                            localSearchRowNum=localSearchRowNum,
                            updatingMechanism=updatingMechanism,
                            selectedMechanism=selectedMechanism,
                            fixMechanism=fixMechanism)
    pop_f_lst = mpda_as.run()


    pop_pareto = pareto_frontier(pop_f_lst)
    df = pd.DataFrame(pop_pareto, columns=['loss', 'time', 'route'])
    paths = f'./data_ACO'
    if not os.path.exists(paths):
        os.makedirs(paths)
    path1 = paths + f'/{date_str}'
    if not os.path.exists(path1):
        os.makedirs(path1)
    path2 = path1 + f'/{benchmarkName}'
    if not os.path.exists(path2):
        os.makedirs(path2)
    df.to_csv(f'{path2}/acaco_{benchmarkName}_{id}.csv', index=False)


def main_loop(all_n=1, this_n=1, date_str='data'):
    insConfDir = './/staticMpdaBenchmarkSet//'

    b_lst = []
    for root, dirs, files in os.walk('.//staticMpdaBenchmarkSet//'):
        for file in files:
            if file.endswith(".txt"):
                b_lst.append(file[:-4])
    print(b_lst)
    id = 0
    args_n = []
    # 将b_lst排列为0, -1, 1, -2, 2, -3 ,...形状

    b_re_lst = []
    if len(b_lst) % 2 == 1:
        b_re_lst.append(b_lst[-1])
        b_lst.pop()
    for i in range(len(b_lst) // 2):
        b_re_lst.append(b_lst[i])
        b_re_lst.append(b_lst[-i-1])

    if all_n != 1:
        part_n = int(np.ceil(len(b_re_lst) // all_n))
        start_n = int((this_n - 1) * part_n)
        if this_n == all_n:
            b_re_lst = b_re_lst[start_n:]
        else:
            b_re_lst = b_re_lst[start_n:start_n + part_n]

        print(f'This process will run {len(b_re_lst)} benchmarks, start from {start_n}, end at {start_n + len(b_re_lst)}')
    for bn, benchmarkName in enumerate(b_re_lst):
        for i in range(20):
            args_n.append((benchmarkName, id, int('123' + str(bn) + str(i)), insConfDir, date_str))
            id += 1
    print(args_n)
    # 查看电脑有几个cpu核心
    cpu_num = multiprocessing.cpu_count()
    cn = cpu_num - 2
    print(f'There are {cpu_num} cpu cores, we will use {cn} cores to run the task ACO')
    # 创建一个进程池
    with multiprocessing.Pool(processes=cn) as pool:
        # 使用 starmap 传递多个参数
        results = pool.starmap(run_one, args_n)

    print("Results:", results)


if __name__ == '__main__':
    date_str = str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    main_loop(8, 1, date_str)

