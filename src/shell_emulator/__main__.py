"""Точка входа: python -m shell_emulator."""

import importlib
import sys

from shell_emulator.app import main


def enable_line_editing():
    """Подключает readline (стрелки, история), если он доступен."""
    try:
        importlib.import_module("readline")
    except ImportError:
        return


if __name__ == "__main__":
    enable_line_editing()
    sys.exit(main())
