'''
Author: your name
Date: 2021-03-06 19:42:58
LastEditTime: 2021-03-06 21:30:42
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /activity-recognition/src/py/remove_unvalid_nmea_file.py
'''

import os
from pathlib import Path

import click

NMEA_FILE_PATTERN = '*.csv'
GPGSV_PATTERN = '$GPGSV'

NMEA_FILE_HEADER_NAMES = [
    'CurrentTimeMillis', 'EventTimestamp(ms)', 'NMEA', 'IndoorOutdoor'
]


def unvalid_nmea_file(nmea_file_path: Path) -> bool:
    nmea_file_path = Path(nmea_file_path)
    with open(nmea_file_path, 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            nmea_sentence = line.split(',')[2]  # like: '"$GPGSV'
            nmea_sentence_type = nmea_sentence[1:]  # skip the " in '"$GPGSV'
            if nmea_sentence_type == GPGSV_PATTERN:
                return False
    return True


def is_unvalid_raw_nmea_file(nmea_file_path: Path) -> bool:
    nmea_file_path = Path(nmea_file_path)

    with open(nmea_file_path, 'r') as f:
        nmea_sentences = f.readlines()
        for i, nmea_sentence in enumerate(nmea_sentences):
            if i < 5:
                print(f'line {i}: {nmea_sentence}')
            nmea_fields = nmea_sentence.split(',')

            if len(nmea_fields) <= 2:
                continue

            sentence_type = nmea_fields[2]
            if sentence_type == '$GPGSV':
                print(f'Valid nmea sentence: {nmea_sentence}')
                return False

    return True


def remove_unvalid_nmea_file(nmea_dir: Path):
    nmea_file_paths = [path for path in nmea_dir.rglob(NMEA_FILE_PATTERN)]

    for i, nmea_file_path in enumerate(nmea_file_paths):
        print(
            f'Processing ({i + 1} / {len(nmea_file_paths)}): {nmea_file_path.name}'
        )
        if unvalid_nmea_file(nmea_file_path):
            os.remove(nmea_file_path)
            print('Unvalid nmea file, removed\n')
        else:
            print('Valid nmea file\n')


@click.command()
@click.argument('nmea_dir')
def main(nmea_dir):
    nmea_dir = Path(nmea_dir)
    remove_unvalid_nmea_file(nmea_dir)


if __name__ == "__main__":
    main()
