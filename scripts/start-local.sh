#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

bash "$ROOT_DIR/scripts/setup-env.sh"
docker compose up --build -d

echo "Services starting..."
echo "Frontend:      http://localhost:3000"
echo "Auth API:      http://localhost:8001/docs"
echo "AI Agent API:  http://localhost:8002/docs"
