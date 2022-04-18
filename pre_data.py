# 考虑到数据使用csv文件存储，因此使用pandas库便于处理
# Pandas教程参考自阿里云天池大数据教程，有需要请访问 https://tianchi.aliyun.com/notebook-ai/detail?spm=5176.12586969.1002.6.99f31c27KIOlLT&postId=137714
# 关联性分析教程参考自阿里云天池大数据教程，如有需要请访问 https://tianchi.aliyun.com/notebook-ai/detail?spm=5176.12586969.1002.3.974f3f732ZjmEu&postId=198142
import os
import pandas as pd
import numpy as np
import seaborn as sns
import sklearn.ensemble
from pylab import mpl
import matplotlib.pyplot as plt


# 对缺失数据进行填充
def pre_fill_isna(df):
    # 统计所有参数缺失数据数量
    for i in column:
        print("{}的缺失数量：{}".format(i,len(df[df[i].isna()])))
    # 车速的缺失数据和累计里程的缺失数据原因在于车辆处于停车状态因此车速使用0进行填充
    # 累计里程则使用前一段数据
    df['车速'] = df['车速'].fillna(0)
    df['累计里程'] = df['累计里程'].fillna(method='ffill')
    # 考虑时间戳，使用线性插值方法对剩余数据进行填充
    for j in column[:16]:
        df[j] = df[j].interpolate(method='index')
    # 充电状态用前一数据填充
    df['充电状态'] = df['充电状态'].fillna(method='ffill')
    return df

    # 没有考虑时间戳，不建议使用该段代码，不过不考虑时间戳的情况下误差也很小
    # 使用线性插值方法对剩余数据进行填充
    # for j in column:
    #     df[j] = df[j].interpolate()
    #     # 若首尾出现nan，此时线性插值无法填充，使用最近邻填充

# 存储为csv格式的文件
def to_csv(df,No):
    w_name = str(No) + ".csv"
    # w_name = input("请输入文件名") + ".csv"
    df.to_csv(w_name)
    print("数据集已存储至{}".format(w_name))
# 使用随机森林算法对数据进行填充
# def Random_Forest():
#     rf = sklearn.ensemble.RandomForestRegressor()

# 设计一个用于切片的算法
# 统计缺失数据，删除缺失数据，数据预处理
def pre_del_isna(file_name,df):
    loss_data = len(df[df.isna().any(1)])
    print("{}数据集{}个数据含有缺失数据".format(file_name,loss_data))
    res = df.dropna(how='any')
    print("数据已删除")
    return res

# 统计参数相关性，绘制热图
def heat_map():
    mcorr = df.corr()
    mask = np.zeros_like(mcorr,dtype=np.bool)
    mask[np.triu_indices_from(mask)] = False
    cmap = sns.diverging_palette(220,10,as_cmap=True)
    plt.figure()
    g = sns.heatmap(mcorr,mask=mask,cmap=cmap,square=True,annot=True,fmt='0.2f',cbar=False)
    return g

if __name__ == "__main__":
    # data_No记录打开的数据集
    # data_No = 0
    for data_No in range(10):
        # 设置存储所有数据的DataFrame
        pd_data = pd.DataFrame()
        # 设置绘图字体
        mpl.rcParams['font.sans-serif'] = ['DengXian']
        mpl.rcParams['axes.unicode_minus'] = False
        # 这里是数据文件夹的路径
        datadir_path = "D:/编程类/实车SOC/data/"
        # 使用dir_list存储数据文件夹下的子文件夹
        dir_list = os.listdir(datadir_path)
        '''
        # 统计数据总量
        sum_data_len = 0
        for dir_name in dir_list:
            file_dir_path = datadir_path + dir_name + "/"
            file_name_list = os.listdir(file_dir_path)
            file_name = file_name_list[0]
            file_path = file_dir_path + file_name
            pd_data = pd.read_csv(file_path)
            data_len = pd_data.index.stop
            sum_data_len += data_len
        print("总数据量是:%d(未排除无效数据)" % sum_data_len)
        '''
        # 后续代码使用第一个文件夹中的第一个文件为例
        file_dir_path = datadir_path + dir_list[data_No] + "/"
        file_name_list = os.listdir(file_dir_path)
        file_name = file_name_list[0]
        file_path = file_dir_path + file_name
        temp_data = pd.read_csv(file_path)
        pd_data = pd_data.append(temp_data)
        '''
        # 读入所有数据的代码，遗留关于pd.DataFrame合并问题没有解决
        # for i in range(len(dir_list)):
        #     file_dir_path = datadir_path + dir_list[data_No] + "/"
        #     file_name_list = os.listdir(file_dir_path)
        #     file_name = file_name_list[0]
        #     file_path = file_dir_path + file_name
        #     temp_data = pd.read_csv(file_path)
        #     pd_data = pd_data.merge(temp_data) # 该部分代码需要修改
        #     data_No += 1
        # file = open(file_path,encoding="utf-8") # 注意使用utf-8编码打开，否则中文字符乱码
        # column = pd_data.columns.tolist()
        '''
        column = ['车速', '总电压', '总电流', '累计里程', 'SOC', '电池单体电压最高值', '电池单体电压最低值', '最高温度值', '最低温度值', '驱动电机转速', '驱动电机转矩',
                  '驱动电机温度', '驱动电机控制器温度', '电机控制器输入电压', '电机控制器直流母流电流', '加速踏板行程值', '充电状态']  # 使用有效参数进行分析
        df = pd_data[column]  # 将所需要用到的参数存入df变量
        df.index = pd.to_datetime(pd_data['时间'])
        df = df.sort_index()
        pre_fill_isna(df)
        to_csv(df,data_No)
