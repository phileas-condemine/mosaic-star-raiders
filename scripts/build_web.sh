#!/usr/bin/env bash
set -euo pipefail
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pygbag --build --ume_block 0 --width 1920 --height 1080 --title "Mosaic Star Raiders" --app_name "Mosaic Star Raiders" .
echo "Build generated in build/web"
