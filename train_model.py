import os
from sklearn import svm
import sklearn as sk
import sklearn.ensemble
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pylab import mpl
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

if __name__ == "__main__":
    # 设置绘图字体
    mpl.rcParams['font.sans-serif'] = ['DengXian']
    mpl.rcParams['axes.unicode_minus'] = False
    x_train = []
    x_test = []
    y_train = []
    y_test = []
    for file_No in range(10):
        file_name = str(file_No) + "_new_data.csv"
        df_data = pd.read_csv(file_name)
        if file_No != 9:
            for i in range(len(df_data)):
                x_train.append([df_data['最低温度'][i],df_data['起始电压'][i]])
            y_train += list(df_data['里程/SOC'])
        if file_No == 9:
            for i in range(len(df_data)):
                x_test.append([df_data['最低温度'][i],df_data['起始电压'][i]])
            y_test += list(df_data['里程/SOC'])
    '''此处是对数据进行归一化的代码，'''
    # x_train = StandardScaler().fit_transform(x_train)
    # x_text = StandardScaler().fit_transform(x_text)
    # y_train_ls = StandardScaler().fit_transform([[y] for y in y_train])
    # y_train = [y[0] for y in y_train_ls]
    # y_text_ls = StandardScaler().fit_transform([[y] for y in y_text])
    # y_text = [y[0] for y in y_text_ls]
    # 调用随机森林回归算法
    rf = sk.ensemble.RandomForestRegressor()
    rf.fit(x_train, y_train)
    plt.scatter(range(len(y_test)), y_test,label="真实值")
    y_pre = rf.predict(x_test)
    plt.scatter(range(len(x_test)), y_pre,label="预测值",marker="^")
    plt.legend()
    RMSE_sums = 0
    MAE_sums = 0
    relative_sums = 0
    for k in range(len(y_test)):
        RMSE_sums += (y_test[k] - y_pre[k]) ** 2
        MAE_sums += abs(y_test[k] - y_pre[k])
        relative_sums += abs(y_test[k] - y_pre[k])/y_test[k]
    relative_error = relative_sums / len(y_test)
    RMSE = (RMSE_sums / len(y_test)) ** (1 / 2)
    MAE = MAE_sums / len(y_test)
    plt.xlabel("放电循环/次")
    plt.ylabel("里程/SOC")
    plt.title("RMSE:{:.4f}\nMAE:{:.4f}\n相对误差:{:.4f}%".format(RMSE, MAE,relative_error*100))
    # plt.plot(df_data['里程差值'])
# 读取单个数据集进行训练与测试
# if __name__ == "__main__":
#     # 设置绘图字体
#     mpl.rcParams['font.sans-serif'] = ['DengXian']
#     mpl.rcParams['axes.unicode_minus'] = False
#     df_data = pd.read_csv("9_new_data.csv")
#     rf = sk.ensemble.ExtraTreesRegressor()
#     x_train = []
#     x_text = []
#     y_train = list(df_data['SOC/里程'][:1200])
#     y_text = list(df_data['SOC/里程'][1200:])
#     for i in range(1200):
#         x_train.append([df_data['终止电压'][i],df_data['最低温度'][i],df_data['起始电压'][i],df_data['里程差值'][i]])
#     for j in range(len(df_data['最低温度'])-1200):
#         x_text.append([df_data['终止电压'][j],df_data['最低温度'][j],df_data['起始电压'][j],df_data['里程差值'][j]])
#     rf.fit(x_train,y_train)
#     plt.plot(range(len(y_text)),y_text)
#     y_pre = rf.predict(x_text)
#     plt.plot(range(len(x_text)),y_pre)
#     RMSE_sums = 0
#     MAE_sums = 0
#     for k in range(len(y_text)):
#         RMSE_sums += (y_text[k] - y_pre[k])**2
#         MAE_sums += abs(y_text[k] - y_pre[k])
#     RMSE = (RMSE_sums/len(y_text))**(1/2)
#     MAE = MAE_sums/len(y_text)
#     plt.title("RMSE:{:.4f}\nMAE:{:.4f}".format(RMSE,MAE))
#     plt.figure()
#     # plt.plot(df_data['里程差值'])