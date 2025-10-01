#!/usr/bin/env bash
set -euo pipefail

if [ ! -d "venv" ]; then
  echo "Virtual environment not found. Run scripts/bootstrap.sh first." >&2
  exit 1
fi

source venv/bin/activate

rm -f dedupe.db out/quotes.csv
rm -f logs/*.log 2>/dev/null || true

python -m src.cli run quotes --demo
