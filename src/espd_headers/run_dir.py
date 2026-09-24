from __future__ import annotations

import datetime
import os
import re
from typing import Optional

DATE_FORMAT = '%d%m%y'


def next_run_number(save_dir: str, date_part: str) -> int:
    pattern = re.compile(rf'^{re.escape(date_part)}-(\d+)(?:_|$)')
    numbers = []
    for name in os.listdir(save_dir):
        match = pattern.match(name)
        if match:
            numbers.append(int(match.group(1)))
    return max(numbers, default=0) + 1


def make_run_dir(save_dir: str, label: str, today: Optional[datetime.date] = None) -> str:
    """Создаёт папку результатов вида ДДММГГ-N_<label>, например 220926-1_ignore_1.
    N — номер запуска за день (по всем режимам)."""
    date_part = (today or datetime.date.today()).strftime(DATE_FORMAT)
    os.makedirs(save_dir, exist_ok=True)
    number = next_run_number(save_dir, date_part)
    path = os.path.join(save_dir, f'{date_part}-{number}_{label}')
    os.makedirs(path)
    return path
