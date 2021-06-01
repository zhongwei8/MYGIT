import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description='Training DNN Models.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--kfold',
                        type=int,
                        default=5,
                        help='k fold',
                        required=True)
    parser.add_argument('--model-file',
                        type=str,
                        default='',
                        dest='model_file',
                        help='load model file',
                        required=True)
    parser.add_argument('--shift',
                        type=float,
                        default=2.0,
                        help='frame shift length',
                        required=True)

    args = parser.parse_args()

    return args


def main():
    args = parse_args()

    print(f'args.model_file = {args.model_file}')
    print(f'args.kfold = {args.kfold}')
    print(f'args.shift = {args.shift}')


if __name__ == '__main__':
    main()
