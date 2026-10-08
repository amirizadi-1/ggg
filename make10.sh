#!/usr/bin/env bash
# Builds the completed 10th-grade answer key and its styled version (Word + PDF).
#   1) option reviews, summary tables, charts and text fixes  → Faraz10_Pasokhname_Kamel.docx
#   2) the look of Faraz11_Styled-2.docx                       → Faraz10_Styled.docx / .pdf
# usage: ./make10.sh [output dir]   (default: ./out)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="${1:-$HERE/out}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$OUT"
SRC="$(ls "$HERE" | grep 'Dahom_Marhale1.*full\.docx$')"

unzip -q "$HERE/$SRC" -d "$WORK/src"
python3 "$HERE/charts10.py" "$WORK/charts" "#E7F2FE" >/dev/null
node "$HERE/render_charts.js" "$WORK/charts/manifest.json" >/dev/null
cd "$HERE" && python3 "$HERE/buildkey.py" fixes10 "$WORK/src" "$WORK/key.docx" "$WORK/charts" "$OUT/changes10.log"

unzip -q "$WORK/key.docx" -d "$WORK/key"
unzip -q "$HERE/Faraz11_Styled-2.docx" -d "$WORK/ref"
node "$HERE/style/make_background.js" "$WORK/ref/word/media/page_design.png" "$WORK/bg.png" "آزمون زیست شناسی دهم"
python3 "$HERE/style/restyle.py" "$WORK/key" "$WORK/ref" "$WORK/bg.png" - "$OUT/Faraz10_Styled.docx"
soffice --headless --convert-to pdf --outdir "$OUT" "$OUT/Faraz10_Styled.docx" >/dev/null 2>&1
ls -la "$OUT"
