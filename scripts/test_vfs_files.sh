#!/usr/bin/env bash
# VFS: несколько файлов и один вложенный каталог, а также особые случаи.
source "$(dirname "$0")/lib.sh"
DEMO="$ROOT/examples/startup_vfs_demo.emu"
SEVERAL="$VFS_DIR/several"

case_title "Несколько файлов: сводка и дерево"
run_emu --vfs "$SEVERAL" --script "$DEMO"
expect_status 0
expect_text "каталогов 1, файлов 6, 157 B"
expect_text "directories: 1"
expect_text "files: 6"
expect_text "total size: 157 B"
expect_text "max depth: 2"
expect_text "├── config.ini (17 B)"
expect_text "├── data.csv (23 B)"
expect_text "├── docs/"
expect_text "│   └── my notes.txt (36 B)"
expect_text "└── todo.txt (25 B)"

case_title "Несколько файлов: пути с пробелом и кавычками"
run_emu_input $'vfs-tree "/docs/my notes.txt"\nvfs-tree /docs/my\\ notes.txt\nvfs-tree \'/docs\'\nexit' --vfs "$SEVERAL"
expect_status 0
expect_text "/docs/my notes.txt (36 B)"
expect_text "/docs"
expect_text "├── guide.txt (26 B)"

case_title "Несколько файлов: имена выводятся отсортированными"
run_emu_input $'vfs-tree\nexit' --vfs "$SEVERAL"
first="$(printf '%s\n' "$LAST_OUTPUT" | grep -n 'config.ini' | cut -d: -f1)"
last="$(printf '%s\n' "$LAST_OUTPUT" | grep -n 'todo.txt' | cut -d: -f1)"
if [ "$first" -lt "$last" ]; then
  echo "  [ OK ] config.ini выведен раньше todo.txt"
else
  echo "  [FAIL] порядок имён нарушен"
  FAILED=1
fi

case_title "Особый случай: символическая ссылка пропускается"
make_tmp_dir
printf 'real\n' > "$NEW_TMP/real.txt"
ln -s "$NEW_TMP/real.txt" "$NEW_TMP/link.txt"
run_emu_input $'vfs-tree\nexit' --vfs "$NEW_TMP"
expect_text "real.txt (5 B)"
expect_no_text "link.txt"

case_title "Особый случай: скрытые файлы входят в VFS"
make_tmp_dir
printf 'x' > "$NEW_TMP/.hidden"
run_emu_input $'vfs-tree\nexit' --vfs "$NEW_TMP"
expect_text ".hidden (1 B)"

case_title "Особый случай: бинарный файл загружается без искажений размера"
make_tmp_dir
head -c 1000 /dev/zero > "$NEW_TMP/zeros.bin"
run_emu_input $'vfs-info\nexit' --vfs "$NEW_TMP"
expect_text "total size: 1000 B"

finish
