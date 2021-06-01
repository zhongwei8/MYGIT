import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker
import datetime


def plot_with_datetime(data: np.ndarray):
    ts = data[:, 0]
    x = data[:, 1]
    y = data[:, 2]

    fig, axes = plt.subplots(2, 1, sharex=True, figsize=(12, 6))

    axes[0].plot(ts, x, label='x', marker='o')
    axes[1].plot(ts, y, label='y', marker='o')

    def format_func(x_tick, pos=None):
        dt = datetime.datetime.fromtimestamp(x_tick // 1000)
        return dt.strftime('%H:%M:%S')

    axes[1].xaxis.set_major_formatter(ticker.FuncFormatter(format_func))

    plt.show()


def test():
    ts = 1608729924633
    offset = [i * 100 + ts for i in range(100)]
    data = np.zeros((100, 3))
    data[:, 0] = np.array(offset)
    data[:, 1:] = np.random.randint(0, 1000, size=(100, 2))
    plot_with_datetime(data)


if __name__ == "__main__":
    test()
