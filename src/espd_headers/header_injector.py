"""Вставка шапок модуля и функций в текст файла."""
from .config import FUNC_HEADER_MARKER, FUNC_HEADER_LOOKBACK
from .function_finder import find_function_definitions
from .param_parser import parse_params
from .access_analyzer import analyze_function
from .header_builder import generate_sections, build_function_header, build_module_header
from .source_file import fit_encoding
from .run_log import log


def insert_module_header(content, header_text, filename, encoding):
    """Добавляет шапку модуля в начало файла, если её там ещё нет."""
    file_header = fit_encoding(build_module_header(header_text, filename), encoding)
    # сверка по первой содержательной строке шапки
    header_marker = file_header.strip().split('\n')[0]
    if not content.lstrip().startswith(header_marker):
        content = file_header + "\n" + content
    return content


def insert_function_headers(content, func_template, file_encoding):
    """Вставляет шаблон перед каждым определением функции."""
    funcs = find_function_definitions(content)
    if not funcs:
        return content, []

    # В обратном порядке, чтобы вставка не смещала позиции следующих функций
    funcs.sort(key=lambda x: x[0], reverse=True)
    new_content = content
    updated_funcs = []

    for start, end, func_name, ret_type, params_str, body, signature in funcs:
        # Защита от дублирования при повторном запуске
        marker = FUNC_HEADER_MARKER.format(funcname=func_name)
        lookback_start = max(0, start - FUNC_HEADER_LOOKBACK)
        if marker in new_content[lookback_start:start]:
            continue
        try:
            params = parse_params(params_str)
            params_modes, return_var, globals_modes = analyze_function(signature, body, params)
            if ret_type == 'void':
                return_var = None
            sections = generate_sections(params_modes, return_var, globals_modes)
            header_block = fit_encoding(build_function_header(func_template, func_name, *sections), file_encoding)
            new_content = new_content[:start] + header_block + new_content[start:]
            updated_funcs.append(func_name)
        except Exception as e:
            log.warning(f"Ошибка анализа функции {func_name}: {e}")
            # В случае ошибки вставляем базовую шапку без анализа
            header_block = build_function_header(func_template, func_name, '// None', '// None', '// None')
            try:
                header_block = fit_encoding(header_block, file_encoding)
                new_content = new_content[:start] + header_block + new_content[start:]
                updated_funcs.append(f"{func_name} (ошибка анализа)")
            except Exception:
                pass

    updated_funcs.reverse()  # в отчёте — в порядке следования в файле
    return new_content, updated_funcs
