"""Парсер командной строки с поддержкой кавычек и экранирования."""

SINGLE_QUOTE = "'"
DOUBLE_QUOTE = '"'
ESCAPE = "\\"
ESCAPABLE_IN_DOUBLE = (DOUBLE_QUOTE, ESCAPE, "$", "`")
ESCAPE_WIDTH = 2
CHAR_WIDTH = 1


class ParseError(Exception):
    """Ошибка разбора командной строки."""


class ParserState:
    """Текущее состояние разбора: готовые слова и накопленное слово."""

    def __init__(self):
        """Создаёт пустое состояние без открытых кавычек."""
        self.tokens = []
        self.buffer = []
        self.has_token = False
        self.quote = None

    def add_char(self, char):
        """Добавляет символ к текущему слову."""
        self.buffer.append(char)
        self.has_token = True

    def finish_token(self):
        """Завершает текущее слово, если оно начато."""
        if self.has_token:
            self.tokens.append("".join(self.buffer))
        self.buffer = []
        self.has_token = False


def read_single_quoted(state, char, index):
    """Обрабатывает символ внутри одинарных кавычек (всё буквально)."""
    if char == SINGLE_QUOTE:
        state.quote = None
    else:
        state.add_char(char)
    return index + CHAR_WIDTH


def read_double_quoted(state, line, index):
    """Обрабатывает символ внутри двойных кавычек (есть экранирование)."""
    char = line[index]
    following = index + CHAR_WIDTH
    if char == DOUBLE_QUOTE:
        state.quote = None
        return following
    if char == ESCAPE and following < len(line):
        if line[following] in ESCAPABLE_IN_DOUBLE:
            state.add_char(line[following])
            return index + ESCAPE_WIDTH
    state.add_char(char)
    return following


def read_unquoted(state, line, index):
    """Обрабатывает символ вне кавычек."""
    char = line[index]
    following = index + CHAR_WIDTH
    if char.isspace():
        state.finish_token()
    elif char in (SINGLE_QUOTE, DOUBLE_QUOTE):
        state.quote = char
        state.has_token = True
    elif char == ESCAPE:
        if following >= len(line):
            raise ParseError("обратная косая черта в конце строки")
        state.add_char(line[following])
        return index + ESCAPE_WIDTH
    else:
        state.add_char(char)
    return following


def advance(state, line, index):
    """Делает один шаг разбора и возвращает индекс следующего символа."""
    if state.quote == SINGLE_QUOTE:
        return read_single_quoted(state, line[index], index)
    if state.quote == DOUBLE_QUOTE:
        return read_double_quoted(state, line, index)
    return read_unquoted(state, line, index)


def parse_line(line):
    """Разбивает строку на слова: имя команды и её аргументы.

    Пробелы разделяют слова. Текст в кавычках остаётся одним словом.
    Пустые кавычки дают пустой аргумент. При незакрытой кавычке
    выбрасывается ParseError.
    """
    state = ParserState()
    index = 0
    while index < len(line):
        index = advance(state, line, index)
    if state.quote is not None:
        raise ParseError("не закрыта кавычка " + state.quote)
    state.finish_token()
    return state.tokens
