"""Чтение ignore.txt: список исключаемых папок (как в espd_parser, но режим один)."""
from __future__ import annotations

import codecs
import os
from typing import List, Optional

from .config import IGNORE_FILE_NAME
from .run_log import log

COMMENT_PREFIXES = ('#', '//')
INLINE_COMMENT_MARKERS = (' // ', ' # ', '//', '#')


def _decode(raw: bytes) -> Optional[str]:
    """UTF-8 (с BOM или без) или Windows-1251."""
    if raw.startswith(codecs.BOM_UTF8):
        raw = raw[len(codecs.BOM_UTF8):]
    for encoding in ('utf-8', 'cp1251'):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return None


class IgnoreConfig:
    """ignore.txt рядом с программой."""

    def __init__(self, app_dir: str):
        self.path = os.path.join(app_dir, IGNORE_FILE_NAME)

    @property
    def stem(self) -> str:
        return os.path.splitext(os.path.basename(self.path))[0]

    def exists(self) -> bool:
        return os.path.isfile(self.path)

    def load_dirs(self) -> List[str]:
        if not self.exists():
            log.warning(f'Файл {self.path} не найден. Папки не исключаются.')
            return []
        try:
            with open(self.path, 'rb') as f:
                text = _decode(f.read())
        except OSError as e:
            log.error(f'Ошибка чтения {self.path}: {e}. Папки не исключаются.')
            return []
        if text is None:
            log.error(f'Не удалось определить кодировку {self.path}. Папки не исключаются.')
            return []

        dirs = []
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith(COMMENT_PREFIXES):
                continue
            for marker in INLINE_COMMENT_MARKERS:
                if marker in line:
                    line = line.split(marker, 1)[0].strip()
                    break
            if line:
                dirs.append(line)

        if dirs:
            log.info(f'Загружены исключения из {self.path}: {dirs}')
        else:
            log.info(f'Файл {self.path} не содержит папок (только комментарии). Папки не исключаются.')
        return dirs
