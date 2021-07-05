'''
Author       : Tianzw
Date         : 2021-04-06 11:33:44
LastEditors  : Please set LastEditors
LastEditTime : 2021-04-06 16:00:41
FilePath     : /my_github/activity_recognizier_demo_.py
'''
from datetime import datetime
from pathlib import Path

from activity_recognizier_c import ActivityRecognizerC
import click
import numpy as np
import pandas as pd

import matplotlib as mpl
from matplotlib import ticker
import matplotlib.pyplot as plt

ACC_SUFFIX = 'accel-52HZ.csv'

HAR_TYPE_NAMES = ["Others", "Walk", "Run", "Rowing", "Elliptical", "Biking"]

ACC_HEADER_NAMES = [
    'CurrentTimeMillis', 'EventTimestamp(ns)', 'AccelX', 'AccelY', 'AccelZ'
]


def simple_downsample(df: pd.DataFrame, expected_period_ns=(1 / 26) * 1e9):
    last_et = df['EventTimestamp(ns)'].values[0]

    mask = np.zeros(df.shape[0], dtype=np.bool)

    for i, et in enumerate(df['EventTimestamp(ns)']):
        if et - last_et >= expected_period_ns:
            last_et = et
            mask[i] = True

    downsampled = df[mask]
    downsampled.reset_index(inplace=True, drop=True)
    return downsampled


def rebase_event_timestamp(df: pd.DataFrame) -> pd.DataFrame:
    utc_ref = df['CurrentTimeMillis'].values[0]
    et_ref = df['EventTimestamp(ns)'].values[0]

    df.loc[:, 'EventTimestamp(ns)'] = df[
        'EventTimestamp(ns)'].values - et_ref + utc_ref * 1e6


def process_standard_accel_xyz_26hz(df: pd.DataFrame) -> pd.DataFrame:
    predicts = {}

    previous_type = 0
    recognizer = ActivityRecognizerC()
    for i, row in df.iterrows():
        update = recognizer.feed_data(row)
        if update:
            result = recognizer.get_result(update)
            current_type = result['PredictActivity']
            et = row['EventTimestamp(ns)'] / 1e9
            utc = datetime.fromtimestamp(et)
            if current_type != previous_type:
                print(
                    f'Activity type from <{HAR_TYPE_NAMES[previous_type]:6s}> '
                    f'CHANGED to <{HAR_TYPE_NAMES[current_type]:6s}> '
                    f'AT {utc} -- {et}')
            previous_type = current_type

            for key, value in result.items():
                if key not in predicts:
                    predicts[key] = [value]
                else:
                    predicts[key].append(value)

    result_df = pd.DataFrame.from_dict(predicts)
    return result_df


def get_standard_accel_from_raw_csv(csv_path: Path) -> pd.DataFrame:
    raw_accel_df = pd.read_csv(csv_path)
    standard_accel_df = simple_downsample(raw_accel_df)
    rebase_event_timestamp(standard_accel_df)

    return standard_accel_df


def get_standard_accel_from_log(log_path: Path,
                                activity_type=-1) -> pd.DataFrame:
    df = pd.read_csv(log_path)
    df.columns = ACC_HEADER_NAMES
    df['Activity'] = activity_type
    rebase_event_timestamp(df)
    return df


def get_standard_accel_from_record(record_dir: Path,
                                   activity_type=0) -> pd.DataFrame:
    file_preffix = record_dir.name
    header_rows = 0
    acc_file = record_dir / f'{file_preffix}-{ACC_SUFFIX}'
    if not acc_file.exists():
        file_preffix = file_preffix.split('-')[0]
        header_rows = 1
        acc_file = record_dir / f'{file_preffix}-{ACC_SUFFIX}'
        if not acc_file.exists():
            print(f'Record has no acc file: {acc_file.name}')
            exit(1)
    print(f'Recording: {acc_file}')

    raw_df = pd.read_csv(acc_file, header=header_rows)
    standard_accel_df = simple_downsample(raw_df)
    rebase_event_timestamp(standard_accel_df)
    standard_accel_df.columns = ACC_HEADER_NAMES
    standard_accel_df['Activity'] = activity_type
    return standard_accel_df


def check_event_timestamp(event_timestamp_values: np.ndarray):
    mpl.use('Qt5Agg')

    plt.plot(np.diff(event_timestamp_values),
             '-o',
             label='Event timestamp diff')
    plt.legend()
    plt.show()


def plot_result(standard_accel_df: pd.DataFrame,
                result_df: pd.DataFrame,
                title='') -> pd.DataFrame:
    acc_columns = ['AccelX', 'AccelY', 'AccelZ']
    prob_columns = ['Prob0', 'Prob1', 'Prob2', 'Prob3', 'Prob4', 'Prob5']
    result_columns = ['Activity', 'Predict', 'PredictActivity']

    mpl.use('Qt5Agg')
    # 311
    fig, axes = plt.subplots(3, 1, figsize=(12, 6), sharex=True)
    for i, col in enumerate(acc_columns):
        axes[0].plot(standard_accel_df['EventTimestamp(ns)'],
                     standard_accel_df[col],
                     '-o',
                     label=col)

    if 'STD' in result_df.columns:
        std = result_df['STD'].values
        axes[0].plot(result_df['EventTimestamp(ns)'], std, '-o', label='STD')
        std_mean = np.mean(std)
        axes[0].hlines(std_mean,
                       xmin=standard_accel_df['EventTimestamp(ns)'].values[0],
                       xmax=standard_accel_df['EventTimestamp(ns)'].values[-1],
                       label=f'STD Mean: {std_mean:.3f}')

    # 312
    for i, col in enumerate(result_columns):
        axes[1].plot(result_df['EventTimestamp(ns)'],
                     result_df[col],
                     '-o',
                     label=col)

    plt.yticks(ticks=[i for i in range(len(HAR_TYPE_NAMES))],
               labels=HAR_TYPE_NAMES)

    # 313
    for i, col in enumerate(prob_columns):
        axes[2].plot(result_df['EventTimestamp(ns)'],
                     result_df[col],
                     '-o',
                     label=HAR_TYPE_NAMES[i])

    @ticker.FuncFormatter
    def func(x, pos):
        return datetime.fromtimestamp(int(x / 1e9)).time()

    axes[0].set_title(title)

    axes[1].set_yticks(ticks=[i for i in range(len(HAR_TYPE_NAMES))])
    axes[1].set_labels(HAR_TYPE_NAMES)

    for ax in axes:
        ax.legend()
        ax.xaxis.set_major_formatter(func)

    plt.show()


def get_standard_accel(data_path: Path, is_record: bool) -> pd.DataFrame:
    if data_path.is_dir():
        if is_record:
            standard_accel_df = get_standard_accel_from_record(data_path)
            return standard_accel_df
        else:
            print('Are you specified one record directory?\n'
                  'Then run with "-r" option')
    elif data_path.is_file():
        assert data_path.suffix in {'.csv', '.log'}
        if data_path.suffix == '.csv':
            standard_accel_df = get_standard_accel_from_record
            return standard_accel_df
        elif data_path.suffix == '.log':
            standard_accel_df = get_standard_accel_from_log(data_path)
            return standard_accel_df


def run(data_path: Path, is_record: bool):

    standard_accel_df = get_standard_accel(data_path)

    check_event_timestamp(standard_accel_df['EventTimestamp(ns)'].values)

    result = process_standard_accel_xyz_26hz(standard_accel_df)

    plot_result(standard_accel_df, result)


@click.command()
@click.argument('data-path')
@click.option('-r', '--record', is_flag=True, help='Data path is a record dir')
def main(data_path: str, is_record: bool):
    data_path = Path(data_path)

    run(data_path, is_record)


if __name__ == '__main__':
    main()
