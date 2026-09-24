"""Чтение шаблонов шапок из папки templates рядом с программой."""
from __future__ import annotations

import os
from dataclasses import dataclass

from .config import TEMPLATES_DIR, HEADER_FILE_NAME, FUNC_HEADER_FILE_NAME
from .run_log import log


class TemplateError(Exception):
    """Шаблон не удалось прочитать; текст — готовое сообщение для пользователя."""


@dataclass
class Templates:
    module_header: str
    func_header: str   # пустая строка — шапки функций не вставляются


def _read(path: str) -> str:
    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            return f.read()
    except OSError as e:
        raise TemplateError(f'Не удалось прочитать шаблон {path} ({e.strerror or e}).')
    except UnicodeDecodeError:
        raise TemplateError(f'Шаблон {path} должен быть сохранён в UTF-8.')


def load_templates(app_dir: str) -> Templates:
    folder = os.path.join(app_dir, TEMPLATES_DIR)
    header_path = os.path.join(folder, HEADER_FILE_NAME)
    func_path = os.path.join(folder, FUNC_HEADER_FILE_NAME)

    if not os.path.isfile(header_path):
        raise TemplateError(f'Не найден шаблон шапки модуля: {header_path}')
    module_header = _read(header_path)
    if not module_header.strip():
        raise TemplateError(f'Шаблон шапки модуля пуст: {header_path}')

    func_header = ''
    if not os.path.isfile(func_path):
        log.warning(f'Не найден шаблон шапки функции {func_path}. Шапки функций не вставляются.')
    else:
        func_header = _read(func_path)
        if not func_header.strip():
            log.warning(f'Шаблон шапки функции пуст: {func_path}. Шапки функций не вставляются.')
            func_header = ''
    log.info(f'Шаблоны: {folder}')
    return Templates(module_header, func_header)
