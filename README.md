# Эмулятор оболочки UNIX (Вариант 19)

## Общее описание

Консольный эмулятор языка оболочки ОС. Этап 1 - REPL: минимальный
прототип с диалогом с пользователем. Реализован на Python 3.9+,
сторонние библиотеки не нужны.

## Описание функций и настроек

Приглашение берётся из реальной ОС: `username@hostname:~$`.

| Команда        | Что делает                                              |
|----------------|---------------------------------------------------------|
| `ls [args]`    | Заглушка: печатает своё имя и аргументы                 |
| `cd [args]`    | Заглушка: печатает своё имя и аргументы                 |
| `exit [код]`   | Завершает работу; код по умолчанию 0                    |

Парсер: слова делятся пробелами; `"..."` - одно слово (внутри работает
`\"` и `\\`); `'...'` - буквально; `""` - пустой аргумент; `\ ` -
экранированный пробел. Ctrl+D завершает работу, Ctrl+C отменяет ввод.

Ошибки: `command not found` (код 127), `syntax error` при незакрытой
кавычке или `\` в конце строки (код 2), `exit: too many arguments`,
`exit: abc: numeric argument required`.

Настроек пока нет (появятся на Этапе 2).

Структура: `src/shell_emulator/` - parser.py (разбор строки),
prompt.py (приглашение), commands.py (команды), repl.py (цикл),
`tests/` - модульные тесты.

## Сборка и запуск тестов

Сборка не требуется. Нужен только Python 3.

    ./run.sh          # запуск эмулятора (или: make run)
    make test         # запуск тестов
    PYTHONPATH=src python3 -m unittest discover -s tests -v

## Примеры использования

    user@host:~$ ls -l "my documents" 'a b'
    command: ls
    arguments (3): ['-l', 'my documents', 'a b']
    user@host:~$ cd
    command: cd
    arguments (0): []
    user@host:~$ ls "abc
    syntax error: не закрыта кавычка "
    user@host:~$ pwd
    pwd: command not found
    user@host:~$ exit abc
    exit: abc: numeric argument required
