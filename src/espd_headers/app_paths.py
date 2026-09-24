import os
import sys


def app_dir() -> str:
    """Папка программы: где лежит espd_headers.exe,
    а при запуске из исходников — папка src (рядом с templates и ignore.txt)."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
