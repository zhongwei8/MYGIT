'''
Author       : Tianzw
Date         : 2021-03-26 15:38:52
LastEditors  : Please set LastEditors
LastEditTime : 2021-04-08 15:21:20
FilePath     : /activity-recognition/src/py/analysis_mdsp.py
'''
from datetime import datetime
from multiprocessing import Process
from pathlib import Path

import click
import matplotlib as mpl
from matplotlib import ticker
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from activity_recognizer_demo import (analysis_result, process_df,
                                      process_log_file)

SPORTS = ['UNKNOWN', 'WALK', 'RUN', 'ELLIPTICAL', 'BIKE']

ACCEL_LOG_COLUMNS = [
    'CurrentTimeMillis',
    'EventTimestamp(ns)',
    'AccelX',
    'AccelY',
    'AccelZ',
]

ACCEL_RAW_COLUMNS = [
    'CurrentTimeMillis',
    'AccelX',
    'AccelY',
    'AccelZ',
]

SPORT_COLUMNS = ['CurrentTimeMillis', 'sport']


def get_timestamp_acc(line: str) -> tuple:
    fields = line.strip().split('|')
    time_timestamp = fields[0].strip().split(' ')
    timestamp = time_timestamp[-1]
    timestamp = int(timestamp)
    feed_data = fields[1].strip().split(',')
    accel_x, accel_y, accel_z = feed_data[2:]
    timestamp_acc = (timestamp, accel_x, accel_y, accel_z)
    return timestamp_acc


def get_timestamp_sport(line: str) -> tuple:
    fields = line.strip().split('|')
    timestamp = int(fields[0].strip().split(' ')[-1])
    sport = fields[-1].strip().split(' ')[0].split('_')[-1]
    timestamp_sport = (timestamp, sport)

    return timestamp_sport


def plot_sport(df: pd.DataFrame):

    timestamp = df['CurrentTimeMillis'].values.astype(np.int)
    sport = df['sport'].apply(lambda x: SPORTS.index(x)
                              if x in SPORTS else '-1').values
    print(f'len = {len(sport)}')

    print(f'sport = {sport}')

    mpl.use('Qt5Agg')

    _, ax = plt.subplots(1, 1, figsize=(10, 5))

    ax.plot(timestamp, sport, marker='o')

    ax.set_yticks([i for i in range(len(SPORTS))])
    ax.set_yticklabels(SPORTS)

    @ticker.FuncFormatter
    def func(x, pos):
        return datetime.fromtimestamp(int(x)).time()

    ax.xaxis.set_major_formatter(func)

    plt.grid()

    plt.show()


def clip_mdsp_with_timerange(mdsp_log_path: Path, timerange: tuple) -> tuple:
    low, high = timerange[0], timerange[1]

    timestamp_accs = []
    timestamp_sports = []
    with open(mdsp_log_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            fields = line.strip().split('|')
            timestamp = fields[0].strip().split(' ')[-1]  # not 1
            timestamp = int(timestamp)
            if timestamp < low:
                continue
            if timestamp > high:
                break
            if line.find('feed_data') != -1:
                timestamp_acc = get_timestamp_acc(line)
                timestamp_accs.append(timestamp_acc)
            if len(fields) == 3 and line.find('MI_HAR') != -1:
                timestamp_sport = get_timestamp_sport(line)
                timestamp_sports.append(timestamp_sport)
    timestamp_acc_df = pd.DataFrame(timestamp_accs, columns=ACCEL_RAW_COLUMNS)
    timestamp_sport_df = pd.DataFrame(timestamp_sports, columns=SPORT_COLUMNS)

    return (timestamp_acc_df, timestamp_sport_df)


def plot_acc_and_sport(acc_df: pd.DataFrame, sport_df: pd.DataFrame) -> None:
    pass


def read_raw_feed_data(log_path: Path) -> pd.DataFrame:
    log_path = Path(log_path)

    records = []
    with open(log_path, 'r') as f:
        line = f.readlines()
        for i, line in enumerate(line):
            fields = line.strip().split('|')
            time_timestamp = fields[0].strip().split(' ')
            timestamp = time_timestamp[-1]
            timestamp = int(timestamp)
            feed_data = fields[1].strip().split(',')
            accel_x, accel_y, accel_z = feed_data[2:]
            record = (timestamp, accel_x, accel_y, accel_z)
            records.append(record)
    raw_feed_data_df = pd.DataFrame(records, columns=ACCEL_RAW_COLUMNS)
    return raw_feed_data_df


def get_timerange(libai_record: Path) -> tuple:
    libai_record = Path(libai_record)
    libai_name = libai_record.name
    timestamp_key = libai_name.split('-')[0]
    accel_name = timestamp_key + '-accel-52HZ.csv'
    accel_path = libai_record / accel_name

    print(f'accel_path = {accel_path}')

    accel_df = pd.read_csv(accel_path, header=1)
    timestamp_begin = accel_df.iloc[0, 0].astype(np.int) // 1000 - 60
    timestamp_end = accel_df.iloc[-1, 0].astype(np.int) // 1000

    return (timestamp_begin, timestamp_end)


def clip_raw_feed_data(raw_feed_data_df: pd.DataFrame,
                       timerange: tuple) -> pd.DataFrame:
    timestamp_begin = timerange[0]
    timestamp_end = timerange[1]

    flag = (raw_feed_data_df.iloc[:, 0] >=
            timestamp_begin) & (raw_feed_data_df.iloc[:, 0] <= timestamp_end)
    feed_data_cliped = raw_feed_data_df[flag]

    return feed_data_cliped


def plot_timestamp(timestamp_values: np.ndarray, timerange: tuple):
    begin, end = timerange[0], timerange[1]

    timestamp_cnt = np.zeros(end - begin + 1).astype(np.int)
    ele, cnt = np.unique(timestamp_values, return_counts=True)

    timestamp_cnt[ele - begin] = cnt

    x = np.arange(begin, end + 1, 1)
    y = timestamp_cnt

    _, axes = plt.subplots(2, 1, figsize=(12, 6))

    axes[0].plot(x, y, marker='o', label='timestamp_cnt')
    axes[1].plot(x, y, marker='o', label='timestamp_cnt')

    @ticker.FuncFormatter
    def func(x, pos):
        return datetime.fromtimestamp(int(x)).time().strftime('%H:%M:%S')

    @ticker.FuncFormatter
    def func_str(x, pos):
        return str(int(x))

    axes[0].xaxis.set_major_formatter(func)
    axes[1].xaxis.set_major_formatter(func_str)

    for ax in axes:
        ax.grid()
        ax.legend()
    plt.show()


def post_process(feed_data_cliped: pd.DataFrame,
                 activity_type=-1) -> pd.DataFrame:
    ms_delta = (1 / 26) * 1e3
    ns_delta = (1 / 26) * 1e9

    size = len(feed_data_cliped)

    timestamp_base = feed_data_cliped.iloc[0, 0] * 1000
    timestamps = [int(ms_delta * i) for i in range(size)] + timestamp_base
    ns = [int(ns_delta * i) for i in range(size)]

    feed_data_cliped.loc[:, 'CurrentTimeMillis'] = timestamps
    feed_data_cliped.loc[:, 'EventTimestamp(ns)'] = ns

    return feed_data_cliped[ACCEL_LOG_COLUMNS]


def save_df_nearly(df: pd.DataFrame, log_path: Path) -> Path:
    log_path = Path(log_path)

    feed_data_path = log_path.parent / (log_path.stem + '_cliped' + '.log')

    df.to_csv(feed_data_path, index=False)

    return feed_data_path


def run(log_path: Path, libai_record: Path):
    timerange = get_timerange(libai_record)

    acc_df, sport_df = clip_mdsp_with_timerange(log_path, timerange)

    plot_sport(sport_df)
    plot_timestamp(acc_df['CurrentTimeMillis'].values, timerange)

    standard_acc_df = post_process(acc_df)
    feed_data_path = save_df_nearly(standard_acc_df, log_path)

    df, result = process_log_file(feed_data_path)

    analysis_result(df, result)


@click.command()
@click.argument('log-path')
@click.option('-l', '--libai-record', required=True)
def main(log_path, libai_record):
    run(log_path, libai_record)


if __name__ == '__main__':
    main()
