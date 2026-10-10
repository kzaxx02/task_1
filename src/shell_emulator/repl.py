"""Цикл чтение-выполнение-вывод (REPL)."""

import sys

from shell_emulator.commands import (
    OK_STATUS,
    Result,
    ShellExitError,
    run_command,
)
from shell_emulator.parser import ParseError, parse_line
from shell_emulator.prompt import build_prompt

SYNTAX_STATUS = 2


def execute_line(line):
    """Разбирает строку и выполняет команду; возвращает Result."""
    try:
        tokens = parse_line(line)
    except ParseError as error:
        return Result(
            error=f"syntax error: {error}", status=SYNTAX_STATUS
        )
    if not tokens:
        return Result()
    return run_command(tokens[0], tokens[1:])


def print_result(result, out, err):
    """Печатает stdout и stderr результата команды."""
    if result.output:
        out.write(result.output + "\n")
    if result.error:
        err.write(result.error + "\n")


def report_exit(request, err):
    """Печатает сообщение о выходе, если оно есть."""
    if request.message:
        err.write(request.message + "\n")


def run_repl(read_line=input, out=None, err=None, make_prompt=build_prompt):
    """Запускает интерактивный диалог и возвращает код возврата.

    read_line - функция чтения строки (по умолчанию input),
    make_prompt - функция, формирующая приглашение.
    """
    out = out or sys.stdout
    err = err or sys.stderr
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
            result = execute_line(line)
        except ShellExitError as request:
            report_exit(request, err)
            return request.code
        status = result.status
        print_result(result, out, err)
