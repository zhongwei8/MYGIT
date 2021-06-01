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


class Filters:
    def __init__(self):
        pass

    def band_filter(self, data, fs, f_order, freq_low, freq_high):
        wn_low = 2 * freq_low / fs
        wn_high = 2 * freq_high / fs
        b, a = signal.butter(f_order, [wn_low, wn_high], 'bandpass')
        return signal.filtfilt(b, a, data)

    def low_filter(self):
        pass

    def high_filter(self):
        pass

    def rls_filter(self, d_data, noise_data, relative_n=20):
        pass


class PreProcess:
    def __init__(self):
        self.filter = Filters()

    def data_norm(self, data, mode='stander'):
        d_mean = np.mean(data)
        d_std = np.std(data)

        return (data - d_mean) / d_std

    def get_noise(self, data, acc_d):
        pass

    def __call__(self, data, acc_d, fs, freq_low, freq_high):
        data = self.filter.band_filter(data, fs, 2, freq_low, freq_high)
        data = self.data_norm(data)
        return data


class ListQueue(object):
    def __init__(self, capacity):
        self._data = []
        self._capacity = capacity

    def append(self, value):
        if len(self._data) >= self._capacity:
            self._data.pop(0)
        self._data.append(value)

    def shift(self, shift_len):
        if shift_len < self._capacity:
            self._data = self._data[shift_len:]
        else:
            self._data.clear()

    def get(self, idx):
        return self._data[idx]

    def get_data(self):
        return self._data

    def reset(self):
        self._data.clear()

    def __len__(self):
        return len(self._data)

    def size(self):
        return len(self._data)

    def is_full(self):
        return self.size() >= self._capacity


class WelchUtils:
    def __init__(self,
                 data,
                 fs=None,
                 unit='s',
                 win_seconds=8.0,
                 shift_seconds=1.0,
                 freq_low=0.5,
                 freq_high=4.2):
        self._data = data
        self._win_seconds = win_seconds
        self._shift_seconds = shift_seconds
        if fs is None:
            if unit == 's':
                self._delta_time = np.diff(data[:, 0]).mean()
            elif unit == 'ms':
                self._delta_time = np.diff(data[:, 0]).mean() / 1e3
            elif unit == 'ns':
                self._delta_time = np.diff(data[:, 0]).mean() / 1e9
            else:
                raise ValueError
            self._fs = 1 / self._delta_time
        else:
            self._fs = fs
            self._delta_time = 1.0 / fs

        self._buffer_length = int(self._win_seconds * self._fs)  # round error
        self._shift_length = int(self._shift_seconds * self._fs)  # round error
        self._win_seconds = self._delta_time * self._buffer_length  # round error
        self._shift_seconds = self._delta_time * self._shift_length  # round error

        self._utc_base = data[self._buffer_length - 1, 0]
        if unit == 's':
            self._utc_base = int(self._utc_base)
        elif unit == 'ms':
            self._utc_base = int(self._utc_base / 1e3)
        elif unit == 'ns':
            self._utc_base = int(self._utc_base / 1e9)
        else:
            raise ValueError

        self._preprocess = PreProcess()
        self._data_buffer = ListQueue(self._buffer_length)
        self._nfft = self._buffer_length
        self._freq_low = freq_low
        self._freq_high = freq_high
        self._freq_delta = self._fs / self._nfft

        self._index_low = int(self._freq_low / self._freq_delta)
        self._index_high = int(self._freq_high / self._freq_delta)
        self._f = np.arange(0, self._fs,
                            self._freq_delta)[self._index_low:self._index_high]
        self._pxx = None

        print(f'self._fs = {self._fs}')
        print(f'self._win_seconds = {self._win_seconds}')
        print(f'self._shift_seconds = {self._shift_seconds}')

        print(f'self._buffer_length = {self._buffer_length}')
        print(f'self._shift_length = {self._shift_length}')
        print(f'self._freq_delta = {self._freq_delta}')
        print(f'self._delta_time = {self._delta_time}')
        print(f'self._f = {self._f}\n')

    def _welch_fft(self):
        win = self._data_buffer.get_data()
        fs = self._fs
        freq_low = self._freq_low
        freq_high = self._freq_high

        win = self._preprocess(win, None, fs, freq_low, freq_high)

        nfft = self._nfft
        nperseg = len(win) // 2
        f, pxx = signal.welch(win,
                              fs,
                              nfft=nfft,
                              nperseg=nperseg,
                              scaling='spectrum',
                              average='mean')
        return f, pxx

    def _feed_data(self, data_point):
        self._data_buffer.append(data_point)
        updated = False

        if self._data_buffer.is_full():
            _, pxx = self._welch_fft()
            self._pxx = pxx[self._index_low:self._index_high]
            self._data_buffer.shift(self._shift_length)
            updated = True
        return updated

    def process_data(self):
        f = self._f
        pxxes = []
        for i, data_point in enumerate(self._data[:, 1]):
            updated = self._feed_data(data_point)
            if updated:
                pxx = self._pxx
                pxxes.append(pxx)

        pxxes_values = np.asarray(pxxes).T  # 转置
        t = np.arange(
            0, pxxes_values.shape[1]) * self._shift_seconds + self._utc_base
        return t, f, pxxes_values

    def plot_timefreq(self):
        t, f, pxx = self.process_data()

        print(
            f'f.shape, pxx.shape, t.shape = {f.shape}, {pxx.shape}, {t.shape}')

        @ticker.FuncFormatter
        def func(x, pos):
            return datetime.fromtimestamp(int(x)).time()

        plt.figure(figsize=(12, 6))
        plt.pcolormesh(t, f, pxx, cmap='jet')
        plt.ylabel('freq(Hz)')

        plt.gca().xaxis.set_major_formatter(func)

        plt.show()


def pop_list_boxes(items: list, location=(400, 300)):
    choice = None
    location = (400, 300)
    layout = [[
        sg.Listbox(values=items,
                   default_values=[items[0]],
                   size=(20, 12),
                   key='Selected-delay',
                   enable_events=True)
    ],
              [
                  sg.Button('Submit(Enter)', key='btn_submit'),
                  sg.Button('Cancel(Esc/BackSpace)', key='btn_cancel')
              ]]
    window = sg.Window('choice', layout=layout, location=location)
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        if event in {'btn_submit', 'Return:36'}:
            choice = values['Selected-delay'][0]
            break
    window.close()

    return choice


def adjust_ppg_and_polar(ppg_t, ppg_f, ppg_pxx, polar_heartrates):
    @ticker.FuncFormatter
    def func(x, pos):
        return datetime.fromtimestamp(int(x)).time()

    ppg_bpm = ppg_f * 60

    delays = [0, 2, 4]
    colors = ['blue', 'green', 'red']
    plt.figure(figsize=(18, 6))
    plt.ylabel('bpm')
    # 1.1 ppg
    plt.pcolormesh(ppg_t, ppg_bpm, ppg_pxx, cmap='jet', shading='auto')
    plt.ylim([ppg_bpm[0], ppg_bpm[-1]])
    plt.xlim([ppg_t[0], ppg_t[-1]])
    for i, delay in enumerate(delays):
        plt.plot(polar_heartrates[:, 0] - delay,
                 polar_heartrates[:, 1],
                 markersize=1,
                 linewidth=2,
                 color=colors[i],
                 label=f'{delay}')
        plt.ylim([ppg_bpm[0], ppg_bpm[-1]])
        plt.xlim([ppg_t[0], ppg_t[-1]])
    plt.legend()

    plt.gca().xaxis.set_major_formatter(func)

    plt.show()

    selected_delay = pop_list_boxes(delays)

    return selected_delay


def plot_ppg_timefreq_and_polar_garmin_lifeq(ppg_t,
                                             ppg_f,
                                             ppg_pxx,
                                             acc_t,
                                             acc_f,
                                             acc_pxx,
                                             polar_heartrates,
                                             lifeq_heartrates,
                                             garmin_heartrates,
                                             plot_acc=False):
    @ticker.FuncFormatter
    def func(x, pos):
        return datetime.fromtimestamp(int(x)).time()

    plt.figure(figsize=(18, 6))
    plt.title('PPG time-freq graph')
    plt.ylabel('bpm')

    # 1 ppg
    ppg_bpm = ppg_f * 60
    plt.pcolormesh(ppg_t, ppg_bpm, ppg_pxx, cmap='jet', shading='auto')
    plt.ylim([ppg_bpm[0], ppg_bpm[-1]])
    plt.xlim([ppg_t[0], ppg_t[-1]])

    # 2 polar_heartrates
    plt.plot(polar_heartrates[:, 0],
             polar_heartrates[:, 1],
             label='polar hearrate',
             markersize=2,
             linewidth=2,
             color='red')
    plt.ylim([ppg_bpm[0], ppg_bpm[-1]])
    plt.xlim([ppg_t[0], ppg_t[-1]])

    # 3 lifeq_heartrates
    if lifeq_heartrates is not None:
        plt.plot(lifeq_heartrates[:, 0],
                 lifeq_heartrates[:, 1],
                 label='lifeq heartrate',
                 markersize=2,
                 linewidth=2,
                 color='green')
        plt.ylim([ppg_bpm[0], ppg_bpm[-1]])
        plt.xlim([ppg_t[0], ppg_t[-1]])

    # 4 garmin_heartrates
    if garmin_heartrates is not None:
        plt.plot(garmin_heartrates[:, 0],
                 garmin_heartrates[:, 1],
                 label='garmin heartrate',
                 markersize=2,
                 linewidth=2,
                 color='yellow')
        plt.ylim([ppg_bpm[0], ppg_bpm[-1]])
        plt.xlim([ppg_t[0], ppg_t[-1]])

    plt.gca().xaxis.set_major_formatter(func)

    plt.legend()

    if plot_acc:
        acc_bpm = acc_f * 60
        plt.figure(figsize=(18, 6))
        plt.pcolormesh(acc_t, acc_bpm, acc_pxx, cmap='jet', shading='auto')
        plt.ylabel('bpm')
        plt.title('accm time-freq graph')
        plt.xlim([ppg_t[0], ppg_t[-1]])
        plt.ylim([ppg_bpm[0], ppg_bpm[-1]])

        plt.gca().xaxis.set_major_formatter(func)

    plt.show()


def process_one_record(libai_record: Path, is_align=True, debug=False):
    libai_record = Path(libai_record)
    libai_record_utils = LibaiRecordUtils(libai_record)

    lifeq_heartrates = libai_record_utils.get_lifeq_heartrates()
    garmin_heartrates = libai_record_utils.get_garmin_heartrates()
    polar_heartrates = libai_record_utils.get_polar_heartrates()
    ppg, acc = libai_record_utils.get_ppg_acc()

    ppg_welch_untils = WelchUtils(ppg, unit='ns')
    ppg_t, ppg_f, ppg_pxx = ppg_welch_untils.process_data()

    accm = np.zeros((acc.shape[0], 2))
    accm[:, 0] = acc[:, 0]
    accm[:, 1] = np.linalg.norm(acc[:, 1:], axis=1)
    accm_welch_untils = WelchUtils(accm, unit='ns')
    accm_t, accm_f, accm_pxx = accm_welch_untils.process_data()
    print(f'accm_pxx.shape = {accm_pxx.shape}')
    if polar_heartrates is None or ppg_pxx is None:
        print(f'NOT EXISTS polar heartrate or ppg: {libai_record.name}\n')
        return

    if is_align:
        selected_delay = adjust_ppg_and_polar(ppg_t, ppg_f, ppg_pxx,
                                              polar_heartrates)
        return selected_delay
        print(f'libai_record = {libai_record.name}')
        print(f'selected_delay = {selected_delay}')
    else:
        plot_ppg_timefreq_and_polar_garmin_lifeq(ppg_t, ppg_f, ppg_pxx, accm_t,
                                                 accm_f, accm_pxx,
                                                 polar_heartrates,
                                                 lifeq_heartrates,
                                                 garmin_heartrates)

    if debug:
        print(f'lifeq_heartrates.shape = {lifeq_heartrates.shape}')
        print(f'garmin_heartrates.shape = {garmin_heartrates.shape}')
        print(f'polar_heartrates.shape = {polar_heartrates.shape}')
        print(f'ppg.shape = {ppg.shape}')
        print(f'acc.shape = {acc.shape}')

        libai_record_utils.plot_polar_lifeq_garmin_ppg_acc()

        ppg_welch_untils.plot_timefreq()


def process_record_dir(record_dir: Path, is_align: bool):
    record_dir = Path(record_dir)

    log_file = Path('./delay.csv')

    libai_records = [libai_record for libai_record in record_dir.iterdir()]
    record_to_delays = []
    with open(log_file, 'a+') as f:
        for i, libai_record in enumerate(libai_records):
            print(f'Propressing {i + 1} / {len(libai_records)}: '
                  f'{libai_record.name}')

            try:
                selected_delay = process_one_record(libai_record, is_align)
                log = f'{libai_record.name},{selected_delay}\n'
                f.write(log)
                record_to_delays.append((libai_record.name, selected_delay))
            except AttributeError:
                print(f'AttributeError')
                continue
            except:
                pass
    record_to_delays_df = pd.DataFrame(
        record_to_delays, columns=['libai_record', 'polar_delay(s)'])
    df_path = Path('.') / (record_dir.name + '.csv')
    record_to_delays_df.to_csv(df_path, index=False)


def run(libai_path: Path, is_align: bool, is_dir: bool):
    if is_dir:
        process_record_dir(libai_path, is_align)
    else:
        process_one_record(libai_path, is_align)


@click.command()
@click.argument('libai-path')
@click.option('-a', '--is-align', is_flag=True)
@click.option('-d', '--is-dir', is_flag=True)
def main(libai_path: str, is_align: bool, is_dir: bool):
    run(libai_path, is_align, is_dir)


if __name__ == '__main__':
    main()
