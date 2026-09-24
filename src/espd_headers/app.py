"""Основной сценарий работы (как в espd_parser: ParserApp -> HeadersApp)."""
from __future__ import annotations

import os
import sys
from typing import Callable, Optional, Sequence

from . import __version__
from .app_paths import app_dir
from .cli import ask_confirmation, parse_options
from .config import APP_NAME, REPORT_SUFFIX
from .header_injector import insert_function_headers, insert_module_header
from .ignore_config import IgnoreConfig
from .reports import STATUS_ERROR, FileResult, write_report
from .run_dir import make_run_dir
from .run_log import RunLog, log
from .scanner import FoundFile, ProjectScanner
from .source_file import detect_write_encoding, read_source, write_source
from .templates import TemplateError, Templates, load_templates


class SaveError(Exception):
    """Результат не удалось записать на диск; текст — готовое сообщение для пользователя."""


def save_or_explain(description: str, path: str, save: Callable[[str], None]) -> None:
    try:
        save(path)
    except PermissionError:
        raise SaveError(
            f'Не удалось сохранить {description}: {path}\n'
            'Файл открыт в другой программе или нет прав на запись в папку. '
            'Закройте файл или укажите другую папку через --out и запустите программу снова.')
    except OSError as e:
        raise SaveError(f'Не удалось сохранить {description}: {path} ({e.strerror or e}).')


def process_file(found: FoundFile, templates: Templates) -> FileResult:
    """Вставляет шапки в один файл на месте."""
    result = FileResult(found.rel_path)
    try:
        encoding = detect_write_encoding(found.full_path)
        result.encoding = encoding
        content = read_source(found.full_path, encoding)
        content = insert_module_header(content, templates.module_header, found.name, encoding)
        if templates.func_header:
            content, result.functions = insert_function_headers(content, templates.func_header, encoding)
        write_source(found.full_path, content, encoding)
    except Exception as e:
        result.status = STATUS_ERROR
        result.error = str(e)
    return result


class HeadersApp:
    def __init__(self, argv: Optional[Sequence[str]] = None):
        self.app_dir = app_dir()
        self.options = parse_options(argv, self.app_dir)
        self.run_log = RunLog()

    @property
    def interactive(self) -> bool:
        return self.options.confirm

    def run(self) -> int:
        try:
            return self._run()
        except (SaveError, TemplateError) as e:
            log.error(str(e))
            return 1
        finally:
            self.run_log.close()

    def _run(self) -> int:
        opts = self.options
        if opts.root_explicit and not os.path.isdir(opts.root):
            log.error(f'Указанная папка проекта не найдена: {opts.root}')
            return 1

        log.info(f'{APP_NAME}, версия {__version__}')
        log.info(f'Папка программы: {self.app_dir}')
        log.info(f'Корневая папка проекта: {opts.root}')
        log.info(f'Папка результатов: {opts.save_dir}')

        templates = load_templates(self.app_dir)
        ignore = IgnoreConfig(self.app_dir)
        scanner = ProjectScanner(opts.root, ignore.load_dirs())
        files = scanner.find_files()
        if not files:
            log.warning(f'Не найдено файлов .c/.h в {opts.root}')
            return 0
        log.info(f'Найдено файлов: {len(files)}')

        if opts.confirm and not ask_confirmation(opts.root, len(files)):
            log.info('Отменено пользователем, файлы не изменены.')
            return 0

        run_dir = self._start_run_dir(ignore)
        results = []
        for found in files:
            result = process_file(found, templates)
            results.append(result)
            if result.status == STATUS_ERROR:
                log.error(f'{found.rel_path}: {result.error}')
            else:
                log.info(f'Обновлён: {found.rel_path} (кодировка: {result.encoding}, шапок функций: {len(result.functions)})')

        report_path = os.path.join(run_dir, f'{APP_NAME}_{REPORT_SUFFIX}.txt')
        save_or_explain('отчёт', report_path, lambda path: write_report(results, path))
        log.info(f'Отчёт сохранён: {report_path}')

        errors = sum(1 for r in results if r.status == STATUS_ERROR)
        functions = sum(len(r.functions) for r in results)
        log.info(f'Готово. Обработано файлов: {len(results) - errors}, с ошибками: {errors}, '
                 f'вставлено шапок функций: {functions}')
        return 1 if errors else 0

    def _start_run_dir(self, ignore: IgnoreConfig) -> str:
        try:
            run_dir = make_run_dir(self.options.save_dir, ignore.stem)
            self.run_log.attach_file(os.path.join(run_dir, f'{APP_NAME}_run.log'))
        except OSError as e:
            raise SaveError(
                f'Не удалось создать папку результатов в {self.options.save_dir} ({e.strerror or e}). '
                'Проверьте права на запись или укажите другую папку через --out.')
        log.info(f'Папка этого запуска: {run_dir}')
        return run_dir


def use_utf8_when_redirected() -> None:
    """Если вывод перенаправлен в файл (scripts\\run_checks.bat), пишем его в UTF-8."""
    for stream in (sys.stdout, sys.stderr):
        if stream is not None and hasattr(stream, 'reconfigure') and not stream.isatty():
            stream.reconfigure(encoding='utf-8')


def wait_for_enter() -> None:
    """При запуске двойным щелчком окно закрывается сразу — даём прочитать сообщение."""
    if sys.stdin is None or not sys.stdin.isatty():
        return
    try:
        input('\nНажмите Enter, чтобы закрыть окно.')
    except EOFError:
        pass


def main(argv: Optional[Sequence[str]] = None) -> None:
    use_utf8_when_redirected()
    app = HeadersApp(argv)
    code = app.run()
    if app.interactive:
        wait_for_enter()
    sys.exit(code)
