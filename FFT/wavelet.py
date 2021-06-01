# -*- coding: utf-8 -*-
from matplotlib.font_manager import FontProperties
import matplotlib.pyplot as plt
import numpy as np
import pywt


def main():
    sampling_rate = 1024
    t = np.arange(0, 1.0, 1.0 / sampling_rate)
    f1 = 100
    f2 = 200
    f3 = 300
    data = np.piecewise(t, [t < 1, t < 0.8, t < 0.3], [
        lambda t: np.sin(2 * np.pi * f1 * t),
        lambda t: np.sin(2 * np.pi * f2 * t),
        lambda t: np.sin(2 * np.pi * f3 * t)
    ])
    wavename = 'cgau8'
    totalscal = 1024  # not important, only effect frequencies delta
    fc = pywt.central_frequency(wavename)  # 中心频率
    cparam = 2 * fc * totalscal
    scales = cparam / np.arange(totalscal, 1, -1)  # 尺度因子

    [cwtmatr, frequencies] = pywt.cwt(data, scales, wavename,
                                      1.0 / sampling_rate)

    print(f'scales delta = {np.diff(scales).mean()}')
    print(f'fc = {fc}')
    print(f'cparam = {cparam}')
    print(f'scales.shape = {scales.shape}')
    print(f'cwtmatr.shape = {cwtmatr.shape}')
    print(f'frequencies.shape = {frequencies.shape}')

    print(f'scales[: 5] = {scales[: 5]}')
    print(f'scales[: 5] = {scales[: 5]}')

    print(f'frequencies[: 5] = {frequencies[: 5]}')
    print(f'frequencies[-5: ] = {frequencies[-5: ]}')

    plt.figure(figsize=(18, 6))
    plt.subplot(211)
    plt.plot(t, data)
    plt.xlabel('s')
    plt.title('300Hz, 200Hz and 100Hz', fontsize=20)

    plt.subplot(212)
    plt.contourf(t, frequencies, abs(cwtmatr))
    plt.ylabel('f(Hz)')
    plt.xlabel('t')
    plt.subplots_adjust(hspace=0.4)
    plt.show()


if __name__ == "__main__":
    main()
