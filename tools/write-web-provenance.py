#!/usr/bin/env python3
"""Persist provenance alongside the atomically deployed PDF + HTML."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

site = Path(sys.argv[1])
commit = Path('tools/latex2md.sha').read_text().strip()
pdf = site / 'diabat.pdf'
assert pdf.is_file(), 'Missing staged PDF'
with (site / 'converter-info.json').open('w', encoding='utf8') as f:
    json.dump({
        'manual_commit': os.environ.get('GITHUB_SHA', 'local-test'),
        'latex2md_commit': commit,
        'mdbook_version': subprocess.check_output(['mdbook','--version'], text=True).strip(),
        'pdf_sha256': hashlib.sha256(pdf.read_bytes()).hexdigest(),
    }, f, indent=2)
    f.write('\n')
