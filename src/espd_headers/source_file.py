"""Определение кодировки, чтение и запись исходного файла."""
import sys

from .config import ENCODINGS_TO_TRY, CHARDET_MIN_CONFIDENCE, CHARDET_SAMPLE_SIZE

try:
    import chardet
    HAS_CHARDET = True
except ImportError:
    HAS_CHARDET = False
    print("Предупреждение: chardet не установлен. Будет использован перебор кодировок.", file=sys.stderr)


def detect_encoding(file_path):
    """Определяет кодировку файла."""
    if HAS_CHARDET:
        with open(file_path, 'rb') as f:
            raw_data = f.read(CHARDET_SAMPLE_SIZE)
            result = chardet.detect(raw_data)
            encoding = result.get('encoding')
            confidence = result.get('confidence')
            if encoding and confidence > CHARDET_MIN_CONFIDENCE:
                return encoding

    for enc in ENCODINGS_TO_TRY:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                f.read()
            return enc
        except UnicodeDecodeError:
            continue
    return 'utf-8'


def detect_write_encoding(file_path):
    """Кодировка для чтения и записи файла.

    Файл без не-ASCII байт корректно читается и в utf-8 (ascii - его
    подмножество), а шапки на кириллице при этом не превращаются в "????".
    """
    encoding = detect_encoding(file_path)
    if encoding and encoding.lower() in ('ascii', 'us-ascii'):
        encoding = 'utf-8'
    return encoding


def read_source(file_path, encoding):
    with open(file_path, 'r', encoding=encoding) as f:
        return f.read()


def write_source(file_path, content, encoding):
    with open(file_path, 'w', encoding=encoding) as f:
        f.write(content)


def fit_encoding(text, encoding):
    """Приводит текст к набору символов кодировки файла (с заменой)."""
    return text.encode(encoding, errors='replace').decode(encoding, errors='replace')
