#!/usr/bin/env python3
"""A production checkout must never silently float with upstream main."""
from pathlib import Path
import re
import sys

pin = (Path(__file__).parent / 'latex2md.sha').read_text(encoding='utf8').strip()
if not re.fullmatch(r'[0-9a-f]{40}', pin):
    print('ERROR: tools/latex2md.sha must contain the reviewed full lowercase 40-character commit SHA.', file=sys.stderr)
    sys.exit(1)
print(pin)
