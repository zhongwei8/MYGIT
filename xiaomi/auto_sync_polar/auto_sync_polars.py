#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Farmer Li
# @Date: 2021-03-19
import os
from pathlib import Path

import pandas as pd

DEAFULT_DOWNLOAD_DIR = Path.home() / 'Downloads/polar_data/'
FILE_PARENT_PATH = Path(__file__).parent


def read_polar_accounts():
    polar_accounts_path = FILE_PARENT_PATH / 'polar_accounts.csv'
    polar_accounts = pd.read_csv(polar_accounts_path)
    return polar_accounts


def process():
    polar_accounts = read_polar_accounts()
    for i, row in polar_accounts.iterrows():
        email = str(row['email'])
        password = str(row['password'])

        polar_tag = str(row['polar_tag'])
        save_dir = DEAFULT_DOWNLOAD_DIR / str(polar_tag)
        python_path = FILE_PARENT_PATH / 'auto_sync_polar.py'

        os.system(f'python {python_path} --email {email} '
                  f'--password {password} -d {save_dir}')


if __name__ == '__main__':
    process()
