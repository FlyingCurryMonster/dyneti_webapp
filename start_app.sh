#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR"

export RNB_WEBAPP_UV_CACHE_DIR="${RNB_WEBAPP_UV_CACHE_DIR:-.uv-cache}"
export UV_CACHE_DIR="$RNB_WEBAPP_UV_CACHE_DIR"

uv run python backend.py "$@"
