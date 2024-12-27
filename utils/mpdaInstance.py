import os
import random
import numpy as np
import utils.readcfg as rd

from enum import Enum
import matplotlib.pyplot as plt


class TaskModelType(Enum):
    ExpModel = 1
    LineModel = 2


class MPDAInstance(object):
    def __init__(self):
        self._taskDisMat = None
        self._rob2taskDisMat = None
        self._taskRateLst = None
        self._taskStateLst = None
        self._robVelLst = None
        self._robAbiLst = None
        self._threhold = None
        self._taskNum = None
        self._robNum = None
        self._insName = None
        self._taskValLst = None
        self._task_x_lst = None
        self._task_y_lst = None
        self._rob_x_lst = None
        self._rob_y_lst = None

    def loadCfg(self, fileName: str):
        # print(fileName)
        self._insName = fileName
        readCfg = rd.Read_Cfg(fileName)
        self._robNum = int(readCfg.getSingleVal('robNum'))
        self._taskNum = int(readCfg.getSingleVal('taskNum'))
        self._threhold = readCfg.getSingleVal('comp_threshold')
        self._robAbiLst = []
        self._robVelLst = []
        self._taskStateLst = []
        self._taskRateLst = []
        self._taskValLst = []
        self._task_x_lst = []
        self._task_y_lst = []
        self._rob_x_lst = []
        self._rob_y_lst = []
        readCfg.get('rob_abi', self._robAbiLst)
        readCfg.get('rob_vel', self._robVelLst)
        readCfg.get('task_rate', self._taskRateLst)
        readCfg.get('task_init_demand', self._taskStateLst)
        readCfg.get('task_value_rate', self._taskValLst)
        readCfg.get('task_x', self._task_x_lst)
        readCfg.get('task_y', self._task_y_lst)
        readCfg.get('rob_x', self._rob_x_lst)
        readCfg.get('rob_y', self._rob_y_lst)
        self._rob2taskDisMat = np.zeros((self._robNum, self._taskNum))
        disLst = []
        readCfg.get('rob2taskDisMat', disLst)
        for i in range(self._robNum):
            for j in range(self._taskNum):
                self._rob2taskDisMat[i][j] = disLst[i * self._taskNum + j]

        self._taskDisMat = np.zeros((self._taskNum, self._taskNum))
        disLst = []
        readCfg.get('taskDisMat', disLst)
        for i in range(self._taskNum):
            for j in range(self._taskNum):
                self._taskDisMat[i][j] = disLst[i * self._taskNum + j]


    def __str__(self):
        return 'robNum = ' + str(self._robNum) + '  taskNum = ' + str(self._taskNum) + '\n' + self._insName

    def drawIns(self):

        plt.plot(self._rob_x_lst, self._rob_y_lst, 'ro', label='Rob')
        for i in range(self._robNum):
            plt.text(self._rob_x_lst[i], self._rob_y_lst[i], 'R' + str(i))

        plt.plot(self._task_x_lst, self._task_y_lst, 'bs', label='Task')
        for i in range(self._taskNum):
            plt.text(self._task_x_lst[i], self._task_y_lst[i], 'T' + str(i))
        plt.legend()

        title_name = os.path.splitext(os.path.basename(self._insName))[0]
        # print(title_name)
        plt.title(f'{title_name} :: RobNum = {self._robNum}  TaskNum = {self._taskNum}')
        plt.show()

        # plt.title(self._insName)
        # plt.savefig(self.figBaseDir + '_box'+ str(insID))


if __name__ == '__main__':
    # print('test')
    # insFileName = './/staticMpdaBenchmarkSet//S_3_15_5.03.txt'

    insConfDir = './/staticMpdaBenchmarkSet//'
    benchmarkName = 'S_3_15_5.03'
    insFileName = insConfDir + benchmarkName + '.txt'

    print(f'benchmarkName: {benchmarkName}     insFileName: {insFileName}')

    # ins = MPDAInstance()
    # # ins.loadCfg(fileName=insConfDir + benchmarkName + '.txt')
    # ins.loadCfg(fileName= insFileName)
    # ins.drawIns()
    # print(ins)

    file_list = []
    for file in os.listdir(insConfDir):
        if file.endswith(".txt"):
            fileName = os.path.join(insConfDir, file)
            file_list.append(fileName)
            ins = MPDAInstance()
            ins.loadCfg(fileName=fileName)
            ins.drawIns()
    print(file_list)

'''
robNum:10
taskNum:10
threhold:0.0
robAbiLst:[0.04063369782359221, 0.04861245764332556, 0.04320387400712767, 0.020083412583193985, 0.04890718754446448, 0.029991239268008806, 0.0351794048981832, 0.0393974903437667, 0.020800499070112558, 0.04437669048005564]
robVelLst:[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
taskStateLst:[2.3025850929940455, 2.3025850929940455, 2.3025850929940455, 2.3025850929940455, 2.3025850929940455, 2.3025850929940455, 2.3025850929940455, 2.3025850929940455, 2.3025850929940455, 2.3025850929940455]
taskRateLst:[0.12911079363323347, 0.19555857979328384, 0.13033259376916023, 0.15651201867964756, 0.11113935635410319, 0.12804332064189122, 0.12075216616641071, 0.1216480156473195, 0.12353213469847045, 0.1914477461565985]
taskValLst:[0.21123397922031228, 0.137234805257327, 0.2555195040214593, 0.3281223559378411, 0.0077299065693119395, 0.7470141234297678, 0.1756948018758423, 0.38020744571523624, 0.7036712633826636, 0.5002623465562132]

rob2taskDisMat:
[65.11528238439882, 14.212670403551895, 50.21951811795888, 22.627416997969522, 48.041648597857254, 27.294688127912362, 31.89043743820395, 36.796738985948195, 39.293765408777, 48.76474136094644]
[65.11528238439882, 14.212670403551895, 50.21951811795888, 22.627416997969522, 48.041648597857254, 27.294688127912362, 31.89043743820395, 36.796738985948195, 39.293765408777, 48.76474136094644]
[65.11528238439882, 14.212670403551895, 50.21951811795888, 22.627416997969522, 48.041648597857254, 27.294688127912362, 31.89043743820395, 36.796738985948195, 39.293765408777, 48.76474136094644]
[65.11528238439882, 14.212670403551895, 50.21951811795888, 22.627416997969522, 48.041648597857254, 27.294688127912362, 31.89043743820395, 36.796738985948195, 39.293765408777, 48.76474136094644]
[65.11528238439882, 14.212670403551895, 50.21951811795888, 22.627416997969522, 48.041648597857254, 27.294688127912362, 31.89043743820395, 36.796738985948195, 39.293765408777, 48.76474136094644]
[65.11528238439882, 14.212670403551895, 50.21951811795888, 22.627416997969522, 48.041648597857254, 27.294688127912362, 31.89043743820395, 36.796738985948195, 39.293765408777, 48.76474136094644]
[65.11528238439882, 14.212670403551895, 50.21951811795888, 22.627416997969522, 48.041648597857254, 27.294688127912362, 31.89043743820395, 36.796738985948195, 39.293765408777, 48.76474136094644]
[65.11528238439882, 14.212670403551895, 50.21951811795888, 22.627416997969522, 48.041648597857254, 27.294688127912362, 31.89043743820395, 36.796738985948195, 39.293765408777, 48.76474136094644]
[65.11528238439882, 14.212670403551895, 50.21951811795888, 22.627416997969522, 48.041648597857254, 27.294688127912362, 31.89043743820395, 36.796738985948195, 39.293765408777, 48.76474136094644]
[65.11528238439882, 14.212670403551895, 50.21951811795888, 22.627416997969522, 48.041648597857254, 27.294688127912362, 31.89043743820395, 36.796738985948195, 39.293765408777, 48.76474136094644]








'''
