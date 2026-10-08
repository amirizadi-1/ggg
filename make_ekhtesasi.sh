#!/usr/bin/env bash
# Styled version (Word + PDF) of the question booklet «Faraz_Azmoon_Ekhtesasi_Zist_Marhale1.docx»
# in the look of Faraz11_Styled-2.docx, with the team credits picture as page 2.
# usage: ./make_ekhtesasi.sh [output dir]   (default: ./out)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="${1:-$HERE/out}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$OUT"

unzip -q "$HERE/Faraz_Azmoon_Ekhtesasi_Zist_Marhale1.docx" -d "$WORK/src"
python3 "$HERE/style/normalize.py" "$WORK/src" "$OUT/changes_ekhtesasi.log"
unzip -q "$HERE/Faraz11_Styled-2.docx" -d "$WORK/ref"
node "$HERE/style/make_background.js" "$WORK/ref/word/media/page_design.png" "$WORK/bg.png" "آزمون اختصاصی زیست شناسی" "دفترچهٔ سؤالات"
python3 "$HERE/style/restyle.py" "$WORK/src" "$WORK/ref" "$WORK/bg.png" - "$WORK/styled.docx"
python3 "$HERE/style/cover10.py" "$WORK/styled.docx" - "$OUT/Faraz_Ekhtesasi_Styled.docx" "$HERE/IMG_20261008_144713_516.jpg"
soffice --headless --convert-to pdf --outdir "$OUT" "$OUT/Faraz_Ekhtesasi_Styled.docx" >/dev/null 2>&1
ls -la "$OUT" | grep -i ekhtesasi
