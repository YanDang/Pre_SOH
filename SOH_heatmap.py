import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle
import random
from pylab import mpl
from scipy.fft import irfft,rfft
import math
import seaborn as sns

def find_index():
    # 设置绘图字体
    mpl.rcParams['font.sans-serif'] = ['DengXian']
    mpl.rcParams['axes.unicode_minus'] = False
    index_list = []
    index_list_l = []
    index_list_r = [0]
    for index in range(len(df['SOC'])-1):
        # 排查发现充电状态中不存在 2，即没有行驶充电这一状态
        # 当前状态为停车充电或是充电完成，下一时刻状态为未充电状态
        if (df['充电状态'][index] == 1 or df['充电状态'][index] == 4) and df['充电状态'][index+1] == 3:
            index_list_r.append(index)
            index_list.append(index)
        if df['充电状态'][index] == 3 and (df['充电状态'][index+1] == 1 or df['充电状态'][index+1] == 4):
            index_list_l.append(index)
            index_list.append(index)
    index_list_l.append(len(df['SOC']) - 1)
    # f = open("pre_SOH_list.txt", "w")
    # f.write(str(index_list_r) + "\n" + str(index_list_l))
    # f.close()
    return index_list_r,index_list_l

if __name__ == "__main__":
    file_No = 9
    # 设置绘图字体
    mpl.rcParams['font.sans-serif'] = ['DengXian']
    mpl.rcParams['axes.unicode_minus'] = False
    # 读取#9Car
    df = pd.read_csv(str(file_No)+".csv")
    df_new_data = pd.read_csv(str(file_No)+"_new_data.csv")
    index_list_r,index_list_l = find_index()
    C_list = []
    for i in range(len(index_list_r)):
        sum_C = 0
        for j in range(index_list_l[i],index_list_r[i+1]):
            time_l = pd.to_datetime(df['时间'][j])
            time_r = pd.to_datetime(df['时间'][j+1])
            time_delta = (time_r - time_l).seconds
            C = abs(df['总电流'][j]) * time_delta #容量不减少反而增加，推测是由于容量计算有误导致的
            sum_C += C
        C_list.append(sum_C/3.6)
    df_new_data['电池容量'] = C_list
    mcorr = df_new_data.corr()
    mask = np.zeros_like(mcorr, dtype=np.bool)
    mask[np.triu_indices_from(mask)] = False
    cmap = sns.diverging_palette(220, 10, as_cmap=True)
    plt.figure()
    g = sns.heatmap(mcorr, mask=mask, cmap=cmap, square=True, annot=True, fmt='0.2f', cbar=False)
