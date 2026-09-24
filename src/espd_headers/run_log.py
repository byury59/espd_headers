import logging
import sys
from logging.handlers import MemoryHandler

log = logging.getLogger('espd_headers')

FILE_FORMAT = '%(asctime)s %(levelname)-7s %(message)s'
FILE_DATE_FORMAT = '%d.%m.%Y %H:%M:%S'


class ConsoleFormatter(logging.Formatter):
    PREFIXES = {
        logging.WARNING: 'ВНИМАНИЕ: ',
        logging.ERROR: 'ОШИБКА: ',
        logging.CRITICAL: 'ОШИБКА: ',
    }

    def format(self, record: logging.LogRecord) -> str:
        return self.PREFIXES.get(record.levelno, '') + record.getMessage()


class RunLog:
    """Журнал работы: сразу пишет в консоль, а в файл — после того,
    как создана папка результатов (всё, что было до этого, буферизуется)."""

    def __init__(self):
        log.setLevel(logging.DEBUG)
        log.propagate = False
        for handler in list(log.handlers):
            log.removeHandler(handler)

        console = logging.StreamHandler(sys.stdout)
        console.setLevel(logging.INFO)
        console.setFormatter(ConsoleFormatter())
        log.addHandler(console)

        self._buffer = MemoryHandler(capacity=100000, flushLevel=logging.CRITICAL + 1)
        log.addHandler(self._buffer)
        self._file = None

    def attach_file(self, path: str) -> None:
        file_handler = logging.FileHandler(path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(FILE_FORMAT, FILE_DATE_FORMAT))

        self._buffer.setTarget(file_handler)
        self._buffer.flush()
        self._buffer.setTarget(None)
        log.removeHandler(self._buffer)

        log.addHandler(file_handler)
        self._file = file_handler

    def close(self) -> None:
        log.removeHandler(self._buffer)
        if self._file is not None:
            log.removeHandler(self._file)
            self._file.close()
            self._file = None
