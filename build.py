import os
import re
import shutil
import sys

APP_NAME = 'espd_headers'

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'src')
WORK = os.path.join(ROOT, 'build')
VERSION_FILE = os.path.join(SRC, APP_NAME, '__init__.py')
INSTRUCTION = os.path.join(ROOT, 'Инструкция.txt')


def read_version() -> str:
    with open(VERSION_FILE, encoding='utf-8') as f:
        match = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", f.read())
    if not match:
        raise RuntimeError(f'Не найден __version__ в {VERSION_FILE}')
    return match.group(1)


def run_pyinstaller(exe_name: str, dist: str) -> None:
    import PyInstaller.__main__
    PyInstaller.__main__.run([
        os.path.join(SRC, 'main.py'),
        '--name', exe_name,
        '--onefile',
        '--console',
        '--paths', SRC,
        '--distpath', dist,
        '--workpath', WORK,
        '--specpath', WORK,
        '--noconfirm',
        '--clean',
    ])


def copy_extras(dist: str) -> None:
    shutil.copytree(os.path.join(SRC, 'templates'), os.path.join(dist, 'templates'))
    shutil.copy2(os.path.join(SRC, 'ignore.txt'), dist)
    if os.path.isfile(INSTRUCTION):
        shutil.copy2(INSTRUCTION, dist)


def main() -> int:
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print('PyInstaller не установлен. Выполните: python -m pip install pyinstaller')
        return 1

    exe_name = f'{APP_NAME}_{read_version()}'
    dist = os.path.join(ROOT, 'dist', exe_name)
    if os.path.isdir(dist):
        shutil.rmtree(dist)

    run_pyinstaller(exe_name, dist)
    copy_extras(dist)
    print(f'\nГотово: {os.path.join(dist, exe_name + ".exe")}')
    print(f'Комплект для копирования в папку PD проекта: {dist}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
