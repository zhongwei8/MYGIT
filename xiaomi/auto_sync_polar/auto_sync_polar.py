#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Farmer Li
# @Date: 2021-03-19

from dataclasses import dataclass
from datetime import date, datetime
import http.cookiejar as cookielib
import json
from pathlib import Path
from typing import List

import click
import requests

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'

DEFAULT_EMAIL = 'jiahuixing@163.com'
DEFAULT_PW = 'qweasdzxc!@#'
DEAFULT_DOWNLOAD_DIR = Path.home() / 'Downloads/polar_data/'
POLAR_TMP_DIR = Path.home() / '.polar/'
if not POLAR_TMP_DIR.exists():
    POLAR_TMP_DIR.mkdir(parents=True)
POLAR_USER_INFO_FILE = Path(f'{POLAR_TMP_DIR}/.info')
POLAR_COOKIES_FILE = POLAR_TMP_DIR / '.cookies'

session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename=f'{POLAR_COOKIES_FILE}')

POLAR_HISTORY_SAMPLE = {
    "calories": 270,
    "distance": 2818.77294921875,
    "duration": 1122031,
    "hasTrainingTarget": False,
    "hrAvg": 158,
    "iconUrl":
    "https://platform.cdn.polar.com/ecosystem/sport/icon/808d0882e97375e68844ec6c5417ea33-2015-10-20_13_46_22",
    "id": 5766193689,
    "isTest": False,
    "note": " ",
    "periodDataUuid": None,
    "recoveryTime": 29940000,
    "sportId": 1,
    "sportName": "Running",
    "startDate": "2021-03-09 14:02:39.000",
    "swimDistance": None,
    "swimmingPoolUnits": "METERS",
    "swimmingSport": False,
    "trainingLoadHtml": None,
    "trainingLoadProHtml": ""
}


@dataclass()
class PolarHistory:
    id: int = -1  # History id
    sport_id: int = 1
    sport_name: str = 'Running'
    start_date: datetime = datetime.fromisoformat('2021-03-09 14:02:39.000')
    calories: int = 0
    distance: float = 0
    duration: float = 0  # In seconds
    hr_avg: int = 100
    recovery_time: int = 0  # In seconds

    def set_by_dict(self, history_dict):
        self.id = history_dict['id']
        self.sport_id = history_dict['sportId']
        self.sport_name = history_dict['sportName']
        self.start_date = datetime.fromisoformat(history_dict['startDate'])
        self.calories = history_dict['calories']
        self.distance = history_dict['distance']
        self.duration = history_dict['duration']
        self.hr_avg = history_dict['hrAvg']
        self.recovery_time = history_dict['recoveryTime']


@dataclass()
class PolarUser:
    id: int = -1  # User id, for request training history
    user_name: str = ''
    fisrt_name: str = "Hello"
    last_name: str = 'World'
    nick_name: str = 'Wahaha'

    def set_by_dict(self, user_dict):
        self.id = user_dict['id']
        self.user_name = user_dict['userName']
        self.fisrt_name = user_dict['firstName']
        self.last_name = user_dict['lastName']
        self.nick_name = user_dict['nickName']


def login_to_polar_flow(email, password):
    print("Begin to login Polar Flow")

    postUrl = "https://flow.polar.com/login"

    header = {'Referer': 'https://flow.polar.com/', 'Rser-Agent': USER_AGENT}
    postData = {
        'returnUrl': '/',
        "email": email,
        "password": password,
    }
    res = session.post(postUrl, data=postData, headers=header)
    if res.status_code == 200:
        print('Login succeed')
        session.cookies.save()
        save_default_account(email, password)
        return True
    else:
        print(f"statusCode = {res.status_code}")
        # print(f"text = {res.text}")
        return False


def is_login():
    header = {
        'Referer': 'https://flow.polar.com/diary/training-list',
        'Rser-Agent': USER_AGENT
    }
    test_url = 'https://flow.polar.com/api/features/balance/available'
    res = session.get(test_url, headers=header)
    if res.status_code == 200:
        print('Already Login')
        return True
    else:
        print(f"Not login, statusCode = {res.status_code}")
        # print(f"text = {res.text}")
        return False


def get_history_list(user: PolarUser,
                     start_date=None,
                     end_date=None) -> List[PolarHistory]:
    histories = []
    if start_date is None:
        start_date = '2021-02-14'
    if end_date is None:
        end_date = str(date.today())
    payload = {
        'userId': user.id,
        'fromDate': start_date,
        'toDate': end_date,
        'sportIds': []
    }
    header = {
        'content-type': 'application/json',
        'origin': 'https://flow.polar.com',
        'referer': 'https://flow.polar.com/diary/training-list',
        'sec-ch-ua':
        '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': USER_AGENT,
        'x-requested-with': 'XMLHttpRequest'
    }
    history_url = 'https://flow.polar.com/api/training/history'
    print('Begin to get the history')
    try:
        res = session.post(history_url,
                           headers=header,
                           data=json.dumps(payload))
    except BaseException as e:
        print('Error occurred!')
        print(e)
    if res.status_code == 200:
        train_list = json.loads(res.text)
        for train in train_list:
            history = PolarHistory()
            history.set_by_dict(train)
            histories.append(history)
    else:
        print(f'Falied with code: {res.status_code}')

    return histories


def get_user_info() -> PolarUser:
    user = None
    header = {
        'content-type': 'application/json; charset=UTF-8',
        'referer': 'https://flow.polar.com/diary/training-list',
        'user-agent': USER_AGENT,
    }
    info_url = 'https://flow.polar.com/api/account/users/current/user'
    print('Request current user info...')
    try:
        res = session.get(info_url, headers=header)
    except BaseException as e:
        print('Error occurred!')
        print(e)
    if res.status_code == 200:
        user_info = json.loads(res.text)
        user = PolarUser()
        user.set_by_dict(user_info['user'])
        print(f'Get user info successfully of id: {user.id}')
        # print(json.dumps(user_info, indent=2))
    else:
        print(f'Falied with code: {res.status_code}')

    return user


def download_history(user: PolarUser, hitories: List[PolarHistory],
                     save_dir: Path):
    dst_dir = save_dir / str(user.id)
    if not dst_dir.exists():
        print(f'Creating directory: {dst_dir}')
        dst_dir.mkdir(parents=True)
    print(f'Begin to downloading, to: {dst_dir}')

    download_url_preffix = 'https://flow.polar.com/api/export/training/csv/'
    total_num = len(hitories)
    for i, h in enumerate(hitories, 1):
        hid = h.id
        download_url = f'{download_url_preffix}{hid}'
        print(f'\nDownloading [{i}/{total_num}]: {download_url}')
        r = session.get(download_url)
        print(f'Status code: {r.status_code}')
        if r.status_code == 200:
            date_time_str = h.start_date.strftime('%Y-%m-%d-%H-%M-%S')
            dst_file_name = f'{user.id}_{date_time_str}_{h.sport_name}.csv'
            dst_file = dst_dir / dst_file_name
            print(f'Writing to file: {dst_file}')
            with dst_file.open('wb') as f:
                f.write(r.content)


def download_url_to_file(url, file_path: Path):
    print(f'Downloading from: {url}')
    r = session.get(url)
    with file_path.open('wb') as f:
        f.write(r.content)


def one_demo():
    url = 'https://flow.polar.com/api/export/training/csv/5777437184'
    file_path = Path('./test.csv')
    download_url_to_file(url, file_path)


def load_default_account():
    if POLAR_USER_INFO_FILE.exists():
        with POLAR_USER_INFO_FILE.open('r') as f:
            info = json.load(f)
            return info['email'], info['pw']
    else:
        return DEFAULT_EMAIL, DEFAULT_PW


def save_default_account(email, pw):
    with POLAR_USER_INFO_FILE.open('w+') as f:
        json.dump({'email': email, 'pw': pw}, f)


@click.command()
@click.option('--email')
@click.option('--password')
@click.option('-d', '--save-dir', default=DEAFULT_DOWNLOAD_DIR)
def main(email, password, save_dir):
    save_dir = Path(save_dir)

    default_email, default_pw = load_default_account()
    if email is None:
        email = click.prompt('Input Email', default=default_email)
    if password is None:
        password = click.prompt('Input password', default=default_pw)
    print(f'Using email: {email} with password: {password}')

    need_login = False
    is_new_user = email != default_email
    has_cache = POLAR_COOKIES_FILE.exists()
    if is_new_user:
        print(f'Login for new user: {email}, old email: {default_email}')
        need_login = True
        if has_cache:
            session.cookies.clear()
    else:
        if has_cache:
            session.cookies.load()
            need_login = is_login()
        else:
            need_login = True

    if need_login:
        # Login when new user or has no cache or login expired
        success = login_to_polar_flow(email, password)
        if not success:
            print('Login falied, please check')
            exit(1)

    user = get_user_info()

    histories = get_history_list(user)

    download_history(user, histories, save_dir)


if __name__ == '__main__':
    main()
