import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator, LinearLocator

def main():
    fig, ax = plt.subplots()
    xs = range(26)
    ys = range(26)
    labels = list('abcdefghijklmnopqrstuvwxyz')


    def format_fn(tick_val, tick_pos):
        if int(tick_val) in xs:
            return labels[int(tick_val)]
        else:
            return ''

    formatter = plt.FuncFormatter(format_fn)


    ax.xaxis.set_major_formatter(formatter)
    #ax.xaxis.set_major_locator(MaxNLocator(integer=True))      # 显示最大范围
    #ax.xaxis.set_major_locator(LinearLocator(10))               # 显示指定范围
    ax.plot(xs, ys)
    plt.show()

if __name__ == "__main__":
    main()