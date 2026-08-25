#!/usr/bin/env bash
# Local API helper — run from repo root or backend/
set -euo pipefail
cd "$(dirname "$0")"
export PORT="${PORT:-8000}"
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --reload
