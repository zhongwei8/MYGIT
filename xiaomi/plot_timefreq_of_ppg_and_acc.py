#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: xiaoping Liu
# @Date:   2021-01-09 15:36:33
# @Last Modified by:   xiaoping Liu
# @Last Modified time: 2021-02-04 22:38:37

from glob import glob
import os
import os.path as osp
from pathlib import Path
import sys

import click
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ALGO_DIR = Path(__file__).parent / 'algo'
sys.path.append(str(ALGO_DIR))

from algo.hr_dataset import HrData
from algo.hr_process_algo import MiotFFT, PreProcess

SAMPLE_FS = 26

MERGED_PATTERN = '*accel-ppg-merged-52HZ.csv'


class DirUtils:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.base_name = root_dir.split('/')[-1]
        self.sample_dir_name = os.listdir(root_dir)

    def _get_datas(self):
        """get data from curr curr dir

        datas: ppg, acc, hr(ground truth)
        """
        print(f'base name {self.base_name}')
        data_file_name = glob(osp.join(self.root_dir, MERGED_PATTERN))[0]
        data_df = pd.read_csv(data_file_name)

        ppg_d = data_df[['CurrentTimeMillis', 'ch1']].values
        acc_d = data_df[[
            'EventTimestamp(ns)', 'accel_x', 'accel_y', 'accel_z'
        ]].values
        ppg_d = ppg_d[::2]
        acc_d = acc_d[::2]

        return acc_d, ppg_d


def get_timefreq(record) -> tuple:
    dir_utils = DirUtils(record)
    acc_vals, ppg_vals = dir_utils._get_datas()

    print(f'acc data shape: {acc_vals.shape}')
    print(f'ppg data shape: {ppg_vals.shape}')
    print(f'total collect second (s): '
          f'{(ppg_vals[-1, 0] - ppg_vals[0, 0]) * 1E-9}')

    # signal preprocess
    time_freq = []
    time_freq_acc = []
    time_freq_accx = []
    time_freq_accy = []
    time_freq_accz = []

    hr_data = HrData(SAMPLE_FS, 1, 8)
    hr_fft = MiotFFT()
    hr_process = PreProcess()

    for i, ppg_d in enumerate(ppg_vals[:, 1]):
        curr_win_ppg, curr_win_acc = hr_data.get_win(ppg_d, acc_vals[i, 1:])
        if curr_win_ppg is None:
            continue

        # signal pre-process
        curr_win_ppg = hr_process(curr_win_ppg, np.sum(curr_win_acc, axis=1),
                                  SAMPLE_FS, 0.5, 4.5)
        _, win_fft = hr_fft._welch_fft(curr_win_ppg, SAMPLE_FS)
        time_freq.append(win_fft)

        # accx spec
        _, win_accx_fft = hr_fft._welch_fft(curr_win_acc[:, 0], SAMPLE_FS)
        time_freq_accx.append(win_accx_fft)

        # accy spec
        _, win_accy_fft = hr_fft._welch_fft(curr_win_acc[:, 1], SAMPLE_FS)
        time_freq_accy.append(win_accy_fft)

        # accz spec
        _, win_accz_fft = hr_fft._welch_fft(curr_win_acc[:, 2], SAMPLE_FS)
        time_freq_accz.append(win_accz_fft)

        _, win_acc_fft = hr_fft._welch_fft(np.sum(curr_win_acc, axis=-1),
                                           SAMPLE_FS)
        time_freq_acc.append(win_acc_fft)

    # handle ppg spec
    time_freq = np.array(time_freq).T
    time_freq = hr_fft._sepc_select(time_freq, SAMPLE_FS, 0.4, 4.5)[::-1]

    timefreq_acc = np.array(time_freq_acc).T
    timefreq_acc = hr_fft._sepc_select(timefreq_acc, SAMPLE_FS, 0.4, 4.5)[::-1]

    # handle acc spec
    time_freq_acc = np.array(time_freq_accx).T
    time_freq_acc = hr_fft._sepc_select(time_freq_acc, SAMPLE_FS, 0.4,
                                        4.5)[::-1]

    time_freq_acc = np.array(time_freq_accy).T
    time_freq_acc = hr_fft._sepc_select(time_freq_acc, SAMPLE_FS, 0.4,
                                        4.5)[::-1]

    time_freq_acc = np.array(time_freq_accz).T
    time_freq_acc = hr_fft._sepc_select(time_freq_acc, SAMPLE_FS, 0.4,
                                        4.5)[::-1]

    return (time_freq, time_freq_acc)


def plot_timefreq(time_freq, time_freq_acc) -> None:
    plt.figure(figsize=(12, 6))
    y_label = [i * 60 * (SAMPLE_FS / (256)) for i in range(time_freq.shape[0])]
    plt.yticks(np.arange(time_freq.shape[0]), y_label[::-1])
    plt.ylabel('Bpm')
    plt.title('PPG time-freq graph (after process)')
    plt.imshow(time_freq, cmap='jet', interpolation='nearest', aspect='auto')

    plt.figure(figsize=(12, 6))

    y_label = [
        i * 60 * (SAMPLE_FS / (256)) for i in range(time_freq_acc.shape[0])
    ]
    plt.yticks(np.arange(time_freq_acc.shape[0]), y_label[::-1])
    plt.ylabel('Bpm')
    plt.title('ACC time-freq graph (after process)')
    plt.imshow(time_freq_acc,
               cmap='jet',
               interpolation='nearest',
               aspect='auto')

    plt.show()


def run(record):
    time_freq, time_freq_acc = get_timefreq(record)
    plot_timefreq(time_freq, time_freq_acc)


@click.command()
@click.argument('record')
def main(record):
    run(record)


if __name__ == "__main__":
    main()
