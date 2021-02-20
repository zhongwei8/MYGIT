import matplotlib.pyplot as plt
import numpy as np

"""
API Overview >> matplotlib.axis >> matplotlib.axis.XAxis.set_major_formatter

matplotlib.axis.XAxis.set_major_formatter


"""

def saveHistogram(fname, x, bins = 50, show = True):
    def to_percent(x, pos):
        s = format(100 * x, '.2f')                  # format(1.2345, '.2f')
        if plt.rcParams['text.usetex'] is True:
            return s + r'$\%$'
        else:
            return s + '%'
        
    plt.hist(x, bins = bins, density = True)

    formatter = plt.FuncFormatter(to_percent)
    plt.gca().xaxis.set_major_formatter(formatter)

    plt.savefig(fname)
    if show == True:
        plt.show()
    plt.close()


def main():
    x = np.random.rand(1000)                        # np.random.rand(d0, d1, ..., dn)
    fname = './codingdict/data/jpg/hist.jpg'
    saveHistogram(fname, x)



if __name__ == '__main__':
    main()