#!/usr/bin/env bash
# The same entry point is used locally and in GitHub's fixed TeX Live image.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
# Generate the high-resolution cover background before LaTeX compilation.
if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 is required to generate the cover background" >&2
  exit 1
fi

python3 tools/generate-cover.py \
  --output assets/cover-background.png \
  --dpi 300

for cmd in latexmk pdflatex biber; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    printf 'ERROR: required program is missing: %s\n' "$cmd" >&2
    exit 1
  fi
done
# latexmk detects BibLaTeX/Biber from main.tex and runs it when needed.
# No source or preamble changes are required.
latexmk -pdf \
  -pdflatex='pdflatex -interaction=nonstopmode -halt-on-error -file-line-error %O %S' \
  main.tex
if [[ ! -s main.pdf ]]; then
  echo 'ERROR: LaTeX returned without a nonempty main.pdf' >&2
  exit 1
fi
