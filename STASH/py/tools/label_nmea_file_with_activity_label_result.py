#!/usr/bin/env python
# -*-coding: utf-8 -*-
# @Author: Tianzw
# @Date: 2021-03-09
# Description: label nmea file with activity label result

import click
from pathlib import Path
import pandas as pd

ACTIVITY_LABEL_FILE_SUFFIX = 'label-result.csv'
ACCEL_FILE_SUFFIX = 'accel-52HZ.csv'

ACCEL_FILE_HEADER_NAMES = [
    'CurrentTimeMillis', 'EventTimestamp(ns)', 'NMEA', 'IndoorOutdoor'
]

NMEA_FILE_HEADER_NAMES = [
    'CurrentTimeMillis', 'EventTimestamp(ms)', 'NMEA', 'IndoorOutdoor'
]

UNKNOW, INDOOR, OUTDOOR = 0, 1, 2

ACTIVITY_LABEL_TO_INDOOR_OUTDOOR_LABEL = {
    0: UNKNOW,
    1: UNKNOW,
    2: UNKNOW,
    3: UNKNOW,
    4: INDOOR,
    5: OUTDOOR,
    6: INDOOR,
    7: OUTDOOR,
    8: INDOOR,
    9: OUTDOOR,
    10: OUTDOOR,
    11: OUTDOOR,
    12: INDOOR,
    13: OUTDOOR,
    14: INDOOR,
    15: INDOOR,
    16: INDOOR,
    17: INDOOR,
    18: UNKNOW,
    19: UNKNOW,
    20: INDOOR,
    21: INDOOR,
    22: INDOOR,
    23: INDOOR,
    24: INDOOR,
    25: UNKNOW,
    26: UNKNOW,
    27: UNKNOW,
}


# Find activity label result file with nmea file path from accel dir
def nmea_file_to_label_result_file_accel_file(nmea_file: Path,
                                              label_result_dir: Path,
                                              accel_dir: Path) -> tuple:
    nmea_file = Path(nmea_file)
    label_result_dir = Path(label_result_dir)
    accel_dir = Path(accel_dir)

    record_key_word = nmea_file.stem.split('-')[1]
    label_result_file_pattern = record_key_word + '*'
    label_result_file_pattern += ACTIVITY_LABEL_FILE_SUFFIX
    accel_file_pattern = record_key_word + '*' + ACCEL_FILE_SUFFIX

    try:
        label_result_file = [
            path for path in label_result_dir.rglob(label_result_file_pattern)
        ][0]
        accel_file = [path for path in accel_dir.rglob(accel_file_pattern)][0]
        print(f'Found label result file: {label_result_file.name}')
        print(f'Found accel file: {accel_file.name}')
        return label_result_file, accel_file
    except IndexError:
        print(f'label result file or accel file NOT exist')
    return (None, None)


# read label result from label_result_file as format:
#   [(activity_label, begin_EventTimestamp(ns), end_EventTimestamp(ns))]
def read_label_result_file(label_result_file: Path) -> list:
    label_result_file = Path(label_result_file)

    activity_labels = []

    with label_result_file.open('r') as f:
        lines = f.readlines()
        if not lines:
            return activity_labels
        for line in lines:
            fields = line.strip().split('_')  # read as str
            try:
                activity_label, begin_ns, end_ns = int(fields[0]), int(
                    fields[1]), int(fields[2])
            except ValueError:
                print(
                    f'Illegal activity_label: {activity_label}, {begin_ns}, {end_ns}'
                )
                continue
            activity_labels.append((activity_label, begin_ns, end_ns))

    return activity_labels


# Firstly, convert EventTimestamp(ns) to CurrentTimeMillis_ms
# So, the accel file of nmea file is needed.
# Secondly, convert activity label to indoor_outdoor_status label
# with ACTIVITY_LABEL_TO_INDOOR_OUTDOOR_LABEL
def activity_labels_to_indoor_outdoor_labels(activity_labels: list,
                                             accel_file: Path) -> list:
    accel_file = Path(accel_file)

    accel_df = pd.read_csv(accel_file)

    event_ts_ns = accel_df['EventTimestamp(ns)'].values
    current_ts_ms = accel_df['CurrentTimeMillis'].values

    event_to_current = dict(zip(event_ts_ns, current_ts_ms))

    indoor_outdoor_labels = []
    for activity_label, begin_ns, end_ns in activity_labels:
        indoor_outdoor_label = ACTIVITY_LABEL_TO_INDOOR_OUTDOOR_LABEL.get(
            activity_label, UNKNOW)
        begin_ms, end_ms = event_to_current[begin_ns], event_to_current[end_ns]
        indoor_outdoor_labels.append((indoor_outdoor_label, begin_ms, end_ms))

    return indoor_outdoor_labels


def label_nmea_file_with_labels(nmea_file: Path, indoor_outdoor_labels: list):
    nmea_file = Path(nmea_file)

    nmea_df = pd.read_csv(nmea_file)
    nmea_df['IndoorOutdoor'] = UNKNOW

    for indoor_outdoor_label, begin_ms, end_ms in indoor_outdoor_labels:
        flags = (nmea_df['EventTimestamp(ms)'] >=
                 begin_ms) & (nmea_df['EventTimestamp(ms)'] <= end_ms)
        nmea_df.loc[flags, 'IndoorOutdoor'] = indoor_outdoor_label

    nmea_df[NMEA_FILE_HEADER_NAMES].to_csv(nmea_file, index=False)
    print(f'{nmea_file.name} labeled succeed with indoor outdoor labels\n')


def process_file(nmea_file: Path, label_result_dir: Path, accel_dir: Path):
    nmea_file = Path(nmea_file)
    label_result_dir = Path(label_result_dir)
    accel_dir = Path(accel_dir)

    label_result_file, accel_file = nmea_file_to_label_result_file_accel_file(
        nmea_file, label_result_dir, accel_dir)

    if label_result_file is None or accel_file is None:
        print(f'Failed to label {nmea_file.name}, ',
              'NO label result file or accel file\n')
        return

    activity_labels = read_label_result_file(label_result_file)
    print(f'activity_labels = {activity_labels}')
    indoor_outdoor_labels = activity_labels_to_indoor_outdoor_labels(
        activity_labels, accel_file)
    print(f'indoor_outdoor_labels = {indoor_outdoor_labels}')
    label_nmea_file_with_labels(nmea_file, indoor_outdoor_labels)


@click.command()
@click.argument('nmea-path')
@click.argument('label-result-dir')
@click.option('--accel-dir', default=None)
def main(nmea_path, label_result_dir, accel_dir):
    nmea_path = Path(nmea_path)
    label_result_dir = Path(label_result_dir)
    # accel_dir is label_result_dir by default
    accel_dir = label_result_dir if accel_dir is None else Path(accel_dir)

    if nmea_path.is_file():
        process_file(nmea_path, label_result_dir, accel_dir)
    elif nmea_path.is_dir():
        nmea_files = [file for file in nmea_path.rglob('*.csv')]
        for i, nmea_file in enumerate(nmea_files):
            print(
                f'Processing ({i + 1} / {len(nmea_files)}): {nmea_file.name}')
            process_file(nmea_file, label_result_dir, accel_dir)


if __name__ == "__main__":
    main()
