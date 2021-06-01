'''
Author       : Tianzw
Date         : 2021-03-22 20:40:29
LastEditors  : Please set LastEditors
LastEditTime : 2021-03-24 10:40:30
FilePath     : /heart-health/src/py/tools/refactor.py
'''
from datetime import date, datetime, timedelta
from enum import Enum, unique
from pathlib import Path
from pprint import pprint
import shutil

import click
import fitparse
import numpy as np
import pandas as pd

ACCEL_HEADER_LINE = 1  # begin with 0
ACCEL_SUFFIX = 'accel-52HZ.csv'
GARMIN_FIT_SUFFIX = '.fit'
POLAR_CSV_SUFFIX = '.csv'

ACCEL_COLUMNS = [
    'CurrentTimeMillis', 'EventTimestamp(ns)', 'accel_x', 'accel_y', 'accel_z'
]
LIBAI_ACCEL_COLLECTED_COLUMNS = [
    'libai_tag', 'garmin_tag', 'polar_tag', 'accel_name', 'date',
    'start_timestamp', 'stop_timestamp', 'seconds', 'sport_name', 'distance',
    'accel_path'
]
GARMIN_FIT_COLLECTED_COLUMNS = [
    'tag', 'garmin_name', 'date', 'start_timestamp', 'stop_timestamp',
    'seconds', 'sport_name', 'distance', 'garmin_path'
]

GARMIN_FIT_INSERTED_COLUMNS = [
    'garmin_name', 'overlap', 'overlap_rate', 'garmin_tag', 'libai_tag',
    'libai_name', 'start_ts_diff', 'stop_ts_diff', 'accel_start_timestamp',
    'accel_stop_timestamp', 'garmin_start_timestamp', 'garmin_stop_timestamp',
    'garmin_path', 'accel_path'
]

POLAR_CSV_INSERTED_COLUMNS = [
    'polar_name', 'overlap', 'overlap_rate', 'polar_tag', 'libai_tag',
    'libai_name', 'start_ts_diff', 'stop_ts_diff', 'accel_start_timestamp',
    'accel_stop_timestamp', 'polar_start_timestamp', 'polar_stop_timestamp',
    'polar_path', 'accel_path'
]

POLAR_CSV_COLLECTED_COLUMNS = [
    'tag', 'polar_name', 'date', 'start_timestamp', 'stop_timestamp',
    'seconds', 'sport_name', 'distance', 'polar_path'
]

MATCH_COLUMNS = [
    'libai_name',
    'match_type',
    'garmin_overlap',
    'polar_overlap',
    'garmin_overlap_rate',
    'polar_overlap_rate',
    'libai_tag',
    'garmin_tag',
    'polar_tag',
    'libai_record',
    'garmin_path',
    'polar_path',
]

GARMIN_UTC_OFFSET = timedelta(hours=8)


@unique
class MatchType(Enum):
    NO_POLAR_GARMIN = 'NO_POLAR_GARMIN',
    NO_POLAR = 'NO_POLAR',
    NO_GARMIN = 'NO_GARMIN',
    VALID_RECORD = 'VALID_RECORD',


def arg_nearest_in_sorted(value, arr_sorted: np.ndarray) -> int:
    i = np.searchsorted(arr_sorted, value)

    if i == len(arr_sorted):
        return i - 1

    if i == 0:
        return 0

    if abs(arr_sorted[i - 1] - value) < abs(arr_sorted[i] - value):
        return i - 1

    return i


def get_insert_info(accel_start_ts: int, accel_stop_ts: int,
                    target_start_ts: int, target_stop_ts: int) -> tuple:
    accel_seconds = accel_stop_ts - accel_start_ts
    target_seconds = target_stop_ts - accel_start_ts

    if target_start_ts < accel_start_ts:
        overlap = target_stop_ts - accel_start_ts
        overlap = min(overlap, accel_seconds)
    elif target_start_ts >= accel_start_ts:
        overlap = accel_stop_ts - target_start_ts
        overlap = min(overlap, target_seconds)

    overlap_rate = (overlap / accel_seconds) * 100

    start_ts_diff = target_start_ts - accel_start_ts
    stop_ts_diff = target_stop_ts - accel_stop_ts

    return (overlap, overlap_rate, start_ts_diff, stop_ts_diff)


def save_df_to_log(df, df_name: str):
    log_dir = Path('./src/py/log')
    log_dir.mkdir(parents=True, exist_ok=True)
    df_path = log_dir / df_name
    df.to_csv(df_path, index=False)
    print(f'Saved: {df_path}\n')


def read_info_from_libai_accel(libai_accel_path: Path) -> tuple:
    libai_accel_path = Path(libai_accel_path)

    start_timestamp, stop_timestamp, seconds = None, None, None
    start_date = None
    sport_name, distance = None, None

    libai_accel_df = pd.read_csv(libai_accel_path, header=ACCEL_HEADER_LINE)

    last = libai_accel_df.index[-1]
    start_timestamp = libai_accel_df.loc[0, 'CurrentTimeMillis'] // 1000
    stop_timestamp = libai_accel_df.loc[last, 'CurrentTimeMillis'] // 1000

    if start_timestamp and stop_timestamp:
        seconds = stop_timestamp - start_timestamp
    if start_timestamp:
        start_date = datetime.fromtimestamp(start_timestamp).date().isoformat()

    return (start_date, start_timestamp, stop_timestamp, seconds, sport_name,
            distance)


def read_info_from_garmin_fit(garmin_fit_path: str) -> tuple:
    garmin_fit_path = str(garmin_fit_path)

    garmin_fit_opened = fitparse.FitFile(garmin_fit_path)

    start_datetime, stop_datetime, distance = None, None, None
    for record in garmin_fit_opened.get_messages('record'):
        for data in record:
            name, value = data.name, data.value
            if name == 'timestamp':  # amateur name for garmin
                if start_datetime is None:
                    start_datetime = value
                stop_datetime = value
            if name == 'distance':
                distance = value

    (start_timestamp, stop_timestamp, start_date_str, seconds) = (None, None,
                                                                  None, None)
    if start_datetime is not None:
        start_datetime += GARMIN_UTC_OFFSET
        start_date_str = start_datetime.date().isoformat()
        start_timestamp = int(start_datetime.timestamp())
    if stop_datetime is not None:
        stop_datetime += GARMIN_UTC_OFFSET
        stop_timestamp = int(stop_datetime.timestamp())
    if isinstance(stop_timestamp, int) and isinstance(start_timestamp, int):
        seconds = stop_timestamp - start_timestamp
    sport_name = None
    return (start_date_str, start_timestamp, stop_timestamp, seconds,
            sport_name, distance)


def collect_garmin_fit_info(garmin_clean: Path) -> pd.DataFrame:
    garmin_clean = Path(garmin_clean)

    garmin_infos = []
    for garmin_fit_path in garmin_clean.rglob(f'*{GARMIN_FIT_SUFFIX}'):
        print(f'Processing: {garmin_fit_path.name}')
        tag = garmin_fit_path.parents[0].name
        garmin_name = garmin_fit_path.name
        garmin_info = read_info_from_garmin_fit(garmin_fit_path)
        garmin_infos.append((tag, garmin_name, *garmin_info, garmin_fit_path))
    garmin_fit_collected = pd.DataFrame(garmin_infos,
                                        columns=GARMIN_FIT_COLLECTED_COLUMNS)
    print(f'Succeed: collect garmin from {garmin_clean}\n')

    return garmin_fit_collected


def collect_libai_accel_info(libai_clean: Path) -> pd.DataFrame:
    libai_clean = Path(libai_clean)

    libai_accel_infos = []
    for libai_accel_path in libai_clean.rglob(f'*{ACCEL_SUFFIX}'):
        print(f'Processing: {libai_accel_path.name}')
        libai_name = libai_accel_path.parent.name
        libai_tag = libai_name.split('-')[-4]
        garmin_tag = libai_name.split('-')[-2]
        polar_tag = libai_name.split('_')[-1]
        accel_name = libai_accel_path.name
        libai_accel_info = read_info_from_libai_accel(libai_accel_path)
        libai_accel_infos.append((libai_tag, garmin_tag, polar_tag, accel_name,
                                  *libai_accel_info, libai_accel_path))
    libai_accel_collected = pd.DataFrame(libai_accel_infos,
                                         columns=LIBAI_ACCEL_COLLECTED_COLUMNS)
    print(f'Succeed: collect libai accel from {libai_clean}\n')
    return libai_accel_collected


def read_info_from_polar_csv(polar_csv_path: Path) -> tuple:
    polar_csv_path = Path(polar_csv_path)
    sport_name = polar_csv_path.stem.split('_')[-1]

    start_date, start_timestamp, stop_timestamp = None, None, None
    seconds, distance = None, None

    with open(polar_csv_path, 'r') as f:
        f.readline()  # skip the first line
        second_line = f.readline().strip()
        fields = second_line.split(',')
        date_str, time_str = fields[2], fields[3]
        distance = fields[5]
        duration = fields[4].split(':')
        duration_timedelta = timedelta(hours=int(duration[0]),
                                       minutes=int(duration[1]),
                                       seconds=int(duration[2]))
        seconds = duration_timedelta.seconds
        start_datetime_str = date_str + ' ' + time_str
        start_datetime = datetime.strptime(start_datetime_str,
                                           '%d-%m-%Y %H:%M:%S')
        start_date = start_datetime.date().isoformat()
        start_timestamp = int(start_datetime.timestamp())
        stop_timestamp = start_timestamp + seconds

    return (start_date, start_timestamp, stop_timestamp, seconds, sport_name,
            distance)


def collect_polar_info(polar_clean: Path) -> pd.DataFrame:
    polar_clean = Path(polar_clean)
    polar_infos = []
    for polar_csv_path in polar_clean.rglob(f'*{POLAR_CSV_SUFFIX}'):
        print(f'Processing: {polar_csv_path.name}')
        tag = polar_csv_path.parents[0].name
        polar_name = polar_csv_path.name
        polar_info = read_info_from_polar_csv(polar_csv_path)
        polar_infos.append((tag, polar_name, *polar_info, polar_csv_path))
    polar_csv_collected = pd.DataFrame(polar_infos,
                                       columns=POLAR_CSV_COLLECTED_COLUMNS)
    print(f'Succeed: collect polar from {polar_clean}\n')

    return polar_csv_collected


def collect_and_save_libai_garmin_polar(libai_clean: Path, garmin_clean: Path,
                                        polar_clean: Path) -> tuple:
    libai_clean = Path(libai_clean)
    garmin_clean = Path(garmin_clean)
    polar_clean = Path(polar_clean)

    libai_accel_collected = collect_libai_accel_info(libai_clean)
    garmin_fit_collected = collect_garmin_fit_info(garmin_clean)
    polar_csv_collected = collect_polar_info(polar_clean)

    save_df_to_log(libai_accel_collected, 'libai_accel_collected.csv')
    save_df_to_log(garmin_fit_collected, 'garmin_fit_collected.csv')
    save_df_to_log(polar_csv_collected, 'polar_csv_collected.csv')

    return (libai_accel_collected, garmin_fit_collected, polar_csv_collected)


def insert_garmin_fit_into_libai_record(garmin_fit_collected: pd.DataFrame,
                                        libai_accel_collected: pd.DataFrame
                                        ) -> dict:
    libai_accel_collected.sort_values(by='start_timestamp', inplace=True)
    libai_name_inserted = {}
    for i, row in garmin_fit_collected.iterrows():
        garmin_path = Path(row['garmin_path'])
        garmin_tag = row['tag']
        garmin_start_timestamp = row['start_timestamp']
        garmin_stop_timestamp = row['stop_timestamp']

        libai_accel_part = libai_accel_collected[
            libai_accel_collected['garmin_tag'] == garmin_tag].copy()

        if libai_accel_part.empty:
            # TODO: process garmin fit file without the same tag libai record
            continue
        libai_accel_part.sort_values(by='start_timestamp', inplace=True)
        libai_accel_part.reset_index(drop=True, inplace=True)

        accel_nearest_index = arg_nearest_in_sorted(
            garmin_start_timestamp, libai_accel_part['start_timestamp'].values)

        libai_accel_path = Path(
            libai_accel_part.loc[accel_nearest_index, 'accel_path'])
        accel_start_timestamp = libai_accel_part.loc[accel_nearest_index,
                                                     'start_timestamp']
        accel_stop_timestamp = libai_accel_part.loc[accel_nearest_index,
                                                    'stop_timestamp']
        libai_tag = libai_accel_part.loc[accel_nearest_index, 'libai_tag']

        garmin_name = garmin_path.name
        libai_record = libai_accel_path.parent
        libai_name = libai_record.name

        (overlap, overlap_rate, start_ts_diff, stop_ts_diff) = get_insert_info(
            accel_start_timestamp, accel_stop_timestamp,
            garmin_start_timestamp, garmin_stop_timestamp)

        if overlap <= 0:
            print(f'Failure match: overlap = {overlap}, '
                  f'garmin_name = {garmin_name}')
            continue

        msg = (garmin_name, overlap, overlap_rate, garmin_tag, libai_tag,
               libai_name, start_ts_diff, stop_ts_diff, accel_start_timestamp,
               accel_stop_timestamp, garmin_start_timestamp,
               garmin_stop_timestamp, garmin_path, libai_accel_path)

        if libai_name in libai_name_inserted:
            print(f'Already matchs: {libai_name}')
            print('old_msg = ')
            old_msg = libai_name_inserted[libai_name]
            pprint(old_msg)
            print('new_msg = ')
            pprint(msg)
            old_overlap = old_msg[1]
            if overlap > old_overlap:
                shutil.copy(garmin_path, libai_record)
                libai_name_inserted[libai_name] = msg
                print(f'Change match: old_overlap, new_overlap = '
                      f'{old_overlap}, {overlap}')
            else:
                print(f'Remain match: old_overlap, new_overlap = '
                      f'{old_overlap}, {overlap}')
            print('\n')
        else:
            shutil.copy(garmin_path, libai_record)
            libai_name_inserted[libai_name] = msg
    print('Succeed: insert garmin fit into libai reocrd\n')
    return libai_name_inserted


def insert_polar_csv_into_libai_record(polar_csv_collected: pd.DataFrame,
                                       libai_accel_collected: pd.DataFrame
                                       ) -> dict:
    libai_accel_collected.sort_values(by='start_timestamp', inplace=True)
    libai_name_inserted = {}
    for i, row in polar_csv_collected.iterrows():
        polar_path = Path(row['polar_path'])
        polar_tag = row['tag']
        polar_start_timestamp = row['start_timestamp']
        polar_stop_timestamp = row['stop_timestamp']

        libai_accel_part = libai_accel_collected[
            libai_accel_collected['polar_tag'] == polar_tag].copy()

        if libai_accel_part.empty:
            # TODO: process polar fit file without the same tag libai record
            continue
        libai_accel_part.sort_values(by='start_timestamp', inplace=True)
        libai_accel_part.reset_index(drop=True, inplace=True)

        accel_nearest_index = arg_nearest_in_sorted(
            polar_start_timestamp, libai_accel_part['start_timestamp'].values)

        libai_accel_path = Path(
            libai_accel_part.loc[accel_nearest_index, 'accel_path'])
        accel_start_timestamp = libai_accel_part.loc[accel_nearest_index,
                                                     'start_timestamp']
        accel_stop_timestamp = libai_accel_part.loc[accel_nearest_index,
                                                    'stop_timestamp']
        libai_tag = libai_accel_part.loc[accel_nearest_index, 'libai_tag']

        polar_name = polar_path.name
        libai_record = libai_accel_path.parent
        libai_name = libai_record.name

        (overlap, overlap_rate, start_ts_diff, stop_ts_diff) = get_insert_info(
            accel_start_timestamp, accel_stop_timestamp, polar_start_timestamp,
            polar_stop_timestamp)

        if overlap <= 0:
            print(f'Failure match: overlap = {overlap}, '
                  f'polar_name = {polar_name}')
            continue

        msg = (polar_name, overlap, overlap_rate, polar_tag, libai_tag,
               libai_name, start_ts_diff, stop_ts_diff, accel_start_timestamp,
               accel_stop_timestamp, polar_start_timestamp,
               polar_stop_timestamp, polar_path, libai_accel_path)

        if libai_name in libai_name_inserted:
            print(f'Already matchs: {libai_name}')
            print('old_msg = ')
            old_msg = libai_name_inserted[libai_name]
            pprint(old_msg)
            print('new_msg = ')
            pprint(msg)
            old_overlap = old_msg[1]
            if overlap > old_overlap:
                shutil.copy(polar_path, libai_record)
                libai_name_inserted[libai_name] = msg
                print(f'Change match: old_overlap, new_overlap = '
                      f'{old_overlap}, {overlap}')
            else:
                print(f'Remain match: old_overlap, new_overlap = '
                      f'{old_overlap}, {overlap}')
            print('\n')
        else:
            shutil.copy(polar_path, libai_record)
            libai_name_inserted[libai_name] = msg
    print('Succeed: insert polar into libai reocrd\n')
    return libai_name_inserted


def save_libai_name_inserted(libai_name_inserted: dict,
                             columns: list) -> pd.DataFrame:
    vals = []
    for val in libai_name_inserted.values():
        vals.append(val)
    inserted_msg = pd.DataFrame(vals, columns=columns)
    return inserted_msg


def match_summary(accel_collected: pd.DataFrame,
                  garmin_fit_inserted: pd.DataFrame,
                  polar_csv_inserted: pd.DataFrame) -> pd.DataFrame:

    matchs = []
    for i, row in accel_collected.iterrows():
        libai_tag = row['libai_tag']
        accel_path = Path(row['accel_path'])
        libai_record = accel_path.parent
        libai_name = libai_record.name

        garmin_part = garmin_fit_inserted[garmin_fit_inserted['libai_name'] ==
                                          libai_name].copy()
        polar_part = polar_csv_inserted[polar_csv_inserted['libai_name'] ==
                                        libai_name].copy()
        garmin_overlap, garmin_overlap_rate, garmin_path = None, None, None
        polar_overlap, polar_overlap_rate, polar_path = None, None, None
        polar_tag, garmin_tag = None, None

        if not garmin_part.empty:
            if len(garmin_part) > 1:
                pass
            garmin_overlap = garmin_part['overlap'].values[0]
            garmin_overlap_rate = garmin_part['overlap_rate'].values[0]
            garmin_path = garmin_part['garmin_path'].values[0]
            garmin_tag = int(garmin_part['garmin_tag'].values[0])
        if not polar_part.empty:
            if len(polar_part) > 1:
                pass
            polar_overlap = polar_part['overlap'].values[0]
            polar_overlap_rate = polar_part['overlap_rate'].values[0]
            polar_path = polar_part['polar_path'].values[0]
            polar_tag = int(polar_part['polar_tag'].values[0])

        if garmin_path is not None:
            if polar_path is not None:
                match_type = MatchType.VALID_RECORD.value[0]
            else:
                match_type = MatchType.NO_POLAR.value[0]
        else:
            if polar_path is not None:
                match_type = MatchType.NO_GARMIN.value[0]
            else:
                match_type = MatchType.NO_POLAR_GARMIN.value[0]

        matchs.append(
            (libai_name, match_type, garmin_overlap, polar_overlap,
             garmin_overlap_rate, polar_overlap_rate, libai_tag, garmin_tag,
             polar_tag, libai_record, garmin_path, polar_path))
    match_df = pd.DataFrame(matchs, columns=MATCH_COLUMNS)
    return match_df


def run(libai_clean, garmin_clean, polar_clean) -> tuple:
    (libai_accel_collected, garmin_fit_collected,
     polar_csv_collected) = collect_and_save_libai_garmin_polar(
         libai_clean, garmin_clean, polar_clean)

    save_df_to_log(libai_accel_collected, 'libai_accel_collected.csv')
    save_df_to_log(garmin_fit_collected, 'garmin_fit_collected.csv')
    save_df_to_log(polar_csv_collected, 'polar_csv_collected.csv')

    garmin_fit_inserted_dict = insert_garmin_fit_into_libai_record(
        garmin_fit_collected, libai_accel_collected)
    garmin_fit_inserted = save_libai_name_inserted(
        garmin_fit_inserted_dict, columns=GARMIN_FIT_INSERTED_COLUMNS)

    polar_csv_inserted_dict = insert_polar_csv_into_libai_record(
        polar_csv_collected, libai_accel_collected)
    polar_csv_inserted = save_libai_name_inserted(
        polar_csv_inserted_dict, columns=POLAR_CSV_INSERTED_COLUMNS)
    print(f'garmin_fit_inserted = {garmin_fit_collected.head()}')

    match_df = match_summary(libai_accel_collected, garmin_fit_inserted,
                             polar_csv_inserted)
    save_df_to_log(match_df, 'match_summary.csv')


@click.command()
@click.argument('libai-clean')
@click.option('-garmin', '--garmin-clean', required=True, type=str)
@click.option('-polar', '--polar-clean', required=True, type=str)
def main(libai_clean, garmin_clean, polar_clean):
    run(libai_clean, garmin_clean, polar_clean)


if __name__ == '__main__':
    main()
