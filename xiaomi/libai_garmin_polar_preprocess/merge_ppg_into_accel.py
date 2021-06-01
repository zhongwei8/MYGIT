from pathlib import Path

import click
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ACCEL_COLUMNS = [
    'CurrentTimeMillis', 'EventTimestamp(ns)', 'accel_x', 'accel_y', 'accel_z'
]
PPG_COLUMNS = [
    'CurrentTimeMillis', 'EventTimestamp(ns)', 'ch1', 'ch2', 'touch'
]
ACCEL_PPG_MATCHED_COLUMNS = ACCEL_COLUMNS + PPG_COLUMNS[2:]


class LibaiRecordUtils:
    def __init__(self,
                 libai_record,
                 libai_prefix='libai_',
                 accel_suffix='-accel-52HZ.csv',
                 ppg_suffix='-ppg-100HZ.csv',
                 accel_ppg_merged_suffix='-accel-ppg-merged-52HZ.csv',
                 accel_header_line=1,
                 ppg_header_line=1):
        self._libai_record = Path(libai_record)
        self._record_key = self._libai_record.name.split('-')[0]
        self._libai_prefix = libai_prefix
        self._accel_suffix = accel_suffix
        self._ppg_suffix = ppg_suffix
        self._accel_ppg_merged_suffix = accel_ppg_merged_suffix
        self._accel_header_line = accel_header_line
        self._ppg_header_line = 1

    def _get_accel_path(self) -> Path:
        record_key = self._record_key
        libai_prefix = self._libai_prefix
        accel_suffix = self._accel_suffix
        accel_name = libai_prefix + record_key + accel_suffix
        accel_path = self._libai_record / accel_name
        return accel_path

    def _get_ppg_path(self) -> Path:
        record_key = self._record_key
        libai_prefix = self._libai_prefix
        ppg_suffix = self._ppg_suffix
        ppg_name = libai_prefix + record_key + ppg_suffix
        ppg_path = self._libai_record / ppg_name
        return ppg_path

    def get_accel_ppg_merged_path(self) -> Path:
        record_key = self._record_key
        libai_prefix = self._libai_prefix
        accel_ppg_merged_suffix = self._accel_ppg_merged_suffix
        accel_ppg_merged_name = libai_prefix + record_key + accel_ppg_merged_suffix
        accel_ppg_merged_path = self._libai_record / accel_ppg_merged_name
        return accel_ppg_merged_path

    def get_accel_values(self) -> np.ndarray:
        accel_path = self._get_accel_path()

        if not accel_path.exists():
            print(f'No accel file in {self._libai_record.name}')
            return None

        accel_header_line = self._accel_header_line
        accel_df = pd.read_csv(accel_path, header=accel_header_line)
        accel_values = accel_df.values

        return accel_values

    def get_ppg_values(self) -> np.ndarray:
        ppg_path = self._get_ppg_path()

        if not ppg_path.exists():
            print(f'No ppg file in {self._libai_record.name}')
            return None

        ppg_header_line = self._ppg_header_line
        ppg_df = pd.read_csv(ppg_path, header=ppg_header_line)
        ppg_values = ppg_df.values.astype(np.int)
        return ppg_values


def get_stable_base_index(ns_values, freq_expected, tolerance_rate=1.2) -> int:
    period_expected = 1.0 / freq_expected * 1e9  # ns
    period_tolerance = tolerance_rate * period_expected
    base_index = 0
    period = None
    for i in range(1, len(ns_values)):
        period = ns_values[i] - ns_values[i - 1]
        if period < period_tolerance and period > 0:
            base_index = i - 1
            break

    print('base_index, period(ms), period_expected(ms) = '
          f'{base_index}, {period / 1e6} {period_expected / 1e6}')

    return base_index


def check_matched(accel_matched_df: pd.DataFrame,
                  ppg_matched_df: pd.DataFrame) -> None:
    ms_distance = accel_matched_df.iloc[:, 0] - ppg_matched_df.iloc[:, 0]
    ns_distance = accel_matched_df.iloc[:, 1] - ppg_matched_df.iloc[:, 1]

    ms_distance_max = ms_distance.max().astype(np.int)
    ns_distance_max = ns_distance.max().astype(np.int)
    ms_distance_mean = ms_distance.mean().astype(np.int)
    ns_distance_mean = ns_distance.mean().astype(np.int)

    print('ms_distance_max, ms_distance_mean = '
          f'{ms_distance_max}, {ms_distance_mean}')
    print('ns_distance_max, ns_distance_mean = '
          f'{ns_distance_max}, {ns_distance_mean}')

    plt.figure(figsize=(12, 6))
    plt.plot(ns_distance / 1e6, label='time diff(ms)', marker='o')
    plt.legend()
    plt.figure(figsize=(12, 6))
    plt.plot(ms_distance)
    plt.show()


def rebase_event_timestamp_ns(values: np.ndarray,
                              freq_expected,
                              tolerance_rate=1.2) -> np.ndarray:
    ns_values = values[:, 1]  # EventTimestamp(ns)
    ms_values = values[:, 0]  # CurrentTimeMillis
    ns_base_index = get_stable_base_index(ns_values, freq_expected,
                                          tolerance_rate)
    ns_base = ns_values[ns_base_index]
    ms_base = ms_values[ns_base_index]
    ns_values -= ns_base
    ns_values += int(ms_base * 1e6)
    return values[ns_base_index:]


def merge_ppg_into_accel(accel_values,
                         ppg_values,
                         match_freq,
                         is_check_matched=False) -> pd.DataFrame:
    match_distance_tolerance = int((1.0 / match_freq) * 1e9)  # unit: ns

    accel_nss = accel_values[:, 1]
    ppg_nss = ppg_values[:, 1]

    accel_matched_index = np.zeros(accel_values.shape[0]).astype(np.int)
    ppg_matched_index = np.zeros(accel_values.shape[0]).astype(np.int)
    matched_cnt = 0

    ppg_start_index = 1
    for accel_index, accel_ns in enumerate(accel_nss):
        for ppg_index in range(ppg_start_index, ppg_nss.shape[0], 1):
            ppg_ns = ppg_nss[ppg_index]
            if ppg_ns >= accel_ns:
                ppg_index_selected = ppg_index
                distance = abs(ppg_ns - accel_ns)
                if abs(ppg_nss[ppg_index - 1] - accel_ns) < distance:
                    ppg_index_selected = ppg_index - 1
                    distance = abs(ppg_nss[ppg_index - 1] - accel_ns)

                if distance < match_distance_tolerance:
                    accel_matched_index[matched_cnt] = accel_index
                    ppg_matched_index[matched_cnt] = ppg_index_selected
                    matched_cnt += 1
                ppg_start_index = ppg_index_selected + 1
                break  # stop finding

    accel_matched = accel_values[accel_matched_index[:matched_cnt]]
    ppg_matched = ppg_values[ppg_matched_index[:matched_cnt]]

    accel_matched_df = pd.DataFrame(accel_matched, columns=ACCEL_COLUMNS)
    ppg_matched_df = pd.DataFrame(ppg_matched, columns=PPG_COLUMNS)

    if is_check_matched:
        check_matched(accel_matched_df, ppg_matched_df)

    time_part = accel_matched_df.iloc[:, :2].astype(np.int)
    accel_part = accel_matched_df.iloc[:, 2:]
    ppg_part = ppg_matched_df.iloc[:, 2:].astype(np.int)
    accel_ppg_matched_df = pd.concat((time_part, accel_part, ppg_part), axis=1)

    return accel_ppg_matched_df


def process_one_record(libai_record: Path,
                       match_freq,
                       is_check_matched=False,
                       print_head=False,
                       tolerance_rate=1.2):
    libai_record_utils = LibaiRecordUtils(libai_record)

    accel_values = libai_record_utils.get_accel_values()
    ppg_values = libai_record_utils.get_ppg_values()

    if accel_values is None or ppg_values is None:
        print(f'Skip {libai_record.name}, because of lake of accel or ppg')
        return

    accel_ppg_merged_path = libai_record_utils.get_accel_ppg_merged_path()

    accel_values_rebased = rebase_event_timestamp_ns(
        accel_values, freq_expected=52, tolerance_rate=tolerance_rate)

    ppg_values_rebased = rebase_event_timestamp_ns(
        ppg_values, freq_expected=100, tolerance_rate=tolerance_rate)

    accel_ppg_matched_df = merge_ppg_into_accel(accel_values_rebased,
                                                ppg_values_rebased, match_freq,
                                                is_check_matched)

    accel_ppg_matched_df.to_csv(accel_ppg_merged_path, index=False)
    print(f'Saved: {accel_ppg_merged_path.name}\n')

    if print_head:
        print(f'accel_ppg_matched_df.head() = \n{accel_ppg_matched_df.head()}')


def run(libai_path: Path,
        is_dir: bool,
        is_root: bool,
        match_freq=50,
        is_check_matched=False,
        print_head=False):
    libai_path = Path(libai_path)

    if is_root:
        date_strs = [_ for _ in libai_path.iterdir()]
        date_str_cnt = len(date_strs)
        for i, date_str in enumerate(date_strs):
            libai_records = [_ for _ in date_str.iterdir()]
            libai_record_cnt = len(libai_records)
            for j, libai_record in enumerate(libai_records):
                print(f'Processing ({i + 1} / {date_str_cnt}, '
                      f'{j + 1} / {libai_record_cnt}): '
                      f'{libai_record.name}')
                process_one_record(libai_record, match_freq, is_check_matched,
                                   print_head)
    elif is_dir:
        libai_records = [_ for _ in libai_path.iterdir()]
        for i, libai_record in enumerate(libai_records):
            print(f'Processing ({(i + 1)} / {len(libai_records)}): '
                  f'{libai_record.name}')
            process_one_record(libai_record, match_freq, is_check_matched,
                               print_head)
    else:
        process_one_record(libai_path, match_freq, is_check_matched,
                           print_head)


@click.command()
@click.argument('libai-path')
@click.option('-d', '--is-dir', is_flag=True)
@click.option('-f', '--match-freq', type=int, default=50)
@click.option('-c', '--is-check-matched', is_flag=True)
@click.option('-p', '--print-head', is_flag=True)
@click.option('-r', '--is-root', is_flag=True)
def main(libai_path: str, is_dir: bool, is_root: bool, match_freq: int,
         is_check_matched: bool, print_head: bool):
    print(f'Running : {libai_path}')
    run(libai_path, is_dir, is_root, match_freq, is_check_matched, print_head)


if __name__ == '__main__':
    main()
