import pandas as pd
import os
from pylab import mpl

if __name__ == "__main__":
    pd_data = pd.DataFrame()
    # 设置绘图字体
    mpl.rcParams['font.sans-serif'] = ['DengXian']
    mpl.rcParams['axes.unicode_minus'] = False
    # 这里是数据文件夹的路径
    datadir_path = "D:/编程类/实车SOC/data/"
    # 使用dir_list存储数据文件夹下的子文件夹
    dir_list = os.listdir(datadir_path)
    file_dir_path = datadir_path + dir_list[0] + "/"
    file_name_list = os.listdir(file_dir_path)
    file_name = file_name_list[0]
    file_path = file_dir_path + file_name
    temp_data = pd.read_csv(file_path)
    pd_data = pd_data.append(temp_data)
    columns = ['经度','维度']
    new_data = (pd_data[columns]/10**6)[:50000]
    lists = []
    for i in range(len(new_data)):
        lists.append([new_data['经度'][i],new_data['维度'][i]])
    save_data = pd.DataFrame({'经纬度':lists})
    save_data.to_csv('plot_route_map.csv')