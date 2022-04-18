import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle
import random
from pylab import mpl
from scipy.fft import irfft,rfft
import math

def pre_80_SOH(new_f_clean):
    # 当SOH为初始值的80%时
    x = range(n)
    coef = np.polyfit(x, new_f_clean, 2)
    y_fit = np.polyval(coef, x)
    plt.figure()
    plt.scatter(x, new_f_clean, label="删去温度影响的值")
    plt.plot(x, y_fit, label="二次函数拟合", c="r")
    print(y_fit[0])
    print(y_fit[-1])
    SOH = y_fit[0] * 0.8
    plt.axhline(y_fit[0]*0.8,linestyle="-.",color="y",label="80%等效续航里程")
    # x_pre = round((SOH - coef[1]) / coef[0])
    a = coef[0]
    b = coef[1]
    c = coef[2] - SOH
    d = b * b - 4 * a * c
    x_pre = round((-b - math.sqrt(d)) / (2 * a))
    y_l_fit = np.polyval(coef,range(x_pre))
    plt.plot(range(x_pre), y_l_fit,c="r")
    plt.axvline(x_pre,ymin=0,ymax=SOH,linestyle="--",color="g")
    plt.plot([x_pre], [SOH], ".k")
    plt.annotate("(%d,%.2f)" % (x_pre, SOH), [x_pre-150, SOH+0.03])
    plt.legend()
    plt.grid(linestyle="--")
    return y_fit

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
    f = open("pre_SOH_list.txt", "w")
    f.write(str(index_list_r) + "\n" + str(index_list_l))
    f.close()
    return index_list_r,index_list_l

def read_index():
    f = open("pre_SOH_list.txt","r")
    temp_str = f.read()
    str_r,str_l = temp_str.split("\n")
    index_list_r = eval(str_r)
    index_list_l = eval(str_l)
    f.close()
    return index_list_r,index_list_l

if __name__ == "__main__":
    file_No = 9
    # 设置绘图字体
    mpl.rcParams['font.sans-serif'] = ['DengXian']
    mpl.rcParams['axes.unicode_minus'] = False
    # 读取#9Car
    df = pd.read_csv(str(file_No)+".csv")
    index_list = []
    index_list_l = []
    index_list_r = [0]
    try:
        index_list_r, index_list_l = read_index()
    except:
        find_index()
        index_list_r, index_list_l = read_index()
    C_list = []
    try:
        with open("C_list.txt") as f:
            C_list = eval(f.read())
    except:
        for i in range(len(index_list_r)-1):
            sum_C = 0
            for j in range(index_list_l[i],index_list_r[i+1]):
                time_l = pd.to_datetime(df['时间'][j])
                time_r = pd.to_datetime(df['时间'][j+1])
                time_delta = (time_r - time_l).seconds
                C = abs(df['总电流'][j]) * time_delta #容量不减少反而增加，推测是由于容量计算有误导致的
                sum_C += C
            if df['SOC'][index_list_r[i+1]] - df['SOC'][index_list_l[i]] == 0:
                sum_C = 0
            else:
                sum_C = sum_C / (df['SOC'][index_list_r[i+1]] - df['SOC'][index_list_l[i]]) * 100
            C_list.append(sum_C/3.6)
        with open("C_list.txt","w") as f:
            f.write(str(C_list))
    plt.figure()
    plt.scatter(range(len(C_list)),C_list)
    plt.xlabel("放电循环")
    plt.ylabel("C/mAh")
    file_name = str(file_No) + "_new_data.csv"
    df_data = pd.read_csv(file_name)
    n = len(C_list)
    yf = rfft(df_data['最低温度'][:n].to_list())
    yf_abs = np.abs(yf)
    indices = yf_abs < 700
    yf = rfft(C_list)
    yf_abs = np.abs(yf)
    indices[0] = True
    yf_clean = indices * yf
    new_f_clean = irfft(yf_clean)
    y_fit = pre_80_SOH(new_f_clean)
    plt.xlabel("放电循环")
    plt.ylabel("C/mAh")
    y_normalize = new_f_clean / y_fit[0]
    pre_80_SOH(y_normalize)
    plt.xlabel("放电循环")
    plt.ylabel("SOH")