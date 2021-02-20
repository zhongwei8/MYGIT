import matplotlib.pyplot as plt
import matplotlib.dates as mdates               # 日期刻度
from datetime import datetime

import matplotlib as mpl

def main():
    #销售数据
    dates=['2021-10-11 12:11:20','2021-10-11 12:12:20','2021-10-11 12:13:20','2021-10-11 12:14:20']
    sales=[102.1,100.6,849,682]
    #将dates改成日期格式
    x= [datetime.strptime(d, '%Y-%m-%d %H:%M:%S').date() for d in dates]
    print(f'x = {x}')
    
    #figure布局
    fig=plt.figure(figsize=(8,4))
    ax1=fig.add_subplot(1,1,1) 
    #绘图
    ax1.plot(x,sales,ls='--',lw=3,color='b',marker='o',ms=6, mec='r',mew=2, mfc='w',label='业绩趋势走向')
    # plt.gcf().autofmt_xdate()  # 自动旋转日期标记
    
    # #设置x轴主刻度格式
    # alldays =  mdates.HourLocator()                #主刻度为每天
    # ax1.xaxis.set_major_locator(alldays)          #设置主刻度
    # ax1.xaxis.set_major_formatter(mdates.DateFormatter('%h'))  
    # #设置副刻度格式
    # hoursLoc = mpl.dates.HourLocator(interval=6) #为6小时为1副刻度
    # secondLoc = mpl.dates.MinuteLocator(interval = 1)
    # # ax1.xaxis.set_minor_locator(hoursLoc)
    # # ax1.xaxis.set_minor_formatter(mdates.DateFormatter('%H'))

    # ax1.xaxis.set_minor_locator(secondLoc)
    # ax1.xaxis.set_minor_formatter(mdates.DateFormatter('%s'))
    # #参数pad用于设置刻度线与标签间的距离
    # ax1.tick_params(pad=10)
    
    #显示图像
    plt.show()

if __name__ == "__main__":
    main()