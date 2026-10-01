#!/usr/bin/env python3
"""Validate co-deployed assets and their exact PDF provenance."""
import hashlib
import json
from pathlib import Path
import sys


def validate(site: Path, source_pdf: Path):
    if not (site / "index.html").is_file():
        raise ValueError("Missing index.html")
    if not (site / ".nojekyll").is_file():
        raise ValueError("Missing .nojekyll")
    if (site / "index.html").stat().st_size == 0:
        raise ValueError("Empty index.html")
    site_pdf = site / "diabat.pdf"
    if not site_pdf.is_file() or not source_pdf.is_file():
        raise ValueError("Missing compiled or published PDF")
    expected = hashlib.sha256(source_pdf.read_bytes()).hexdigest()
    actual = hashlib.sha256(site_pdf.read_bytes()).hexdigest()
    if actual != expected:
        raise ValueError("Site PDF and compiled PDF do not match")
    manifest = json.loads((site / "build-info.json").read_text(encoding="utf8"))
    if manifest["pdf_sha256"] != actual:
        raise ValueError("Site manifest does not match the PDF")
    for item in site.rglob('*'):
        if item.is_symlink():
            raise ValueError(f"Pages tree contains a symlink: {item}")
    print(f"VALID SITE: identical PDF ({actual}), source={manifest['source_commit']}")


if __name__ == "__main__":
    try:
        validate(Path(sys.argv[1]) if len(sys.argv)>1 else Path('site'),
                 Path(sys.argv[2]) if len(sys.argv)>2 else Path('main.pdf'))
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"SITE VALIDATION FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
