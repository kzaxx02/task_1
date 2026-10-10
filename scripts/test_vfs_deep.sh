#!/usr/bin/env bash
# VFS: глубокая вложенность (5 уровней), полный стартовый скрипт, работа в памяти.
source "$(dirname "$0")/lib.sh"
DEEP="$VFS_DIR/deep"
FULL="$ROOT/examples/startup_full.emu"

case_title "Глубокая VFS: сводка"
run_emu --vfs "$DEEP" --script "$ROOT/examples/startup_vfs_demo.emu"
expect_status 0
expect_text "каталогов 5, файлов 6, 93 B"
expect_text "max depth: 5"
expect_text "│   │   │   │   └── four.txt (16 B)"

case_title "Глубокая VFS: полный стартовый скрипт (последняя строка - ошибка)"
before="$(fingerprint "$DEEP")"
run_emu --vfs "$DEEP" --script "$FULL"
after="$(fingerprint "$DEEP")"
expect_status 1
expect_text "arguments (3): ['my documents', 'a b', 'plain']"
expect_text "arguments (1): ['a b']"
expect_text "arguments (2): ['say \"hi\"', 'its']"
expect_text "arguments (1): ['/tmp/new folder']"
expect_text "total size: 93 B"
expect_text "/level1/level2/level3/level4/four.txt (16 B)"
expect_text "/level1/one.txt (15 B)"
expect_text "vfs-tree: /no/such/path: No such file or directory"
expect_text "script: остановлен на строке 30 (код 1)"
expect_no_text "NEVER_PRINTED"
expect_equal "каталог VFS на диске не изменился" "$before" "$after"

case_title "Глубокая VFS: пути с . и .. и выход выше корня"
INPUT=$'vfs-tree /level1/level2/../../other\nvfs-tree /../../level1/one.txt\n'
INPUT+=$'vfs-tree /level1/level2/level3/level4/..\nexit'
run_emu_input "$INPUT" --vfs "$DEEP"
expect_status 0
expect_text "/other"
expect_text "/level1/one.txt (15 B)"
expect_text "/level1/level2/level3"

case_title "Работа в памяти: исходный каталог удалён после запуска"
make_tmp_dir
copy="$NEW_TMP/vfs_copy"
cp -R "$DEEP" "$copy"
out_file="$NEW_TMP/out.txt"
( sleep 1; printf 'vfs-tree /level1/one.txt\nvfs-info\nexit\n' ) | "$EMU" --vfs "$copy" > "$out_file" 2>&1 &
job=$!
sleep 0.4
rm -rf "$copy"
wait "$job"
LAST_STATUS=$?
LAST_OUTPUT="$(cat "$out_file")"
echo "(каталог $copy удалён с диска через 0.4 с после запуска)"
echo "$LAST_OUTPUT"
expect_status 0
expect_text "/level1/one.txt (15 B)"
expect_text "files: 6"

finish
