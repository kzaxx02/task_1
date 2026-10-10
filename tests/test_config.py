"""Тесты разбора параметров командной строки."""

import contextlib
import io
import os
import tempfile
import unittest

from shell_emulator.config import NOT_SET, Config, format_debug, parse_args


def parse_quietly(argv):
    """Разбирает argv, скрывая сообщения argparse; возвращает код выхода."""
    with contextlib.redirect_stderr(io.StringIO()):
        with contextlib.redirect_stdout(io.StringIO()):
            try:
                parse_args(argv)
            except SystemExit as stop:
                return stop.code
    return None


class ParseArgsTest(unittest.TestCase):
    """Проверки parse_args и format_debug."""

    def test_no_arguments(self):
        """Без параметров всё не задано."""
        self.assertEqual(parse_args([]), Config())

    def test_valid_arguments(self):
        """Существующие каталог и файл принимаются как абсолютные пути."""
        with tempfile.TemporaryDirectory() as folder:
            script = os.path.join(folder, "start.emu")
            open(script, "w", encoding="utf-8").close()
            config = parse_args(["--vfs", folder, "--script", script])
        self.assertEqual(config.vfs_path, os.path.abspath(folder))
        self.assertEqual(config.script_path, os.path.abspath(script))

    def test_missing_vfs(self):
        """Несуществующий каталог VFS - ошибка с кодом 2."""
        self.assertEqual(parse_quietly(["--vfs", "/no/such/dir"]), 2)

    def test_missing_script(self):
        """Несуществующий скрипт - ошибка с кодом 2."""
        self.assertEqual(parse_quietly(["--script", "/no/such.emu"]), 2)

    def test_unknown_and_abbreviated(self):
        """Неизвестные и сокращённые параметры отвергаются."""
        self.assertEqual(parse_quietly(["--foo"]), 2)
        self.assertEqual(parse_quietly(["--vf", "."]), 2)

    def test_missing_value(self):
        """Параметр без значения - ошибка."""
        self.assertEqual(parse_quietly(["--vfs"]), 2)

    def test_debug_lists_all(self):
        """Отладочный вывод содержит все параметры."""
        text = "\n".join(format_debug(Config("/v", None)))
        self.assertIn("--vfs    = /v", text)
        self.assertIn("--script = " + NOT_SET, text)


if __name__ == "__main__":
    unittest.main()
