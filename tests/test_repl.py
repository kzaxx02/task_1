"""Тесты цикла REPL."""

import io
import unittest
from dataclasses import dataclass

from shell_emulator.repl import run_repl


@dataclass
class Run:
    """Итог запуска: код возврата, stdout и stderr."""

    code: int
    out: str
    err: str


def run_lines(lines):
    """Запускает REPL на заданных строках и возвращает Run."""
    source = iter(lines)

    def read_line(prompt):
        """Отдаёт следующую строку или EOFError, как input()."""
        try:
            return next(source)
        except StopIteration:
            raise EOFError from None

    out, err = io.StringIO(), io.StringIO()
    code = run_repl(
        read_line=read_line,
        out=out,
        err=err,
        make_prompt=lambda: "$ ",
    )
    return Run(code, out.getvalue(), err.getvalue())


class ReplTest(unittest.TestCase):
    """Проверки run_repl."""

    def test_exit(self):
        """exit завершает цикл."""
        run = run_lines(["exit"])
        self.assertEqual((run.code, run.out, run.err), (0, "", ""))

    def test_quoted_args(self):
        """Аргументы в кавычках доходят до команды целыми."""
        run = run_lines(['ls "my docs" a', "exit"])
        self.assertIn("arguments (2): ['my docs', 'a']", run.out)

    def test_syntax_error_does_not_stop(self):
        """После синтаксической ошибки работа продолжается."""
        run = run_lines(['ls "abc', "ls ok", "exit 5"])
        self.assertIn("syntax error", run.err)
        self.assertIn("arguments (1): ['ok']", run.out)
        self.assertEqual(run.code, 5)

    def test_empty_line_ignored(self):
        """Пустая строка ничего не делает."""
        run = run_lines(["", "   ", "exit"])
        self.assertEqual((run.code, run.out, run.err), (0, "", ""))

    def test_end_of_input(self):
        """Конец ввода (Ctrl+D) завершает работу."""
        run = run_lines([])
        self.assertEqual(run.out, "exit\n")
        self.assertEqual(run.code, 0)

    def test_interrupt(self):
        """Ctrl+C не завершает работу."""
        events = iter([KeyboardInterrupt(), "exit"])

        def read_line(prompt):
            """Возвращает строку или выбрасывает исключение."""
            event = next(events)
            if isinstance(event, BaseException):
                raise event
            return event

        out = io.StringIO()
        code = run_repl(read_line, out, io.StringIO(), lambda: "$ ")
        self.assertEqual(code, 0)
        self.assertEqual(out.getvalue(), "\n")


if __name__ == "__main__":
    unittest.main()
