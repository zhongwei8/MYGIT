'''
Author: Tianzw
Date: 2021-03-03 19:26:35
LastEditors: Please set LastEditors
LastEditTime: 2021-03-08 19:00:37
Description:
    process a nmea file, and report its result
'''
import multiprocessing
from multiprocessing import Pool

import shutil
import click
import datetime

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from pathlib import Path

from indoor_outdoor_recognizer import IndoorOutdoorRecognizer

HEADER_LINES_TO_SKIP = 2

NMEA_FILE_HEADER_NAMES = [
    'CurrentTimeMillis', 'EventTimestamp(ms)', 'NMEA', 'IndoorOutdoor'
]

NMEA_FILE_REPORT_COLUMNS = [
    'EventTimestamp(ms)', 'num', 'snr_sum', 'indoor_outdoor_predict',
    'indoor_outdoor_label'
]

NMEA_FILE_PATTERN = '*.csv'

YTICKS_STATUS = [0, 1, 2]
YLABELS_STATUS = ['undefine', 'indoor', 'outdoor']
UNKNOW, INDOOR, OUTDOOR = 0, 1, 2

INDOOR_OUTDOOR_RECOGNIZATION_REPORT_DIR = Path(
    './src/data/indoor_outdoor_recognization_report')
INDOOR_OUTDOOR_RECOGNIZATION_PNG_DIR = Path(
    './src/data/indoor_outdoor_recognization_png')

REPORT_FILE_HEADER = 'nmea_file,C11,C12,C21,C22\n'


def get_indoor_outdoor_label_from_buffer(indoor_outdoor_buffer: list) -> int:
    indoor_outdoor_buffer_set = set(indoor_outdoor_buffer)
    if OUTDOOR in indoor_outdoor_buffer_set:
        return OUTDOOR
    elif INDOOR in indoor_outdoor_buffer_set:
        return INDOOR
    return UNKNOW


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
    nmea_df = pd.DataFrame(data, columns=NMEA_FILE_HEADER_NAMES)
    print(f'nmea_df = \n{nmea_df.head()}')
    return nmea_df


def get_preprocessed_nmea_df(nmea_file_path: Path,
                             is_raw_nmea_file=False) -> pd.DataFrame:
    if is_raw_nmea_file:
        return preprocess_raw_nmea_file(nmea_file_path, UNKNOW)

    return pd.read_csv(nmea_file_path)


def nmea_file_recognization(nmea_file_path: Path,
                            is_raw_nmea_file=False) -> pd.DataFrame:

    recognizer = IndoorOutdoorRecognizer()

    nmea_file_df = get_preprocessed_nmea_df(nmea_file_path, is_raw_nmea_file)

    results = []
    indoor_outdoor_buffer = []
    for i, row in nmea_file_df.iterrows():
        timestamp = int(row['EventTimestamp(ms)'])
        indoor_outdoor_buffer.append(int(row['IndoorOutdoor']))
        update = recognizer.feed_data(row)
        if update:
            indoor_outdoor_predict = recognizer.get_status()
            satel_num, satel_snr_sum = recognizer.get_satellite_status()
            indoor_outdoor_label = get_indoor_outdoor_label_from_buffer(
                indoor_outdoor_buffer)
            indoor_outdoor_buffer.clear()

            result = (timestamp, satel_num, satel_snr_sum,
                      indoor_outdoor_predict, indoor_outdoor_label)
            results.append(result)

    return pd.DataFrame(results, columns=NMEA_FILE_REPORT_COLUMNS)


def indoor_outdoor_recognization_confusion_matrix(results: pd.DataFrame):
    indoor_outdoor_label = results['indoor_outdoor_label'].values
    indoor_outdoor_predict = results['indoor_outdoor_predict'].values

    c11 = np.sum((indoor_outdoor_label == 1) & (indoor_outdoor_predict == 1))
    c12 = np.sum((indoor_outdoor_label == 1) & (indoor_outdoor_predict == 2))
    c21 = np.sum((indoor_outdoor_label == 2) & (indoor_outdoor_predict == 1))
    c22 = np.sum((indoor_outdoor_label == 2) & (indoor_outdoor_predict == 2))

    cm = np.array([c11, c12, c21, c22])

    return cm


def write_confusion_matrix(cm: np.ndarray, nmea_file_path):
    sport = Path(nmea_file_path).name.split('-')[0]

    cm_flattened = cm.flatten()

    if not INDOOR_OUTDOOR_RECOGNIZATION_REPORT_DIR.exists():
        INDOOR_OUTDOOR_RECOGNIZATION_REPORT_DIR.mkdir(parents=True)
        print(f'Created dir: {INDOOR_OUTDOOR_RECOGNIZATION_REPORT_DIR}')

    report_path = INDOOR_OUTDOOR_RECOGNIZATION_REPORT_DIR / (sport + '.csv')
    print(f'report_path: {report_path}')

    if not report_path.exists():
        with open(report_path, mode='w') as f:
            f.write(REPORT_FILE_HEADER)
        print(f'Created file: {report_path.absolute()}')

    with open(report_path, mode='a') as f:
        fields_to_write = [str(nmea_file_path.name)]
        fields_to_write.extend([str(i) for i in cm_flattened])
        line_to_write = ','.join(fields_to_write)
        line_to_write += '\n'
        f.write(line_to_write)
        print(f'Written confusion matrix to {report_path.absolute()}\n')


def plot_indoor_outdoor_reports(results: pd.DataFrame, nmea_file_path: Path,
                                is_save_plt: bool):
    nmea_file_path = Path(nmea_file_path)

    fig, axes = plt.subplots(3, 1, figsize=(12, 6), sharex=True)

    axes[0].set_title(nmea_file_path.name)
    axes[0].plot(results['EventTimestamp(ms)'].values,
                 results['indoor_outdoor_predict'].values,
                 label='indoor_outdoor_predict',
                 marker='o',
                 color='r')
    axes[0].plot(results['EventTimestamp(ms)'].values,
                 results['indoor_outdoor_label'],
                 label='indoor_outdoor_label',
                 marker='o',
                 color='blue')
    axes[1].plot(results['EventTimestamp(ms)'].values,
                 results['num'],
                 label='num',
                 marker='o',
                 color='r')
    axes[2].plot(results['EventTimestamp(ms)'].values,
                 results['snr_sum'],
                 label='snr_sum',
                 marker='o',
                 color='r')

    for ax in axes:
        ax.legend()

    axes[0].set_ylim([-0.2, 2.2])
    axes[0].set_yticks(YTICKS_STATUS)
    axes[0].set_yticklabels(YLABELS_STATUS)

    def format_func(x_tick, pos=None):
        x = x_tick // 1000
        dt = datetime.datetime.fromtimestamp(x)
        return dt.strftime('%H:%M:%S')

    axes[2].xaxis.set_major_formatter(ticker.FuncFormatter(format_func))

    if is_save_plt:
        sport = str(nmea_file_path.name).split('-')[0]
        fig_parent = INDOOR_OUTDOOR_RECOGNIZATION_PNG_DIR / sport

        if not fig_parent.exists():
            fig_parent.mkdir(parents=True)

        fig_path = fig_parent / (nmea_file_path.stem + '.png')

        plt.savefig(fig_path, dpi=500)
        print(f'{fig_path.name} saved\n')
        plt.close('all')
        return

    plt.show()
    plt.close('all')


def process_nmea_file(nmea_file_path: Path,
                      is_plot=False,
                      is_save_plt=False,
                      is_raw_nmea_file=False,
                      is_report_cm=False,
                      is_write_cm=False,
                      job_num=0):
    print(f'Processing job_num {job_num}: {nmea_file_path.name}')

    nmea_file_path = Path(nmea_file_path)

    results = nmea_file_recognization(nmea_file_path, is_raw_nmea_file)

    if is_plot:
        plot_indoor_outdoor_reports(results, nmea_file_path, is_save_plt)

    if is_report_cm:
        cm = indoor_outdoor_recognization_confusion_matrix(results)
        if is_write_cm:
            write_confusion_matrix(cm, nmea_file_path)


@click.command()
@click.argument('nmea_path')
@click.option('-p',
              '--is_plot',
              is_flag=True,
              help='Whether to plot results of nmea recognization')
@click.option('-s', '--is_save_plt', is_flag=True, help='Whether to save plot')
@click.option('-r', '--is_raw_nmea_file', is_flag=True, default=False)
@click.option('-c', '--is_report_cm', is_flag=True)
@click.option('-w',
              '--is_write_cm',
              is_flag=True,
              help=f'write confusion matrix to file')
@click.option('-x',
              '--is_clear_summary',
              is_flag=True,
              help='clear summary file')
def main(nmea_path, is_plot, is_save_plt, is_raw_nmea_file, is_report_cm,
         is_write_cm, is_clear_summary):
    nmea_path = Path(nmea_path)
    if is_clear_summary and INDOOR_OUTDOOR_RECOGNIZATION_REPORT_DIR.exists():
        shutil.rmtree(INDOOR_OUTDOOR_RECOGNIZATION_REPORT_DIR)
        print(
            f'Remove dir: {INDOOR_OUTDOOR_RECOGNIZATION_REPORT_DIR.resolve()}')
        pass

    if nmea_path.is_file():
        process_nmea_file(nmea_path=nmea_path,
                          is_plot=is_plot,
                          is_save_plt=is_save_plt,
                          is_raw_nmea_file=is_raw_nmea_file,
                          is_report_cm=is_report_cm,
                          is_write_cm=is_write_cm)
    elif nmea_path.is_dir():
        nmea_file_paths = [path for path in nmea_path.rglob(NMEA_FILE_PATTERN)]
        cpu_cnt = multiprocessing.cpu_count()
        p = Pool(cpu_cnt)
        for i, nmea_file_path in enumerate(nmea_file_paths):
            p.apply_async(process_nmea_file,
                          args=(nmea_file_path, is_plot, is_save_plt,
                                is_raw_nmea_file, is_report_cm, is_write_cm,
                                i + 1))
        p.close()
        p.join()


if __name__ == "__main__":
    main()
