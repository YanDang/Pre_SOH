import sklearn as sk
import pandas as pd
import sklearn.ensemble
import matplotlib.pyplot as plt
from pylab import mpl
import pickle

if __name__ == "__main__":
    mpl.rcParams['font.sans-serif'] = ['DengXian']
    mpl.rcParams['axes.unicode_minus'] = False
    model_No = 3
    model = [sk.ensemble.BaggingRegressor(),sk.linear_model.LinearRegression(),sk.svm.SVR(),sk.tree.DecisionTreeRegressor(),sk.tree.ExtraTreeRegressor()]
    V_x_train = []
    V_y_train = []
    for file_No in range(4):
        file_name = str(file_No) + "_new_data.csv"
        df_data = pd.read_csv(file_name)
        for i in range(len(df_data)):
            V_x_train.append([df_data['最低温度'][i],df_data['起始电压'][i]])
        V_y_train += list(df_data['终止电压'])
    rf_end_V = model[model_No]
    rf_end_V.fit(V_x_train,V_y_train)
    V_x_pre = []
    V_y_test = []
    # 预测终止电压
    for file_No in range(4,9):
        file_name = str(file_No) + "_new_data.csv"
        df_data = pd.read_csv(file_name)
        for i in range(len(df_data)):
            V_x_pre.append([ df_data['最低温度'][i], df_data['起始电压'][i]])
        V_y_test += list(df_data['终止电压'])
    plt.figure()
    plt.scatter(range(len(V_y_test)), V_y_test,label="真实值")
    V_y_pre = rf_end_V.predict(V_x_pre)
    plt.scatter(range(len(V_y_pre)), V_y_pre,label="预测值",marker="^")
    plt.legend()
    RMSE_sums = 0
    MAE_sums = 0
    relative_sums = 0
    for k in range(len(V_y_test)):
        RMSE_sums += (V_y_test[k] - V_y_pre[k]) ** 2
        MAE_sums += abs(V_y_test[k] - V_y_pre[k])
        relative_sums += abs(V_y_test[k] - V_y_pre[k]) / V_y_test[k]
    relative_error = relative_sums / len(V_y_test)
    RMSE = (RMSE_sums / len(V_y_test)) ** (1 / 2)
    MAE = MAE_sums / len(V_y_test)
    plt.xlabel("放电循环/次")
    plt.ylabel("终止电压/V")
    plt.title("RMSE:{:.4f}\nMAE:{:.4f}\n相对误差:{:.4f}%".format(RMSE, MAE,relative_error*100))
    pkl_filename = "pickle_V_model.pkl"
    with open(pkl_filename, 'wb') as file:
        pickle.dump(rf_end_V, file)

    index = 0
    x_train = []
    x_test = []
    y_train = []
    y_test = []
    for file_No in range(4,10):
        file_name = str(file_No) + "_new_data.csv"
        df_data = pd.read_csv(file_name)
        if file_No != 9:
            for i in range(len(df_data)):
                x_train.append([V_y_pre[index], df_data['最低温度'][i], df_data['起始电压'][i]])
                index += 1
            y_train += list(df_data['里程/SOC'])
        if file_No == 9:
            for i in range(len(df_data)):
                x_test.append([df_data['终止电压'][i],df_data['最低温度'][i],df_data['起始电压'][i]])
            y_test += list(df_data['里程/SOC'])
    rf = model[model_No]
    rf.fit(x_train, y_train)
    plt.figure()
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
    # 存储模型
    pkl_filename = "pickle_model.pkl"
    with open(pkl_filename,'wb') as file:
        pickle.dump(rf,file)