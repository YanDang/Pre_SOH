import pandas as pd
import matplotlib.pyplot as plt
from pylab import mpl
import numpy as np
from scipy.fft import irfft,rfft

def pre_80_SOH():
    # 当SOH为初始值的80%时
    SOH = y_fit[0] * 0.8
    plt.axhline(y_fit[0]*0.8,linestyle="-.",color="y",label="80%等效续航里程")
    x_pre = round((SOH - coef[2]) / coef[1])
    y_l_fit = np.polyval(coef,range(x_pre))
    plt.plot(range(x_pre), y_l_fit,c="r")
    plt.axvline(x_pre,ymin=0,ymax=SOH,linestyle="--",color="g")
    plt.plot([x_pre], [SOH], ".k")
    plt.annotate("(%d,%.2f)" % (x_pre, SOH), [x_pre-400, SOH+0.03])
    plt.legend()

if __name__ == "__main__":
    file_No = 9
    file_name = str(file_No) + "_new_data.csv"
    df_data = pd.read_csv(file_name)
    mpl.rcParams['font.sans-serif'] = ['DengXian']
    mpl.rcParams['axes.unicode_minus'] = False
    x = range(len(df_data))
    coef = np.polyfit(x,df_data['里程/SOC'],2)
    y_fit = np.polyval(coef, x)
    plt.subplot(2, 1, 1)
    plt.xlabel("放电循环")
    plt.ylabel("等效续航里程/km")
    plt.scatter(x, df_data['里程/SOC'],label="等效续航里程")
    plt.plot(x, y_fit, c="r", label="二次方程")
    plt.legend()
    plt.grid(linestyle="--")
    plt.subplot(2, 1, 2)
    coef_T = np.polyfit(x,df_data['最低温度'],2)
    y_T_fit = np.polyval(coef_T,x)
    plt.xlabel("放电循环")
    plt.ylabel("最低温度值/℃")
    plt.scatter(x,df_data['最低温度'],label="最低温度值")
    plt.plot(x,y_T_fit,c="r",label="二次方程")
    plt.legend()
    plt.grid(linestyle="--")
    # 傅里叶变换
    plt.figure()
    n = len(df_data)
    yf = rfft(df_data['最低温度'].to_list())
    yf_abs = np.abs(yf)
    indices = yf_abs > 700
    yf_clean = indices * yf
    new_f_clean = irfft(yf_clean)
    plt.plot(range(len(yf_abs)),yf_abs,"-o",label="最低温度")
    plt.xlabel("频率/Hz")
    plt.title("最低温度频率域视图")
    plt.figure()
    plt.plot(range(n - 1), new_f_clean)
    plt.xlabel("放电循环")
    plt.ylabel("最低温度/℃")
    plt.figure()
    n = len(df_data)
    indices = yf_abs < 700
    yf = rfft(df_data['里程/SOC'].to_list())
    yf_abs = np.abs(yf)
    indices[0] = True
    yf_clean = indices * yf
    new_f_clean = irfft(yf_clean)
    plt.plot(range(len(yf_abs)),yf_abs,"-o",label="等效续航里程")
    plt.xlabel("频率/Hz")
    plt.title("等效续航里程频率域视图")
    plt.figure()
    x = range(len(df_data)-1)
    coef = np.polyfit(x, new_f_clean, 2)
    y_fit = np.polyval(coef, x)
    plt.scatter(range(n-1),new_f_clean,label="删去温度影响的值")
    plt.plot(range(n - 1), y_fit,label="二次函数拟合",c="r")
    print(y_fit[0])
    print(y_fit[-1])
    plt.legend()
    plt.grid(linestyle="--")
    plt.xlabel("放电循环")
    plt.ylabel("等效续航里程/km")
    plt.title("({:.1f}e-11)x^2+({:.1f}e-5)x+{:.1f}".format(coef[0]*10**11,coef[1]*10**5,coef[2]))
    pre_80_SOH()
    plt.figure()
    y_normalize = new_f_clean / y_fit[0]
    plt.scatter(range(n-1),y_normalize,label="转换后的SOH")
    plt.plot([0,5843],[1,0.8],color="r",label="二次函数拟合")
    plt.axhline(0.8, linestyle="-.", color="y", label="80%等效续航里程")
    plt.axvline(5843, ymin=0, ymax=0.8, linestyle="--", color="g")
    plt.plot([5843], [0.8], ".k")
    plt.annotate("(%d,%.2f)" % (5843, 0.8), [5843 - 400, 0.8 + 0.03])
    plt.xlabel("放电循环")
    plt.ylabel("SOH")
    plt.grid(linestyle="--")
    plt.legend()