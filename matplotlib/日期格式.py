from datetime import date, datetime, timedelta

import numpy as np

import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.pyplot as plt


def run1():
    dates = ['1991-01-02', '1991-01-03', '1991-01-04']
    xs = [datetime.strptime(d, '%Y-%m-%d').date() for d in dates]
    ys = range(len(xs))

    plt.figure(figsize=(12, 6))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().yaxis.set_major_locator(mdates.DayLocator())

    plt.plot(xs, ys)
    # plt.gcf().autofmt_xdate()  # 自动旋转日期标记
    plt.show()


def run2():
    dates = ['2017-11-01', '2017-11-02', '2017-11-03', '2017-11-04']
    sales = [102.1, 100.6, 849, 682]
    x = [datetime.strptime(d, '%Y-%m-%d').date() for d in dates]
    y = sales

    fig = plt.figure(figsize=(12, 6))

    ax1 = fig.add_subplot(1, 1, 1)
    ax1.plot(x,
             y,
             ls='--',
             lw=3,
             color='b',
             marker='o',
             ms=6,
             mec='r',
             mew=2,
             mfc='w',
             label='业绩趋势走向')
    # plt.gcf().autofmt_xdate()  # 自动旋转日期标记

    # 1. 设置主刻度格式
    alldays = mdates.DayLocator()  # 主刻度为每天

    ax1.xaxis.set_major_locator(alldays)  # 设置主刻度
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    # 2. 设置副刻度格式
    hoursLoc = mpl.dates.HourLocator(interval=6)  # 6 小时为 1 副刻度
    ax1.xaxis.set_minor_locator(hoursLoc)
    ax1.xaxis.set_minor_formatter(mdates.DateFormatter('%H:%M:%S'))

    # 3. 其他设置
    ax1.tick_params(pad=15)  # pad: 刻度线与标签间的距离

    plt.show()


if __name__ == "__main__":
    run2()

##
# ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d')) # 主刻度
# ax.xaxis.set_minor_formatter(mdates.DateFormatter(%m))    # 副刻度
#
# monthsLoc = mpl.dates.MonthLocator()
# weeksLoc = mpl.dates.WeekdayLocator()
# ax.xaxis.set_major_locator(monthsLoc) # 主刻度位置
# ax.xaxis.set_minor_locator(weeksLoc) # 副刻度位置
#
# monthsFmt = mpl.dates.DateFormatter('%b')
# ax.xaxis.set_major_formatter(monthsFmt)
#
##
