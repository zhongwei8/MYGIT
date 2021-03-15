'''
Author       :
Date         : 2021-03-10 11:29:14
LastEditors  : Please set LastEditors
LastEditTime : 2021-03-10 16:22:29
FilePath     : /my_github/STASH/indoor_outdoor_nmea_preprocess_standard.py
'''
import click
import pandas as pd
from pathlib import Path

NMEA_FILE_PATTERN = '*-nmea.csv'
HEADER_LINES_TO_SKIP = 2
NMEA_FILE_NEW_HEADER_NAMES = [
    'CurrentTimeMillis', 'EventTimestamp(ms)', 'NMEA', 'IndoorOutdoor'
]
SAVED_DIR = Path('~/data/samples')
LINES_THRESHOLD = 10


def extract_standard_nmea_file(record_path: Path, indoor_outdoor_status=0):
    record_path = Path(record_path)

    sport_field = record_path.name.split('_')[-1]

    nmea_file_path = [path for path in record_path.glob(NMEA_FILE_PATTERN)][0]

    with open(nmea_file_path, 'r') as f:
        lines = f.readlines()
        if len(lines) < LINES_THRESHOLD:
            print(
                f'Skip, lines of {nmea_file_path.name} < {LINES_THRESHOLD}\n')
            return
        data = []
        for line in lines[HEADER_LINES_TO_SKIP:-1]:
            line = line.rstrip('\n')
            metas = line.split(',')
            if len(metas) <= 3:
                continue
            ts, ets = metas[0], metas[1]
            try:
                ts = int(ts)
                ets = int(ets)
            except ValueError:
                print(f'Skip, unvalid ({ts, ets}) in {nmea_file_path.name}')
                return
            nmea = ','.join(metas[2:])
            data.append([ts, ets, nmea, indoor_outdoor_status])
    nmea_df = pd.DataFrame(data, columns=NMEA_FILE_NEW_HEADER_NAMES)

    standard_nmea_name = sport_field + '-' + record_path.name + '.csv'

    standard_nmea_path = SAVED_DIR / standard_nmea_name

    nmea_df.to_csv(standard_nmea_path, index=False)

    # print(f'nmea_df = \n{nmea_df.head()}')
    print(f'Saved: {standard_nmea_path}\n')


@click.command()
@click.argument('record_dir')
def main(record_dir):
    record_dir = Path(record_dir)

    records = [record for record in record_dir.iterdir() if record.is_dir()]

    for i, record in enumerate(records[:]):
        print(f'Processing {i + 1} / {len(records)}: {record.name}')
        extract_standard_nmea_file(record)


if __name__ == "__main__":
    main()
