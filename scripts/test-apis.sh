#!/usr/bin/env bash
set -euo pipefail

AUTH_URL="${AUTH_URL:-http://localhost:8001}"
AI_URL="${AI_URL:-http://localhost:8002}"
EMAIL="${TEST_EMAIL:-devops@example.com}"
PASSWORD="${TEST_PASSWORD:-SecurePass123}"
USERNAME="${TEST_USERNAME:-devopsuser}"

echo "== Health checks =="
curl -s "$AUTH_URL/health" | python -m json.tool
curl -s "$AI_URL/health" | python -m json.tool

echo "== Register =="
REGISTER=$(curl -s -X POST "$AUTH_URL/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}" || true)
echo "$REGISTER" | python -m json.tool || echo "$REGISTER"

echo "== Login =="
LOGIN=$(curl -s -X POST "$AUTH_URL/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")
TOKEN=$(echo "$LOGIN" | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo "Token acquired"

echo "== Upload test diagram =="
# Create minimal 1x1 PNG
TMPPNG=$(mktemp).png
python - <<'PY' "$TMPPNG"
import struct, zlib, sys
path = sys.argv[1]
def chunk(tag, data):
    return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
raw = b'\x00' + struct.pack('>IHH', 1, 1, 0) + b'\x08\x02\x00\x00\x00\x90wS\xde'
png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b'')
open(path, 'wb').write(png)
PY

UPLOAD=$(curl -s -X POST "$AI_URL/upload-diagram" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@$TMPPNG;type=image/png")
FILE_ID=$(echo "$UPLOAD" | python -c "import sys,json; print(json.load(sys.stdin)['file_id'])")
echo "Uploaded file_id=$FILE_ID"

echo "== Generate manifest =="
GEN=$(curl -s -X POST "$AI_URL/generate-manifest" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"file_id\":\"$FILE_ID\",\"namespace\":\"production\",\"app_name\":\"web-app\"}")
MANIFEST_ID=$(echo "$GEN" | python -c "import sys,json; print(json.load(sys.stdin)['manifest_id'])")
echo "manifest_id=$MANIFEST_ID"

echo "== Validate manifest =="
curl -s -X POST "$AI_URL/validate-manifest" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"manifest_id\":\"$MANIFEST_ID\"}" | python -m json.tool

echo "== Download manifest =="
curl -s -H "Authorization: Bearer $TOKEN" "$AI_URL/download-manifest?manifest_id=$MANIFEST_ID" | head -n 20

rm -f "$TMPPNG"
echo "API test flow completed."
