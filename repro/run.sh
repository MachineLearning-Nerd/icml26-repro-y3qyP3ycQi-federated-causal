#!/usr/bin/env bash
# Fixed run command for every experiment node (cardinal rule: identical command).
# Bootstraps uv without system pip (curl installer), then runs the master verifier
# from the locked environment. Works on a plain python:3.12 HF cpu image.
set -euo pipefail

if ! command -v uv >/dev/null 2>&1; then
  if command -v curl >/dev/null 2>&1; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
  else
    pip install --quiet uv
  fi
fi

uv run --locked python repro/src/run_all.py
