"""Общие типы результатов выполнения команд и коды возврата."""

from dataclasses import dataclass

OK_STATUS = 0
GENERAL_ERROR_STATUS = 1
USAGE_STATUS = 2
NOT_FOUND_STATUS = 127


class ShellExitError(Exception):
    """Сигнал о завершении работы оболочки (команда exit)."""

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
