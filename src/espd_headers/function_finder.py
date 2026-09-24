"""Поиск определений функций в тексте C."""
import re

from .config import C_KEYWORDS

FUNC_PATTERN = re.compile(
    r'(?P<before>^|\n)\s*'
    r'(?:(?:static|inline|extern|volatile|const|__attribute__\s*\(\([^)]*(?:\([^)]*\)[^)]*)*\)\)|[A-Z_]+)\s+)*'
    r'(?P<ret>[a-zA-Z_]\w*(?:\s*[*\s]+[a-zA-Z_]\w*)*)(?P<sep>\s*\*+\s*|\s+)'
    r'(?P<name>[a-zA-Z_]\w*)\s*'
    r'\((?P<params>[^;{}]*?)\)\s*'
    r'(?P<brace>\{)',
    re.DOTALL | re.VERBOSE
)


def find_closing_brace(content, brace_pos):
    """Позиция за закрывающей '}' с учётом вложенности или None."""
    stack = 0
    for i in range(brace_pos, len(content)):
        ch = content[i]
        if ch == '{':
            stack += 1
        elif ch == '}':
            stack -= 1
            if stack == 0:
                return i + 1
    return None


def find_function_definitions(content):
    """
    Находит определения функций.
    Возвращает список (start, end, name, ret_type, params_str, body, signature).
    """
    funcs = []
    for match in FUNC_PATTERN.finditer(content):
        start = match.start()
        func_name = match.group('name')
        ret_type = match.group('ret').strip()
        if '*' in match.group('sep'):
            ret_type += ' ' + '*' * match.group('sep').count('*')
        params_str = match.group('params').strip()
        brace_pos = match.end('brace') - 1

        # Отсеиваем ложные срабатывания на управляющих конструкциях,
        # например "else if (cond) {".
        if func_name in C_KEYWORDS:
            continue
        ret_tokens = re.findall(r'[a-zA-Z_]\w*', ret_type)
        if ret_tokens and all(tok in C_KEYWORDS for tok in ret_tokens):
            continue

        end = find_closing_brace(content, brace_pos)
        if end is not None:
            signature = content[start:brace_pos+1].strip()
            body = content[brace_pos+1:end-1]
            funcs.append((start, end, func_name, ret_type, params_str, body, signature))
    return funcs
