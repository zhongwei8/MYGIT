#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Farmer Li
# @Date: 2021-02-19

from pathlib import Path
import sys

import click
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

current_dir = Path(__file__).parent.resolve()
depolyment_dir = current_dir / '../../../ai-algorithm-depolyment/'
if not depolyment_dir.exists():
    print(f'Warnning: ai-algorithm-depolyment not exits: {depolyment_dir}')
sys.path.append(str(depolyment_dir))
# Import from ai-algorithm-depolyment repo
from utils.base import SensorAlgo

build_dir = current_dir / '../../build_linux-x86_64/'
sys.path.append(str(build_dir))
# Import C interface built with pybind11
from mi_ior_py import MIIndoorOutdoorRecognizerPy


class IndoorOutdoorRecognizerC(SensorAlgo):
    """ Class for counting steps with accelerate data """
    def __init__(self):
        self._model = MIIndoorOutdoorRecognizerPy()
        self._version = self._model.get_version()
        self._algo_name = 'IndoorOutdoorRecognizerC'

        self._input_names = ['EventTimestamp(ms)', 'NMEA', 'IndoorOutdoor']
        self._output_names = ['EventTimestamp(ms)', 'IndoorOutdoor', 'Status']

        self._cur_timestamp = 0
        self._cnt = 0  # count points
        self._status = 0
        self._res = {}

    def is_realtime(self):
        return True

    def get_version(self):
        return self._version

    def reset(self):
        self._model.init_algo()
        self._cur_timestamp = 0
        self._cnt = 0
        self._status = 0
        self._res = {}

    def feed_data(self, data_point):
        """ main function processes data and count steps"""
        self._cur_timestamp = data_point['EventTimestamp(ms)']
        ts = data_point['EventTimestamp(ms)']
        nmea = data_point['NMEA']

        updated = self._model.process_data(ts, nmea)
        if updated > 0:
            self._status = self._model.get_status()
            self._res = {
                'EventTimestamp(ms)': self._cur_timestamp,
                'IndoorOutdoor': data_point['IndoorOutdoor'],
                'Status': self._status
            }
        return (updated > 0)

    def get_status(self):
        return self._status

    def get_update_timestamp(self):
        return self._model.get_update_timestamp()

    def get_result(self):
        return self._res

    def get_model(self):
        return self._model

    def process_file(self, file_path):
        df = pd.read_csv(file_path)
        predicts = {}
        for i, row in df.iterrows():
            update = self.feed_data(row)
            if update:
                result = self.get_result()
                for key in result:
                    if key not in predicts:
                        predicts[key] = [result[key]]
                    else:
                        predicts[key].append(result[key])
        result = pd.DataFrame.from_dict(predicts)
        return result


def analysis_result(file_name, result):
    result = result.drop('EventTimestamp(ms)', axis='columns')
    result_columns = ['IndoorOutdoor', 'Status']
    result = result[result_columns]
    mpl.use('Qt5Agg')
    plt.figure()
    plt.title(file_name)
    result.plot(ax=plt.gca(), style='-o')
    plt.legend()
    plt.show()


@click.command()
@click.argument('file-path')
def main(file_path):
    file_path = Path(file_path)
    print(f'Processing file: {file_path}')
    model = IndoorOutdoorRecognizerC()
    result = model.process_file(file_path)
    analysis_result(file_path.name, result)


if __name__ == '__main__':
    main()
