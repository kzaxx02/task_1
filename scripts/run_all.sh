#!/usr/bin/env bash
# Запуск всех тестовых скриптов реальной ОС.
cd "$(dirname "$0")"
STATUS=0
for script in test_vfs_param.sh test_script_param.sh test_all_params.sh; do
  echo
  echo "################ $script ################"
  bash "./$script" || STATUS=1
done
exit "$STATUS"
