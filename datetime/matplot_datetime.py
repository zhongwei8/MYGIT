from datetime import datetime
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


iosformat = '%Y-%m-%d %H:%M:%S'
iosdateformat = '%Y-%m-%d'
iostimeformat = '%H:%M:%S'

def main():
    date_strings = ['2016-12-20 09:52:54',
                    '2016-12-20 15:52:54',
                    '2016-12-20 21:52:54',
                    '2016-12-21 03:52:54']
    xs = [datetime.strptime(m, iosformat) for m in date_strings]
    ys = range(len(xs))

    fig, axes = plt.subplots(2, 1, figsize = (12, 8), sharex = True)

    axes[0].plot(xs, ys)
    axes[0].xaxis.set_major_formatter(mdates.DateFormatter(iosdateformat))

    axes[1].plot(xs, ys)
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter(iostimeformat))

    plt.gcf().autofmt_xdate()               # 自动旋转 figure 对象的 日期标记
    plt.show()

if __name__ == "__main__":
    main()
