import os
import click
import datetime
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import ticker

NMEA_FILE_PATTERN = '*.csv'

NMEA_FILE_HEADER_NAMES = [
    'CurrentTimeMillis', 'EventTimestamp(ms)', 'NMEA', 'IndoorOutdoor',
    'indoor_outdoor_label'
]

UNKNOW, INDOOR, OUTDOOR = 0, 1, 2

SAVED_DIR = Path('./src/data')
SUMMARY_FILE_PARENT = SAVED_DIR / 'summary'
SUMMARY_FILE_NAME = 'indoor_outdoor_recognization_report.csv'
SUMMARY_FILE_PATH = SUMMARY_FILE_PARENT / SUMMARY_FILE_NAME
SUMMARY_FILE_HEADER_NAMES = 'nmea_file, cnt, t_cnt, f_cnt, precision'


def summary_labeled_nmea_file(nmea_file: Path, is_show: bool,
                              is_save_fig: bool, is_statics: bool):
    nmea_file = Path(nmea_file)

    nmea_df = pd.read_csv(nmea_file)
    try:
        eventtimestamp = nmea_df['EventTimestamp(ms)'].values
        indoor_outdoor_predict = nmea_df['IndoorOutdoor'].values
        indoor_outdoor_label = nmea_df['indoor_outdoor_label'].values
    except KeyError:
        print(f'KeyError happens at file: {nmea_file.name}')
        return

    fig, axes = plt.subplots(2, 1, figsize=(12, 6), sharex=True)

    axes[0].set_title(nmea_file.name)
    axes[0].plot(eventtimestamp,
                 indoor_outdoor_predict,
                 label='indoor_outdoor_predict',
                 color='red',
                 marker='o')
    axes[1].plot(eventtimestamp,
                 indoor_outdoor_label,
                 label='indoor_outdoor_label',
                 color='blue',
                 marker='o')

    for ax in axes:
        ax.set_yticks([0, 1, 2])
        ax.set_yticklabels(['undefine', 'indoor', 'outdoor'])
        ax.legend()

    def format_func(x_tick, pos=None):
        x = x_tick // 1000
        dt = datetime.datetime.fromtimestamp(x)
        return dt.strftime('%H:%M:%S')

    axes[1].xaxis.set_major_formatter(ticker.FuncFormatter(format_func))

    if is_save_fig:  # before plt.show()
        fig_parent = SAVED_DIR / 'fig'
        os.makedirs(fig_parent, exist_ok=True)
        fig_name = nmea_file.stem + '.png'
        fig_path = fig_parent / fig_name
        plt.savefig(fig_path, dpi=500, bbox_inches='tight')
        print(f'Saved fig: {fig_path.name}')
        if not is_show:
            plt.close('all')

    if is_show:
        plt.show()

    if is_statics:
        valid_masks = np.where(indoor_outdoor_label != UNKNOW)[0]
        valid_predict = indoor_outdoor_predict[valid_masks]
        valid_label = indoor_outdoor_label[valid_masks]

        cnt = len(valid_masks)
        t_cnt = np.sum(valid_predict == valid_label)
        f_cnt = cnt - t_cnt
        precision = -1
        if cnt != 0:
            precision = t_cnt / cnt

        os.makedirs(SUMMARY_FILE_PARENT, exist_ok=True)

        if not os.path.exists(SUMMARY_FILE_PATH):
            with open(SUMMARY_FILE_PATH, 'w') as f:
                f.write(SUMMARY_FILE_HEADER_NAMES)
                f.write('\n')

        with SUMMARY_FILE_PATH.open('a') as f:
            f.write(f'{nmea_file.name},{cnt},{t_cnt},{f_cnt},{precision}\n')
    plt.close('all')


@click.command()
@click.argument('nmea_path')
@click.option('-p', '--is_show', is_flag=True, help='show plt')
@click.option('-s', '--is_save_fig', is_flag=True, help='save plt')
@click.option('-t', '--is_statistic', is_flag=True, help='static metrics')
@click.option('-r', '--is_rewrite', is_flag=True, help='rewrite summary file')
def main(nmea_path: Path, is_show: bool, is_save_fig: bool, is_statistic: bool,
         is_rewrite: bool):
    nmea_path = Path(nmea_path)

    if is_rewrite and os.path.exists(SUMMARY_FILE_PATH):
        os.remove(SUMMARY_FILE_PATH)

    if nmea_path.is_file():
        summary_labeled_nmea_file(nmea_path, is_show, is_save_fig,
                                  is_statistic)
    elif nmea_path.is_dir():
        nmea_files = [path for path in nmea_path.rglob(NMEA_FILE_PATTERN)]
        for i, nmea_file in enumerate(nmea_files):
            print(
                f'Processing ({i + 1} / {len(nmea_files)}): {nmea_file.name}')
            summary_labeled_nmea_file(nmea_file, is_show, is_save_fig,
                                      is_statistic)


if __name__ == "__main__":
    main()
