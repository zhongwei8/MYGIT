'''
Author: your name
Date: 2021-03-04 13:38:03
LastEditTime : 2021-03-10 11:28:53
LastEditors  : Please set LastEditors
Description: In User Settings Edit
FilePath     : /my_github/STASH/indoor_outdoor_nmea_preprocess.py
'''
import click
from pathlib import Path
import pandas as pd

HEADER_LINES_TO_SKIP = 2

NMEA_FILE_NEW_HEADER_NAMES = [
    'CurrentTimeMillis', 'EventTimestamp(ms)', 'NMEA', 'IndoorOutdoor'
]

NMEA_FILE_PATTERN = '*nmea.csv'


def preprocess_raw_nmea_file(raw_nmea_file_path: Path,
                             indoor_outdoor_status=0):

    with Path(raw_nmea_file_path).open('r') as f:
        lines = f.readlines()
        data = []
        for line in lines[HEADER_LINES_TO_SKIP:-1]:
            line = line.rstrip('\n')
            metas = line.split(',')
            ts = int(metas[0])
            ets = int(metas[1])
            nmea = ','.join(metas[2:])
            data.append([ts, ets, nmea, indoor_outdoor_status])
    nmea_df = pd.DataFrame(data, columns=NMEA_FILE_NEW_HEADER_NAMES)
    print(f'nmea_df = \n{nmea_df.head()}')
    return nmea_df


def save_preprocessed_nmea_df(nmea_df: pd.DataFrame, raw_nmea_file_path: Path):
    preproceed_path = Path(raw_nmea_file_path).with_name('preproceed.csv')
    nmea_df.to_csv(preproceed_path, index=False)


@click.command()
@click.argument('nmea_file')
@click.option('-s', '--indoor_outdoor_status', default=0)
def main(nmea_file, indoor_outdoor_status):
    nmea_file = Path(nmea_file)

    nmea_df = preprocess_raw_nmea_file(nmea_file, indoor_outdoor_status)
    save_preprocessed_nmea_df(nmea_df, nmea_file)


if __name__ == "__main__":
    main()
