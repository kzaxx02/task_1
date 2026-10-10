"""Реестр команд: заглушки ls и cd, команда exit, служебные команды VFS."""

from shell_emulator.results import (
    NOT_FOUND_STATUS,
    OK_STATUS,
    USAGE_STATUS,
    Result,
    ShellExitError,
)
from shell_emulator.vfs_commands import handle_vfs_info, handle_vfs_tree

EXIT_MAX_ARGS = 1
EXIT_CODE_MODULO = 256


def describe_stub(name, args):
    """Формирует вывод заглушки: имя команды и её аргументы."""
    text = f"command: {name}\narguments ({len(args)}): {args!r}"
    return Result(output=text)


def handle_ls(args, context):
    """Заглушка команды ls."""
    return describe_stub("ls", args)


def handle_cd(args, context):
    """Заглушка команды cd."""
    return describe_stub("cd", args)


def handle_exit(args, context):
    """Завершает работу оболочки; необязательный аргумент - код возврата."""
    if len(args) > EXIT_MAX_ARGS:
        return Result(error="exit: too many arguments", status=USAGE_STATUS)
    if not args:
        raise ShellExitError(OK_STATUS)
    try:
        code = int(args[0])
    except ValueError:
        message = f"exit: {args[0]}: numeric argument required"
        raise ShellExitError(USAGE_STATUS, message) from None
    raise ShellExitError(code % EXIT_CODE_MODULO)


COMMANDS = {
    "ls": handle_ls,
    "cd": handle_cd,
    "exit": handle_exit,
    "vfs-info": handle_vfs_info,
    "vfs-tree": handle_vfs_tree,
}


def run_command(name, args, context):
    """Находит команду по имени и выполняет её в контексте сеанса."""
    handler = COMMANDS.get(name)
    if handler is None:
        return Result(
            error=f"{name}: command not found", status=NOT_FOUND_STATUS
        )
    return handler(args, context)
