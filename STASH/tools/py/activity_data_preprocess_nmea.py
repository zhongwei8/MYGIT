#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Farmer Li
# @Date: 2021-01-04

import multiprocessing as mp
from pathlib import Path

import click
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

NMEA_SUFFIX = 'nmea.csv'
NMEA_DATA_DURARION_MS_MIN = 8000

HEADER_NAMES = [
    'CurrentTimeMillis', 'EventTimestamp(ms)', 'NMEA', 'IndoorOutdoor'
]
HEADER_TYPES = [int, int, str, int]
HEADER_NAMES_TYPE = dict(zip(HEADER_NAMES, HEADER_TYPES))

LOCATION_MAP = {
    'Indoor': [
        'BriskWalkInDoor', 'RuningInDoor', 'SwimmingInDoor', 'SubwayTaking',
        'EllipticalMachine', 'RowingMachine'
    ],
    'Outdoor': ['BriskWalkOutSide', 'BikingOutSide']
}
LOCATION_NAMES = ['Undefined', 'Indoor', 'Outdoor']

DATASET_TO_USE = [
    '20201117-20201204', '20201205-20201211', '20201217-20201231',
    '20210101-20210107'
]


def scenes_category(scene):
    for k, v in LOCATION_MAP.items():
        if scene in v:
            return k
    return None


def scenes_filter(scene):
    return scenes_category(scene) is not None


def get_activity_type_name_by_record_name(record_name: str):
    metas = record_name.split('-')
    return metas[7].split('_')[1]


def align_and_relabel_one_record(record_dir: Path,
                                 dst_dir: Path,
                                 indoor_outdoor_status=0,
                                 debug=False):
    nmea_file = record_dir / f'{record_dir.name}-{NMEA_SUFFIX}'
    print(f'Processing NMEA file: {nmea_file}')
    if not nmea_file.exists():
        print('File NOT EXISTS!, do nothing')
        return
    with Path(nmea_file).open('r') as f:
        lines = f.readlines()
        data = []
        # Skip the header and broken end of file
        for line in lines[1:-1]:
            line = line.rstrip('\n')
            metas = line.split(',')
            ts = int(metas[0])
            ets = int(metas[1])
            nmea = ','.join(metas[2:])
            data.append([ts, ets, nmea, indoor_outdoor_status])
        data_duration = data[-1][0] - data[0][0]
        if data_duration < NMEA_DATA_DURARION_MS_MIN:
            print(f'Data too less with {data_duration} ms, skipped')
            return
        df = pd.DataFrame(data, columns=HEADER_NAMES)

        if dst_dir is not None:
            activity_type = get_activity_type_name_by_record_name(
                record_dir.name)
            dst_file = dst_dir / f'{activity_type}-{record_dir.name}.csv'
            print(f'Saving to file: {dst_file}')
            df.to_csv(dst_file, index=False)


def align_and_relabel_datasets(data_dir: Path, save_dir: Path, dataset_names):
    datasets = [data_dir / name for name in dataset_names]
    set_num = len(datasets)
    for i, dataset in enumerate(datasets, 1):
        print(f'\nProcess dataset [{i:02d}/{set_num:02d}]: {dataset.name}')
        scenes = [
            r for r in dataset.iterdir()
            if r.is_dir() and scenes_filter(r.name)
        ]
        scene_num = len(scenes)
        dst_dir = save_dir / dataset.name
        if not dst_dir.exists():
            dst_dir.mkdir(parents=True)
        for j, scene in enumerate(scenes):
            indoor_outdoor = scenes_category(scene.name)
            indoor_outdoor_type = LOCATION_NAMES.index(indoor_outdoor)

            print(f'\nProcess scene [{j:02d}/{scene_num:02d}]: {scene.name} '
                  f'as {indoor_outdoor}')
            records = [r for r in scene.iterdir() if r.is_dir()]
            record_num = len(records)
            type_dir = dst_dir / indoor_outdoor
            if not type_dir.exists():
                type_dir.mkdir(parents=True)
            for k, record in enumerate(records, 1):
                print(f'\nProcessing record [{k:02d}/{record_num:02d}]: '
                      f'{record.name}')
                align_and_relabel_one_record(record, type_dir,
                                             indoor_outdoor_type)


@click.command()
@click.argument('data-dir')
@click.option('-s', '--save-dir')
def main(data_dir, save_dir):
    if save_dir is not None:
        save_dir = Path(save_dir)
        align_and_relabel_datasets(Path(data_dir), save_dir, DATASET_TO_USE)
    else:
        align_and_relabel_one_record(Path(data_dir), Path('./'))
        print('Must set save dir by "-s or --save-dir"')


if __name__ == "__main__":
    main()
