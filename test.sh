#!/usr/bin/env bash

set -ex
echo $PWD
uv sync --extra=test
uv run mypy bugdantic
uv run pytest --ruff --ruff-format
