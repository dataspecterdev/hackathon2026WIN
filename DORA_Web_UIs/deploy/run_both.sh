#!/usr/bin/env bash
# Start all three DORA UIs side by side:
#
#   http://localhost:8081  — deterministic rule pipeline (website/, blue)
#   http://localhost:8082  — Gemini agent with LOCAL tools (website-gemini/, violet)
#   http://localhost:8083  — Microsoft Copilot Studio agent (website-copilot/, teal)
#
# The 8082 backend runs the tool-use loop locally (DORA_BACKEND=gemini), so
# packages uploaded through any UI are immediately reviewable by the model.
# It needs a Gemini API key exported before launch:
#
#   export GOOGLE_API_KEY=AQ....
#   ./deploy/run_both.sh
#
# 8083 embeds the Copilot Studio webchat iframe — that agent runs on
# Microsoft's side and cannot see local uploads. The Google-hosted widget
# page is likewise still served at http://localhost:8082/widget.html.
#
# Ctrl-C stops all three.

set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PY:-.venv/bin/python}"

if [ -z "${GOOGLE_API_KEY:-}" ]; then
  echo "warning: GOOGLE_API_KEY is not set — 8082 chat will return 503 until it is." >&2
fi

PORT=8081 DORA_BACKEND=rules DORA_STATIC_DIR=website \
  "$PY" deploy/dora_chat.py &
RULES_PID=$!

PORT=8082 DORA_BACKEND=gemini DORA_STATIC_DIR=website-gemini \
  "$PY" deploy/dora_chat.py &
GEMINI_PID=$!

PORT=8083 DORA_BACKEND=rules DORA_STATIC_DIR=website-copilot \
  "$PY" deploy/dora_chat.py &
COPILOT_PID=$!

trap 'kill "$RULES_PID" "$GEMINI_PID" "$COPILOT_PID" 2>/dev/null' INT TERM
wait
