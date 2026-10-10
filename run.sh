#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
PYTHONPATH=src exec python3 -m shell_emulator "$@"
