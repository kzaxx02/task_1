#!/usr/bin/env bash
# VFS и прошлые этапы: обработка ошибок.
source "$(dirname "$0")/lib.sh"
DEEP="$VFS_DIR/deep"

case_title "Команды VFS без параметра --vfs"
run_emu_input $'vfs-info\nvfs-tree\nexit 0'
expect_status 0
expect_text "vfs-info: VFS не подключена (запустите с --vfs)"
expect_text "vfs-tree: VFS не подключена (запустите с --vfs)"

case_title "Ошибки в диалоге не завершают эмулятор"
INPUT=$'vfs-tree /nope\nvfs-tree /top.txt/x\nvfs-tree a b\nvfs-info extra\n'
INPUT+=$'vfs-tree ""\nfoo\nls "unclosed\nls still_alive\nexit 3'
run_emu_input "$INPUT" --vfs "$DEEP"
expect_text "vfs-tree: /nope: No such file or directory"
expect_text "vfs-tree: /top.txt/x: Not a directory"
expect_text "vfs-tree: too many arguments"
expect_text "vfs-info: too many arguments"
expect_text "vfs-tree: empty path: No such file or directory"
expect_text "foo: command not found"
expect_text "syntax error: не закрыта кавычка"
expect_text "arguments (1): ['still_alive']"
expect_status 3

case_title "Ошибки команды exit"
run_emu_input $'exit 1 2\nexit abc\nls unreachable' --vfs "$DEEP"
expect_text "exit: too many arguments"
expect_text "exit: abc: numeric argument required"
expect_no_text "unreachable"
expect_status 2

case_title "Ошибка в стартовом скрипте с VFS останавливает скрипт"
make_tmp_dir
printf 'vfs-info\nvfs-tree /nope\nvfs-tree\n' > "$NEW_TMP/bad.emu"
run_emu --vfs "$DEEP" --script "$NEW_TMP/bad.emu"
expect_status 1
expect_text "script: остановлен на строке 2 (код 1)"
expect_no_text "└── top.txt"

case_title "Источник VFS нельзя прочитать (нет прав)"
if [ "$(id -u)" -eq 0 ]; then
  echo "  [SKIP] запущено от root: root читает любые каталоги"
else
  make_tmp_dir
  mkdir "$NEW_TMP/locked"
  chmod 000 "$NEW_TMP/locked"
  run_emu --vfs "$NEW_TMP/locked"
  expect_status 1
  expect_text "vfs: не удалось прочитать"
  chmod 700 "$NEW_TMP/locked"
fi

case_title "Вложенный каталог источника нельзя прочитать"
if [ "$(id -u)" -eq 0 ]; then
  echo "  [SKIP] запущено от root: root читает любые каталоги"
else
  make_tmp_dir
  mkdir -p "$NEW_TMP/ok/locked"
  chmod 000 "$NEW_TMP/ok/locked"
  run_emu --vfs "$NEW_TMP/ok"
  expect_status 1
  expect_text "vfs: не удалось прочитать"
  chmod 700 "$NEW_TMP/ok/locked"
fi

finish
