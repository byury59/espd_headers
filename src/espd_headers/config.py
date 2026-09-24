"""Константы программы: расширения, исключения, ключевые слова, имена файлов."""

APP_NAME = 'espd_headers'
RESULTS_DIR_NAME = 'Результаты'

# Файлы рядом с программой
TEMPLATES_DIR = 'templates'
HEADER_FILE_NAME = 'header.txt'
FUNC_HEADER_FILE_NAME = 'header_func.txt'
IGNORE_FILE_NAME = 'ignore.txt'

# Отчёт в папке запуска
REPORT_SUFFIX = 'Шапки'

# Обрабатываемые расширения
SOURCE_EXTENSIONS = ('.c', '.h', '.C', '.H')

# Кодировки для перебора, если chardet не дал уверенного ответа
ENCODINGS_TO_TRY = ['utf-8', 'cp1251', 'koi8-r', 'latin1', 'iso-8859-1']

# Порог уверенности chardet
CHARDET_MIN_CONFIDENCE = 0.5

# Сколько байт отдаётся chardet
CHARDET_SAMPLE_SIZE = 10000

# Ключевые слова C/C++, которые не могут быть именем функции или её типом
# возврата. Нужны, чтобы отсеять ложные срабатывания парсера функций на
# управляющих конструкциях вида "else if (cond) {", "for (...) {" и т.п.
C_KEYWORDS = {
    'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'default',
    'return', 'goto', 'break', 'continue', 'sizeof', 'typedef',
    'struct', 'union', 'enum'
}

# Квалификаторы, которые пропускаются при поиске имени параметра
PARAM_QUALIFIERS = ('const', 'volatile', 'static', 'extern', 'inline', 'void')

# Квалификаторы, которые не могут быть именем локальной переменной
DECL_QUALIFIERS = ('const', 'volatile', 'static', 'extern', 'inline')

# Базовые типы для распознавания объявлений локальных переменных
TYPE_KEYWORDS = (r'(?:int|char|float|double|long|short|unsigned|signed|void|struct|union|enum|'
                 r'int8_t|uint8_t|int16_t|uint16_t|int32_t|uint32_t|int64_t|uint64_t|'
                 r'size_t|ptrdiff_t|time_t|clock_t|bool|boolean)')

# Служебные слова, исключаемые из списка глобальных переменных
NON_VARIABLE_WORDS = {
    'int', 'char', 'float', 'double', 'void', 'long', 'short', 'unsigned', 'signed',
    'struct', 'union', 'enum', 'const', 'volatile', 'static', 'extern', 'inline',
    'return', 'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break', 'continue',
    'sizeof', 'typedef', 'goto', 'default', 'NULL', 'true', 'false',
    'int8_t', 'uint8_t', 'int16_t', 'uint16_t', 'int32_t', 'uint32_t',
    'int64_t', 'uint64_t', 'size_t', 'ptrdiff_t', 'time_t', 'clock_t',
    'bool', 'boolean'
}

# Маркер защиты от дублей шапки функции (должен совпадать с header_func.txt)
FUNC_HEADER_MARKER = "// Name:     {funcname}\n"

# Сколько символов перед функцией просматривается в поиске маркера
FUNC_HEADER_LOOKBACK = 2000
