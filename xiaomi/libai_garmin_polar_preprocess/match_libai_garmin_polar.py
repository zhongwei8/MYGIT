from collections import namedtuple
from datetime import datetime, timedelta
from enum import Enum, unique
from pathlib import Path
import shutil

import click
import fitparse
import numpy as np
import pandas as pd

GARMIN_UTC_OFFSET = timedelta(hours=8)

LOG_DIR = Path(__file__).parent / 'log'

RecordInfo = namedtuple('RecordInfo', [
    'date', 'start_timestamp', 'stop_timestamp', 'seconds', 'sport_name',
    'distance'
])


@unique
class MatchType(Enum):
    NO_POLAR_GARMIN = 'NO_POLAR_GARMIN',
    NO_POLAR = 'NO_POLAR',
    NO_GARMIN = 'NO_GARMIN',
    VALID_RECORD = 'VALID_RECORD',


LIBAI_ACCEL_SUFFIX = 'accel-52HZ.csv'
LIBAI_ACCEL_HEADER_LINE = 1  # begin with 0
LIBAI_ACCEL_COLLECTED_COLUMNS = [
    'libai_tag', 'garmin_tag', 'polar_tag', 'name', 'date', 'start_timestamp',
    'stop_timestamp', 'seconds', 'sport_name', 'distance', 'path'
]

GARMIN_FIT_SUFFIX = '.fit'
GARMIN_FIT_COLLECTED_COLUMNS = [
    'tag', 'name', 'date', 'start_timestamp', 'stop_timestamp', 'seconds',
    'sport_name', 'distance', 'path'
]
GARMIN_FIT_INSERTED_COLUMNS = [
    'garmin_name', 'overlap', 'overlap_rate', 'garmin_tag', 'libai_tag',
    'libai_name', 'start_timestamp_diff', 'stop_timestamp_diff',
    'accel_start_timestamp', 'accel_stop_timestamp', 'garmin_start_timestamp',
    'garmin_stop_timestamp', 'garmin_fit_path', 'libai_accel_path'
]

POLAR_CSV_SUFFIX = '.csv'
POLAR_CSV_COLLECTED_COLUMNS = [
    'tag', 'name', 'date', 'start_timestamp', 'stop_timestamp', 'seconds',
    'sport_name', 'distance', 'path'
]

POLAR_CSV_INSERTED_COLUMNS = [
    'polar_name', 'overlap', 'overlap_rate', 'polar_tag', 'libai_tag',
    'libai_name', 'start_timestamp_diff', 'stop_timestamp_diff',
    'accel_start_timestamp', 'accel_stop_timestamp', 'polar_start_timestamp',
    'polar_stop_timestamp', 'polar_csv_path', 'libai_accel_path'
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
    'garmin_fit_path',
    'polar_csv_path',
]


def save_df_to_log(df, df_name: str):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    df_path = LOG_DIR / df_name
    df.to_csv(df_path, index=False)
    print(f'Saved: {df_path}\n')


def arg_nearest_in_sorted(value, arr_sorted: np.ndarray) -> int:
    i = np.searchsorted(arr_sorted, value)

    if i == len(arr_sorted):
        return i - 1

    if i == 0:
        return 0

    if abs(arr_sorted[i - 1] - value) < abs(arr_sorted[i] - value):
        return i - 1

    return i


def read_info_from_libai_accel(libai_accel_path: Path) -> RecordInfo:

    libai_accel_path = Path(libai_accel_path)

    start_timestamp, stop_timestamp, seconds = (None, None, None)
    start_date_str = None
    sport_name, distance = None, None

    libai_accel_df = pd.read_csv(libai_accel_path,
                                 header=LIBAI_ACCEL_HEADER_LINE)

    last = libai_accel_df.index[-1]

    start_timestamp = libai_accel_df.loc[0, 'CurrentTimeMillis'] // 1000
    stop_timestamp = libai_accel_df.loc[last, 'CurrentTimeMillis'] // 1000

    if start_timestamp and stop_timestamp:
        seconds = stop_timestamp - start_timestamp
    if start_timestamp:
        start_date_str = datetime.fromtimestamp(
            start_timestamp).date().isoformat()

    record_info = RecordInfo(start_date_str, start_timestamp, stop_timestamp,
                             seconds, sport_name, distance)
    return record_info


def read_info_from_garmin_fit(garmin_fit_path: Path) -> RecordInfo:
    garmin_fit_path = str(garmin_fit_path)

    garmin_fit_opened = fitparse.FitFile(garmin_fit_path)

    start_datetime, stop_datetime = None, None
    distance = None
    for record in garmin_fit_opened.get_messages('record'):
        for data in record:
            name, value = data.name, data.value
            if name == 'timestamp':
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
    if isinstance(start_timestamp, int) and isinstance(stop_timestamp, int):
        seconds = stop_timestamp - start_timestamp
    sport_name = None

    record_info = RecordInfo(start_date_str, start_timestamp, stop_timestamp,
                             seconds, sport_name, distance)
    return record_info


def read_info_from_polar_csv(polar_csv_path: Path) -> RecordInfo:
    polar_csv_path = Path(polar_csv_path)

    sport_name = polar_csv_path.stem.split('_')[-1]

    start_date_str, start_timestamp, stop_timestamp = None, None, None
    seconds, distance = None, None

    with open(polar_csv_path, 'r') as f:
        f.readline()
        second_line = f.readline().strip()
        fields = second_line.split(',')
        start_date_str, start_time_str = fields[2], fields[3]
        distance = fields[5]
        duration = fields[4].split(':')
        duration_timedelta = timedelta(hours=int(duration[0]),
                                       minutes=int(duration[1]),
                                       seconds=int(duration[2]))
        seconds = duration_timedelta.seconds
        start_datetime_str = start_date_str + ' ' + start_time_str
        start_datetime = datetime.strptime(start_datetime_str,
                                           '%d-%m-%Y %H:%M:%S')  # 日月年 时分秒
        start_date_str = start_datetime.date().isoformat()
        start_timestamp = int(start_datetime.timestamp())
        stop_timestamp = start_timestamp + seconds

    record_info = RecordInfo(start_date_str, start_timestamp, stop_timestamp,
                             seconds, sport_name, distance)

    return record_info


def collect_libai_accel_infos(libai_clean: Path) -> pd.DataFrame:
    libai_clean = Path(libai_clean)

    libai_accel_infos = []
    for libai_accel_path in libai_clean.rglob(f'*{LIBAI_ACCEL_SUFFIX}'):
        print(f'Collecting libai accel info: {libai_accel_path.name}')
        libai_name = libai_accel_path.parent.name
        libai_tag = libai_name.split('-')[-4]
        garmin_tag = libai_name.split('-')[-2]
        polar_tag = libai_name.split('_')[-1]
        accel_name = libai_accel_path.name
        libai_accel_info = read_info_from_libai_accel(libai_accel_path)

        msg = (libai_tag, garmin_tag, polar_tag, accel_name, *libai_accel_info,
               libai_accel_path)
        libai_accel_infos.append(msg)

    libai_accel_collected = pd.DataFrame(libai_accel_infos,
                                         columns=LIBAI_ACCEL_COLLECTED_COLUMNS)

    libai_accel_collected.sort_values(by='start_timestamp', inplace=True)

    print(f'Succeed: collect libai accel info from {libai_clean}\n')

    return libai_accel_collected


def collect_garmin_fit_infos(garmin_clean: Path) -> pd.DataFrame:
    garmin_clean = Path(garmin_clean)

    garmin_fit_infos = []
    for garmin_fit_path in garmin_clean.rglob(f'*{GARMIN_FIT_SUFFIX}'):
        print(f'Collecting garmin fit info: {garmin_fit_path.name}')
        garmin_tag = garmin_fit_path.parents[0].name
        garmin_name = garmin_fit_path.name
        garmin_fit_info = read_info_from_garmin_fit(garmin_fit_path)
        msg = (garmin_tag, garmin_name, *garmin_fit_info, garmin_fit_path)
        garmin_fit_infos.append(msg)

    garmin_fit_collected = pd.DataFrame(garmin_fit_infos,
                                        columns=GARMIN_FIT_COLLECTED_COLUMNS)
    garmin_fit_collected.sort_values(by='start_timestamp', inplace=True)

    print(f'Succeed: collect garmin fit info from {garmin_clean}\n')

    return garmin_fit_collected


def collect_polar_csv_infos(polar_clean: Path) -> pd.DataFrame:
    polar_clean = Path(polar_clean)

    polar_csv_infos = []
    for polar_csv_path in polar_clean.rglob(f'*{POLAR_CSV_SUFFIX}'):
        print(f'Collect polar csv info: {polar_csv_path.name}')
        polar_tag = polar_csv_path.parents[0].name
        polar_name = polar_csv_path.name
        polar_csv_info = read_info_from_polar_csv(polar_csv_path)
        msg = (polar_tag, polar_name, *polar_csv_info, polar_csv_path)
        polar_csv_infos.append(msg)

    polar_csv_collected = pd.DataFrame(polar_csv_infos,
                                       columns=POLAR_CSV_COLLECTED_COLUMNS)
    polar_csv_collected.sort_values(by='start_timestamp', inplace=True)

    print(f'Succeed: collect polar csv info from {polar_clean}\n')

    return polar_csv_collected


def get_insert_info(accel_start_timestamp: int, accel_stop_timestamp: int,
                    target_start_timestamp: int,
                    target_stop_timestamp: int) -> tuple:
    accel_seconds = accel_stop_timestamp - accel_start_timestamp
    target_seconds = target_stop_timestamp - accel_start_timestamp

    if target_start_timestamp < accel_start_timestamp:
        overlap = target_stop_timestamp - accel_start_timestamp
        overlap = min(overlap, accel_seconds)
    elif target_start_timestamp >= accel_start_timestamp:
        overlap = accel_stop_timestamp - target_start_timestamp
        overlap = min(overlap, target_seconds)

    overlap_rate = (overlap / accel_seconds) * 100

    start_ts_diff = target_start_timestamp - accel_start_timestamp
    stop_ts_diff = target_stop_timestamp - accel_stop_timestamp

    return (overlap, overlap_rate, start_ts_diff, stop_ts_diff)


def insert_target_into_libai_record(target_collected: pd.DataFrame,
                                    libai_accel_collected: pd.DataFrame,
                                    garmin_or_polar: str,
                                    columns: list) -> pd.DataFrame:
    libai_accel_collected.sort_values(by='start_timestamp', inplace=True)

    inserted_infos = {}
    for i, row in target_collected.iterrows():
        target_path = Path(row['path'])
        target_tag = row['tag']
        target_start_timestamp = row['start_timestamp']
        target_stop_timestamp = row['stop_timestamp']

        if garmin_or_polar == 'garmin':
            libai_accel_part = libai_accel_collected[
                libai_accel_collected['garmin_tag'] == target_tag].copy()
        elif garmin_or_polar == 'polar':
            libai_accel_part = libai_accel_collected[
                libai_accel_collected['polar_tag'] == target_tag].copy()

        if libai_accel_part.empty:
            # TODO: process target without match tag libai accel
            continue
        libai_accel_part.sort_values(by='start_timestamp', inplace=True)
        libai_accel_part.reset_index(drop=True, inplace=True)

        accel_nearest_index = arg_nearest_in_sorted(
            target_start_timestamp, libai_accel_part['start_timestamp'].values)

        libai_accel_path = Path(libai_accel_part.loc[accel_nearest_index,
                                                     'path'])
        accel_start_timestamp = libai_accel_part.loc[accel_nearest_index,
                                                     'start_timestamp']
        accel_stop_timestamp = libai_accel_part.loc[accel_nearest_index,
                                                    'stop_timestamp']
        libai_tag = libai_accel_part.loc[accel_nearest_index, 'libai_tag']

        target_name = target_path.name
        libai_record = libai_accel_path.parent
        libai_name = libai_record.name

        (overlap, overlap_rate, start_timestamp_diff,
         stop_timestamp_diff) = get_insert_info(accel_start_timestamp,
                                                accel_stop_timestamp,
                                                target_start_timestamp,
                                                target_stop_timestamp)

        if overlap <= 0:
            print(f'Failure match: overlap = {overlap}, '
                  f'target_name = {target_name}')
            continue
        insert_msg = (target_name, overlap, overlap_rate, target_tag,
                      libai_tag, libai_name, start_timestamp_diff,
                      stop_timestamp_diff, accel_start_timestamp,
                      accel_stop_timestamp, target_start_timestamp,
                      target_stop_timestamp, target_path, libai_accel_path)
        if libai_name in inserted_infos:
            old_overlap = inserted_infos[libai_name][1]
            if overlap > old_overlap:
                # to_remove = Path(inserted_infos[libai_name][-2])
                # os.remove(to_remove)
                # print(f'Removed: {to_remove}')
                # shutil.copy(target_path, libai_record)
                # print(f'Copy {target_path.name} into {libai_record.name}')
                # print(f'Replace "{to_remove}" with "{target_name}"')
                inserted_infos[libai_name] = insert_msg
            else:
                print(f'Giveup insert {target_name} into {libai_name} '
                      f'overlap, old_overlap = {overlap}, {old_overlap}')
        else:
            # shutil.copy(target_path, libai_record)
            print(f'Copy {target_path.name} into {libai_record.name}')
            inserted_infos[libai_name] = insert_msg

    inserted_collected = pd.DataFrame(
        [value for value in inserted_infos.values()], columns=columns)

    return inserted_collected


def copy_file_to_libai(inserted_collected: pd.DataFrame, name: str):

    assert name in {'garmin_fit_path', 'polar_csv_path'}

    for i, row in inserted_collected.iterrows():
        target_path = row[name]
        target_path = Path(target_path)

        libai_accel_path = row['libai_accel_path']
        libai_record = Path(libai_accel_path).parent
        shutil.copy(target_path, libai_record)
        print(f'Copy {target_path.name} into {libai_record}')


def get_match_summary(libai_accel_collected: pd.DataFrame,
                      garmin_fit_inserted: pd.DataFrame,
                      polar_csv_inserted: pd.DataFrame,
                      match_columns=MATCH_COLUMNS) -> pd.DataFrame:

    matchs = []

    for i, row in libai_accel_collected.iterrows():
        libai_tag = row['libai_tag']
        libai_accel_path = Path(row['path'])
        libai_record = libai_accel_path.parent
        libai_name = libai_record.name

        garmin_fit_part = garmin_fit_inserted[garmin_fit_inserted['libai_name']
                                              == libai_name].copy()
        polar_csv_part = polar_csv_inserted[polar_csv_inserted['libai_name'] ==
                                            libai_name].copy()

        garmin_overlap, garmin_overlap_rate, garmin_fit_path = None, None, None
        polar_overlap, polar_overlap_rate, polar_csv_path = None, None, None
        polar_tag, garmin_tag = None, None

        if not garmin_fit_part.empty:
            if len(garmin_fit_part) > 1:
                pass
            garmin_overlap = garmin_fit_part['overlap'].values[0]
            garmin_overlap_rate = garmin_fit_part['overlap_rate'].values[0]
            garmin_fit_path = garmin_fit_part['garmin_fit_path'].values[0]
            garmin_tag = int(garmin_fit_part['garmin_tag'].values[0])
        if not polar_csv_part.empty:
            if len(polar_csv_part) > 1:
                pass
            polar_overlap = polar_csv_part['overlap'].values[0]
            polar_overlap_rate = polar_csv_part['overlap_rate'].values[0]
            polar_csv_path = polar_csv_part['polar_csv_path'].values[0]
            polar_tag = int(polar_csv_part['polar_tag'].values[0])

        match_type = None
        if garmin_fit_path is not None:
            if polar_csv_path is not None:
                match_type = MatchType.VALID_RECORD.value[0]
            else:
                match_type = MatchType.NO_GARMIN.value[0]
        else:
            if polar_csv_path is not None:
                match_type = MatchType.NO_GARMIN.value[0]
            else:
                match_type = MatchType.NO_POLAR_GARMIN.value[0]
        msg = (libai_name, match_type, garmin_overlap, polar_overlap,
               garmin_overlap_rate, polar_overlap_rate, libai_tag, garmin_tag,
               polar_tag, libai_record, garmin_fit_path, polar_csv_path)
        matchs.append(msg)

    match_df = pd.DataFrame(matchs, columns=match_columns)

    match_df.sort_values(by='libai_name', inplace=True)

    return match_df


def run(libai_clean: Path, garmin_clean: Path,
        polar_clean: Path) -> pd.DataFrame:
    libai_accel_collected = collect_libai_accel_infos(libai_clean)
    garmin_fit_collected = collect_garmin_fit_infos(garmin_clean)
    polar_csv_collected = collect_polar_csv_infos(polar_clean)

    garmin_fit_inserted = insert_target_into_libai_record(
        garmin_fit_collected, libai_accel_collected, 'garmin',
        GARMIN_FIT_INSERTED_COLUMNS)

    polar_csv_inserted = insert_target_into_libai_record(
        polar_csv_collected, libai_accel_collected, 'polar',
        POLAR_CSV_INSERTED_COLUMNS)

    save_df_to_log(garmin_fit_inserted, 'garmin_fit_inserted.csv')

    save_df_to_log(polar_csv_inserted, 'polar_csv_inserted.csv')

    copy_file_to_libai(garmin_fit_inserted, 'garmin_fit_path')

    copy_file_to_libai(polar_csv_inserted, 'polar_csv_path')

    match_summarys = get_match_summary(libai_accel_collected,
                                       garmin_fit_inserted,
                                       polar_csv_inserted,
                                       match_columns=MATCH_COLUMNS)

    save_df_to_log(libai_accel_collected, 'libai_accel_collected.csv')
    save_df_to_log(garmin_fit_collected, 'garmin_fit_collected.csv')
    save_df_to_log(polar_csv_collected, 'polar_csv_collected.csv')
    save_df_to_log(match_summarys, 'match_summarys.csv')

    return match_summarys


@click.command()
@click.argument('libai-cleaned')
@click.option('-g', '--garmin-cleaned', required=True, type=str)
@click.option('-p', '--polar-cleaned', required=True, type=str)
def main(libai_cleaned, garmin_cleaned, polar_cleaned):
    libai_cleaned = Path(libai_cleaned)
    garmin_cleaned = Path(garmin_cleaned)
    polar_cleaned = Path(polar_cleaned)

    run(libai_cleaned, garmin_cleaned, polar_cleaned)


if __name__ == "__main__":
    main()
