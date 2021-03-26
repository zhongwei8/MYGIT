'''
Author       : Tianzw
Date         : 2021-03-25 09:46:20
LastEditors  : Please set LastEditors
LastEditTime : 2021-03-26 10:16:34
FilePath     : /heart-health/src/py/tools/merge_ppg_into_accel.py
'''
from pathlib import Path

import click
import numpy as np
import pandas as pd

ACCEL_HEADER = [
    'CurrentTimeMillis', 'EventTimestamp(ns)', 'accel_x', 'accel_y', 'accel_z'
]
PPG_HEADER = ['CurrentTimeMillis', 'EventTimestamp(ns)', 'ch1', 'ch2', 'touch']

ACCEL_PPG_COLUMNS = ACCEL_HEADER + PPG_HEADER[2:]
ACCEL_PPG_TYPE = [int, int, float, float, float, int, int, int]

PPG_HEADER_LINE = 1  # begin with 0
ACCEL_HEADER_LINE = 1  # begin with 0
PPG_LINE_SKIP = 5  # skip the head of ppg, the ns may error

LIBAI_FILE_PREFIX = 'libai_'
LIBAI_ACCEL_SUFFIX = '-accel-52HZ.csv'
LIBAI_PPG_SUFFIX = '-ppg-100HZ.csv'


def arg_nearest_in_sorted(value, arr_sorted: np.ndarray) -> int:
    i = np.searchsorted(arr_sorted, value)

    if i == len(arr_sorted):
        return i - 1

    if i == 0:
        return 0

    if abs(arr_sorted[i - 1] - value) < abs(arr_sorted[i] - value):
        return i - 1

    return i


def get_accel_ppg_path(libai_record: Path) -> tuple:
    libai_record = Path(libai_record)

    record_name = libai_record.name
    record_datetime_key = record_name.split('-')[0]

    accel_name = LIBAI_FILE_PREFIX + record_datetime_key + LIBAI_ACCEL_SUFFIX
    ppg_name = LIBAI_FILE_PREFIX + record_datetime_key + LIBAI_PPG_SUFFIX

    accel_path = libai_record / accel_name
    ppg_path = libai_record / ppg_name

    return (accel_path, ppg_path)


def read_accel_ppg_values(accel_path: Path, accel_header_line: int,
                          ppg_path: Path, ppg_header_line: int) -> tuple:
    accel_path = Path(accel_path)
    ppg_path = Path(ppg_path)

    accel_df = pd.read_csv(accel_path, header=accel_header_line)
    ppg_df = pd.read_csv(ppg_path, header=ppg_header_line)

    accel_values = accel_df.values
    ppg_values = ppg_df.values[
        PPG_LINE_SKIP:, :]  # skip the head of ppg, the ns may error

    return (accel_values, ppg_values)


def preprocess_accel_ppg_values(accel: np.ndarray, ppg: np.ndarray) -> tuple:

    accel_ms_base, accel_ns_base = accel[0, 0], accel[0, 1]
    ppg_ms_base, ppg_ns_base = ppg[0, 0], ppg[0, 1]

    ppg_lateness_ms = ppg_ms_base - accel_ms_base
    ppg_lateness_ns = ppg_lateness_ms * int(1e6)

    accel[:, 1] -= accel_ns_base
    ppg[:, 1] -= ppg_ns_base

    ppg[:, 1] += ppg_lateness_ns

    accel_start_ns, accel_stop_ns = accel[0, 1], accel[-1, 1]
    ppg_start_ns, ppg_stop_ns = ppg[0, 1], ppg[-1, 1]

    start_ns = max(accel_start_ns, ppg_start_ns)
    stop_ns = min(accel_stop_ns, ppg_stop_ns)

    print(f'start_ns, stop_ns, seconds = '
          f'{int(start_ns)}, {int(stop_ns)}, '
          f'{int(stop_ns - start_ns) // int(1e9)}')

    accel_mask = (accel[:, 1] >= start_ns) & (accel[:, 1] <= stop_ns)
    ppg_mask = (ppg[:, 1] >= start_ns) & (ppg[:, 1] <= stop_ns)

    accel_cliped = accel[accel_mask]
    ppg_cliped = ppg[ppg_mask]

    print(f'accel_cliped_df.head() = \n'
          f'{pd.DataFrame(accel_cliped, columns = ACCEL_HEADER).head()}')

    print(f'ppg_cliped_df.head() = \n'
          f'{pd.DataFrame(ppg_cliped, columns = PPG_HEADER).head()}')

    print(f'accel_cliped.shape = {accel_cliped.shape}')
    print(f'ppg_cliped.shape = {ppg_cliped.shape}')

    return (accel_cliped, ppg_cliped)


def merge_ppg_into_accel(ppg: np.ndarray, accel: np.ndarray) -> np.ndarray:
    """ align with ns """
    accel_ns, ppg_ns = accel[:, 1], ppg[:, 1]

    ppg_index = np.full_like(accel_ns, -1).astype(np.int)

    for i, ns in enumerate(accel_ns):
        nearest = arg_nearest_in_sorted(ns, ppg_ns)
        ppg_index[i] = nearest

    ppg_part = ppg[ppg_index, 2:]

    accel_ppg_merged = np.hstack((accel, ppg_part))

    return accel_ppg_merged


def convert_accel_ppg_values(accel_ppg_values: np.ndarray) -> pd.DataFrame:

    column_types = dict(zip(ACCEL_PPG_COLUMNS, ACCEL_PPG_TYPE))

    accel_ppg_df = pd.DataFrame(
        accel_ppg_values, columns=ACCEL_PPG_COLUMNS).astype(dtype=column_types)

    return accel_ppg_df


def save_accel_ppg_df_nearly(accel_ppg_df, accel_path: Path):
    accel_path = Path(accel_path)

    accel_ppg_name = accel_path.name.replace('accel', 'accel-ppg-merged')

    accel_ppg_path = accel_path.with_name(accel_ppg_name)

    accel_ppg_df.to_csv(accel_ppg_path, index=False)

    print(f'Saved: {accel_ppg_path}')


def process_one_record(record_path: Path):
    accel_path, ppg_path = get_accel_ppg_path(record_path)

    if not accel_path.exists() or not ppg_path.exists():
        print(f'Not exists: {accel_path} or {ppg_path}')
        return

    accel_values, ppg_values = read_accel_ppg_values(accel_path,
                                                     ACCEL_HEADER_LINE,
                                                     ppg_path, PPG_HEADER_LINE)

    accel_cliped_values, ppg_cliped_values = preprocess_accel_ppg_values(
        accel_values, ppg_values)

    accel_ppg_values = merge_ppg_into_accel(ppg_cliped_values,
                                            accel_cliped_values)

    accel_ppg_df = convert_accel_ppg_values(accel_ppg_values)

    save_accel_ppg_df_nearly(accel_ppg_df, accel_path)


def process_record_dir(record_dir: Path):
    record_dir = Path(record_dir)
    for date_str in record_dir.iterdir():
        for libai_record in date_str.iterdir():
            print(f'Processing: {libai_record.name}')
            process_one_record(libai_record)


@click.command()
@click.argument('libai-dir')
@click.option('-d', '--is-dir', is_flag=True, help='Directory to process')
def main(libai_dir: str, is_dir: bool):
    libai_dir = Path(libai_dir)

    if is_dir:
        process_record_dir(libai_dir)
    else:
        process_one_record(libai_dir)


if __name__ == '__main__':
    main()
