# -*- coding: utf-8 -*-
"""
Created on Tue Sep  4 11:18:03 2018

inh is an abbreviation for inherent
@author: robot
"""

import numpy as np
import math
import sys
import copy


class Task():
    def __init__(self):
        self._initState = 0
        self._initRate = 0
        self.cState = 0
        self.cRate = 0
        self.changeRateTime = 0
        self.cmplt = False
        self._threhod = 0
        self.cmpltTime = 0
        self.taskValue = 0

    def calExecuteDur(self):
        e_dur = (self.cState - self._threhod)/(-self.cRate)
        if e_dur < 0:
            print(f'threhod {self._threhod} cState {self.cState} cRate {self.cRate} e_dur {e_dur}')
            raise Exception('Bug dur')
            print('bug dur')
        return e_dur

    def calCurrentState(self, time):
        changeDur = time - self.changeRateTime
        incre = changeDur * self.cRate
        self.cState = self.cState + incre
        self.changeRateTime = time
        return True

    def calPovertyLoss(self, time):
        changeDur = time - self.changeRateTime
        incre = changeDur * self.cRate
        PovertyLoss = self.taskValue * changeDur * (self.cState + 0.5 * incre)
        return PovertyLoss

    def isCmplt(self):
        bias = abs(self.cState - self._threhod)
        if bias < 1e-6:
            self.cmplt = True
            return True
        else:
            self.cmplt = False
            return False

    def display(self):
        print('initState', self.initState, ' initRate', self.initRate,
              ' cState', self.cState, ' cRate', self.cRate,
              ' changeRateTime', self.changeRateTime, ' cmplt ', self.cmplt,
              ' threhod ', self.threhod)

    def __str__(self):
        return 'initState = ' + str(self.initState) + ' initRate = ' + str(self.initRate) + ' cState = ' + str(
            self.cState) \
               + ' cRate = ' + str(self.cRate) + ' changeRateTime = ' + str(self.changeRateTime) + ' cmplt  = ' + str(
            self.cmplt) \
               + ' threhod ' + str(self.threhod) + ' cmpltTime = ' + str(self.cmpltTime)


if __name__ == '__main__':
    tsk = Task()
    tsk.display()
    # print(tsk.initState)
    # print(math.log(1.7976931348623157e+308))
