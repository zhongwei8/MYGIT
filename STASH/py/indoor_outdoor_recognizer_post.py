'''
Author: your name
Date: 2021-03-09 10:06:47
LastEditTime : 2021-03-09 17:54:43
LastEditors  : Please set LastEditors
Description: In User Settings Edit
FilePath     : /my_github/STASH/indoor_outdoor_recognizer_post.py
'''
import click
from pathlib import Path
import pandas as pd

SUMMARY_HEADER_NAMES = ['sport', '总准确率', '平均准确率', '样本量', '记录个数']

REPORT_DIR = Path('/home/mi/xiaomi/activity-recognition/src/data/'
                  'indoor_outdoor_recognization_report')


def get_sport_summary(sport_summary_path: Path):
    sport_summary_path = Path(sport_summary_path)

    data = pd.read_csv(sport_summary_path)
    data['总样本量'] = data['C11'] + data['C12'] + data['C21'] + data['C22']
    data = data[data['总样本量'] > 0]
    data['准确率'] = (data['C11'] + data['C22']) / data['总样本量']

    precision_macro = data['准确率'].values.mean()
    precision_micro = (data['C11'].values.sum() +
                       data['C22'].values.sum()) / data['总样本量'].values.sum()
    sample_cnt = data['总样本量'].values.sum()
    record_cnt = len(data)
    summary = (sport_summary_path.stem, precision_macro, precision_micro,
               sample_cnt, record_cnt)

    return summary


def get_sport_summarys(report_dir_path: Path):
    report_dir_path = Path(report_dir_path)

    summarys = []
    for sport_summary_path in report_dir_path.iterdir():
        summary = get_sport_summary(sport_summary_path)
        summarys.append(summary)

    summarys_df = pd.DataFrame(summarys, columns=SUMMARY_HEADER_NAMES)
    summary_path = Path('./src/data/summarys.csv')
    summarys_df.to_csv(summary_path, index=False)
    print(f'Saved: {summary_path}')
    return summarys_df


@click.command()
@click.argument('report_dir_path')
def main(report_dir_path: Path):
    report_dir_path = Path(report_dir_path)
    summarys = get_sport_summarys(report_dir_path)
    print(f'summarys = \n{summarys}')


if __name__ == "__main__":
    main()