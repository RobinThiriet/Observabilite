#!/usr/bin/env bash
set -eu

BASE="${1:-http://localhost:8000}"

echo "Generating traffic against $BASE - Ctrl+C to stop"

while true; do
  curl -s -o /dev/null "$BASE/api/users"
  curl -s -o /dev/null "$BASE/api/orders"
  sleep 0.5
done
