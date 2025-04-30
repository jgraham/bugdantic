#!/usr/bin/env bash

set -ex

uv sync --extra=test
uv run mypy bugdantic
uv run pytest --ruff --ruff-format .
