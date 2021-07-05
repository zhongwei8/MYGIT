'''
Author       : Tianzw
Date         : 2021-04-01 16:52:23
LastEditors  : Please set LastEditors
LastEditTime : 2021-04-02 11:54:27
FilePath     : /activity-recognition/src/py/plot_mi_har.py
'''
from datetime import datetime
from pathlib import Path

import click
import matplotlib as mpl
from matplotlib import ticker
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SPORTS = ['UNKNOWN', 'WALK', 'RUN', 'ELLIPTICAL', 'BIKE']


def get_timerange(libai_record: Path) -> tuple:
    libai_record = Path(libai_record)
    libai_name = libai_record.name
    timestamp_key = libai_name.split('-')[0]
    accel_name = timestamp_key + '-accel-52HZ.csv'
    accel_path = libai_record / accel_name
    accel_df = pd.read_csv(accel_path, header=1)
    timestamp_begin = accel_df.iloc[0, 0].astype(np.int) // 1000
    timestamp_end = accel_df.iloc[-1, 0].astype(np.int) // 1000

    return (timestamp_begin, timestamp_end)


def read_timestamp_and_sport(log_path: Path) -> pd.DataFrame:

    timestamp_sports = []
    with open(log_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            fields = line.strip().split('|')
            timestamp = int(fields[0].strip().split(' ')[-1])
            sport = fields[-1].strip().split(' ')[0].split('_')[-1]
            timestamp_sport = (timestamp, sport)
            timestamp_sports.append(timestamp_sport)

    timestamp_sport_df = pd.DataFrame(timestamp_sports,
                                      columns=['timestamp', 'sport'])

    timestamp_sport_df.to_csv(Path('./log.log'), index=False)

    print(f'timestamp_sport_df = {timestamp_sport_df.head()}')
    return timestamp_sport_df


def plot_sport(df: pd.DataFrame, timerange: tuple):

    low, high = timerange[0], timerange[1]
    mask = (df['timestamp'] >= low) & (df['timestamp'] <= high)
    df_cliped = df[mask]

    timestamp = df_cliped['timestamp'].values.astype(np.int)
    sport = df_cliped['sport'].apply(lambda x: SPORTS.index(x)
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


def run(log_path: Path, libai_record: Path):
    timerange = get_timerange(libai_record)
    timestamp_sport_df = read_timestamp_and_sport(log_path)
    plot_sport(timestamp_sport_df, timerange)


@click.command()
@click.argument('log-path')
@click.option('-l', '--libai-record', required=True, type=str)
def main(log_path, libai_record):
    log_path = Path(log_path)
    libai_record = Path(libai_record)

    run(log_path, libai_record)


if __name__ == '__main__':
    main()
