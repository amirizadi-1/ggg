#!/usr/bin/env bash
# Builds the styled version (Word + PDF) of «سند (50) - تکمیل_شده.docx» in the look of Faraz11_Styled-2.docx
# (without its cover and credits pages).
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
python3 "$HERE/style/stylize.py" "$WORK/src" "$WORK/ref" "$WORK/bg.png" "$OUT/Sanad50_Styled.docx"
soffice --headless --convert-to pdf --outdir "$OUT" "$OUT/Sanad50_Styled.docx" >/dev/null 2>&1
ls -la "$OUT"
