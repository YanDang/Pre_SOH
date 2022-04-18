import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from pylab import mpl
    # 查找数据的转折点下标
# 该方法时间复杂度为O(n)，有合适的方法时需要进行优化
# 该段代码已经acc，但是运行时间较长因此使用缓存的思想
# 设置绘图字体
mpl.rcParams['font.sans-serif'] = ['DengXian']
mpl.rcParams['axes.unicode_minus'] = False
#寻找并保存下标至txt文件
def find_index():
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
    f = open("SOC_list.txt", "w")
    f.write(str(index_list_r) + "\n" + str(index_list_l))
    f.close()
    return index_list_r,index_list_l

def plot_div():
    plt.figure()
    plt.plot(df['SOC'])
    for i in index_list_r[:-2]:
        plt.axvline(x=i, ls='--', c='r')
    plt.axvline(x=index_list_r[-1], ls='--', c='r', label="充电结束")
    for j in index_list_l[:-2]:
        plt.axvline(x=j, ls='-.', c='y')
    plt.axvline(x=index_list_l[-1], ls='-.', c='y',label="充电开始")
    plt.legend()
'''该部分代码已被优化'''
'''
def find_index():
    flag = True # 设置flag
    for index in range(len(df['SOC'])-50):
        if flag:
            if df['SOC'][index] < min(df['SOC'][index+1:index+50]):
                index_list_l.append(index)
                index_list.append(index)
                flag = False
                continue
        else:
            if df['SOC'][index] > max(df['SOC'][index+1:index+50]):
                index_list_r.append(index)
                index_list.append(index)
                flag = True
    index_list_l.append(len(df['SOC'])-1)
    f = open("SOC_list.txt","w")
    f.write(str(index_list_r)+"\n"+str(index_list_l))
    '''

# 读取下标
def read_index():
    f = open("SOC_list.txt","r")
    temp_str = f.read()
    str_r,str_l = temp_str.split("\n")
    index_list_r = eval(str_r)
    index_list_l = eval(str_l)
    f.close()
    return index_list_r,index_list_l

if __name__ == "__main__":
    df = pd.read_csv("9.csv")
    index_list = []
    index_list_l = []
    index_list_r = [0]
    try:
        index_list_r, index_list_l = read_index()
    except:
        find_index()
        index_list_r, index_list_l = read_index()
    # 得到每一段放电阶段里程与SOC消耗
    mileage = []
    SOC_deplete = []
    for i in range(len(index_list_r)):
        mileage.append(round(df['累计里程'][index_list_l[i]]-df['累计里程'][index_list_r[i]],1))
        SOC_deplete.append(df['SOC'][index_list_r[i]]-df['SOC'][index_list_l[i]])
    # 该数组用于记录出现问题的数据下标
    err_index = []
    for j in range(len(mileage)):
        # 单次行程普遍小于100
        if mileage[j] >= 40 or mileage[j] <= 20:
            # 出现误差的行程值暂时使用线性插值法进行填补
            mileage[j] = (mileage[j-2] + mileage[j-1])/2
            err_index.append(j)
        # SOC差值大于等于0
        if SOC_deplete[j] <= 20 or SOC_deplete[j] >= 70:
            SOC_deplete[j] = (SOC_deplete[j-2] + SOC_deplete[j-1])/2
    SOC_Eff = np.array(mileage)/np.array(SOC_deplete)
    mile_Eff = np.array(SOC_deplete)/np.array(mileage)
    start_I = []
    end_I = []
    start_U = []
    end_U = []
    min_tem = []
    for k in range(len(index_list_r)):
        start_I.append(df['总电流'][index_list_r[k]])
        end_I.append(df['总电流'][index_list_l[k]])
        start_U.append(df['总电压'][index_list_r[k]])
        end_U.append(df['总电压'][index_list_l[k]])
        min_tem.append(df['最低温度值'][index_list_r[k]])
    # 建立一个新的数据集
    new_data = pd.DataFrame({'里程/SOC':SOC_Eff,'SOC/里程':mile_Eff,'里程差值':mileage,'SOC差值':SOC_deplete,'起始电流':start_I,'终止电流':end_I,
                             '起始电压':start_U,'终止电压':end_U,'最低温度':min_tem})

def save_new_data(new_data,data_file_name):
    file_name = str(data_file_name) + "_new_data.csv"
    new_data.to_csv(file_name)
    print("文件"+file_name+"已保存")

def heat_map():
    mcorr = new_data.corr()
    mask = np.zeros_like(mcorr, dtype=np.bool)
    mask[np.triu_indices_from(mask)] = False
    cmap = sns.diverging_palette(220, 10, as_cmap=True)
    plt.figure()
    g = sns.heatmap(mcorr, mask=mask, cmap=cmap, square=True, annot=True, fmt='0.2f', cbar=False)
    return g

# if __name__ == "__main__":
#     for No in range(10):
#         file_name = str(No) + ".csv"
#         df = pd.read_csv(file_name)
#         index_list_r, index_list_l = find_index()
#         # 得到每一段放电阶段里程与SOC消耗
#         mileage = []
#         SOC_deplete = []
#         for i in range(len(index_list_r)):
#             mileage.append(round(df['累计里程'][index_list_l[i]]-df['累计里程'][index_list_r[i]],1))
#             SOC_deplete.append(df['SOC'][index_list_r[i]]-df['SOC'][index_list_l[i]])
#         # 该数组用于记录出现问题的数据下标
#         err_index = []
#         for j in range(len(mileage)):
#             # 单次行程普遍小于40且大于20
#             if mileage[j] >= 40 or mileage[j] <= 30:
#                 # 出现误差的行程值暂时使用线性插值法进行填补
#                 mileage[j] = (mileage[j-2] + mileage[j-1])/2
#                 err_index.append(j)
#             # SOC差值大于等于0
#             if SOC_deplete[j] <= 20 or SOC_deplete[j] >= 70:
#                 SOC_deplete[j] = (SOC_deplete[j-2] + SOC_deplete[j-1])/2
#         SOC_Eff = np.array(mileage)/np.array(SOC_deplete)
#         mile_Eff = np.array(SOC_deplete)/np.array(mileage)
#         start_I = []
#         end_I = []
#         start_U = []
#         end_U = []
#         min_tem = []
#         for k in range(len(index_list_r)):
#             start_I.append(df['总电流'][index_list_r[k]])
#             end_I.append(df['总电流'][index_list_l[k]])
#             start_U.append(df['总电压'][index_list_r[k]])
#             end_U.append(df['总电压'][index_list_l[k]])
#             min_tem.append(df['最低温度值'][index_list_r[k]])
#         # 建立一个新的数据集
#         new_data = pd.DataFrame({'里程/SOC':SOC_Eff,'SOC/里程':mile_Eff,'里程差值':mileage,'SOC差值':SOC_deplete,'起始电流':start_I,'终止电流':end_I,
#                                  '起始电压':start_U,'终止电压':end_U,'最低温度':min_tem})
#         save_new_data(new_data,No)
