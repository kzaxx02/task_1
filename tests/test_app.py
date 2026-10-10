"""Тесты сборки приложения."""

import io
import os
import tempfile
import unittest
from dataclasses import dataclass

from shell_emulator.app import main

ROOT_USER_ID = 0
NO_ACCESS_MODE = 0
OWNER_ONLY_MODE = 0o700


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

    def test_vfs_loaded_and_used(self):
        """С --vfs дерево загружается и доступно командам."""
        with tempfile.TemporaryDirectory() as folder:
            write_file(folder, "one.txt", "abc")
            run = run_emulator(["--vfs", folder], ["vfs-info", "exit"])
        self.assertIn("VFS загружена в память", run.out)
        self.assertIn("files: 1", run.out)
        self.assertIn("total size: 3 B", run.out)

    def test_vfs_command_without_vfs(self):
        """Без --vfs служебные команды сообщают об ошибке."""
        run = run_emulator([], ["vfs-info", "exit"])
        self.assertIn("VFS не подключена", run.err)

    def test_vfs_with_script(self):
        """Стартовый скрипт видит подключённую VFS."""
        with tempfile.TemporaryDirectory() as folder:
            write_file(folder, "one.txt", "abc")
            script = write_file(folder, "s.emu", "vfs-tree\n")
            run = run_emulator(
                ["--vfs", folder, "--script", script], ["exit"]
            )
        self.assertIn("one.txt (3 B)", run.out)

    @unittest.skipIf(
        not hasattr(os, "geteuid") or os.geteuid() == ROOT_USER_ID,
        "нужен обычный пользователь: root читает любые каталоги",
    )
    def test_vfs_unreadable_source(self):
        """Если источник нельзя прочитать, эмулятор сообщает и выходит."""
        with tempfile.TemporaryDirectory() as folder:
            os.chmod(folder, NO_ACCESS_MODE)
            try:
                run = run_emulator(["--vfs", folder])
            finally:
                os.chmod(folder, OWNER_ONLY_MODE)
        self.assertEqual(run.code, 1)
        self.assertIn("vfs: не удалось прочитать", run.err)


if __name__ == "__main__":
    unittest.main()
