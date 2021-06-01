'''
Author       : Tianzw
Date         : 2021-04-15 19:02:28
LastEditors  : Please set LastEditors
LastEditTime : 2021-04-16 11:47:49
FilePath     : /my_github/FFT/signal_welch.py
'''
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

np.random.seed(1234)


def main():
    fs = 10e3
    N = 1e5
    amp = 2 * np.sqrt(2)
    freq = 1234.0
    noise_power = 0.001 * fs / 2
    time = np.arange(N) / fs
    x = amp * np.sin(2 * np.pi * freq * time)
    x += np.random.normal(scale=np.sqrt(noise_power), size=time.shape)

    f, Pxx_den = signal.welch(x, fs, nperseg=1024)  # x.shape = ()

    print(f'f.shape, Pxx_den.shape = {f.shape}, {Pxx_den.shape}')

    print(f'f = {f}')

    print(f'Pxx_den = {Pxx_den}')
    plt.semilogy(f, Pxx_den)
    plt.ylim([0.5e-3, 1])
    plt.xlabel('frequency [Hz]')
    plt.ylabel('PSD [V**2/Hz]')
    plt.show()


if __name__ == '__main__':
    main()
