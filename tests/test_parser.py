"""Тесты парсера командной строки."""

import unittest

from shell_emulator.parser import ParseError, parse_line


class ParseLineTest(unittest.TestCase):
    """Проверки функции parse_line."""

    def test_empty_line(self):
        """Пустая строка и пробелы дают пустой список."""
        self.assertEqual(parse_line(""), [])
        self.assertEqual(parse_line("   \t "), [])

    def test_simple_words(self):
        """Слова разделяются любым числом пробелов."""
        self.assertEqual(parse_line("ls   -l  /tmp"), ["ls", "-l", "/tmp"])

    def test_double_quotes(self):
        """Текст в двойных кавычках - одно слово."""
        self.assertEqual(parse_line('cd "my docs"'), ["cd", "my docs"])

    def test_single_quotes(self):
        """В одинарных кавычках всё буквально."""
        self.assertEqual(parse_line("ls 'a \\n \"b\"'"), ["ls", 'a \\n "b"'])

    def test_empty_quotes(self):
        """Пустые кавычки - пустой аргумент."""
        self.assertEqual(parse_line('ls "" x'), ["ls", "", "x"])

    def test_glued_quotes(self):
        """Соседние части склеиваются в одно слово."""
        self.assertEqual(parse_line("ls a\"b c\"'d e'"), ["ls", "ab cd e"])

    def test_escapes(self):
        """Экранирование внутри и вне кавычек."""
        self.assertEqual(parse_line('ls "a\\"b"'), ["ls", 'a"b'])
        self.assertEqual(parse_line("ls a\\ b"), ["ls", "a b"])
        self.assertEqual(parse_line('ls "a\\nb"'), ["ls", "a\\nb"])

    def test_unclosed_quote(self):
        """Незакрытая кавычка - ошибка."""
        with self.assertRaises(ParseError):
            parse_line('ls "abc')
        with self.assertRaises(ParseError):
            parse_line("ls 'abc")

    def test_trailing_backslash(self):
        """Обратная косая черта в конце - ошибка."""
        with self.assertRaises(ParseError):
            parse_line("ls abc\\")


if __name__ == "__main__":
    unittest.main()
