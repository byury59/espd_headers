"""Параметры командной строки (как в espd_parser, но без режимов)."""
from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from typing import Optional, Sequence

from . import __version__
from .config import APP_NAME, RESULTS_DIR_NAME

EPILOG = f"""примеры:
  {APP_NAME}.exe                         весь проект (папка на уровень выше программы), с подтверждением
  {APP_NAME}.exe --path ..\\src\\drivers   только указанная папка
  {APP_NAME}.exe --yes                   без подтверждения
  {APP_NAME}.exe <путь> [<папка_результатов>]   короткая запись
"""


@dataclass
class Options:
    root: str
    root_explicit: bool
    save_dir: str
    confirm: bool


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=APP_NAME,
        description='Вставка шапок модулей и функций в исходные тексты на C.',
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('path_pos', nargs='?', metavar='путь',
                        help='папка проекта (по умолчанию — папка на уровень выше программы)')
    parser.add_argument('out_pos', nargs='?', metavar='папка_результатов',
                        help=f'куда складывать папки запусков (по умолчанию — {RESULTS_DIR_NAME} рядом с программой)')
    parser.add_argument('-p', '--path', dest='path_opt', metavar='ПУТЬ',
                        help='обработать только эту папку (например, часть большого проекта)')
    parser.add_argument('-o', '--out', dest='out_opt', metavar='ПАПКА',
                        help=f'куда складывать папки запусков вместо {RESULTS_DIR_NAME}')
    parser.add_argument('-y', '--yes', action='store_true',
                        help='не спрашивать подтверждение перед изменением файлов')
    parser.add_argument('-v', '--version', action='version', version=f'{APP_NAME} {__version__}')
    return parser


def parse_options(argv: Optional[Sequence[str]], app_dir: str) -> Options:
    args = build_arg_parser().parse_args(argv)
    path = args.path_opt or args.path_pos
    out = args.out_opt or args.out_pos

    if path:
        root = os.path.abspath(path)
        root_explicit = True
    else:
        root = os.path.dirname(app_dir)
        root_explicit = False

    return Options(
        root=root,
        root_explicit=root_explicit,
        save_dir=os.path.abspath(out) if out else os.path.join(app_dir, RESULTS_DIR_NAME),
        confirm=not args.yes,
    )


def ask_confirmation(root: str, count: int) -> bool:
    print(f'\nПапка проекта: {root}')
    print(f'Найдено файлов: {count}')
    print('Шапки будут вставлены прямо в эти файлы. Убедитесь, что есть резервная копия проекта.')
    while True:
        answer = input('Продолжить? (y/n): ').strip().lower()
        if answer in ('y', 'д'):
            return True
        if answer in ('n', 'н', ''):
            return False
        print('Введите y или n.')
