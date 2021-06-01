'''
Author: your name
Date: 2021-03-08 16:33:11
LastEditTime: 2021-03-09 10:05:01
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /my_github/多进程/usage.py
'''
import time

import multiprocessing
from multiprocessing import Pool, cpu_count


def func(msg):
    return multiprocessing.current_process() + '-' + msg


def test():
    p = Pool(cpu_count)
    pool_cnt = cpu_count
    start_time = time.time()

    results = []
    for i in range(pool_cnt):
        msg = f'hello {i}'
        result = p.apply_async(func, args=(msg, ))
        results.append(result)
    p.close()  # 关闭进程池
    p.join()  # 阻塞进程池

    end_time = time.time()

    print(f'use {end_time - start_time} seconds')

    for result in results:
        print(result.get())


if __name__ == '__main__':
    test()
