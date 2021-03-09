'''
Author: your name
Date: 2021-03-09 10:06:47
LastEditTime: 2021-03-09 10:38:46
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /activity-recognition/src/py/indoor_outdoor_recognizer_post.py
'''
from pathlib import Path
import pandas as pd

REPORT_DIR = Path('/home/mi/xiaomi/activity-recognition/src/data/'
                  'indoor_outdoor_recognization_report')


def get_summary_from_report(report_file_path: Path):
    report_file_path = Path(report_file_path)

    data = pd.read_csv(report_file_path)
    data['总样本量'] = data['C11'] + data['C12'] + data['C21'] + data['C22']
    data['准确率'] = (data['C11'] + data['C22']) / data['总样本量']

    precision_macro = data['准确率'].values.mean()
    precision_micro = (data['C11'] + data['C22']) / data['总样本量'].values.sum()
    summary = (report_file_path.name, precision_macro, precision_micro)

    return summary


def get_summary_from_reports(report_dir_path: Path):
    report_dir_path = Path(report_dir_path)

    report_file_paths = [path for path in report_dir_path.iterdir()]

    summary =