'''
Author       : Tianzw
Date         : 2021-02-08 20:10:36
LastEditors  : Please set LastEditors
LastEditTime : 2021-03-29 21:39:28
FilePath     : /my_github/datetime/temp.py
'''
from datetime import datetime

import click
from matplotlib import ticker
import matplotlib.pyplot as plt
import pandas as pd

# # FuncFormatter can be used as a decorator
# @ticker.FuncFormatter
# def major_formatter(x, pos):
#     return "[%.2f]" % x

# ax.xaxis.set_major_formatter(major_formatter)


@click.command()
@click.argument('file-path')
def main(file_path):
    data = pd.read_csv(file_path)

    ts_ns = data['EventTimestamp(ns)'].values
    ts_ns_base = ts_ns[0]
    ts_ns = ts_ns - ts_ns_base
    acc = data[['AccelX', 'AccelY', 'AccelZ']].values

    plt.figure(figsize=(10, 5))
    plt.plot(ts_ns, acc[:, 0], label='AccelX')
    plt.plot(ts_ns, acc[:, 1], label='AccelY')
    plt.plot(ts_ns, acc[:, 2], label='AccelZ')

    @ticker.FuncFormatter
    def formatter(x, pos):
        x += ts_ns_base
        return datetime.fromtimestamp(int(
            x / 1e9)).time()  # xtick 为 datetime.time() 对象

    plt.gca().xaxis.set_major_formatter(formatter)
    plt.yticks(range(0, 20, 5), ['A', 'B', 'C', 'D'])

    plt.legend()

    plt.show()

    # data['EventTimestamp(ns)'] = data['EventTimestamp(ns)'].apply(lambda x: datetime.fromtimestamp(x / 1e9).time())
    # data.set_index('EventTimestamp(ns)', inplace = True)

    # plt.figure()
    # data[['AccelX', 'AccelY', 'AccelZ']].plot(figsize = (10, 5), ax = plt.gca())
    # plt.show()


if __name__ == "__main__":
    main()
