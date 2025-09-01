#!/bin/bash
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

if [ ! -d ".venv" ]; then
  /usr/bin/python3 -m venv .venv
fi

"./.venv/bin/python" -m pip install --upgrade pip
"./.venv/bin/python" -m pip install -r requirements.txt

exec "./.venv/bin/python" main.py