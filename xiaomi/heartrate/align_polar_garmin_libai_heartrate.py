from datetime import datetime, timedelta
from pathlib import Path

import click
import fitparse
from matplotlib import ticker
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

UTC_OFFSET = timedelta(hours=8)
GARMIN_FIT_COLUMNS = [
    'cadence', 'distance', 'enhanced_altitude', 'enhanced_speed',
    'fractional_cadence', 'heart_rate', 'position_lat', 'position_long',
    'temperature', 'timestamp', 'unknown_135', 'unknown_136', 'unknown_87'
]
LIBAI_HEARTRATE_SUFFIX = 'heartrate-xHZ.csv'
POLAR_PATTERN_IN_LIBAI = 'polar*.csv'
GARMIN_PATTERN_IN_LIBAI = 'garmin*.fit'

LIBAI_FILE_PREFIX = 'libai_'
GARMIN_FIT_PREFIX = 'garmin_'
POLAR_CSV_PREFIX = 'polar_'

LIBAI_HEARTRATE_HEADER_LINE = 1
GARMIN_HEARTRATE_HEADER_LINE = 2


@ticker.FuncFormatter
def func(x, pos) -> None:
    return datetime.fromtimestamp(int(x)).time()


def save_garmin_df(garmin_df, garmin_fit_path: Path):
    garmin_fit_path = Path(garmin_fit_path)

    garmin_save_dir = Path('./src/py/data')
    garmin_save_dir.mkdir(parents=True, exist_ok=True)

    garmin_save_name = garmin_fit_path.with_suffix('.csv').name
    garmin_save_path = garmin_save_dir / garmin_save_name
    garmin_df.to_csv(garmin_save_path, index=False)

    print(f'Saved: {garmin_save_path}')


def save_garmin_df_nearly(garmin_df, garmin_fit_path: Path):
    garmin_fit_path = Path(garmin_fit_path)

    garmin_csv_path = garmin_fit_path.with_suffix('.csv')
    garmin_df.to_csv(garmin_csv_path, index=False)

    print(f'Saved: {garmin_csv_path}')


def parse_garmin_fit(garmin_fit_path: str, is_save=False) -> pd.DataFrame:
    assert garmin_fit_path is not None
    assert Path(garmin_fit_path).exists()

    garmin_fit_path = str(garmin_fit_path)

    garmin_fit_file = fitparse.FitFile(garmin_fit_path)

    records = []
    for i, fields in enumerate(garmin_fit_file.get_messages('record')):
        timestamp, heartrate = None, None
        for data in fields:
            name, value = data.name, data.value
            if name == 'timestamp':
                value += UTC_OFFSET
                value = value.timestamp()
                timestamp = value
            elif name == 'heart_rate':
                heartrate = value
        if timestamp is not None and heartrate is not None:
            records.append((timestamp, heartrate))

    garmin_df = pd.DataFrame(records, columns=['timestamp', 'heartrate'])

    if is_save:
        save_garmin_df_nearly(garmin_df, garmin_fit_path)

    return garmin_df


def plot_garmin_fit_heartrate(timestamps: np.ndarray,
                              heartrates: np.ndarray) -> None:
    print(f'timestamps = {timestamps[:5]}')
    plt.figure(figsize=(12, 5))
    plt.plot(timestamps, heartrates)
    plt.gca().xaxis.set_major_formatter(func)

    plt.show()


def get_libai_garmin_polar_heartrate_path(libai_record: Path) -> tuple:
    record_key = libai_record.name.split('-')[0]
    libai_heartrate_name = (LIBAI_FILE_PREFIX + record_key + '-' +
                            LIBAI_HEARTRATE_SUFFIX)
    libai_heartrate_path = libai_record / libai_heartrate_name

    garmin_iter = libai_record.glob(GARMIN_PATTERN_IN_LIBAI)
    polar_iter = libai_record.glob(POLAR_PATTERN_IN_LIBAI)

    garmin_heartrate_path = None
    try:
        garmin_heartrate_path = [path for path in garmin_iter][0]
    except IndexError:
        print(f'Not exists garmin heartrate file in {libai_record.name}')

    polar_heartrate_path = None
    try:
        polar_heartrate_path = [path for path in polar_iter][0]
    except IndexError:
        print(f'Not exists polar heartrate file in {libai_record.name}')

    return (libai_heartrate_path, garmin_heartrate_path, polar_heartrate_path)


def get_heartrate_from_libai(libai_heartrate_path: Path) -> np.ndarray:
    if libai_heartrate_path is None or not libai_heartrate_path.exists():
        return None

    heartrate_df = pd.read_csv(libai_heartrate_path,
                               header=LIBAI_HEARTRATE_HEADER_LINE)
    heartrate_df = heartrate_df[heartrate_df['BPM'] > 0]
    timestamps = heartrate_df['CurrentTimeMillis'].values.reshape(-1, 1) / 1e3
    heartrates = heartrate_df['BPM'].values.reshape(-1, 1)

    return np.hstack((timestamps, heartrates)).astype(np.int)


def get_heartrate_from_polar(polar_heartrate_path: Path) -> np.ndarray:
    if polar_heartrate_path is None or not polar_heartrate_path.exists():
        return None

    start_timestamp = None
    with open(str(polar_heartrate_path), 'r') as f:
        f.readline()
        secondline = f.readline()
        date_str, time_str = secondline.split(',')[2], secondline.split(',')[3]
        datetime_str = date_str + ' ' + time_str
        start_datetime = datetime.strptime(datetime_str, '%d-%m-%Y %H:%M:%S')
        start_timestamp = int(start_datetime.timestamp())

    heartrate_df = pd.read_csv(polar_heartrate_path,
                               header=GARMIN_HEARTRATE_HEADER_LINE)

    heartrate_df = heartrate_df[heartrate_df['HR (bpm)'] > 0]

    heartrates = heartrate_df[['HR (bpm)']].values
    timestamps = np.arange(len(heartrates)).reshape((-1, 1)) + start_timestamp

    return np.hstack((timestamps, heartrates)).astype(np.int)


def get_heartrate_from_garmin(garmin_heartrate_path: Path) -> np.ndarray:
    if garmin_heartrate_path is None or not garmin_heartrate_path.exists():
        return None

    garmin_df = parse_garmin_fit(garmin_heartrate_path)
    garmin_df = garmin_df[garmin_df['heartrate'] > 0]

    return garmin_df[['timestamp', 'heartrate']].values.astype(np.int)


def plot_libai_garmin_polar_heartrates(libai_heartrates: np.ndarray,
                                       libai_heartrates_adjusted: np.ndarray,
                                       garmin_heartrates: np.ndarray,
                                       garmin_heartrates_adjusted: np.ndarray,
                                       polar_heartrates: np.ndarray,
                                       libai_name) -> None:
    _, axes = plt.subplots(2, 1, figsize=(18, 10), sharex=True, sharey=True)
    if polar_heartrates is not None:
        axes[0].plot(polar_heartrates[:, 0],
                     polar_heartrates[:, 1],
                     marker='o',
                     color='black',
                     label='polar',
                     markersize=2,
                     linewidth=0.5)
        axes[1].plot(polar_heartrates[:, 0],
                     polar_heartrates[:, 1],
                     marker='o',
                     color='black',
                     label='polar',
                     markersize=2,
                     linewidth=0.5)
    if libai_heartrates is not None:
        axes[0].plot(libai_heartrates[:, 0],
                     libai_heartrates[:, 1],
                     marker='o',
                     color='red',
                     label='LifeQ',
                     markersize=2,
                     linewidth=0.5)
        axes[1].plot(libai_heartrates_adjusted[:, 0],
                     libai_heartrates_adjusted[:, 1],
                     marker='o',
                     color='red',
                     label='LifeQ_adjusted',
                     markersize=2,
                     linewidth=0.5)
    if garmin_heartrates is not None:
        axes[0].plot(garmin_heartrates[:, 0],
                     garmin_heartrates[:, 1],
                     marker='o',
                     color='green',
                     label='garmin',
                     markersize=2,
                     linewidth=0.5)
        axes[1].plot(garmin_heartrates_adjusted[:, 0],
                     garmin_heartrates_adjusted[:, 1],
                     marker='o',
                     color='green',
                     label='garmin_adjusted',
                     markersize=2,
                     linewidth=0.5)

    for ax in axes:
        ax.set_title(libai_name)
        ax.xaxis.set_major_formatter(func)
        ax.legend()
        ax.grid()
    plt.show()
    return


def get_point_wise_error(polar_heartrates: np.ndarray,
                         target_heartrates: np.ndarray) -> tuple:
    timestamp_set = set(polar_heartrates[:, 0]) & set(target_heartrates[:, 0])

    polar_mask = [False] * len(polar_heartrates)
    timestamp_visited = set()
    for i, timestamp in enumerate(polar_heartrates[:, 0]):
        if timestamp in timestamp_set and timestamp not in timestamp_visited:
            polar_mask[i] = True
            timestamp_visited.add(timestamp)

    target_mask = [False] * len(target_heartrates)
    timestamp_visited.clear()
    for i, timestamp in enumerate(target_heartrates[:, 0]):
        if timestamp in timestamp_set and timestamp not in timestamp_visited:
            target_mask[i] = True
            timestamp_visited.add(timestamp)

    polar_heartrate = polar_heartrates[polar_mask][:, 1]
    target_heartrate = target_heartrates[target_mask][:, 1]

    error = np.abs(target_heartrate - polar_heartrate)
    error_mean = error.mean()
    error_max = error.max()
    error_20 = np.percentile(error, 20)
    error_50 = np.percentile(error, 50)
    error_80 = np.percentile(error, 80)

    return (error_mean, error_20, error_50, error_80, error_max)


def compare_polar_libai_garmin_heartrate(libai_heartrates,
                                         libai_heartrates_adjusted,
                                         garmin_heartrates,
                                         garmin_heartrates_adjusted,
                                         polar_heartrates) -> tuple:
    if polar_heartrates is None:
        return None

    (error_libai, error_garmin, error_libai_adjusted,
     error_garmin_adjusted) = (None, None, None, None)

    if libai_heartrates is not None:
        error_libai = get_point_wise_error(polar_heartrates, libai_heartrates)
        error_libai_adjusted = get_point_wise_error(polar_heartrates,
                                                    libai_heartrates_adjusted)
        print(f'error_libai, error_libai_adjusted = '
              f'{error_libai}, {error_libai_adjusted}')
    if garmin_heartrates is not None:
        error_garmin = get_point_wise_error(polar_heartrates,
                                            garmin_heartrates)
        error_garmin_adjusted = get_point_wise_error(
            polar_heartrates, garmin_heartrates_adjusted)

        print(f'error_garmin, error_garmin_adjusted = '
              f'{error_garmin}, {error_garmin_adjusted}')

    return (error_libai, error_garmin, error_libai_adjusted,
            error_garmin_adjusted)


def get_best_delay(polar_heartrates: np.ndarray,
                   target_heartrates: np.ndarray) -> tuple:
    delay_length = 20

    best_delay = 0
    min_mean_error = np.inf
    for i in range(-delay_length, delay_length + 1, 1):
        target_heartrates_adjust = target_heartrates.copy()
        target_heartrates_adjust[:, 0] += i
        point_wise_error = get_point_wise_error(polar_heartrates,
                                                target_heartrates_adjust)
        if point_wise_error[0] < min_mean_error:
            best_delay = i
            min_mean_error = point_wise_error[0]
            # print(f'best_delay, error = {best_delay}, {point_wise_error}')
    return (best_delay, min_mean_error)


def adjust_garmin_libai_heartrates(polar_heartrates, garmin_heartrates,
                                   libai_heartrates) -> tuple:
    garmin_delay = get_best_delay(polar_heartrates, garmin_heartrates)

    libai_delay = get_best_delay(polar_heartrates, libai_heartrates)

    print(f'garmin_delay = {garmin_delay}')
    print(f'libai_delay = {libai_delay}')

    garmin_heartrates_adjusted = garmin_heartrates.copy()
    garmin_heartrates_adjusted[:, 0] += garmin_delay[0]

    libai_heartrates_adjusted = libai_heartrates.copy()
    libai_heartrates_adjusted[:, 0] += libai_delay[0]

    return (garmin_heartrates_adjusted, libai_heartrates_adjusted)


def run(libai_record: str) -> None:
    libai_record = Path(libai_record)

    (libai_heartrate_path, garmin_heartrate_path, polar_heartrate_path
     ) = get_libai_garmin_polar_heartrate_path(libai_record)

    libai_heartrates = get_heartrate_from_libai(libai_heartrate_path)
    garmin_heartrates = get_heartrate_from_garmin(garmin_heartrate_path)
    polar_heartrates = get_heartrate_from_polar(polar_heartrate_path)

    (garmin_heartrates_adjusted,
     libai_heartrates_adjusted) = adjust_garmin_libai_heartrates(
         polar_heartrates, garmin_heartrates, libai_heartrates)

    plot_libai_garmin_polar_heartrates(libai_heartrates,
                                       libai_heartrates_adjusted,
                                       garmin_heartrates,
                                       garmin_heartrates_adjusted,
                                       polar_heartrates, libai_record.name)
    compare_polar_libai_garmin_heartrate(libai_heartrates,
                                         libai_heartrates_adjusted,
                                         garmin_heartrates,
                                         garmin_heartrates_adjusted,
                                         polar_heartrates)


@click.command()
@click.argument('libai-record')
def main(libai_record: str):
    run(libai_record)


if __name__ == '__main__':
    main()
