#!/usr/bin/env bash
# Запуск всех тестовых скриптов реальной ОС.
cd "$(dirname "$0")" || exit 1
STATUS=0
for script in test_param_vfs.sh test_param_script.sh test_param_all.sh \
  test_vfs_minimal.sh test_vfs_files.sh test_vfs_deep.sh test_vfs_errors.sh; do
  echo
  echo "################ $script ################"
  bash "./$script" || STATUS=1
done
exit "$STATUS"
