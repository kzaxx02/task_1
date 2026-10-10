"""Тесты выполнения стартового скрипта."""

import io
import unittest
from dataclasses import dataclass

from shell_emulator.script import ScriptOutcome, run_script


@dataclass
class Run:
    """Итог запуска: итог скрипта, stdout и stderr."""

    outcome: ScriptOutcome
    out: str
    err: str


def run_lines(lines):
    """Выполняет скрипт и возвращает Run."""
    out, err = io.StringIO(), io.StringIO()
    outcome = run_script(lines, out, err, lambda: "$ ")
    return Run(outcome, out.getvalue(), err.getvalue())


class RunScriptTest(unittest.TestCase):
    """Проверки run_script."""

    def test_shows_input_and_output(self):
        """На экране видны и ввод, и вывод."""
        run = run_lines(['ls "a b"'])
        self.assertIn("$ ls \"a b\"\n", run.out)
        self.assertIn("arguments (1): ['a b']", run.out)
        self.assertFalse(run.outcome.stop)

    def test_skips_blank_and_comments(self):
        """Пустые строки и комментарии не выполняются и не печатаются."""
        run = run_lines(["", "   ", "# заметка", "cd x"])
        self.assertNotIn("заметка", run.out)
        self.assertEqual(run.out.count("$ "), 1)
        self.assertEqual(run.err, "")

    def test_stops_on_first_error(self):
        """После первой ошибки остальные строки не выполняются."""
        run = run_lines(["ls one", "bad", "ls never"])
        self.assertTrue(run.outcome.stop)
        self.assertEqual(run.outcome.status, 127)
        self.assertNotIn("never", run.out)
        self.assertIn("bad: command not found", run.err)
        self.assertIn("остановлен на строке 2", run.err)

    def test_stops_on_syntax_error(self):
        """Синтаксическая ошибка тоже останавливает скрипт."""
        run = run_lines(['ls "oops', "ls never"])
        self.assertEqual(run.outcome.status, 2)
        self.assertNotIn("never", run.out)

    def test_exit_stops(self):
        """exit в скрипте завершает эмулятор с заданным кодом."""
        run = run_lines(["exit 7", "ls never"])
        self.assertEqual(run.outcome, ScriptOutcome(7, True))
        self.assertNotIn("never", run.out)


if __name__ == "__main__":
    unittest.main()
