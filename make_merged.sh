#!/usr/bin/env bash
# Full answer key: Sanad51_Styled (covers + questions 1–20) followed by Sanad50_Styled (questions 21–45),
# with the picture layout fixed (no picture-only pages, each question starts on a new page).
# usage: ./make_merged.sh [output dir]   (default: ./out) — run make51_styled.sh and make50_styled.sh first
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="${1:-$HERE/out}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$OUT"
python3 "$HERE/style/merge_docx.py" "$OUT/Sanad51_Styled.docx" "$OUT/Sanad50_Styled.docx" "$WORK/merged.docx"
python3 "$HERE/style/fix_layout.py" "$WORK/merged.docx" "$OUT/Faraz_Zist_Ekhtesasi_Pasokhname_Kamel.docx" "$WORK"
soffice --headless --convert-to pdf --outdir "$OUT" "$OUT/Faraz_Zist_Ekhtesasi_Pasokhname_Kamel.docx" >/dev/null 2>&1
ls -la "$OUT" | grep Ekhtesasi_Pasokhname
