#!/usr/bin/env bash
# DAGMAS Brain Vault - Shell wrapper for autonomous CLI installer
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN=""

if command -v python3 &>/dev/null; then
    PYTHON_BIN="python3"
elif command -v python &>/dev/null; then
    PYTHON_BIN="python"
else
    echo "Error: Python 3 is required but not found in PATH." >&2
    exit 1
fi

exec "$PYTHON_BIN" "$SCRIPT_DIR/install.py" "$@"
