import os
from pathlib import Path
import shutil
import sys

FIG_PATH = Path('/home/mi/data/good/FIG')
SOURCE_DIR = Path(
    '/home/mi/data/new-sensor-bucket/libai/heartrate/cleaned/libai/')
TARGET_DIR = Path('/home/mi/data/good/record/')


def get_figs(fig_dir=FIG_PATH, source_dir=SOURCE_DIR):
    record_names = [path.stem for path in fig_dir.iterdir()]
    record_paths = []
    for name in record_names:
        date_str = '-'.join(name.split('_')[:3])
        record_path = source_dir / date_str / name
        record_paths.append(record_path)
    return record_paths


def copyfiles(record_paths, target_dir=TARGET_DIR):
    for record_path in record_paths:
        record_path_str = str(record_path)
        target_dir_str = str(target_dir)
        cmd = f'cp -r {record_path_str} {target_dir_str}'
        os.system(cmd)


def main():
    records = get_figs()
    copyfiles(records)


if __name__ == '__main__':
    main()
