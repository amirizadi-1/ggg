#!/usr/bin/env bash
# Styled version (Word + PDF) of «Sanad51_Pasokhname_Kamel_1.docx» in the look of Faraz11_Styled-2.docx.
# Pages 1–2 as in the Ekhtesasi booklet: its cover (subtitle «دفترچهٔ سؤال و پاسخ») and the credits picture.
# usage: ./make51_styled.sh [output dir]   (default: ./out)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="${1:-$HERE/out}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$OUT"

unzip -q "$HERE/Sanad51_Pasokhname_Kamel_1.docx" -d "$WORK/src"
python3 "$HERE/style/prepend_cover.py" "$HERE/Faraz_Azmoon_Ekhtesasi_Zist_Marhale1.docx" "$WORK/src"
unzip -q "$HERE/Faraz11_Styled-2.docx" -d "$WORK/ref"
node "$HERE/style/make_background.js" "$WORK/ref/word/media/page_design.png" "$WORK/bg.png" "آزمون زیست شناسی دوازدهم"
python3 "$HERE/style/restyle.py" "$WORK/src" "$WORK/ref" "$WORK/bg.png" - "$WORK/styled.docx"
node "$HERE/style/cover_subtitle.js" "$WORK/src/word/media/cover1.jpg" "$WORK/cover.jpg" "دفترچهٔ سؤال و پاسخ"
python3 "$HERE/style/cover10.py" "$WORK/styled.docx" "$WORK/cover.jpg" "$OUT/Sanad51_Styled.docx" "$HERE/IMG_20261008_144713_516.jpg"
soffice --headless --convert-to pdf --outdir "$OUT" "$OUT/Sanad51_Styled.docx" >/dev/null 2>&1
ls -la "$OUT" | grep Sanad51_Styled
