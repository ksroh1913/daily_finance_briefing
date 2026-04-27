#!/usr/bin/env bash
set -euo pipefail

echo "[secure] This script will read secrets without echoing to terminal."
read -rsp "KFTC_ACCESS_TOKEN: " KFTC_ACCESS_TOKEN; echo
read -rsp "KFTC_USER_SEQ_NO: " KFTC_USER_SEQ_NO; echo
read -rsp "KFTC_AUTH_CODE: " KFTC_AUTH_CODE; echo

export KFTC_USE_SAMPLE=false
export KFTC_INCLUDE_BALANCE=true
export KFTC_ACCESS_TOKEN
export KFTC_USER_SEQ_NO
export KFTC_AUTH_CODE

echo "[secure] Running tests..."
pytest -q

echo "[secure] Running live bootstrap..."
python week1_bootstrap.py

echo "[secure] Done. Secrets were only in this shell session."
