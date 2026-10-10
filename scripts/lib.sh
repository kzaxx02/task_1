#!/usr/bin/env bash
# Общие функции для тестовых скриптов (совместимо с bash 3.2 из macOS).

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EMU="$ROOT/run.sh"
VFS_DIR="$ROOT/examples/vfs"
FAILED=0
LAST_STATUS=0
LAST_OUTPUT=""
NEW_TMP=""
TMP_LIST=()

# cleanup: удаляет временные каталоги, созданные make_tmp_dir
cleanup() {
  local dir
  for dir in "${TMP_LIST[@]}"; do
    chmod -R u+rwx "$dir" 2> /dev/null
    rm -rf "$dir"
  done
}
trap cleanup EXIT

# make_tmp_dir: создаёт временный каталог, путь кладёт в NEW_TMP
make_tmp_dir() {
  NEW_TMP="$(mktemp -d "${TMPDIR:-/tmp}/emu.XXXXXX")"
  TMP_LIST+=("$NEW_TMP")
}

# fingerprint <каталог>: контрольная сумма имён и содержимого файлов
fingerprint() {
  (find "$1" | sort; find "$1" -type f -exec cat {} +) | cksum
}

# case_title <заголовок>
case_title() {
  echo
  echo "=== $1 ==="
}

# run_emu <аргументы эмулятора...>: stdin пустой (Ctrl+D сразу)
run_emu() {
  echo "\$ ./run.sh $*"
  LAST_OUTPUT="$("$EMU" "$@" 2>&1 < /dev/null)" && LAST_STATUS=0 || LAST_STATUS=$?
  echo "$LAST_OUTPUT"
}

# run_emu_input <текст для stdin> <аргументы эмулятора...>
# Строки разделяются переводами строк: $'ls a\nexit 4'
run_emu_input() {
  local input="$1"
  shift
  echo "\$ ./run.sh $*   <<< (команды ниже вводятся с клавиатуры)"
  echo "$input" | sed 's/^/  > /'
  LAST_OUTPUT="$(printf '%s\n' "$input" | "$EMU" "$@" 2>&1)" && LAST_STATUS=0 || LAST_STATUS=$?
  echo "$LAST_OUTPUT"
}

# expect_status <код>
expect_status() {
  if [ "$LAST_STATUS" -eq "$1" ]; then
    echo "  [ OK ] код возврата = $1"
  else
    echo "  [FAIL] код возврата = $LAST_STATUS, ожидался $1"
    FAILED=1
  fi
}

# expect_text <подстрока>
expect_text() {
  if printf '%s' "$LAST_OUTPUT" | grep -qF -- "$1"; then
    echo "  [ OK ] в выводе есть: $1"
  else
    echo "  [FAIL] в выводе нет: $1"
    FAILED=1
  fi
}

# expect_no_text <подстрока>
expect_no_text() {
  if printf '%s' "$LAST_OUTPUT" | grep -qF -- "$1"; then
    echo "  [FAIL] в выводе не должно быть: $1"
    FAILED=1
  else
    echo "  [ OK ] в выводе нет: $1"
  fi
}

# expect_equal <описание> <значение1> <значение2>
expect_equal() {
  if [ "$2" = "$3" ]; then
    echo "  [ OK ] $1"
  else
    echo "  [FAIL] $1 ($2 != $3)"
    FAILED=1
  fi
}

# finish: итог набора проверок
finish() {
  echo
  if [ "$FAILED" -eq 0 ]; then
    echo "ИТОГ: все проверки пройдены"
  else
    echo "ИТОГ: есть непройденные проверки"
  fi
  exit "$FAILED"
}
