#!/usr/bin/env bash
# Builds the completed answer key (Word + PDF) from «سند (51).docx».
# usage: ./make51.sh [output dir]   (default: ./out)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="${1:-$HERE/out}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$OUT"

unzip -q "$HERE/سند (51).docx" -d "$WORK/src"
python3 "$HERE/charts51.py" "$WORK/charts" >/dev/null
node "$HERE/render_charts.js" "$WORK/charts/manifest.json" >/dev/null
cd "$HERE" && python3 "$HERE/buildkey.py" fixes51 "$WORK/src" "$OUT/Sanad51_Pasokhname_Kamel.docx" "$WORK/charts" "$OUT/changes51.log"
soffice --headless --convert-to pdf --outdir "$OUT" "$OUT/Sanad51_Pasokhname_Kamel.docx" >/dev/null 2>&1
ls -la "$OUT"
