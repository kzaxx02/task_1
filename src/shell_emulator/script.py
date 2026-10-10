"""Выполнение стартового скрипта эмулятора."""

from dataclasses import dataclass

from shell_emulator.commands import OK_STATUS, ShellExitError
from shell_emulator.prompt import build_prompt
from shell_emulator.repl import (
    execute_line,
    print_result,
    report_exit,
    write_error,
)

COMMENT_MARK = "#"
FIRST_LINE_NUMBER = 1
READ_ERROR_STATUS = 1


@dataclass(frozen=True)
class ScriptOutcome:
    """Итог скрипта: код возврата и признак, что эмулятор надо завершить."""

    status: int = OK_STATUS
    stop: bool = False


def read_script(path):
    """Читает файл скрипта и возвращает список его строк."""
    with open(path, encoding="utf-8") as handle:
        return handle.read().splitlines()


def is_skipped(line):
    """Пустые строки и строки-комментарии не выполняются."""
    stripped = line.strip()
    return not stripped or stripped.startswith(COMMENT_MARK)


def run_script_line(line, number, out, err, make_prompt):
    """Выполняет строку; возвращает итог, если скрипт нужно остановить."""
    out.write(make_prompt() + line + "\n")
    try:
        result = execute_line(line)
    except ShellExitError as request:
        report_exit(request, out, err)
        return ScriptOutcome(request.code, True)
    print_result(result, out, err)
    if result.status != OK_STATUS:
        text = f"script: остановлен на строке {number} (код {result.status})"
        write_error(out, err, text)
        return ScriptOutcome(result.status, True)
    return None


def run_script(lines, out, err, make_prompt=build_prompt):
    """Выполняет строки скрипта, показывая ввод и вывод как диалог.

    Работа останавливается на первой ошибке (ненулевой код команды)
    или на команде exit.
    """
    numbered = enumerate(lines, FIRST_LINE_NUMBER)
    for number, line in numbered:
        if is_skipped(line):
            continue
        outcome = run_script_line(line, number, out, err, make_prompt)
        if outcome is not None:
            return outcome
    return ScriptOutcome()


def run_script_file(path, out, err, make_prompt=build_prompt):
    """Читает файл скрипта и выполняет его."""
    try:
        lines = read_script(path)
    except (OSError, UnicodeDecodeError) as error:
        write_error(out, err, f"script: не удалось прочитать: {error}")
        return ScriptOutcome(READ_ERROR_STATUS, True)
    return run_script(lines, out, err, make_prompt)
