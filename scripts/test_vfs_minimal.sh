#!/usr/bin/env bash
# VFS: минимальные варианты (один файл, пустой каталог, пустой файл).
source "$(dirname "$0")/lib.sh"
DEMO="$ROOT/examples/startup_vfs_demo.emu"

case_title "Минимальная VFS: один файл"
run_emu --vfs "$VFS_DIR/minimal" --script "$DEMO"
expect_status 0
expect_text "VFS загружена в память: каталогов 0, файлов 1, 27 B"
expect_text "directories: 0"
expect_text "files: 1"
expect_text "total size: 27 B"
expect_text "max depth: 1"
expect_text "└── readme.txt (27 B)"

case_title "Минимальная VFS: пустой каталог"
make_tmp_dir
run_emu --vfs "$NEW_TMP" --script "$DEMO"
expect_status 0
expect_text "каталогов 0, файлов 0, 0 B"
expect_text "files: 0"
expect_text "max depth: 0"
expect_no_text "──"

case_title "Минимальная VFS: единственный пустой файл"
make_tmp_dir
: > "$NEW_TMP/empty.txt"
run_emu --vfs "$NEW_TMP" --script "$DEMO"
expect_status 0
expect_text "total size: 0 B"
expect_text "└── empty.txt (0 B)"

case_title "Минимальная VFS: только вложенные пустые каталоги"
make_tmp_dir
mkdir -p "$NEW_TMP/a/b"
run_emu --vfs "$NEW_TMP" --script "$DEMO"
expect_status 0
expect_text "directories: 2"
expect_text "files: 0"
expect_text "max depth: 2"

finish
