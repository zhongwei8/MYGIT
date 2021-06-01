from datetime import datetime, timedelta
from pathlib import Path

import PySimpleGUI as sg
import click
import fitparse
from matplotlib import ticker
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import signal

LIBAI_PREFIX = 'libai_'
LIFEQ_HEARTRATE_SUFFIX = '-heartrate-xHZ.csv'
ACC_PPG_MERGED_SUFFIX = '-accel-ppg-merged-52HZ.csv'

POLAR_HEARTRATE_PATTERN = 'polar_*.csv'
GARMIN_HEARTRATE_PATTERN = 'garmin_*.fit'
GARMIN_UTC_OFFSET = timedelta(hours=8)


class LibaiRecordUtils:
    def __init__(self, libai_record: Path):
        self._libai_record = Path(libai_record)
        self._lifeq_header_line = 1
        self._lifeq_columns = ['CurrentTimeMillis', 'BPM']
        self._acc_columns = [
            'EventTimestamp(ns)', 'accel_x', 'accel_y', 'accel_z'
        ]
        self._ppg_columns = ['EventTimestamp(ns)', 'ch1']
        self._polar_header_line = 2

    def _get_lifeq_heartrate_file(self):
        libai_record = self._libai_record
        record_key = libai_record.name.split('-')[0]
        lifeq_heartrate_name = (LIBAI_PREFIX + record_key +
                                LIFEQ_HEARTRATE_SUFFIX)
        lifeq_heartrate_file = libai_record / lifeq_heartrate_name

        return lifeq_heartrate_file

    def _get_garmin_heartrate_file(self):
        libai_record = self._libai_record
        garmin_iter = libai_record.glob(GARMIN_HEARTRATE_PATTERN)
        garmin_heartrate_file = None
        try:
            garmin_heartrate_file = [path for path in garmin_iter][0]
        except IndexError:
            print(f'No garmin heartrate file in {libai_record.name}')

        return garmin_heartrate_file

    def _get_polar_heartrate_file(self):
        libai_record = self._libai_record
        polar_iter = libai_record.glob(POLAR_HEARTRATE_PATTERN)

        polar_heartrate_file = None
        try:
            polar_heartrate_file = [path for path in polar_iter][0]
        except IndexError:
            print(f'No polar heartrate file in {libai_record.name}')

        return polar_heartrate_file

    def _get_acc_ppg_merged_file(self):
        libai_record = self._libai_record
        record_key = libai_record.name.split('-')[0]

        acc_ppg_merged_name = LIBAI_PREFIX + record_key + ACC_PPG_MERGED_SUFFIX
        acc_ppg_merged_file = libai_record / acc_ppg_merged_name
        return acc_ppg_merged_file

    def get_lifeq_heartrates(self):
        lifeq_heartrate_file = self._get_lifeq_heartrate_file()

        if lifeq_heartrate_file is None or not lifeq_heartrate_file.exists():
            return None

        lifeq_header_line = self._lifeq_header_line
        lifeq_columns = self._lifeq_columns

        lifeq_heartrate_df = pd.read_csv(lifeq_heartrate_file,
                                         header=lifeq_header_line)
        lifeq_heartrates = lifeq_heartrate_df[lifeq_columns].values
        lifeq_heartrates[:, 0] = lifeq_heartrates[:, 0] // 1000

        return lifeq_heartrates.astype(np.int)

    def get_garmin_heartrates(self):
        garmin_heartrate_file = self._get_garmin_heartrate_file()

        if garmin_heartrate_file is None or not garmin_heartrate_file.exists():
            print(f'No garmin file in {self._libai_record.name}')
            return None

        garmin_heartrate_file = str(garmin_heartrate_file)

        garmin_fit_file = fitparse.FitFile(garmin_heartrate_file)

        records = []
        for i, fields in enumerate(garmin_fit_file.get_messages('record')):
            timestamp, heartrate = None, None
            for data in fields:
                name, value = data.name, data.value
                if name == 'timestamp':
                    value += GARMIN_UTC_OFFSET
                    value = value.timestamp()
                    timestamp = value
                elif name == 'heart_rate':
                    heartrate = value
            if timestamp is not None and heartrate is not None:
                records.append((timestamp, heartrate))

        garmin_df = pd.DataFrame(records, columns=['timestamp', 'heartrate'])

        return garmin_df.values.astype(np.int)

    def get_polar_heartrates(self):
        polar_heartrate_file = self._get_polar_heartrate_file()

        if polar_heartrate_file is None or not polar_heartrate_file.exists():
            return None

        start_timestamp = None
        with open(str(polar_heartrate_file), 'r') as f:
            f.readline()
            secondline = f.readline()
            date_str, time_str = secondline.split(',')[2], secondline.split(
                ',')[3]
            datetime_str = date_str + ' ' + time_str
            start_datetime = datetime.strptime(datetime_str,
                                               '%d-%m-%Y %H:%M:%S')
            start_timestamp = int(start_datetime.timestamp())

        polar_header_line = self._polar_header_line
        heartrate_df = pd.read_csv(polar_heartrate_file,
                                   header=polar_header_line)

        heartrate_df = heartrate_df[heartrate_df['HR (bpm)'] > 0]

        heartrates = heartrate_df[['HR (bpm)']].values
        timestamps = np.arange(len(heartrates)).reshape(
            (-1, 1)) + start_timestamp

        return np.hstack((timestamps, heartrates)).astype(np.int)

    def _rebase_acc_ppg(self, df):
        current_time_millis_base = df.loc[0, 'CurrentTimeMillis']
        event_timestamp_ns = df['EventTimestamp(ns)'].values.copy()
        event_timestamp_ns -= event_timestamp_ns[0]
        event_timestamp_ns += int(current_time_millis_base * 1e6)
        df.loc[:, 'EventTimestamp(ns)'] = event_timestamp_ns

    def get_ppg_acc(self):
        acc_ppg_merged_file = self._get_acc_ppg_merged_file()

        if acc_ppg_merged_file is None or not acc_ppg_merged_file.exists():
            return None

        acc_ppg_merged_df = pd.read_csv(acc_ppg_merged_file)
        self._rebase_acc_ppg(acc_ppg_merged_df)

        ppg_columns = self._ppg_columns
        ppg_vals = acc_ppg_merged_df[ppg_columns].values.astype(np.int)

        acc_columns = self._acc_columns
        acc_vals = acc_ppg_merged_df[acc_columns].values.astype(np.int)

        return (ppg_vals, acc_vals)

    def plot_polar_lifeq_garmin_ppg_acc(self):

        polar_heartrates = self.get_polar_heartrates()
        lifeq_heartrates = self.get_lifeq_heartrates()
        garmin_heartrates = self.get_garmin_heartrates()
        ppg, acc = self.get_ppg_acc()

        @ticker.FuncFormatter
        def func(x, pos) -> None:
            return datetime.fromtimestamp(int(x)).time()

        _, axes = plt.subplots(3, 1, figsize=(12, 6), sharex=True)

        axes[0].set_title(self._libai_record.name)
        axes[0].plot(polar_heartrates[:, 0],
                     polar_heartrates[:, 1],
                     label='polar_heartrates')
        axes[0].plot(lifeq_heartrates[:, 0],
                     lifeq_heartrates[:, 1],
                     label='lifeq_heartrates')
        axes[0].plot(garmin_heartrates[:, 0],
                     garmin_heartrates[:, 1],
                     label='garmin_heartrates')

        axes[1].plot(ppg[:, 0] / 1e9, ppg[:, 1], label='ppg')

        axes[2].plot(acc[:, 0] / 1e9, acc[:, 1], label='acc_x')
        axes[2].plot(acc[:, 0] / 1e9, acc[:, 2], label='acc_y')
        axes[2].plot(acc[:, 0] / 1e9, acc[:, 3], label='acc_z')

        for ax in axes:
            ax.legend()
            ax.grid()
            ax.xaxis.set_major_formatter(func)

        plt.show()
