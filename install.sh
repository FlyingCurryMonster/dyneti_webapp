#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR"

UV_CACHE_DIR="${UV_CACHE_DIR:-.uv-cache}"
mkdir -p "$UV_CACHE_DIR"
export UV_CACHE_DIR

uv sync "$@"
