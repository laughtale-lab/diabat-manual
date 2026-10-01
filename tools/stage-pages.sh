#!/usr/bin/env bash
# Stage a *single*, complete site tree to deploy atomically.
# Phase 1: SITE_SOURCE=web/landing (default).
# Phase 3: SITE_SOURCE=web/generated/book; only change the workflow after
# latex2md + mdBook have both passed all their own checks.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
PDF_SOURCE="${PDF_SOURCE:-main.pdf}"
SITE_SOURCE="${SITE_SOURCE:-web/landing}"
SITE_DEST="${SITE_DEST:-site}"
if [[ ! -s "$PDF_SOURCE" ]]; then
  echo "ERROR: missing or empty compiled PDF: $PDF_SOURCE" >&2
  exit 1
fi
if [[ ! -f "$SITE_SOURCE/index.html" ]]; then
  echo "ERROR: site input has no index.html: $SITE_SOURCE" >&2
  exit 1
fi
# Refuse to stage the source tree over itself or into the input.
if [[ "$SITE_SOURCE" == "$SITE_DEST" || "$SITE_DEST" == "." || "$SITE_DEST" == "/" ]]; then
  echo 'ERROR: unsafe output directory' >&2
  exit 1
fi
rm -rf -- "$SITE_DEST"
mkdir -p -- "$SITE_DEST"
cp -a -- "$SITE_SOURCE"/. "$SITE_DEST"/
install -m 0644 -- "$PDF_SOURCE" "$SITE_DEST/diabat.pdf"
printf '' > "$SITE_DEST/.nojekyll"
if find "$SITE_DEST" -type l | grep -q .; then
  echo 'ERROR: Pages tree must not contain symbolic links' >&2
  exit 1
fi
export PDF_SOURCE SITE_DEST
python3 - <<'PYCODE'
import hashlib
import json
import os
from pathlib import Path

pdf = Path(os.environ['SITE_DEST']) / 'diabat.pdf'
source = Path(os.environ['PDF_SOURCE'])
if pdf.read_bytes() != source.read_bytes():
    raise SystemExit('ERROR: staged PDF differs from the compiled PDF')
manifest = {
    'source_commit': os.environ.get('GITHUB_SHA', 'local-validation'),
    'pdf_sha256': hashlib.sha256(pdf.read_bytes()).hexdigest(),
    'texlive_year': '2025',
    'site_mode': os.environ.get('SITE_MODE', 'pdf-landing'),
}
(Path(os.environ['SITE_DEST']) / 'build-info.json').write_text(
    json.dumps(manifest, indent=2) + '\n', encoding='utf-8'
)
print(f"Staged complete site in {os.environ['SITE_DEST']}/")
PYCODE
