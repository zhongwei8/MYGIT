#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: xiaoping Liu
# @Date:   2021-01-09 15:36:33
# @Last Modified by:   xiaoping Liu
# @Last Modified time: 2021-02-04 22:38:37

from datetime import datetime
from glob import glob
from multiprocessing import Pool, cpu_count
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
NFFT = 1024
MERGED_PATTERN = '*accel-ppg-merged-52HZ.csv'
POLAR_HEARTRATE_PATTERN = 'polar_*.csv'
GARMIN_HEARTRATE_PATTERN = 'garmin_*.fit'
LIFEQ_HEARTRATE_SUFFIX = '-heartrate-xHZ.csv'
LIBAI_PREFIX = 'libai_'

GARMIN_HEARTRATE_HEADER_LINE = 2

FIG_DIR = Path(__file__).parent / '../../data/fig'


def get_lifeq_heartrate_path(record: Path) -> Path:
    record_key = record.name.split('-')[0]
    lifeq_heartrate_name = LIBAI_PREFIX + record_key + LIFEQ_HEARTRATE_SUFFIX
    lifeq_heartrate_path = record / lifeq_heartrate_name

    return lifeq_heartrate_path


def get_lifeq_heartrates(lifeq_heartrate_path: Path,
                         lifeq_header_line=1) -> np.ndarray:

    lifeq_heartrate_df = pd.read_csv(lifeq_heartrate_path,
                                     header=lifeq_header_line)
    lifeq_heartrates = lifeq_heartrate_df[['CurrentTimeMillis', 'BPM']].values
    lifeq_heartrates[:, 0] = lifeq_heartrates[:, 0] // 1000

    return lifeq_heartrates


def get_polar_heartrate_path(record: Path) -> Path:
    polar_iter = record.glob(POLAR_HEARTRATE_PATTERN)

    polar_heartrate_path = None
    try:
        polar_heartrate_path = [path for path in polar_iter][0]
    except IndexError:
        print(f'No polar heartrate file in {record.name}')

    return polar_heartrate_path


def get_polar_heartrates(polar_heartrate_path: Path) -> np.ndarray:

    if polar_heartrate_path is None or not polar_heartrate_path.exists():
        return

    start_timestamp = None
    with open(str(polar_heartrate_path), 'r') as f:
        f.readline()
        secondline = f.readline()
        date_str, time_str = secondline.split(',')[2], secondline.split(',')[3]
        datetime_str = date_str + ' ' + time_str
        start_datetime = datetime.strptime(datetime_str, '%d-%m-%Y %H:%M:%S')
        start_timestamp = int(start_datetime.timestamp())

    heartrate_df = pd.read_csv(polar_heartrate_path,
                               header=GARMIN_HEARTRATE_HEADER_LINE)

    heartrate_df = heartrate_df[heartrate_df['HR (bpm)'] > 0]

    heartrates = heartrate_df[['HR (bpm)']].values
    timestamps = np.arange(len(heartrates)).reshape((-1, 1)) + start_timestamp

    return np.hstack((timestamps, heartrates)).astype(np.int)


class DirUtilsV2:
    def __init__(self, record_dir: Path):
        self.record_dir = Path(record_dir)

    def _get_acc_ppg_merged_path(self):
        acc_ppg_merged_iter = self.record_dir.glob(MERGED_PATTERN)

        acc_ppg_merged_path = None
        try:
            acc_ppg_merged_path = [path for path in acc_ppg_merged_iter][0]
        except IndexError:
            print(f'No acc ppg merged file in {self.libai_record.name}')

        return acc_ppg_merged_path

    def _get_polar_heartrate_path(self):
        polar_iter = self.libai_record.glob(POLAR_HEARTRATE_PATTERN)

        polar_heartrate_path = None
        try:
            polar_heartrate_path = [path for path in polar_iter][0]
        except IndexError:
            print(f'No polar heartrate file in {self.libai_record.name}')

        return polar_heartrate_path

    def _get_garmin_heartrate_path(self):
        garmin_iter = self.libai_record.glob(GARMIN_HEARTRATE_PATTERN)

        garmin_heartrate_path = None
        try:
            garmin_heartrate_path = [path for path in garmin_iter][0]
        except IndexError:
            print(f'No garmin heartrate file in {self.libai_record.name}')

        return garmin_heartrate_path

    def _get_polar_heartrates(self, polar_heartrate_path) -> np.ndarray:

        if polar_heartrate_path is None or not polar_heartrate_path.exists():
            return

        start_timestamp = None
        with open(str(polar_heartrate_path), 'r') as f:
            f.readline()
            secondline = f.readline()
            date_str, time_str = secondline.split(',')[2], secondline.split(
                ',')[3]
            datetime_str = date_str + ' ' + time_str
            start_datetime = datetime.strptime(datetime_str,
                                               '%d-%m-%Y %H:%M:%S')
            start_timestamp = int(start_datetime.timestamp())

        heartrate_df = pd.read_csv(polar_heartrate_path,
                                   header=GARMIN_HEARTRATE_HEADER_LINE)

        heartrate_df = heartrate_df[heartrate_df['HR (bpm)'] > 0]

        heartrates = heartrate_df[['HR (bpm)']].values
        timestamps = np.arange(len(heartrates)).reshape(
            (-1, 1)) + start_timestamp

        return np.hstack((timestamps, heartrates)).astype(np.int)

    def _get_acc_ppg_values(self, acc_ppg_merged_path) -> tuple:
        acc_ppg_merged_df = pd.read_csv(acc_ppg_merged_path)

        acc_vals = acc_ppg_merged_df[[
            'EventTimestamp(ns)', 'accel_x', 'accel_y', 'accel_z'
        ]]
        ppg_vals = acc_ppg_merged_df[['CurrentTimeMillis', 'ch1']]
        return (acc_vals, ppg_vals)

    def get_acc_ppg_values(self) -> tuple:
        acc_ppg_merged_path = self._get_acc_ppg_merged_path()
        acc_vals, ppg_vals = self._get_acc_ppg_values(acc_ppg_merged_path)
        return acc_vals[::2], ppg_vals[::2]

    def get_polar_heartrates(self) -> np.ndarray:
        polar_heartrate_path = self._get_polar_heartrate_path()
        polar_heartrates = self._get_polar_heartrates(polar_heartrate_path)
        return polar_heartrates


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


def get_freq

def get_timefreq_graph(signal) -> np.ndarray:
    pass


def get_timefreq_of_acc_ppg(record: Path) -> tuple:
    dir_utils = DirUtilsV2(record)
    acc_vals, ppg_vals = dir_utils.get_acc_ppg_values()

    print(f'acc data shape: {acc_vals.shape}')
    print(f'ppg data shape: {ppg_vals.shape}')
    # print(f'total collect second (s): '
    #       f'{(ppg_vals[-1, 0] - ppg_vals[0, 0]) * 1E-3}')

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


def get_timefreq(record: str) -> tuple:
    record = str(record)
    dir_utils = DirUtils(record)
    acc_vals, ppg_vals = dir_utils._get_datas()

    ppg_utc_base = int(ppg_vals[0, 0] / 1e3) + 8

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
    time_freq = np.array(time_freq).T[::-1]
    # time_freq = hr_fft._sepc_select(time_freq, SAMPLE_FS, 0.4, 4.5)[::-1]

    timefreq_acc = np.array(time_freq_acc).T[::-1]
    # timefreq_acc = hr_fft._sepc_select(timefreq_acc, SAMPLE_FS, 0.4, 4.5)[::-1]

    # handle acc spec
    time_freq_acc = np.array(time_freq_accx).T[::-1]
    # time_freq_acc = hr_fft._sepc_select(time_freq_acc, SAMPLE_FS, 0.4,
    #                                     4.5)[::-1]

    time_freq_acc = np.array(time_freq_accy).T[::-1]
    # time_freq_acc = hr_fft._sepc_select(time_freq_acc, SAMPLE_FS, 0.4,
    #                                     4.5)[::-1]

    time_freq_acc = np.array(time_freq_accz).T[::-1]
    # time_freq_acc = hr_fft._sepc_select(time_freq_acc, SAMPLE_FS, 0.4,
    #                                     4.5)[::-1]

    return (ppg_utc_base, time_freq, timefreq_acc)


def plot_timefreq(ppg_time_freq: np.ndarray,
                  time_freq_acc: np.ndarray,
                  polar_heartrates: np.ndarray,
                  lifeq_heartrates: np.ndarray,
                  fig_stem=None) -> None:
    # 1. time_freq img
    freq_particle = 60 * (SAMPLE_FS / NFFT)
    y_label = [i * freq_particle for i in range(ppg_time_freq.shape[0])]

    plt.figure(figsize=(12, 6))
    plt.ylabel('Bpm')
    plt.title('PPG time-freq graph (after process)')
    plt.pcolormesh(np.arange(0, ppg_time_freq.shape[1]),
                   y_label,
                   ppg_time_freq[::-1],
                   cmap='jet')

    plt.yticks(y_label[::-1])
    plt.xlim([0, polar_heartrates.shape[0]])

    # 2. polar heartrates
    plt.plot(polar_heartrates[:, 0],
             polar_heartrates[:, 1],
             label='polar_heartrate',
             markersize=2,
             linewidth=2,
             color='red')
    plt.xlim([0, polar_heartrates.shape[0]])

    # 3 lifeq heartrates
    plt.plot(lifeq_heartrates[:, 0],
             lifeq_heartrates[:, 1],
             label='lifeq',
             markersize=2,
             linewidth=2,
             color='green')
    plt.xlim([0, polar_heartrates.shape[0]])

    plt.legend()

    if fig_stem is not None:
        fig_path = FIG_DIR / (fig_stem + '.png')
        plt.savefig(fig_path, dpi=1000)
        # return
    # 3 acc
    plt.figure(figsize=(12, 6))
    plt.yticks(np.arange(time_freq_acc.shape[0]), y_label[::-1])
    plt.ylabel('Bpm')
    plt.title('ACC time-freq graph (after process)')
    plt.imshow(time_freq_acc,
               cmap='jet',
               interpolation='nearest',
               aspect='auto')

    plt.show()


def rebase_heartrages(heartrates, ppg_utc_base, ppg_length) -> np.ndarray:
    heartrates_copy = heartrates.copy()
    heartrates_copy[:, 0] = heartrates_copy[:, 0] - ppg_utc_base
    mask = (heartrates_copy[:, 0] >= 0) & (heartrates_copy[:, 0] <= ppg_length)
    heartrates_rebased = heartrates_copy[mask]
    # heartrates_rebased[:, 1] -= 24
    return heartrates_rebased


def process_record(record: Path, i=0):
    record = Path(record)

    print(f'Processing {i}: {record.name}')

    ppg_utc_base, time_freq, time_freq_acc = get_timefreq(record)
    ppg_length = time_freq.shape[1]

    record = Path(record)
    polar_heartrate_path = get_polar_heartrate_path(record)
    lifeq_heartrate_path = get_lifeq_heartrate_path(record)
    if polar_heartrate_path is None or not polar_heartrate_path.exists():
        print(f'No polar heartrate file in {record.name}')
        return
    if lifeq_heartrate_path is None or not lifeq_heartrate_path.exists():
        print(f'No lifeq heartrate file in {record.name}')
        return
    polar_heartrates = get_polar_heartrates(polar_heartrate_path)
    polar_heartrates_rebased = rebase_heartrages(polar_heartrates,
                                                 ppg_utc_base, ppg_length)

    lifeq_heartrates = get_lifeq_heartrates(lifeq_heartrate_path)
    lifeq_heartrates_rebased = rebase_heartrages(lifeq_heartrates,
                                                 ppg_utc_base, ppg_length)

    plot_timefreq(time_freq,
                  time_freq_acc,
                  polar_heartrates_rebased,
                  lifeq_heartrates_rebased,
                  fig_stem=record.name)


def process_record_dir(record_dir: Path):

    p = Pool(cpu_count() // 2)
    for i, record in enumerate(record_dir.iterdir()):
        p.apply_async(process_record, args=(
            record,
            i,
        ))
    p.close()
    p.join()


def run(record: str, is_dir: bool):
    record = Path(record)
    if is_dir:
        process_record_dir(record)
    else:
        process_record(record)


@click.command()
@click.argument('record')
@click.option('-r', '--is-dir', is_flag=True, help='record dir')
def main(record, is_dir):
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    run(record, is_dir)


if __name__ == "__main__":
    main()
