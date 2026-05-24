#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

copy_if_missing() {
  local src="$1"
  local dest="$2"
  if [ ! -f "$dest" ]; then
    cp "$src" "$dest"
    echo "Created $dest"
  else
    echo "Exists $dest (skipped)"
  fi
}

copy_if_missing "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
copy_if_missing "$ROOT_DIR/authservice/.env.example" "$ROOT_DIR/authservice/.env"
copy_if_missing "$ROOT_DIR/ai-agent-service/.env.example" "$ROOT_DIR/ai-agent-service/.env"
copy_if_missing "$ROOT_DIR/frontend/.env.example" "$ROOT_DIR/frontend/.env"

echo "Environment files are ready."
