"""Команды эмулятора: заглушки ls и cd, а также команда exit."""

from dataclasses import dataclass

OK_STATUS = 0
USAGE_STATUS = 2
NOT_FOUND_STATUS = 127
EXIT_MAX_ARGS = 1
EXIT_CODE_MODULO = 256


class ShellExitError(Exception):
    """Сигнал о завершении работы оболочки."""

    def __init__(self, code=OK_STATUS, message=""):
        """Запоминает код возврата и необязательное сообщение."""
        super().__init__(code)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class Result:
    """Результат выполнения команды."""

    output: str = ""
    error: str = ""
    status: int = OK_STATUS


def describe_stub(name, args):
    """Формирует вывод заглушки: имя команды и её аргументы."""
    text = f"command: {name}\narguments ({len(args)}): {args!r}"
    return Result(output=text)


def handle_ls(args):
    """Заглушка команды ls."""
    return describe_stub("ls", args)


def handle_cd(args):
    """Заглушка команды cd."""
    return describe_stub("cd", args)


def handle_exit(args):
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
}


def run_command(name, args):
    """Находит команду по имени и выполняет её."""
    handler = COMMANDS.get(name)
    if handler is None:
        return Result(
            error=f"{name}: command not found", status=NOT_FOUND_STATUS
        )
    return handler(args)
