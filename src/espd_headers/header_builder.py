"""Построение текста шапок по шаблонам."""


def generate_sections(params_modes, return_var, globals_modes):
    """Строки для разделов Parameters, Return value, External data."""
    params_str = "\n".join([f"// {name} ({mode}) - " for name, mode in params_modes.items()]) if params_modes else "// None"
    ret_str = f"// {return_var} (out) - " if return_var else "// None"
    ext_str = "\n".join([f"// {name} ({mode}) - " for name, mode in globals_modes.items()]) if globals_modes else "// None"
    return params_str, ret_str, ext_str


def build_function_header(func_template, func_name, params_lines, ret_lines, ext_lines):
    header_block = func_template.replace('{funcname}', func_name)
    header_block = header_block.replace('{PARAMS}', params_lines)
    header_block = header_block.replace('{RETURN}', ret_lines)
    header_block = header_block.replace('{EXTERNAL}', ext_lines)
    return header_block


def build_module_header(header_text, filename):
    return header_text.replace('{filename}', filename)
