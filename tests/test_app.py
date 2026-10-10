"""Тесты сборки приложения."""

import io
import os
import tempfile
import unittest
from dataclasses import dataclass

from shell_emulator.app import main


@dataclass
class Run:
    """Итог запуска: код возврата, stdout и stderr."""

    code: int
    out: str
    err: str


def run_emulator(argv, lines=()):
    """Запускает main на заданных строках и возвращает Run."""
    source = iter(lines)

    def read_line(prompt):
        """Отдаёт следующую строку или EOFError, как input()."""
        try:
            return next(source)
        except StopIteration:
            raise EOFError from None

    out, err = io.StringIO(), io.StringIO()
    code = main(argv, read_line, out, err)
    return Run(code, out.getvalue(), err.getvalue())


def write_file(folder, name, text):
    """Создаёт файл и возвращает его путь."""
    path = os.path.join(folder, name)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    return path


class MainTest(unittest.TestCase):
    """Проверки main."""

    def test_debug_output_without_params(self):
        """Отладочный вывод есть всегда."""
        run = run_emulator([])
        self.assertIn("[debug] параметры запуска:", run.out)
        self.assertEqual(run.code, 0)

    def test_debug_shows_given_paths(self):
        """Отладочный вывод содержит заданные пути."""
        with tempfile.TemporaryDirectory() as folder:
            script = write_file(folder, "a.emu", "ls first\n")
            run = run_emulator(["--vfs", folder, "--script", script])
        self.assertIn(f"--vfs    = {os.path.abspath(folder)}", run.out)
        self.assertIn(f"--script = {os.path.abspath(script)}", run.out)

    def test_script_then_interactive(self):
        """После успешного скрипта начинается диалог."""
        with tempfile.TemporaryDirectory() as folder:
            script = write_file(folder, "a.emu", "ls first\n")
            run = run_emulator(["--script", script], ["cd second"])
        self.assertIn("['first']", run.out)
        self.assertIn("['second']", run.out)
        self.assertEqual(run.code, 0)

    def test_script_error_ends_emulator(self):
        """Ошибка в скрипте завершает эмулятор, диалога нет."""
        with tempfile.TemporaryDirectory() as folder:
            script = write_file(folder, "b.emu", "bad\n")
            run = run_emulator(["--script", script], ["ls hidden"])
        self.assertEqual(run.code, 127)
        self.assertNotIn("hidden", run.out)

    def test_unreadable_script(self):
        """Скрипт не в UTF-8 даёт ошибку чтения."""
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "c.emu")
            with open(path, "wb") as handle:
                handle.write(b"\xff\xfe\x00bad")
            run = run_emulator(["--script", path])
        self.assertEqual(run.code, 1)
        self.assertIn("не удалось прочитать", run.err)


if __name__ == "__main__":
    unittest.main()
