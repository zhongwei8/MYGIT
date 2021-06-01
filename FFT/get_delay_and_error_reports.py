from pathlib import Path

import click
import numpy as np
import pandas as pd

from utils import LibaiRecordUtils


def get_point_wise_error(polar_heartrates: np.ndarray,
                         target_heartrates: np.ndarray) -> tuple:
    error_return = (None, None, None, None, None)
    timestamp_set = set(polar_heartrates[:, 0]) & set(target_heartrates[:, 0])
    if len(timestamp_set) == 0:
        print('NO same timestamp')
        return error_return

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

    if len(error) == 0:
        print('Empty error')
        return error_return

    error_mean = error.mean()
    error_max = error.max()
    error_20 = np.percentile(error, 20)
    error_50 = np.percentile(error, 50)
    error_80 = np.percentile(error, 80)

    return (error_mean, error_20, error_50, error_80, error_max)


def get_best_delay_error(polar_heartrates: np.ndarray,
                         target_heartrates: np.ndarray) -> tuple:
    error_return = (None, None)
    if polar_heartrates is None or target_heartrates is None:
        return error_return

    delay_length = 20

    best_delay = 0
    min_mean_error = np.inf
    for i in range(-delay_length, delay_length + 1, 1):
        target_heartrates_adjust = target_heartrates.copy()
        target_heartrates_adjust[:, 0] -= i
        point_wise_error = get_point_wise_error(polar_heartrates,
                                                target_heartrates_adjust)
        if point_wise_error is None or point_wise_error[0] is None:
            continue

        if point_wise_error[0] < min_mean_error:
            best_delay = i
            min_mean_error = point_wise_error[0]

    if min_mean_error == np.inf:
        return error_return

    return (best_delay, min_mean_error)


def get_delay_and_error_report(libai_record: Path):
    libai_record = Path(libai_record)

    error_return = (libai_record.name, None, None, None, None, None, None)

    libai_record_utils = LibaiRecordUtils(libai_record)

    polar_heartrates = libai_record_utils.get_polar_heartrates()

    if polar_heartrates is None:
        return error_return

    lifeq_heartrates = libai_record_utils.get_lifeq_heartrates()

    lifeq_error = None
    lifeq_best_delay = None
    lifeq_error_min = None
    if lifeq_heartrates is not None:
        lifeq_point_wise_error = get_point_wise_error(polar_heartrates,
                                                      lifeq_heartrates)
        lifeq_error = lifeq_point_wise_error[0]

        lifeq_best_delay, lifeq_error_min = get_best_delay_error(
            polar_heartrates, lifeq_heartrates)

    garmin_heartrates = libai_record_utils.get_garmin_heartrates()
    garmin_error = None
    garmin_best_delay = None
    garmin_error_min = None
    if garmin_heartrates is not None:
        garmin_point_wise_error = get_point_wise_error(polar_heartrates,
                                                       garmin_heartrates)
        garmin_error = garmin_point_wise_error[0]

        garmin_best_delay, garmin_error_min = get_best_delay_error(
            polar_heartrates, garmin_heartrates)

    report = (libai_record.name, lifeq_error, lifeq_best_delay,
              lifeq_error_min, garmin_error, garmin_best_delay,
              garmin_error_min)
    return report


def get_delay_and_error_reports(libai_record_dir: Path) -> pd.DataFrame:
    libai_record_dir = Path(libai_record_dir)

    libai_records = [
        libai_record for libai_record in libai_record_dir.iterdir()
    ]

    reports = []
    for i, libai_record in enumerate(libai_records):
        print(f'Processing {i + 1} / {len(libai_records)}: '
              f'{libai_record.name}')
        report = get_delay_and_error_report(libai_record)
        reports.append(report)

    report_columns = [
        'libai_record', 'lifeq_error', 'lifeq_best_delay', 'lifeq_error_min',
        'garmin_error', 'garmin_best_delay', 'garmin_error_min'
    ]
    report_df = pd.DataFrame(reports, columns=report_columns)
    return report_df


def run(libai_path: str, is_dir: bool):
    libai_path = Path(libai_path)

    if is_dir:
        report_df = get_delay_and_error_reports(libai_path)
        report_path = Path(__file__).parent / (libai_path.name +
                                               '_delay_reports.csv')

        print(f'{report_df.iloc[:, 1:].abs().mean()}')
        report_df.to_csv(report_path, index=False)
        print(f'Saved: {report_path.absolute()}')

    else:
        report = get_delay_and_error_report(libai_path)
        print(f'report = {report}')


@click.command()
@click.argument('libai-path')
@click.option('-d', '--is-dir', is_flag=True)
def main(libai_path: str, is_dir: bool):
    run(libai_path, is_dir)


if __name__ == '__main__':
    main()
