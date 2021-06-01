'''
Author       : Tianzw
Date         : 2021-04-06 16:58:36
LastEditors  : Please set LastEditors
LastEditTime : 2021-04-07 12:18:05
FilePath     : /activity-recognition/src/py/add_event_timestamp.py
'''
from pathlib import Path

import click
import numpy as np
import pandas as pd

ACC_HEADER_NAMES = [
    'CurrentTimeMillis', 'EventTimestamp(ns)', 'AccelX', 'AccelY', 'AccelZ'
]

DELTA_NS = (1 / 25) * 1e9


def add_event_timestamp(accel_path: Path) -> pd.DataFrame:
    df = pd.read_csv(accel_path)
    df.columns = ['CurrentTimeMillis', 'AccelX', 'AccelY', 'AccelZ']
    df.loc[:, 'AccelX'] = df.loc[:, 'AccelX'] * 9.8
    df.loc[:, 'AccelY'] = df.loc[:, 'AccelY'] * 9.8
    df.loc[:, 'AccelZ'] = df.loc[:, 'AccelZ'] * 9.8
    event_timestamp = [i * DELTA_NS for i in range(len(df))]
    df['EventTimestamp(ns)'] = event_timestamp
    df['CurrentTimeMillis'] = df['CurrentTimeMillis'].astype(np.int)
    df['EventTimestamp(ns)'] = df['EventTimestamp(ns)'].astype(np.int)

    df = df[ACC_HEADER_NAMES]

    df.to_csv(accel_path.with_suffix('.log'), index=False)
    print(f'df.head() = \n{df.head()}')


@click.command()
@click.argument('data-dir')
def main(data_dir):
    data_dir = Path(data_dir)

    for file in data_dir.iterdir():
        if file.suffix == '.csv':
            add_event_timestamp(file)


if __name__ == '__main__':
    main()
