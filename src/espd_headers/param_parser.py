"""Разбор списка параметров функции."""
import re

from .config import PARAM_QUALIFIERS


def split_top_level(text, open_chars='(', close_chars=')'):
    """Делит строку по запятым верхнего уровня вложенности."""
    parts = []
    depth = 0
    current = []
    for ch in text:
        if ch == ',' and depth == 0:
            parts.append(''.join(current).strip())
            current = []
        else:
            if ch in open_chars:
                depth += 1
            elif ch in close_chars:
                depth -= 1
            current.append(ch)
    if current:
        parts.append(''.join(current).strip())
    return parts


def parse_params(params_str):
    """Возвращает список (тип, имя) параметров."""
    if not isinstance(params_str, str):
        return []
    params_str = params_str.strip()
    if not params_str or re.match(r'^\s*void\s*$', params_str):
        return []

    params = []
    for p in split_top_level(params_str):
        if not p:
            continue
        # Имя параметра — последний идентификатор в строке
        name = None
        for m in re.finditer(r'[a-zA-Z_]\w*', p):
            token = m.group(0)
            if token in PARAM_QUALIFIERS:
                continue
            name = token
            name_start = m.start()

        if name:
            type_str = p[:name_start].strip()
            type_str = re.sub(r'\s+', ' ', type_str)
            params.append((type_str, name))
        else:
            params.append((p, ""))
    return params
