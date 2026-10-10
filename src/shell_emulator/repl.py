"""Цикл чтение-выполнение-вывод (REPL)."""

import sys

from shell_emulator.commands import run_command
from shell_emulator.context import ShellContext
from shell_emulator.parser import ParseError, parse_line
from shell_emulator.prompt import build_prompt
from shell_emulator.results import OK_STATUS, Result, ShellExitError

SYNTAX_STATUS = 2


def execute_line(line, context):
    """Разбирает строку и выполняет команду; возвращает Result."""
    try:
        tokens = parse_line(line)
    except ParseError as error:
        return Result(
            error=f"syntax error: {error}", status=SYNTAX_STATUS
        )
    if not tokens:
        return Result()
    return run_command(tokens[0], tokens[1:], context)


def write_error(out, err, text):
    """Пишет строку в поток ошибок, сохраняя порядок с обычным выводом."""
    out.flush()
    err.write(text + "\n")
    err.flush()


def print_result(result, out, err):
    """Печатает stdout и stderr результата команды."""
    if result.output:
        out.write(result.output + "\n")
    out.flush()
    if result.error:
        write_error(out, err, result.error)


def report_exit(request, out, err):
    """Печатает сообщение о выходе, если оно есть."""
    if request.message:
        write_error(out, err, request.message)


def run_repl(
    read_line=input,
    out=None,
    err=None,
    make_prompt=build_prompt,
    context=None,
):
    """Запускает интерактивный диалог и возвращает код возврата.

    read_line - функция чтения строки (по умолчанию input),
    make_prompt - функция, формирующая приглашение,
    context - состояние сеанса (по умолчанию пустое, без VFS).
    """
    out = out or sys.stdout
    err = err or sys.stderr
    context = context or ShellContext()
    status = OK_STATUS
    while True:
        try:
            line = read_line(make_prompt())
        except EOFError:
            out.write("exit\n")
            return status
        except KeyboardInterrupt:
            out.write("\n")
            continue
        try:
            result = execute_line(line, context)
        except ShellExitError as request:
            report_exit(request, out, err)
            return request.code
        status = result.status
        print_result(result, out, err)
