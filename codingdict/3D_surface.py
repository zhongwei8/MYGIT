import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np


def surface_3d():
    fig = plt.figure()
    ax = fig.gca(projection='3d')

    # Make data.
    X = np.arange(-5, 5, 0.25)
    Y = np.arange(-5, 5, 0.25)
    X, Y = np.meshgrid(X, Y)
    R = np.sqrt(X**2 + Y**2)
    Z = np.sin(R)

    # Plot the surface.
    surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm,
                        linewidth=0, antialiased=False)

    # Customize the z axis.
    ax.set_zlim(-1.01, 1.01)
    ax.zaxis.set_major_locator(LinearLocator(10))               # 刻度的个数
    ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))   # 刻度的格式

    # Add a color bar which maps values to colors.
    fig.colorbar(surf, shrink=0.5, aspect=5)

    plt.show()

if __name__ == '__main__':
    surface_3d()



x = ['2008-09-03',
    '2008-09-04',
    '2008-09-05',
    '2008-09-08',
    '2008-09-09',
    '2008-09-10',
    '2008-09-11',
    '2008-09-12',
    '2008-09-15',
    '2008-09-16',
    '2008-09-17',
    '2008-09-18',
    '2008-09-19',
    '2008-09-22',
    '2008-09-23',
    '2008-09-24',
    '2008-09-25',
    '2008-09-26',
    '2008-09-29',
    '2008-09-30',
    '2008-10-01',
    '2008-10-02',
    '2008-10-03',
    '2008-10-06',
    '2008-10-07',
    '2008-10-08',
    '2008-10-09',
    '2008-10-10',
    '2008-10-13',
    '2008-10-14']