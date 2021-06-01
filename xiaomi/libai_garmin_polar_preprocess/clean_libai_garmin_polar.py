from pathlib import Path
import shutil

import click

LIBAI_FILE_SUFFIX = '.csv'
GARMIN_FIT_SUFFIX = '.fit'
POLAR_CSV_SUFFIX = '.csv'

LIBAI_FILE_PREFIX = 'libai_'
GARMIN_FIT_PREFIX = 'garmin_'
POLAR_CSV_PREFIX = 'polar_'

CLEANED_DIR = Path().home() / 'data/new-sensor-bucket/libai/heartrate/cleaned'
LIBAI_CLEANED_DIR = CLEANED_DIR / 'libai'
GARMIN_CLEANED_DIR = CLEANED_DIR / 'garmin'
POLAR_CLEANED_DIR = CLEANED_DIR / 'polar'


def rename_and_clean_libai_record(source_dir: Path, target_dir: Path,
                                  libai_file_suffix: str):
    source_dir = Path(source_dir)
    target_dir = Path(target_dir)

    assert source_dir != target_dir

    for file_path in source_dir.rglob(f'*{libai_file_suffix}'):
        file_name = file_path.name

        if len(file_name.split('.')) == 3:  # Unvisiable file in __MAXCOSX
            print(f'Unvalid file: {file_path}')
            continue

        file_new_name = LIBAI_FILE_PREFIX + file_name
        libai_name = file_path.parent.name
        libai_date_str = '-'.join(libai_name.split('_')[:3])
        save_dir = target_dir / libai_date_str / libai_name
        save_dir.mkdir(parents=True, exist_ok=True)
        file_new_path = save_dir / file_new_name
        shutil.copyfile(file_path, file_new_path)
        print(f'Copy {file_path.name} to {file_new_path.name}')
    print(f'Succeed: copy {source_dir} to {LIBAI_CLEANED_DIR}')


def rename_and_clean_garmin_fit(source_dir: Path, target_dir: Path,
                                garmin_fit_suffix: str):
    source_dir = Path(source_dir)
    target_dir = Path(target_dir)

    for garmin_fit_path in source_dir.rglob(f'*{garmin_fit_suffix}'):
        tag = garmin_fit_path.parents[1].name

        garmin_fit_name = garmin_fit_path.name
        garmin_new_name = GARMIN_FIT_PREFIX + garmin_fit_name

        garmin_date_str = '-'.join(garmin_fit_name.split('-')[:3])

        save_dir = target_dir / garmin_date_str / tag

        save_dir.mkdir(parents=True, exist_ok=True)

        garmin_fit_new_path = save_dir / garmin_new_name

        shutil.copyfile(garmin_fit_path, garmin_fit_new_path)

        print(f'Copy {garmin_fit_path.name} to {garmin_fit_new_path}')


def rename_and_clean_polar_csv(source_dir: Path, target_dir: Path,
                               polar_csv_suffix: str):
    source_dir = Path(source_dir)
    target_dir = Path(target_dir)

    for polar_csv_path in source_dir.rglob(f'*{polar_csv_suffix}'):
        tag = polar_csv_path.parents[1].name

        polar_csv_name = polar_csv_path.name
        polar_new_name = POLAR_CSV_PREFIX + polar_csv_name

        polar_date_str = '-'.join(polar_csv_name.split('_')[1].split('-')[:3])

        save_dir = target_dir / polar_date_str / tag

        save_dir.mkdir(parents=True, exist_ok=True)

        polar_fit_new_path = save_dir / polar_new_name

        shutil.copyfile(polar_csv_path, polar_fit_new_path)

        print(f'Copy {polar_csv_path.name} to {polar_fit_new_path}')


def run(libai_source_dir: Path, garmin_source_dir: Path,
        polar_source_dir: Path):

    if libai_source_dir is not None and Path(libai_source_dir).exists():
        rename_and_clean_libai_record(libai_source_dir, LIBAI_CLEANED_DIR,
                                      LIBAI_FILE_SUFFIX)
    if garmin_source_dir is not None and Path(garmin_source_dir).exists():
        rename_and_clean_garmin_fit(garmin_source_dir, GARMIN_CLEANED_DIR,
                                    GARMIN_FIT_SUFFIX)

    if polar_source_dir is not None and Path(polar_source_dir).exists():
        rename_and_clean_polar_csv(polar_source_dir, POLAR_CLEANED_DIR,
                                   POLAR_CSV_SUFFIX)


@click.command()
@click.option('-libai', '--libai-source-dir', type=str)
@click.option('-garmin', '--garmin-source-dir', type=str)
@click.option('-polar', '--polar-source-dir', type=str)
def main(libai_source_dir, garmin_source_dir, polar_source_dir):

    run(libai_source_dir, garmin_source_dir, polar_source_dir)


if __name__ == '__main__':
    main()
