#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Farmer Li
# @Date: 2021-03-19

from dataclasses import dataclass
from datetime import date, datetime
import http.cookiejar as cookielib
import json
import os
from pathlib import Path
from typing import List

import click
import pandas as pd
import requests

DEAFULT_DOWNLOAD_DIR = Path.home() / 'Downloads/polar_data/'


def read_polar_accounts():
    polar_accounts_path = Path('./src/py/tools/polar_accounts.csv')
    polar_accounts = pd.read_csv(polar_accounts_path)
    return polar_accounts


def process():
    polar_accounts = read_polar_accounts()
    for i, row in polar_accounts.iterrows():
        email = str(row['email'])
        password = str(row['password'])

        polar_tag = str(row['polar_tag'])
        save_dir = DEAFULT_DOWNLOAD_DIR / str(polar_tag)
        python_path = Path('./src/py/tools/auto_sync_polar.py')

        os.system(f'python {python_path} --email {email} '
                  f'--password {password} -d {save_dir}')


if __name__ == '__main__':
    process()
