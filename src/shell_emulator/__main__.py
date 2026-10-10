"""Точка входа: python -m shell_emulator."""

import importlib
import sys

from shell_emulator.repl import run_repl


def enable_line_editing():
    """Подключает readline (стрелки, история), если он доступен."""
    try:
        importlib.import_module("readline")
    except ImportError:
        return


def main():
    """Запускает эмулятор и возвращает код возврата."""
    enable_line_editing()
    return run_repl()


if __name__ == "__main__":
    sys.exit(main())
