#!/usr/bin/env bash
# Builds the completed answer key (Word + PDF) from faraz11zamanifinal.docx.
# usage: ./make11.sh [output dir]   (default: ./out)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="${1:-$HERE/out}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$OUT"

unzip -q "$HERE/faraz11zamanifinal.docx" -d "$WORK/src"
python3 "$HERE/charts11.py" "$WORK/charts" >/dev/null
node "$HERE/render_charts.js" "$WORK/charts/manifest.json" >/dev/null
python3 "$HERE/build11.py" "$WORK/src" "$OUT/Faraz11_Pasokhname_Kamel.docx" "$WORK/charts" "$OUT/changes.log"
soffice --headless --convert-to pdf --outdir "$OUT" "$OUT/Faraz11_Pasokhname_Kamel.docx" >/dev/null 2>&1
ls -la "$OUT"
