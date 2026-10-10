"""Сборка приложения: параметры, стартовый скрипт, интерактивный режим."""

import sys

from shell_emulator.config import format_debug, parse_args
from shell_emulator.repl import run_repl
from shell_emulator.script import run_script_file


def print_debug(config, out):
    """Печатает все заданные параметры запуска."""
    for line in format_debug(config):
        out.write(line + "\n")
    out.flush()


def main(argv=None, read_line=input, out=None, err=None):
    """Запускает эмулятор и возвращает код возврата.

    Порядок: разбор параметров, отладочный вывод, стартовый скрипт
    (если задан), затем интерактивный диалог. Ошибка или exit в скрипте
    завершают эмулятор.
    """
    out = out or sys.stdout
    err = err or sys.stderr
    config = parse_args(argv)
    print_debug(config, out)
    if config.script_path is not None:
        outcome = run_script_file(config.script_path, out, err)
        if outcome.stop:
            return outcome.status
    return run_repl(read_line, out, err)
