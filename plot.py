from pathlib import Path


def main():
    path = Path('./log.log')
    with open(path, 'a+') as f:
        for i in range(5):
            log = f'{i}\n'
            f.write(log)


if __name__ == '__main__':
    main()
