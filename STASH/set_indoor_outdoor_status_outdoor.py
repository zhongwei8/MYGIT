'''
Author       :
Date         : 2021-03-10 12:19:30
LastEditors  : Please set LastEditors
LastEditTime : 2021-03-10 14:11:34
FilePath     : /my_github/STASH/set_indoor_outdoor_status_outdoor.py
'''
import click
from pathlib import Path
import pandas as pd


def set_all_outdoor(nmea_file_path: Path) -> None:
    nmea_file_path = Path(nmea_file_path)

    nmea_df = pd.read_csv(nmea_file_path)
    nmea_df.loc[:, 'IndoorOutdoor'] = 2

    nmea_df.to_csv(nmea_file_path, index=False)
    print(f'{nmea_file_path.name} set all outdoor\n')


@click.command()
@click.argument('nmea_dir')
def main(nmea_dir):
    nmea_dir = Path(nmea_dir)
    nmea_paths = [path for path in nmea_dir.iterdir()]
    for i, nmea_path in enumerate(nmea_paths):
        print(f'Processing ({i + 1} / {len(nmea_paths)}): {nmea_path.name}')
        set_all_outdoor(nmea_path)


if __name__ == "__main__":
    main()
