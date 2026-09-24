"""Текстовый отчёт по обработанным файлам."""
from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import List, Sequence

NOW_FORMAT = '%Y-%m-%d %H:%M:%S'

STATUS_OK = 'OK'
STATUS_ERROR = 'Ошибка'


@dataclass
class FileResult:
    rel_path: str
    encoding: str = ''
    status: str = STATUS_OK
    error: str = ''
    functions: List[str] = field(default_factory=list)


def write_report(results: Sequence[FileResult], path: str) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f"=== Обработка от {datetime.datetime.now().strftime(NOW_FORMAT)} ===\n\n")
        for item in results:
            f.write(f'Файл: {item.rel_path}\n')
            f.write(f'  Кодировка: {item.encoding}\n')
            f.write(f'  Статус: {item.status}\n')
            if item.error:
                f.write(f'  Ошибка: {item.error}\n')
            if item.functions:
                f.write('  Шапки функций:\n')
                for name in item.functions:
                    f.write(f'    - {name}\n')
            elif item.status == STATUS_OK:
                f.write('  Шапки функций: нет новых\n')
            f.write('\n')
