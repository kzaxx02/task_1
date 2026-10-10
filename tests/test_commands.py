"""Тесты команд эмулятора."""

import unittest

from shell_emulator.commands import run_command
from shell_emulator.context import ShellContext
from shell_emulator.results import (
    NOT_FOUND_STATUS,
    USAGE_STATUS,
    ShellExitError,
)


class CommandsTest(unittest.TestCase):
    """Проверки run_command для команд без VFS."""

    def test_ls_stub(self):
        """ls выводит своё имя и аргументы."""
        result = run_command("ls", ["-l", "my docs"], ShellContext())
        self.assertIn("command: ls", result.output)
        self.assertIn("['-l', 'my docs']", result.output)

    def test_cd_stub_without_args(self):
        """cd без аргументов выводит пустой список."""
        result = run_command("cd", [], ShellContext())
        self.assertIn("command: cd", result.output)
        self.assertIn("arguments (0): []", result.output)

    def test_unknown_command(self):
        """Неизвестная команда даёт ошибку и статус 127."""
        result = run_command("foo", [], ShellContext())
        self.assertEqual(result.error, "foo: command not found")
        self.assertEqual(result.status, NOT_FOUND_STATUS)

    def test_exit_default(self):
        """exit без аргументов завершает работу с кодом 0."""
        with self.assertRaises(ShellExitError) as caught:
            run_command("exit", [], ShellContext())
        self.assertEqual(caught.exception.code, 0)

    def test_exit_with_code(self):
        """exit N завершает работу с кодом N."""
        with self.assertRaises(ShellExitError) as caught:
            run_command("exit", ["3"], ShellContext())
        self.assertEqual(caught.exception.code, 3)

    def test_exit_bad_code(self):
        """exit с нечисловым аргументом - ошибка и код 2."""
        with self.assertRaises(ShellExitError) as caught:
            run_command("exit", ["abc"], ShellContext())
        self.assertEqual(caught.exception.code, USAGE_STATUS)
        self.assertIn("numeric argument required", caught.exception.message)

    def test_exit_too_many_args(self):
        """exit с двумя аргументами не завершает работу."""
        result = run_command("exit", ["1", "2"], ShellContext())
        self.assertEqual(result.error, "exit: too many arguments")
        self.assertEqual(result.status, USAGE_STATUS)


if __name__ == "__main__":
    unittest.main()
