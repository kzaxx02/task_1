"""Тесты служебных команд VFS."""

import contextlib
import tempfile
import unittest

from shell_emulator.commands import run_command
from shell_emulator.context import ShellContext
from shell_emulator.results import GENERAL_ERROR_STATUS, USAGE_STATUS
from shell_emulator.vfs import load_vfs
from test_vfs import SAMPLE_FILES, build_tree


@contextlib.contextmanager
def sample_context():
    """Создаёт дерево на диске и отдаёт (каталог, контекст с VFS)."""
    with tempfile.TemporaryDirectory() as folder:
        build_tree(folder, SAMPLE_FILES)
        yield folder, ShellContext(vfs=load_vfs(folder))


class VfsCommandsTest(unittest.TestCase):
    """Проверки vfs-info и vfs-tree."""

    def test_info(self):
        """vfs-info показывает источник и сводку."""
        with sample_context() as (folder, context):
            result = run_command("vfs-info", [], context)
        self.assertIn(f"source: {folder}", result.output)
        self.assertIn("directories: 2", result.output)
        self.assertIn("files: 3", result.output)
        self.assertIn("total size: 10 B", result.output)
        self.assertIn("max depth: 3", result.output)

    def test_info_too_many_args(self):
        """vfs-info не принимает аргументов."""
        with sample_context() as (folder, context):
            result = run_command("vfs-info", ["x"], context)
        self.assertEqual(result.status, USAGE_STATUS)

    def test_tree_default_and_path(self):
        """vfs-tree без аргументов печатает всё, с путём - часть."""
        with sample_context() as (folder, context):
            whole = run_command("vfs-tree", [], context)
            part = run_command("vfs-tree", ["/docs"], context)
        self.assertTrue(whole.output.startswith("/\n"))
        self.assertTrue(part.output.startswith("/docs\n"))
        self.assertNotIn("a.txt", part.output)

    def test_tree_missing_path(self):
        """Несуществующий путь - ошибка со статусом 1."""
        with sample_context() as (folder, context):
            result = run_command("vfs-tree", ["/nope"], context)
        self.assertEqual(result.status, GENERAL_ERROR_STATUS)
        self.assertIn("vfs-tree: /nope: No such file", result.error)

    def test_tree_too_many_args(self):
        """Два аргумента - ошибка использования."""
        with sample_context() as (folder, context):
            result = run_command("vfs-tree", ["a", "b"], context)
        self.assertEqual(result.status, USAGE_STATUS)

    def test_without_vfs(self):
        """Без VFS обе команды сообщают об ошибке."""
        for name in ("vfs-info", "vfs-tree"):
            result = run_command(name, [], ShellContext())
            self.assertEqual(result.status, GENERAL_ERROR_STATUS, name)
            self.assertIn("VFS не подключена", result.error)


if __name__ == "__main__":
    unittest.main()
