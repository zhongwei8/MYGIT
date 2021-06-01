#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Farmer Li
# @Date: 2021-02-23

from datetime import datetime
from pathlib import Path
import sys

import click
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from activity_recognizer import ActivityRecognizer
from activity_recognizer_c import ActivityRecognizerC

current_dir = Path(__file__).parent.resolve()
project_dir = current_dir / '../../'
sys.path.append(str(project_dir))
from src.py.utils.common import (label_name_to_category_idx,
                                 record_name_metas_to_dict)

mpl.rcParams['lines.markersize'] = 3

HEADER_NAMES = [
    'CurrentTimeMillis', 'EventTimestamp(ns)', 'AccelX', 'AccelY', 'AccelZ',
    'GyroX', 'GyroY', 'GyroZ', 'MagX', 'MagY', 'MagZ', 'Activity'
]
ACC_HEADER_NAMES = [
    'CurrentTimeMillis', 'EventTimestamp(ns)', 'AccelX', 'AccelY', 'AccelZ'
]
ACC_SUFFIX = 'accel-52HZ.csv'

HAR_TYPE_NAMES = ["Others", "Walk", "Run", "Rowing", "Elliptical", "Biking"]


def convert_event_timestamp_to_utc(ref_utc, ref_et, et):
    return datetime.fromtimestamp(ref_utc + ((et - ref_et) / 1e9))


def event_timesamp_to_utc(ets, ref_utc, ref_et):
    res = []
    for et in ets:
        utc = convert_event_timestamp_to_utc(ref_utc, ref_et, et)
        res.append(utc)
    return res


def simple_downsample(df: pd.DataFrame, expected_period_ns=(1 / 26) * 1e9):
    last_ets = 0
    mask = np.zeros(df.shape[0], dtype=np.bool)
    for i, row in df.iterrows():
        ets = row['EventTimestamp(ns)']
        if ets - last_ets >= expected_period_ns:
            last_ets = ets
            mask[i] = True
    df = df[mask]
    df.reset_index(inplace=True, drop=True)
    return df


def process_df(df: pd.DataFrame):
    """Activity standard data frame with 26Hz

    Parameters
    ----------
    df : pd.DataFrame
        Activity standard data frame

    Returns
    -------
    dict
        Recognition results
    """
    predicts = {}
    recognizer = ActivityRecognizerC()
    print(f'Current algo version: {recognizer.get_version()}')
    predict_type = 0
    ref_utc = df['CurrentTimeMillis'].iloc[0] / 1000
    ref_et = df['EventTimestamp(ns)'].iloc[0]
    for i, row in df.iterrows():
        update = recognizer.feed_data(row)
        if update:
            result = recognizer.get_result()
            current_type = result['PredictActivity']
            et = row['EventTimestamp(ns)']
            utc = convert_event_timestamp_to_utc(ref_utc, ref_et, et)
            if predict_type != current_type:
                print(f'Activity type from <{HAR_TYPE_NAMES[predict_type]:6s}>'
                      f' CHANGED to <{HAR_TYPE_NAMES[current_type]:6s}>'
                      f' AT {utc} -- {et}')
                predict_type = current_type
            for key in result:
                if key not in predicts:
                    predicts[key] = [result[key]]
                else:
                    predicts[key].append(result[key])
    result = pd.DataFrame.from_dict(predicts)
    return result


def process_standard_file(data_file: Path):
    """Process standard acc data file for activity recognition

    File with columns: @HEADER_NAMES

    Parameters
    ----------
    data_file : Path
        Standard acc data file path

    Returns
    -------
    tuple
        Raw acc data, Recognition result
    """
    df = pd.read_csv(data_file)
    return df, process_df(df)


def process_log_file(log_file: Path, activity_type=-1):
    """Process acc log data file saved by SensorCapture app

    Parameters
    ----------
    log_file : Path
        Log file path
    """
    df = pd.read_csv(log_file)
    df.columns = ACC_HEADER_NAMES
    df['Activity'] = activity_type
    return df, process_df(df)


def process_file(file_path: Path, activity_type=-1):
    suffix = file_path.suffix
    if suffix == '.csv':
        return process_standard_file(file_path)
    elif suffix == '.log':
        return process_log_file(file_path, activity_type)
    else:
        raise RuntimeError(f'Unsupported data file type: {suffix}')


def load_record_as_df(record_dir: Path, activity_type):
    file_preffix = record_dir.name
    header_rows = 1
    acc_file = record_dir / f'{file_preffix}-{ACC_SUFFIX}'
    if not acc_file.exists():
        print(f'NMEA file not exits: {acc_file.name}')
        file_preffix = file_preffix.split('-')[0]
        header_rows = 2
        acc_file = record_dir / f'{file_preffix}-{ACC_SUFFIX}'
        print(f'Trying {acc_file.name}')
        if not acc_file.exists():
            print(f'Record has no NMEA data file: {acc_file}')
            exit(1)
    print(f'Reading: {acc_file}')
    if header_rows == 1:
        df = pd.read_csv(acc_file)
        df.columns = ACC_HEADER_NAMES
    else:
        df = pd.read_csv(acc_file, skiprows=[0])
        df.columns = ACC_HEADER_NAMES
    df['Activity'] = activity_type
    return df


def process_record(record_dir: Path, activity_type=0):
    meta_dict = record_name_metas_to_dict(record_dir.stem)
    activity_name = meta_dict.get('scene', 'Undefined')
    activity_type = label_name_to_category_idx(activity_name)
    df = load_record_as_df(record_dir, activity_type)

    # Down sample
    df = simple_downsample(df)

    start_timestamp = df.iloc[0, 0]
    end_timestamp = df.iloc[-1, 0]
    print(
        f'start_timestamp, end_timestamp = {start_timestamp}, {end_timestamp}')
    seconds = (end_timestamp - start_timestamp) / 1000
    cnt = len(df)
    print(f'df.head() = \n{df.head()}')
    print(f'cnt, seconds, freq = {cnt}, {seconds}, {cnt / seconds}')

    online_res_file_name = f'{record_dir.name.split("-")[0]}-hardetector.csv'
    online_res_file = record_dir / online_res_file_name
    print(online_res_file)
    if online_res_file.exists():
        print('===================== Online results =========================')
        res = pd.read_csv(online_res_file, skiprows=[0])
        res_ts = res['EventTimestamp(ns)']
        ref_et = df['EventTimestamp(ns)'].values[0]
        ref_utc = df['CurrentTimeMillis'].iloc[0] / 1000
        res_utc = event_timesamp_to_utc(res_ts, ref_utc, ref_et)
        predcits = res['harDetect'].values
        for i, predict in enumerate(predcits):
            if i == 0:
                current_type = 0
            else:
                current_type = predcits[i - 1]
            print(f'Activity type from <{HAR_TYPE_NAMES[current_type]:6s}>'
                  f' CHANGED to <{HAR_TYPE_NAMES[predict]:6s}>'
                  f' AT {res_utc[i]} -- {res_ts[i]}')
        print('============================================================')

    return df, process_df(df)


def analysis_result(raw_df: pd.DataFrame, result_df: pd.DataFrame, title=''):
    retsult_ts = result_df['EventTimestamp(ns)']
    et = raw_df['EventTimestamp(ns)'].values
    ref_et = et[0]
    ref_utc = raw_df['CurrentTimeMillis'].iloc[0] / 1000

    raw_utc = event_timesamp_to_utc(et, ref_utc, ref_et)
    raw_df['utc'] = raw_utc

    result_utc = event_timesamp_to_utc(retsult_ts, ref_utc, ref_et)
    result_df['utc'] = result_utc

    result_df = result_df.drop('EventTimestamp(ns)', axis='columns')
    acc_columns = ['AccelX', 'AccelX', 'AccelZ']
    prob_columns = ['Prob0', 'Prob1', 'Prob2', 'Prob3', 'Prob4', 'Prob5']
    result_columns = ['Activity', 'Predict', 'PredictActivity']

    mpl.use('Qt5Agg')
    plt.figure('Timestamp check')
    plt.plot(np.diff(et), '-o', label='Event timestamp diff')
    plt.legend()
    plt.figure('Raw data and results')
    plt.subplot(311)
    plt.title(title)
    ax1 = plt.gca()
    for i, col in enumerate(acc_columns):
        plt.plot(raw_utc, raw_df[col], '-o', label=col)
    if 'STD' in result_df.columns:
        std = result_df['STD'].values
        std_mean = np.mean(std)
        plt.plot(result_utc, std, '-o', label='STD')
        plt.hlines(std_mean,
                   xmin=raw_utc[0],
                   xmax=raw_utc[-1],
                   label=f'STD Mean: {std_mean:.3f}')
    plt.legend()
    plt.subplot(312, sharex=ax1)
    for i, col in enumerate(result_columns):
        plt.plot(result_utc, result_df[col], '-o', label=col)
    plt.yticks(ticks=[i for i in range(len(HAR_TYPE_NAMES))],
               labels=HAR_TYPE_NAMES)
    plt.subplot(313, sharex=ax1)
    for i, col in enumerate(prob_columns):
        plt.plot(result_utc, result_df[col], '-o', label=HAR_TYPE_NAMES[i])
    plt.legend()
    plt.show()


@click.command()
@click.argument('data-path')
@click.option('-r', '--record', is_flag=True, help='Data path is a record dir')
def main(data_path, record):
    data_path = Path(data_path)
    if data_path.is_dir():
        if record:
            df, res = process_record(data_path)
            analysis_result(df, res, data_path.name)
        else:
            print('Are you specified one record directory?\n'
                  'Then run with "-r" option')
    else:
        if data_path.is_file():
            print(f'Processing file: {data_path}')
            df, res = process_file(data_path)
            analysis_result(df, res, data_path.stem)


if __name__ == '__main__':
    main()
