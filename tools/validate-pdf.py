#!/usr/bin/env python3
"""Fail closed on obviously damaged, truncated, or incomplete Manuals.

Requires poppler-utils (pdfinfo and pdftotext), installed on the CI host.
"""
import argparse
import hashlib
from pathlib import Path
import re
import shutil
import subprocess
import sys


def validate(path: Path, min_pages: int) -> None:
    if not path.is_file():
        raise ValueError(f"PDF does not exist: {path}")
    data = path.read_bytes()
    if len(data) < 100_000:
        raise ValueError(f"PDF is suspiciously small ({len(data)} bytes)")
    if not data.startswith(b"%PDF-"):
        raise ValueError("Missing PDF signature")
    if b"%%EOF" not in data[-4096:]:
        raise ValueError("Missing PDF end-of-file marker")
    for cmd in ("pdfinfo", "pdftotext"):
        if not shutil.which(cmd):
            raise ValueError(f"Missing PDF validation tool: {cmd} (install poppler-utils)")
    info = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True, check=True).stdout
    match = re.search(r"^Pages:\s*(\d+)\s*$", info, flags=re.MULTILINE)
    if not match:
        raise ValueError("Could not determine PDF page count")
    pages = int(match.group(1))
    if pages < min_pages:
        raise ValueError(f"Only {pages} pages; expected at least {min_pages}")
    content = subprocess.run(
        ["pdftotext", str(path), "-"], capture_output=True, text=True, check=True
    ).stdout
    for expected in ("Diabat", "References"):
        if expected not in content:
            raise ValueError(f"PDF text does not contain: {expected}")
    print(f"VALID PDF: {pages} pages, {len(data)} bytes, sha256={hashlib.sha256(data).hexdigest()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--min-pages", type=int, default=100)
    args = parser.parse_args()
    try:
        validate(args.pdf, args.min_pages)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"PDF VALIDATION FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
