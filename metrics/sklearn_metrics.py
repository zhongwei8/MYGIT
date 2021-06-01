'''
Author: your name
Date: 2021-03-08 10:40:07
LastEditTime: 2021-03-08 13:12:27
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /my_github/metrics/sklearn_metrics.py
'''
import numpy as np
from sklearn.metrics import precision_recall_fscore_support


def main():
    y_true = np.array(['cat', 'dog', 'pig', 'cat', 'dog', 'pig'])
    y_pred = np.array(['cat', 'dog', 'pig', 'dog', 'cat', 'cat'])

    prfsa = precision_recall_fscore_support(y_true, y_pred, average='macro')

    prfsi = precision_recall_fscore_support(y_true, y_pred, average='micro')

    prfsw = precision_recall_fscore_support(y_true, y_pred, average='weighted')

    print(f'precision_recall_fscore_support_micro: {prfsa}\n')

    print(f'precision_recall_fscore_support_macro: {prfsi}\n')

    print(f'precision_recall_fscore_support_weighted = {prfsw}\n')


if __name__ == '__main__':
    main()