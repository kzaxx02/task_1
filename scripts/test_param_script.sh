#!/usr/bin/env bash
# Проверка параметра --script.
source "$(dirname "$0")/lib.sh"

case_title "--script: успешный скрипт, затем диалог (stdin пуст)"
run_emu --script "$ROOT/examples/startup_ok.emu"
expect_status 0
expect_text "arguments (3): ['my documents', 'a b', 'plain']"
expect_text "arguments (1): ['']"
expect_no_text "Файл"

case_title "--script: ввод и вывод видны как диалог"
run_emu --script "$ROOT/examples/startup_ok.emu"
expect_text "ls -l /home"
expect_text "arguments (2): ['-l', '/home']"

case_title "--script: остановка на первой ошибке"
run_emu --script "$ROOT/examples/startup_error.emu"
expect_status 127
expect_text "unknown_command: command not found"
expect_text "остановлен на строке 3"
expect_no_text "NEVER_PRINTED"

case_title "--script: синтаксическая ошибка останавливает скрипт"
run_emu --script "$ROOT/examples/startup_syntax_error.emu"
expect_status 2
expect_text "syntax error"
expect_no_text "NEVER_PRINTED"

case_title "--script: exit с кодом завершает эмулятор"
run_emu --script "$ROOT/examples/startup_exit.emu"
expect_status 7
expect_no_text "NEVER_PRINTED"

case_title "--script: файла не существует"
run_emu --script "$ROOT/examples/no_such.emu"
expect_status 2
expect_text "файл не найден"

case_title "--script: вместо файла указан каталог"
run_emu --script "$ROOT/examples"
expect_status 2

finish
