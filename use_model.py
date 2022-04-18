import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle
import random
from pylab import mpl
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
    f = open("use_model_SOC_list.txt", "w")
    f.write(str(index_list_r) + "\n" + str(index_list_l))
    f.close()
    return index_list_r,index_list_l

def read_index():
    f = open("use_model_SOC_list.txt","r")
    temp_str = f.read()
    str_r,str_l = temp_str.split("\n")
    index_list_r = eval(str_r)
    index_list_l = eval(str_l)
    f.close()
    return index_list_r,index_list_l

def pre_data(df,index_l,index_r,rf_end_V,rf,end_index):
    mileage = df['累计里程'][end_index] - df['累计里程'][index_l]
    start_I = df['总电流'][index_l]
    min_tem = df['最低温度值'][index_l]
    start_V = df['总电压'][index_l]
    # x_pre_V = [[start_I,min_tem,start_V,mileage]]
    x_pre_V = [[min_tem, start_V]]
    pre_end_V = rf_end_V.predict(x_pre_V)
    x_pre = [list(pre_end_V) + x_pre_V[0]]
    pre_mileage_SOC = rf.predict(x_pre)
    SOC_deplete = df['SOC'][index_l] - df['SOC'][index_r]
    pre_mileage = SOC_deplete * pre_mileage_SOC
    pre_total_mileage = pre_mileage + df['累计里程'][index_l]
    pre_SOC_deplete = mileage / pre_mileage_SOC
    pre_SOC = df['SOC'][index_r] - pre_SOC_deplete
    return pre_SOC,pre_total_mileage,pre_mileage

if __name__ == "__main__":
    # 设置绘图字体
    mpl.rcParams['font.sans-serif'] = ['DengXian']
    mpl.rcParams['axes.unicode_minus'] = False
    pkl_V_filename = "pickle_V_model.pkl"
    with open(pkl_V_filename,"rb") as file:
        rf_end_V = pickle.load(file)
    pkl_filename = "pickle_model.pkl"
    with open(pkl_filename,"rb") as file:
        rf = pickle.load(file)
    # 这里以第一个数据集为例
    df = pd.read_csv("0.csv")
    pre_cloumn = ['总电压','总电流','最低温度值','累计里程']
    index_list = []
    index_list_l = []
    index_list_r = [0]
    try:
        index_list_r, index_list_l = read_index()
    except:
        find_index()
        index_list_r, index_list_l = read_index()
    # 取其中的一个数据
    rand_num = random.randint(0,len(index_list_l))
    #index_l = random.randint(index_list_r[rand_num],index_list_l[rand_num])
    # index_r = random.randint(index_l + 1,index_list_l[rand_num])
    index_l = index_list_r[rand_num]
    index_r = index_list_l[rand_num]
    # index_r = index_l + 100
    pre_SOC,pre_total_mileage,pre_mileage = pre_data(df,index_l,index_r,rf_end_V,rf,index_r)
    plt.plot(range(index_list_r[rand_num],index_list_l[rand_num]),df['SOC'][index_list_r[rand_num]:index_list_l[rand_num]],label="真实值")
    plt.plot([index_l,index_r],[df['SOC'][index_l],pre_SOC],label="预测值")
    plt.xticks([index_l,index_r],[df['时间'][index_l],df['时间'][index_r]])
    # 预测可行驶的里程值
    plt.figure()
    plt.plot(range(index_list_r[rand_num], index_list_l[rand_num]),df['累计里程'][index_list_r[rand_num]:index_list_l[rand_num]],label="真实值")
    pre_list = []
    # 已经行驶了一段时间
    old_drive = 0
    for i in range(index_l+1+old_drive,index_r+1):
        pre_SOC, pre_total_mileage, pre_mileage = pre_data(df, index_l+old_drive, i, rf_end_V, rf,index_r)
        pre_list.append(pre_total_mileage)
    # plt.plot([index_l, index_r], [df['累计里程'][index_l], pre_total_mileage],linestyle="--",label="预测值")
    plt.plot(range(index_list_r[rand_num]+old_drive, index_list_l[rand_num]),pre_list,linestyle="--",label="预测值")
    plt.xticks([index_l,index_l+old_drive,index_r], [df['时间'][index_l], df['时间'][index_l+old_drive],df['时间'][index_r]])
    plt.ylabel("累计里程/km")
    plt.xlabel("时间")
    deviation = abs(abs(df['累计里程'][index_r]-df['累计里程'][index_l+old_drive])-float(pre_mileage)) / abs(df['累计里程'][index_r]-df['累计里程'][index_l+old_drive]) * 100
    total_deviation = abs(float(pre_total_mileage)-df['累计里程'][index_r])/df['累计里程'][index_r] * 100
    plt.title("累计里程误差为:{:.4f}%\n当次行驶里程误差为:{:.2f}%\n误差值为:{}".format(total_deviation,deviation,float(pre_total_mileage)-df['累计里程'][index_r]))
    plt.legend()