#!/usr/bin env python
# -*- coding: utf-8 -*-
# @Author: Tianzw
# @Date: 2021-03-09
# Description: clip nmea file with accel file

import click
import pandas as pd

from pathlib import Path

NMEA_FILE_COLUMNS = [
    'CurrentTimeMillis', 'EventTimestamp(ms)', 'NMEA', 'IndoorOutdoor'
]

ACCEL_FILE_SUFFIX = 'accel-52HZ.csv'
NMEA_FILE_PATTERN = '*.csv'

SOURCE_BASE = 'source_nmea'
CLIPED_BASE = 'cliped_nmea'


def read_tail(input_file: Path, tail=5):
    file_size = Path(input_file).stat().st_size
    blocksize = 1024
    data_file = open(input_file, 'r')
    if file_size > blocksize:
        maxseekpoint = (file_size // blocksize)
        data_file.seek((maxseekpoint - 1) * blocksize)
    elif file_size:
        data_file.seek(0, 0)
    lines = data_file.readlines()
    last_lines = []
    if lines:
        for line in lines[-tail:]:
            last_lines.append(line.strip())
    data_file.close()
    return last_lines


def read_head(input_file: Path, head=5):
    head_lines = []
    with Path(input_file).open('r') as f:
        for i in range(head):
            line = f.readline().strip()
            head_lines.append(line)
    return head_lines


def get_accel_file_path_from_nmea_file_path(nmea_file_path: Path, accel_dir):
    """
    nmea file path like:
        BriskWalkInDoor-2020_11_19_18_12_14_656-15133509928-xxx_BriskWalkInDoor.csv
    where 2020_11_19_18_12_14_656-15133509928 is the record key word

    accel_dir:
        that contains the corresponding nmea file
    """
    nmea_file_path = Path(nmea_file_path)
    accel_dir = Path(accel_dir)

    record_key_word = nmea_file_path.stem.split('-')[1]
    accel_file_pattern = record_key_word + '*' + ACCEL_FILE_SUFFIX
    try:
        accel_file_path = [
            path for path in accel_dir.rglob(accel_file_pattern)
        ][0]
        return accel_file_path
    except IndexError:
        print(f'accel file of {nmea_file_path.name} Not exist')

    return None


def get_timerange_from_accel_file(accel_file_path: Path) -> tuple:
    if not accel_file_path:
        print('accel_file_path = None')
        return
    accel_file_path = Path(accel_file_path)

    head_lines = read_head(accel_file_path)
    last_lines = read_tail(accel_file_path)

    head_meta_ts = head_lines[1].split(',')[0]  # skip the header
    last_meta_ts = last_lines[-1].split(',')[0]  # CurrentTimeMillis
    begin_ts, end_ts = -1, -1
    try:
        begin_ts = int(head_meta_ts)
        end_ts = int(last_meta_ts)
    except ValueError:
        print(f'Can not convert ({begin_ts}, {end_ts}) to int')
        return (begin_ts, end_ts)
    return (begin_ts, end_ts)


def clip_nmea_file_and_save(nmea_file_path: Path, timerange: tuple):

    nmea_file_path = Path(nmea_file_path)
    timestamp_low, timestamp_high = timerange[0], timerange[1]

    raw_line_cnt = 0
    cliped_lines = []
    with nmea_file_path.open('r') as f:
        raw_lines = f.readlines()
        if raw_lines is None:
            return
        raw_line_cnt = len(raw_lines)
        for raw_line in raw_lines[1:]:  # skip the header of nmea file
            timestamp = raw_line.strip().split(',')[0]  # CurrentTimeMillis
            try:
                timestamp = int(timestamp)
            except ValueError:
                return
            if timestamp < timestamp_low:
                continue
            if timestamp > timestamp_high:
                break
            cliped_lines.append(raw_line)

    cliped_line_cnt = len(cliped_lines)

    cliped_nmea_file_path = Path(
        str(nmea_file_path.resolve()).replace(SOURCE_BASE, CLIPED_BASE, 1))

    cliped_nmea_file_path.parent.mkdir(parents=True, exists_ok=True)
    cliped_lines_df = pd.DataFrame(cliped_lines, columns=NMEA_FILE_COLUMNS)
    cliped_lines_df.to_csv(cliped_nmea_file_path, index=False)
    print(f'Cliped from {raw_line_cnt} lines to {cliped_line_cnt} lines\n')


def process_file(nmea_file_path: Path, accel_dir: Path):
    accel_file_path = get_accel_file_path_from_nmea_file_path(
        nmea_file_path, accel_dir)
    if accel_file_path:
        timerange = get_timerange_from_accel_file(accel_file_path)
        clip_nmea_file_and_save(nmea_file_path, timerange)
    else:
        print(f'Skip, not found accel file of {nmea_file_path.name}\n')


@click.command()
@click.argument('nmea_path')
@click.argument('accel_dir')
def main(nmea_path, accel_dir):
    nmea_path = Path(nmea_path)
    accel_dir = Path(accel_dir)

    if nmea_path.is_file():
        process_file(nmea_path, accel_dir)
    elif nmea_path.is_dir():
        nmea_paths = [path for path in nmea_path.rglob(NMEA_FILE_PATTERN)]
        for i, nmea_path in enumerate(nmea_paths):
            print(
                f'Processing ({i + 1} / {len(nmea_paths)}): {nmea_path.name}')
            process_file(nmea_path, accel_dir)


if __name__ == "__main__":
    main()
