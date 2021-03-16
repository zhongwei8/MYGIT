#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Farmer Li
#          Zhongwei Tian
# @Date: 2021-02-23

import numpy as np

RECOGNIZE_WIN_DURATION_MS = 4000
THRESHOLD_SATELLITE_CNT = 4
THRESHOLD_SNR_SUM = 40
SATELLITE_MAX = 32

UNDEFINED = 0
INDOOR = 1
OUTDOOR = 2


class IndoorOutdoorRecognizer():
    def __init__(self,
                 threshold_satellite_cnt=THRESHOLD_SATELLITE_CNT,
                 threshold_snr_sum=THRESHOLD_SNR_SUM,
                 win_duration_ms=RECOGNIZE_WIN_DURATION_MS):
        self.threshold_satellite_cnt = threshold_satellite_cnt
        self.threshold_snr_sum = threshold_snr_sum
        self.indoor_outdoor_width_ms = win_duration_ms

        self.update_timestamp_ms = 0
        self.snrs = np.zeros(SATELLITE_MAX).astype(np.int)
        self._status = UNDEFINED
        self.satellite_num = 0
        self.snr_sum = 0
        self._res = {}

    def reset(self) -> None:
        self.update_timestamp_ms = 0
        self.snrs.fill(0)
        self._status = UNDEFINED
        self.satellite_num = 0
        self.snr_sum = 0
        self._res = {}

    def _reset_recognize_status(self):
        self.snrs.fill(0)

    def _parse_gpgsv_sentence(self, gpgsv_sentence: str) -> tuple:
        # Exmaple： $GPGSV,1,1,03,13,00,000,29,15,00,000,34,30,00,000,19,1*56
        error_return = ([], [])
        if len(gpgsv_sentence) == 0:
            return error_return

        fields = gpgsv_sentence.split(',')
        if (fields[0] != "$GPGSV"):
            return error_return

        field_cnt = len(fields)
        field_idx = 0
        try:
            id_num = int(fields[3])
        except ValueError:
            return error_return

        if id_num <= 0:
            return error_return

        field_idx = 4
        ids = []
        snrs = []
        while (True):
            if (field_idx >= field_cnt):
                break
            s_id = fields[field_idx]
            field_idx += 3
            if (field_idx >= field_cnt):
                break
            snr = fields[field_idx]
            field_idx += 1

            if (s_id == ''):
                continue
            if (snr == ''):
                snr = 0

            ids.append(int(s_id))
            snrs.append(int(snr))

        return ids, snrs

    def _update_gpgsv_info(self, num, snr) -> None:
        assert (1 <= num <= 32)
        num -= 1
        if (snr >= 0):
            self.snrs[num] = snr
        else:
            assert (snr >= 0)

    def _classify(self):
        # print(f'Current satellite info arr: {self.snrs}')
        snr_cnt = 0
        snr_sum = 0
        for snr in self.snrs:
            if snr > 0:
                snr_cnt += 1
                snr_sum += snr

        if (snr_cnt >= THRESHOLD_SATELLITE_CNT
                and snr_sum >= THRESHOLD_SNR_SUM):
            self._status = OUTDOOR
        else:
            self._status = INDOOR

        self.satellite_num = snr_cnt
        self.snr_sum = snr_sum
        # print(f'Classify jugements: {self.satellite_num}, {self.snr_sum}\n')

    def process(self, timestamp_ms: int, ids: list, snrs: list) -> None:
        if (self.update_timestamp_ms == 0):
            self.update_timestamp_ms = timestamp_ms

        # TODO(Farmer): Process timestamp rollback, maybe there is a better solution
        if timestamp_ms < self.update_timestamp_ms:
            return False

        ids_len, snrs_len = len(ids), len(snrs)
        assert (ids_len == snrs_len)
        assert (ids_len <= SATELLITE_MAX)

        for i in range(ids_len):
            num, snr = ids[i], snrs[i]
            self._update_gpgsv_info(num, snr)

        update = False
        if (timestamp_ms - self.update_timestamp_ms >
                RECOGNIZE_WIN_DURATION_MS):
            update = True
            self.update_timestamp_ms = timestamp_ms
            self._classify()
            self._reset_recognize_status()

        return update

    def process_with_raw_nmea_sentence(self, ts, nmea_sentence: str):
        nums, snrs = self._parse_gpgsv_sentence(nmea_sentence)
        return self.process(ts, nums, snrs)

    def feed_data(self, data_point):
        ts = data_point['EventTimestamp(ms)']
        nmea = data_point['NMEA']
        updated = self.process_with_raw_nmea_sentence(ts, nmea)
        if updated > 0:
            self._res = {'EventTimestamp(ms)': ts, 'Status': self._status}
            if 'IndoorOutdoor' in data_point:
                self._res['IndoorOutdoor'] = data_point['IndoorOutdoor']
        return updated

    def get_result(self):
        return self._res

    def get_status(self) -> int:
        return self._status

    def get_satellite_status(self):
        return self.satellite_num, self.snr_sum

    def get_update_timestamp(self):
        return self.update_timestamp_ms
