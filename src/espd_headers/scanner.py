"""Обход проекта и поиск исходных файлов (как в espd_parser)."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable, List, Sequence

from .config import SOURCE_EXTENSIONS


@dataclass
class FoundFile:
    rel_dir: str
    name: str
    full_path: str

    @property
    def rel_path(self) -> str:
        return os.path.join(self.rel_dir, self.name) if self.rel_dir else self.name


class ProjectScanner:
    def __init__(self, root: str, ignore_dirs: Iterable[str], extensions: Sequence[str] = SOURCE_EXTENSIONS):
        self.root = root
        self.ignore_dirs = set(ignore_dirs)
        self.extensions = tuple(extensions)

    def find_files(self) -> List[FoundFile]:
        """Все файлы с нужными расширениями, кроме исключённых папок (на любом уровне), по пути."""
        found = []
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames[:] = [d for d in dirnames if d not in self.ignore_dirs]
            rel_dir = os.path.relpath(dirpath, self.root)
            if rel_dir == '.':
                rel_dir = ''
            for name in filenames:
                if name.endswith(self.extensions):
                    found.append(FoundFile(rel_dir, name, os.path.join(dirpath, name)))
        found.sort(key=lambda f: f.rel_path.lower())
        return found
