#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Farmer Li
# @Date: 2021-02-23

from pathlib import Path

import click
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from indoor_outdoor_recognizer import IndoorOutdoorRecognizer

HEADER_NAMES = [
    'CurrentTimeMillis', 'EventTimestamp(ms)', 'NMEA', 'IndoorOutdoor'
]
NMEA_SUFFIX = 'nmea.csv'


def indoor_outdoor_vote(status_arr):
    status, counts = np.unique(status_arr, return_counts=True)
    print(status)
    print(counts)


def plot_results(res: pd.DataFrame):
    plt.figure('Indoor/Outdoor recognize result')
    plt.subplot(311)
    ax = plt.gca()
    res['status'].plot(style='-o')
    plt.legend()
    plt.subplot(312)
    res['num'].plot(sharex=ax, style='-o')
    plt.legend()
    plt.subplot(313)
    res['snr_sum'].plot(sharex=ax, style='-o')
    plt.legend()
    plt.show()


def process_df(df):
    res = []
    recognizer = IndoorOutdoorRecognizer()
    for i, row in df.iterrows():
        update = recognizer.feed_data(row)
        if update:
            current_status = recognizer.get_status()
            satel_num, satel_snr_sum = recognizer.get_satellite_status()
            res.append([current_status, satel_num, satel_snr_sum])
    return pd.DataFrame(res, columns=['status', 'num', 'snr_sum'])


def process_file(data_file: Path):
    """Process standard NMEA data file

    File with columns:
    'CurrentTimeMillis', 'EventTimestamp(ms)', 'NMEA', 'IndoorOutdoor'

    Parameters
    ----------
    data_file : Path
        Standard NMEA data file path

    Returns
    -------
    list
        Recognizer result
    """
    df = pd.read_csv(data_file)
    return process_df(df)


def load_record_as_df(record_dir: Path, indoor_outdoor):
    file_preffix = record_dir.name
    header_rows = 1
    nmea_file = record_dir / f'{file_preffix}-{NMEA_SUFFIX}'
    if not nmea_file.exists():
        print(f'NMEA file not exits: {nmea_file.name}')
        file_preffix = file_preffix.split('-')[0]
        header_rows = 2
        nmea_file = record_dir / f'{file_preffix}-{NMEA_SUFFIX}'
        print(f'Trying {nmea_file.name}')
        if not nmea_file.exists():
            print(f'Record has no NMEA data file: {nmea_file}')
            exit(1)

    with Path(nmea_file).open('r') as f:
        lines = f.readlines()
        data = []
        # Skip the header and broken end of file
        for line in lines[header_rows:-1]:
            line = line.rstrip('\n')
            metas = line.split(',')
            ts = int(metas[0])
            ets = int(metas[1])
            nmea = ','.join(metas[2:])
            data.append([ts, ets, nmea, indoor_outdoor])
        df = pd.DataFrame(data, columns=HEADER_NAMES)
    return df


def process_record(record_dir: Path,
                   record_format_version=1,
                   indoor_outdoor=0):
    df = load_record_as_df(record_dir, indoor_outdoor)
    return process_df(df)


@click.command()
@click.argument('data-path')
@click.option('-r', '--record', is_flag=True, help='Data path is a record dir')
def main(data_path, record):
    data_path = Path(data_path)
    if data_path.is_dir():
        if record:
            res = process_record(data_path)
            plot_results(res)
        else:
            print('Are you specified one record directory?\n'
                  'Then run with "-r" option')
    else:
        if data_path.is_file():
            print(f'Processing file: {data_path}')
            res = process_file(Path(data_path))
            plot_results(res)
            indoor_outdoor_vote(res['status'].values)


if __name__ == '__main__':
    main()
