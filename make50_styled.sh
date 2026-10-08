#!/usr/bin/env bash
# Builds «سند (50) - تکمیل_شده.docx» in the exact look of Faraz11_Styled-2.docx (Word + PDF),
# without the reference's cover and credits pages.
# usage: ./make50_styled.sh [output dir]   (default: ./out)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="${1:-$HERE/out}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$OUT"

unzip -q "$HERE/سند (50) - تکمیل_شده.docx" -d "$WORK/src"
unzip -q "$HERE/Faraz11_Styled-2.docx" -d "$WORK/ref"
node "$HERE/style/make_background.js" "$WORK/ref/word/media/page_design.png" "$WORK/bg.png" "آزمون زیست شناسی دهم"
python3 "$HERE/style/diag50.py" "$WORK/charts" >/dev/null
node "$HERE/render_charts.js" "$WORK/charts/manifest.json" >/dev/null
python3 "$HERE/style/rebuild50.py" "$WORK/src" "$WORK/ref" "$WORK/bg.png" "$WORK/charts" "$OUT/Sanad50_Styled.docx"
soffice --headless --convert-to pdf --outdir "$OUT" "$OUT/Sanad50_Styled.docx" >/dev/null 2>&1
ls -la "$OUT"
