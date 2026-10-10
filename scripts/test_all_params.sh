#!/usr/bin/env bash
# Проверка совместной работы параметров и служебных случаев.
source "$(dirname "$0")/lib.sh"

case_title "Без параметров: в отладке оба параметра не заданы"
run_emu
expect_status 0
expect_text "--vfs    = <не задан>"
expect_text "--script = <не задан>"

case_title "Оба параметра вместе"
run_emu --vfs "$ROOT/examples/vfs_sample" --script "$ROOT/examples/startup_ok.emu"
expect_status 0
expect_text "--vfs    = $ROOT/examples/vfs_sample"
expect_text "--script = $ROOT/examples/startup_ok.emu"
expect_text "ls -l /home"

case_title "Порядок параметров не важен"
run_emu --script "$ROOT/examples/startup_ok.emu" --vfs "$ROOT/examples/vfs_sample"
expect_status 0

case_title "Оба параметра, скрипт с ошибкой"
run_emu --vfs "$ROOT/examples/vfs_sample" --script "$ROOT/examples/startup_error.emu"
expect_status 127
expect_text "--vfs    = $ROOT/examples/vfs_sample"
expect_no_text "NEVER_PRINTED"

case_title "После скрипта продолжается интерактивный режим"
run_emu_input 'ls from_stdin\nexit 4\n' --script "$ROOT/examples/startup_ok.emu"
expect_status 4
expect_text "arguments (1): ['from_stdin']"

case_title "Справка --help"
run_emu --help
expect_status 0
expect_text "--vfs DIR"
expect_text "--script FILE"

case_title "Неизвестный параметр"
run_emu --foo
expect_status 2

finish
