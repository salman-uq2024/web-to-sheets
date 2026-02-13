#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -d "venv" ]; then
  echo "Virtual environment not found. Run scripts/bootstrap.sh first." >&2
  exit 1
fi

source venv/bin/activate
ws run quotes --demo
