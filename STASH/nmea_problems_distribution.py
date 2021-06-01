'''
Author: your name
Date: 2021-03-09 10:35:58
LastEditTime: 2021-03-09 16:11:11
LastEditors: your name
Description: In User Settings Edit
FilePath: /my_github/STASH/nmea_problems_distribution.py
'''
import click
from pathlib import Path

from enum import IntEnum, unique

NMEA_FILE_LINES_LEAST = 2

NMEA_FILE_PATTERN = '*nmea.csv'


@unique
class NmeaFileProblemType(IntEnum):
    NoNmeaSignal = 0  # 没有 nmea 信号，可直接判断
    NoGpgsvSentence = 1  # 没有 GPGSV 信号，延后判断
    EmptyGpgsvSentence = 2  #
    EmptySnr = 3
    ZeroSnr = 4
    NormalNmea = 5


def get_nmea_file_problem_type(nmea_file_path: Path) -> str:
    nmea_file_path = Path(nmea_file_path)
    is_exists_gpgsv = False
    is_empty_gpgsv = True
    is_empty_snr = True
    is_zero_snr = False
    NormalNmea = True

    with nmea_file_path.open('r') as f:
        lines = f.readlines()
        if len(lines) <= NMEA_FILE_LINES_LEAST:
            return NmeaFileProblemType.NoNmeaSignal
        for line in lines:
            fields = line.strip().split(',')
            if len(fields) < 3 or fields[2] != '$GPGSV':
                continue
            is_exists_gpgsv = True

            if len(fields) <= 7:
                continue
            is_empty_gpgsv = False

            if len(fields) <= 9:
                continue

            for snr in fields[9:-1:4]:
                if snr == '':
                    continue
                is_empty_snr = False

                if int(snr) > 0:
                    return NmeaFileProblemType.NormalNmea

                if snr.isdigits() and int(snr) == 0:
                    is_zero_snr = True

    if is_exists_gpgsv == False:
        return NmeaFileProblemType.NoGpgsvSentence
    elif is_empty_gpgsv == True:
        return NmeaFileProblemType.EmptyGpgsvSentence
    elif is_empty_snr == True:
        return NmeaFileProblemType.EmptySnr
    elif is_zero_snr == True:
        return NmeaFileProblemType.ZeroSnr

    return NmeaFileProblemType.NormalNmea


@click.command()
@click.argument('nmea_path')
def main(nmea_path: Path):
    nmea_path = Path(nmea_path)

    if nmea_path.is_file():
        problem_type = get_nmea_file_problem_type(nmea_path)
        print(f'problem_type = {problem_type}')
    elif nmea_path.is_dir():
        problem_types = [0] * 6
        nmea_file_paths = [
            nmea_file for nmea_file in nmea_path.rglob(NMEA_FILE_PATTERN)
        ]
        for i, nmea_file_path in enumerate(nmea_file_paths):
            print(
                f'Processing ({i + 1} / {len(nmea_file_paths)}): {nmea_file_path.name}'
            )
            problem_type = get_nmea_file_problem_type(nmea_file_path)
            print(f'problem_type = {problem_type}\n')
            problem_types[problem_type] += 1
        print(f'problem_types: {problem_types}')


if __name__ == "__main__":
    main()
