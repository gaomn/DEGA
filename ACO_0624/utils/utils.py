# -*- coding: UTF-8 -*-
# @Date    :2024/5/24 12:13
# @Author  :高猛
# @Project :MPDA_ACO-main 
# @File    :utils.py
# @IDE     :PyCharm

import numpy as np
import copy

class Utils:
    @staticmethod
    def static_fitness(pop, function):
        fit_lst = []
        cul_lst = []
        for ind in pop:
            fit_lst.append(list(function(ind)))
            cul_lst.append(copy.copy(fit_lst[-1]))
        clu_lst = Utils.normalize(cul_lst)
        weight_lst = [np.sum(clu_lst[i]) for i in range(clu_lst.shape[0])]
        min_w_ind = fit_lst[np.argmin(weight_lst)]
        min_w_index = np.argmin(weight_lst)
        max_w_ind = fit_lst[np.argmax(weight_lst)]
        mean_w_ind = np.mean(fit_lst, axis=0)
        std_w_ind = np.std(fit_lst, axis=0)
        info_dict = {"min": min_w_ind, "max": max_w_ind, "mean": mean_w_ind, "std": std_w_ind, 'min_idx': min_w_index}
        return info_dict

    @staticmethod
    def print_fitness(info_dict, gen=0):
        # 打印种群的适应度信息,同时保证所有适应值打印的时候都有两位小数且占用10位空间
        # formatted_min = format_floats(info_dict['min'])
        # formatted_max = format_floats(info_dict['max'])
        # formatted_mean = format_floats(info_dict['mean'])
        # formatted_std = format_floats(info_dict['std'])

        formatted_min, formatted_max, formatted_mean, formatted_std = \
            info_dict['min'], info_dict['max'], info_dict['mean'], info_dict['std']
        # print()
        p_str = (
            f"Fitness in generation {gen}: "
            f"min: ({formatted_min[0]:.2e}, {formatted_min[1]:.2e}, {formatted_min[2]:.2e}); "
            f"max: ({formatted_max[0]:.2e}, {formatted_max[1]:.2e}, {formatted_max[2]:.2e}); "
            f"mean: ({formatted_mean[0]:.2e}, {formatted_mean[1]:.2e}, {formatted_mean[2]:.2e}); "
            f"std: ({formatted_std[0]:.2e}, {formatted_std[1]:.2e}, {formatted_std[2]:.2e})"
        )
        print(p_str)

    @staticmethod
    def normalize(matrix):
        # 归一化函数，将一个矩阵的每一列归一化到[0,1]之间，再拼接成一个新的矩阵返回
        matrix = np.array(matrix)
        m_lst = [Utils.normalize_one_arr(matrix[:, i]) for i in range(matrix.shape[1])]
        new_matrix = np.array(m_lst).T
        return new_matrix

    @staticmethod
    def normalize_one_arr(one_arr):
        # 归一化函数，将一个数组归一化到[0,1]之间
        one_arr = np.array(one_arr)
        max_val = np.max(one_arr)
        min_val = np.min(one_arr)
        return (one_arr - min_val) / (max_val - min_val)


class my_pop:
    def __init__(self):
        self.pop = []

    def add_ind(self, ind):
        self.pop.append(ind)

    def get_pop(self):
        return self.pop

    def reset_pop(self):
        self.pop = []

# test_matrix = [[1, 1, 1], [2, 2, 2], [3, 3, 3], [4, 4, 4], [5, 5, 5]]
# print(Utils.static_fitness(test_matrix, lambda x: x))