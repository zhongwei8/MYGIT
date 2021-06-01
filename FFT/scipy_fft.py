'''
Author       : Tianzw
Date         : 2021-03-30 12:44:10
LastEditors  : Please set LastEditors
LastEditTime : 2021-03-30 12:50:58
FilePath     : /my_github/FFT/scipy_fft.py
'''
import import
import matplotlib.pylab
import matplotlib.pyplot as plt
import mpl
import numpy as np
from scipy.fftpack import fft, ifft

x = np.linspace(0, 1, 1400)
y = 7 * np.sin(2 * np.pi * 200 * x) +\
    5 * np.sin(2 * np.pi * 400 * x) +\
    3 * np.sin(2 * np.pi * 600 * x)

fft_y = fft(y)

print(len(fft_y))
print(fft_y[0: 5])

N = 1400
x = np.arange(N)
abs_y = np.abs(fft_y)
angle_y = np.angle(fft_y)

plt.figure()
plt.plot(x, abs_y)

plt.figure()
plt.plot(x, angle_y)
plt.show()
