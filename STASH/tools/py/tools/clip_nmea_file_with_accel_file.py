from multiprocessing import Pool, cpu_count
from pathlib import Path

import click
import pandas as pd

NMEA_FILE_SUFFIX = '*.csv'

NMEA_CSV_COLUMNS = [
    'CurrentTimeMillis', 'EventTimestamp(ms)', 'NMEA', 'IndoorOutdoor'
]

NMEA_CLEANED_DIR_NAME = 'nmea_cleaned'


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


def nmea_file_path_to_accel_file_path(nmea_file_path: Path, accel_dir: Path):
    nmea_file_path = Path(nmea_file_path)
    accel_dir = Path(accel_dir)

    sport = nmea_file_path.name.split('-')[0]

    for accel_dataset in accel_dir.iterdir():
        accel_file_path = accel_dataset / sport / nmea_file_path.name
        if accel_file_path.exists():
            return accel_file_path

    return None


def get_timerange_from_accel_file_path(accel_file_path: Path) -> tuple:
    begin_ts, end_ts = -1, -1

    if not accel_file_path:
        print('accel_file_path = None')
        return (begin_ts, end_ts)

    accel_file_path = Path(accel_file_path)

    if not accel_file_path.exists():
        print(f'Not exists: {accel_file_path.name}')
        return (begin_ts, end_ts)

    head_lines = read_head(accel_file_path)
    last_lines = read_tail(accel_file_path)

    head_meta_ts = head_lines[1].split(',')[0]  # skip the header
    last_meta_ts = last_lines[-1].split(',')[0]  # CurrentTimeMillis
    try:
        begin_ts = int(head_meta_ts)
        end_ts = int(last_meta_ts)
    except ValueError:
        print(f'Can not convert ({begin_ts}, {end_ts}) to int')
        return (begin_ts, end_ts)

    return (begin_ts, end_ts)


def clip_nmea_file(nmea_file_path: Path, timerange: tuple) -> pd.DataFrame:
    nmea_file_path = Path(nmea_file_path)

    nmea_file_df = pd.read_csv(nmea_file_path)

    timestamp_low, timestamp_high = timerange[0], timerange[1]

    flags = (nmea_file_df['EventTimestamp(ms)'] >= timestamp_low) & (
        nmea_file_df['EventTimestamp(ms)'] <= timestamp_high)

    return nmea_file_df.loc[flags, :]


def save_cliped_nmea_df(cliped_nmea_df: pd.DataFrame, nmea_file_path: Path,
                        nmea_cleaned_dir: Path):
    cliped_nmea_file_name = Path(nmea_file_path).name
    cliped_nmea_file_path = Path(nmea_cleaned_dir) / cliped_nmea_file_name
    cliped_nmea_df.to_csv(cliped_nmea_file_path, index=False)
    print(f'Saved: {cliped_nmea_file_path}')


def process_one_nmea_file(nmea_file_path: Path,
                          accel_dir: Path,
                          nmea_cleaned_dir: Path,
                          job_idx=1,
                          job_num=1):
    accel_file_path = nmea_file_path_to_accel_file_path(
        nmea_file_path, accel_dir)

    if not accel_file_path:
        print(f'Not exist: {accel_file_path}\n')
        return

    timerange = get_timerange_from_accel_file_path(accel_file_path)

    if timerange == (-1, -1):
        print(f'{accel_file_path.name} without legal timarange')
        return

    cliped_nmea_df = clip_nmea_file(nmea_file_path, timerange)
    save_cliped_nmea_df(cliped_nmea_df, nmea_file_path, nmea_cleaned_dir)
    print(f'Processed ({job_idx} / {job_num}): {nmea_file_path}\n')


@click.command()
@click.argument('nmea-raw-dir')
@click.argument('accel-dir')
def main(nmea_raw_dir: Path, accel_dir: Path):
    nmea_raw_dir = Path(nmea_raw_dir)
    accel_dir = Path(accel_dir)

    if not nmea_raw_dir.exists():
        print(f'No nmea_raw_dir directory')
    if not accel_dir.exists():
        print(f'No accel_dir directory!')
        return

    nmea_cleaned_dir = nmea_raw_dir.with_name(NMEA_CLEANED_DIR_NAME)
    nmea_cleaned_dir.mkdir(parents=True, exist_ok=True)

    nmea_file_paths = [path for path in nmea_raw_dir.rglob(NMEA_FILE_SUFFIX)]
    p = Pool(cpu_count())
    for i, nmea_file_path in enumerate(nmea_file_paths):
        p.apply_async(process_one_nmea_file,
                      args=(nmea_file_path, accel_dir, nmea_cleaned_dir, i + 1,
                            len(nmea_file_paths)))
    p.close()
    p.join()


if __name__ == '__main__':
    main()
