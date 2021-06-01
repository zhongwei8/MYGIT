'''
Author       : Tianzw
Date         : 2021-03-31 21:52:12
LastEditors  : Please set LastEditors
LastEditTime : 2021-04-06 15:02:33
FilePath     : /my_github/activity_recognizer_demo.py
'''
from datetime import datetime
from pathlib import Path

from activity_recognizer_c import ActivityRecognizerC
import click
import numpy as np
import pandas as pd

import matplotlib as mpl
import matplotlib.pyplot as plt

HAR_TYPE_NAMES = []

ACC_HEADER_NAMES = []

ACC_SUFFIX = ''

EXPECTED_PERIOD_NS = (1 / 26) * 1e9


def convert_event_timestamp_to_utc(ref_utc, ref_et, et):
    return datetime.fromtimestamp(ref_utc + (et - ref_et) / 1e9)


def simple_downsample(df,
                      expected_period_ns=EXPECTED_PERIOD_NS) -> pd.DataFrame:
    last_ets = 0
    mask = np.zeros(df.shape[0], dtype=np.bool)

    for i, row in df.iterrows():
        ets = row['EventTimestamp(ns)']
        if ets - last_ets >= expected_period_ns:
            last_ets = ets
            mask[i] = True
    df_downsampled = df[mask]
    df_downsampled.reset_index(inplace=True, drop=True)
    return df_downsampled


def process_standard_df(df: pd.DataFrame) -> pd.DataFrame:
    predicts = {}
    recognizer = ActivityRecognizerC()
    ref_utc = df['CurrentTimeMillis'].iloc[0] / 1000
    ref_et = df['EventTimestamp(ns)'].iloc[0]
    previous_type = 0
    for i, row in df.iterrows():
        update = recognizer.feed_data(row)
        if update:
            result = recognizer.get_result()
            current_type = result['PredictActivity']
            et = row['EventTimestamp(ns)']
            utc = convert_event_timestamp_to_utc(ref_utc, ref_et, et)
            if current_type != previous_type:
                print(
                    f'Activity type from <{HAR_TYPE_NAMES[previous_type]:6s}> '
                    f' CHANGED TO <{HAR_TYPE_NAMES[current_type]:6s}>'
                    f' AT {utc} -- {et}')
            previous_type = current_type

        for key, value in result.items():
            if key not in predicts:
                predicts[key] = [value]
            else:
                predicts[key].append(value)
    result = pd.DataFrame.from_dict(predicts)
    return result


def read_accel_from_csv(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    return df


def read_accel_from_log(log_path: Path, activity_type=-1) -> pd.DataFrame:
    df = pd.read_csv(log_path)
    df.columns = ACC_HEADER_NAMES
    df['Activity'] = activity_type
    return df


def read_accel(file_path: Path) -> pd.DataFrame:
    suffix = file_path.suffix

    assert suffix in {'.csv', '.log'}

    if suffix == '.csv':
        df = read_accel_from_csv(file_path)
    elif suffix == '.log':
        df = read_accel_from_log(file_path)

    return df


def load_accel_from_record(record_dir: Path,
                           activity_type: int) -> pd.DataFrame:
    file_preffix = record_dir.name
    header_rows = 0
    acc_file = record_dir / f'{file_preffix}-{ACC_SUFFIX}'
    if not acc_file.exists():
        print(f'Acc file not exists: {acc_file.name}')
        file_preffix = file_preffix.split('-')[0]
        header_rows = 1
        acc_file = record_dir / f'{file_preffix}-{ACC_SUFFIX}'
        if not acc_file.exists():
            print(f'Record has no acc file: {acc_file.name}')
            exit(1)
    print(f'Reading: {acc_file}')

    df = pd.read_csv(acc_file, header=header_rows)
    df.columns = ACC_HEADER_NAMES
    df['Activity'] = activity_type
    return df


def check_event_timestamp_diff(event_timestamp_ns: np.ndarray):
    diff = np.diff(event_timestamp_ns)

    mpl.use('Qt5Agg')
    plt.figure('Timestamp check')
    plt.plot(diff, '-o', label='Event timestamp diff')
    plt.legend()
    plt.show()


def analysis_result(raw_df: pd.DataFrame, result_df: pd.DataFrame, title=''):

    ref_et = raw_df['EventTimestamp(ns)'].values[0]
    ref_utc = raw_df['CurrentTimeMillis'].values[0] / 1000

    raw_df['utc'] = raw_df['EventTimestamp(ns)'].apply(
        lambda x: convert_event_timestamp_to_utc(ref_utc, ref_et, x))
    result_df['utc'] = result_df['EventTimestamp(ns)'].apply(
        lambda x: convert_event_timestamp_to_utc(ref_utc, ref_et, x))

    acc_columns = ['AccelX', 'AccelY', 'AccelZ']
    prob_columns = ['Prob0', 'Prob1', 'Prob2', 'Prob3', 'Prob4', 'Prob5']
    result_columns = ['Activity', 'Predict', 'PredictActivity']
    # 311
    plt.subplot(311)
    plt.title(title)

    for i, col in enumerate(acc_columns):
        plt.plot(raw_df['utc'], raw_df[col], '-o', label=col)

    if 'STD' in result_df.columns:
        std = result_df['STD'].values
        plt.plot(result_df['utc'], std, '-o', label='STD')
        std_mean = np.mean(std)
        plt.hlines(std_mean,
                   xmin=raw_df['utc'].values[0],
                   xmax=raw_df['utc'].values[-1],
                   label=f'STD Mean: {std_mean:.3f}')
    plt.legend()

    # 312
    ax1 = plt.gca()
    plt.subplot(312, sharex=ax1)
    for i, col in enumerate(result_columns):
        plt.plot(result_df['utc'], result_df[col], '-o', label=col)
    plt.yticks(ticks=[i for i in range(len(HAR_TYPE_NAMES))],
               labels=HAR_TYPE_NAMES)
    plt.legend()

    # 313
    plt.subplot(313, sharex=ax1)
    for i, col in enumerate(prob_columns):
        plt.plot(result_df['utc'],
                 result_df[col],
                 '-o',
                 label=HAR_TYPE_NAMES[i])
    plt.legend()

    plt.show()


def run(data_path: Path, record: bool):
    if data_path.is_dir():
        if record:
            df = load_accel_from_record(data_path)
        else:
            print('Are you specified one record directory?\n'
                  'Then run with "-r" option')
    else:
        if


@click.command()
@click.argument('data-path')
@click.option('-r', '--record', is_flag=True, help='Data path is a record dir')
def main(data_path, record):
    data_path = Path(data_path)

    run(data_path, record)
