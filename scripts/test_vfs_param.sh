#!/usr/bin/env bash
# Проверка параметра --vfs.
source "$(dirname "$0")/lib.sh"

case_title "--vfs: существующий каталог"
run_emu --vfs "$ROOT/examples/vfs_sample"
expect_status 0
expect_text "--vfs    = $ROOT/examples/vfs_sample"

case_title "--vfs: относительный путь превращается в абсолютный"
(cd "$ROOT" && run_emu --vfs examples/vfs_sample && \
  expect_text "$ROOT/examples/vfs_sample")

case_title "--vfs: каталог не существует"
run_emu --vfs "$ROOT/no_such_dir"
expect_status 2
expect_text "каталог не найден"

case_title "--vfs: вместо каталога указан файл"
run_emu --vfs "$ROOT/examples/startup_ok.emu"
expect_status 2
expect_text "каталог не найден"

case_title "--vfs: не указано значение"
run_emu --vfs
expect_status 2
expect_text "--vfs"

finish
