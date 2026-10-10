"""Параметры командной строки эмулятора и их отладочный вывод."""

import argparse
import os
from dataclasses import dataclass
from typing import Optional

NOT_SET = "<не задан>"


@dataclass(frozen=True)
class Config:
    """Параметры запуска эмулятора."""

    vfs_path: Optional[str] = None
    script_path: Optional[str] = None


def existing_dir(value):
    """Проверяет, что value - каталог; возвращает абсолютный путь."""
    path = os.path.abspath(os.path.expanduser(value))
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(f"каталог не найден: {value}")
    return path


def existing_file(value):
    """Проверяет, что value - файл; возвращает абсолютный путь."""
    path = os.path.abspath(os.path.expanduser(value))
    if not os.path.isfile(path):
        raise argparse.ArgumentTypeError(f"файл не найден: {value}")
    return path


def build_arg_parser():
    """Создаёт разборщик аргументов командной строки."""
    parser = argparse.ArgumentParser(
        prog="shell_emulator",
        description="Эмулятор языка оболочки UNIX-подобной ОС.",
        allow_abbrev=False,
    )
    parser.add_argument(
        "--vfs",
        metavar="DIR",
        type=existing_dir,
        help="путь к физическому расположению VFS (каталог)",
    )
    parser.add_argument(
        "--script",
        metavar="FILE",
        type=existing_file,
        help="путь к стартовому скрипту с командами эмулятора",
    )
    return parser


def parse_args(argv=None):
    """Разбирает аргументы; при ошибке завершает программу с кодом 2."""
    namespace = build_arg_parser().parse_args(argv)
    return Config(vfs_path=namespace.vfs, script_path=namespace.script)


def format_debug(config):
    """Возвращает строки отладочного вывода всех параметров."""
    vfs = config.vfs_path or NOT_SET
    script = config.script_path or NOT_SET
    return [
        "[debug] параметры запуска:",
        f"[debug]   --vfs    = {vfs}",
        f"[debug]   --script = {script}",
    ]
