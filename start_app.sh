#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR"

export UV_CACHE_DIR=".uv-cache"
export DYNETI_DATABASE_PATH="instance/webapp.sqlite"
export DYNETI_MODEL_PATH="model.tflite"
export DYNETI_TEST_IMAGES_PATH="test_images"
export DYNETI_HOST="127.0.0.1"
export DYNETI_PORT="5000"
export DYNETI_DEBUG="false"
export DYNETI_CAT_THRESHOLD="0.975"

mkdir -p "$UV_CACHE_DIR"

uv run python backend.py "$@"
