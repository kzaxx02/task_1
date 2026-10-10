"""Сборка приложения: параметры, VFS, стартовый скрипт, диалог."""

import sys

from shell_emulator.config import format_debug, parse_args
from shell_emulator.context import ShellContext
from shell_emulator.repl import run_repl, write_error
from shell_emulator.results import GENERAL_ERROR_STATUS
from shell_emulator.script import run_script_file
from shell_emulator.vfs import VfsError, load_vfs


def print_debug(config, out):
    """Печатает все заданные параметры запуска."""
    for line in format_debug(config):
        out.write(line + "\n")
    out.flush()


def create_context(config, out):
    """Создаёт состояние сеанса; при заданном --vfs загружает VFS в память."""
    if config.vfs_path is None:
        return ShellContext()
    vfs = load_vfs(config.vfs_path)
    stats = vfs.stats()
    out.write(
        "[debug] VFS загружена в память: "
        f"каталогов {stats.directories}, файлов {stats.files}, "
        f"{stats.total_bytes} B\n"
    )
    out.flush()
    return ShellContext(vfs=vfs)


def main(argv=None, read_line=input, out=None, err=None):
    """Запускает эмулятор и возвращает код возврата.

    Порядок: разбор параметров, отладочный вывод, загрузка VFS (если
    задана), стартовый скрипт (если задан), затем интерактивный диалог.
    Ошибка или exit в скрипте завершают эмулятор.
    """
    out = out or sys.stdout
    err = err or sys.stderr
    config = parse_args(argv)
    print_debug(config, out)
    try:
        context = create_context(config, out)
    except VfsError as error:
        write_error(out, err, f"vfs: {error}")
        return GENERAL_ERROR_STATUS
    if config.script_path is not None:
        outcome = run_script_file(
            config.script_path, out, err, context=context
        )
        if outcome.stop:
            return outcome.status
    return run_repl(read_line, out, err, context=context)
