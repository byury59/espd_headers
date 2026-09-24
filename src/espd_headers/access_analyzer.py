"""Анализ доступа: режимы параметров и глобальных переменных, возвращаемая переменная."""
import re

from .config import TYPE_KEYWORDS, DECL_QUALIFIERS, NON_VARIABLE_WORDS
from .lexer import strip_literals_and_comments
from .param_parser import parse_params, split_top_level


def is_variable_written(var_name, body):
    """Проверяет, производится ли запись в переменную var_name в теле функции."""
    v = re.escape(var_name)
    # 1. Прямое или составное присваивание (исключая ==, !=)
    if re.search(rf'\b{v}\s*(?:[\+\-\*/\%\&\|\^]?=(?!=))', body):
        return True
    # 2. Разыменование указателя: *var =
    if re.search(rf'\*\s*{v}\s*=', body):
        return True
    # 3. Инкремент/декремент
    if re.search(rf'(?:\+\+|--)\s*{v}\b|\b{v}\s*(?:\+\+|--)', body):
        return True
    # 4. Присваивание элементу массива: var[...] =
    if re.search(rf'\b{v}\s*\[.*?\]\s*=', body):
        return True
    return False


def extract_local_vars(body):
    """Извлекает имена локальных переменных, включая объявления в циклах for."""
    local_vars = set()
    decl_pattern = re.compile(
        r'\b(' + TYPE_KEYWORDS + r'(?:\s+(?:const|volatile|unsigned|signed|struct|union|enum|long|short|int|char|float|double|[*])+)*)\s+([^;]+);',
        re.DOTALL
    )
    for match in decl_pattern.finditer(body):
        decl_part = match.group(2).strip()
        for part in split_top_level(decl_part, '({[', ')}]'):
            if '=' in part:
                part = part.split('=')[0].strip()
            part = part.lstrip('*').strip()
            part = re.sub(r'\[[^\]]*\]', '', part).strip()
            words = re.findall(r'[a-zA-Z_]\w*', part)
            if words:
                var_name = words[-1]
                if var_name not in DECL_QUALIFIERS:
                    local_vars.add(var_name)

    for_pattern = re.compile(r'\bfor\s*\(\s*(?:' + TYPE_KEYWORDS + r'(?:\s+[*\w]+)*)\s+([a-zA-Z_]\w*)\s*=')
    for match in for_pattern.finditer(body):
        local_vars.add(match.group(1))
    return local_vars


def _normalize_params(params):
    safe_params = []
    try:
        if isinstance(params, list):
            for item in params:
                if isinstance(item, tuple) and len(item) == 2:
                    safe_params.append(item)
                elif isinstance(item, str):
                    safe_params.append(('', item))
        elif isinstance(params, str):
            safe_params = parse_params(params)
    except Exception:
        safe_params = []
    return safe_params


def param_modes(params, body):
    param_names = [name for _, name in params if name]
    param_is_ptr = {name: '*' in t for t, name in params if name}
    modes = {}
    for name in param_names:
        if is_variable_written(name, body):
            if param_is_ptr.get(name, False):
                # есть чтение (*name не слева от =) -> in/out, иначе out
                if re.search(rf'\*\s*{re.escape(name)}(?!\s*[\+\-\*/\%\&\|\^]?=(?!=))', body):
                    modes[name] = 'in/out'
                else:
                    modes[name] = 'out'
            else:
                modes[name] = 'in/out'
        else:
            modes[name] = 'in'
    return modes


def find_return_var(body):
    matches = re.compile(r'\breturn\s+([a-zA-Z_]\w*)\s*;').findall(body)
    return matches[0] if matches else None


def global_modes(body, param_names):
    body_no_literals = strip_literals_and_comments(body)
    local_vars = extract_local_vars(body_no_literals)
    all_identifiers = set(re.findall(r'\b([a-zA-Z_]\w*)\b', body_no_literals))
    potential_globals = all_identifiers - set(param_names) - local_vars - NON_VARIABLE_WORDS

    # Исключаем вызовы функций
    global_vars = set()
    for var in potential_globals:
        if not re.search(rf'\b{re.escape(var)}\s*\(', body):
            global_vars.add(var)

    modes = {}
    for var in global_vars:
        modes[var] = 'in/out' if is_variable_written(var, body) else 'in'
    return modes


def analyze_function(signature, body, params):
    """Возвращает (режимы параметров, возвращаемая переменная, режимы глобалей)."""
    params = _normalize_params(params)
    param_names = [name for _, name in params if name]
    return param_modes(params, body), find_return_var(body), global_modes(body, param_names)
