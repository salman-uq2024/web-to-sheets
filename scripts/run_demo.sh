#!/usr/bin/env bash
set -euo pipefail

if [ ! -d "venv" ]; then
  echo "Virtual environment not found. Run scripts/bootstrap.sh first." >&2
  exit 1
fi

source venv/bin/activate
python -m src.cli validate quotes
python -m src.cli run quotes --demo
