#!/usr/bin/env python3
"""Generate a smooth, star-free A4 cover background as an opaque sRGB PNG.

The gradient is strictly one-dimensional and monotonically darkens downward.
No light bands, radial glows, transparency, or external dependencies.
"""
import argparse
import math
from pathlib import Path
import struct
import zlib

# Colors chosen to maintain white ASCII-logo contrast near the upper third.
TOP = (48, 77, 105)       # #304D69: airy slate blue at top edge
BOTTOM = (5, 9, 17)      # #050911: near-black at bottom edge
DECAY = 3.15             # faster darkening at top; gradual descent below

# Ordered dithering reduces visible 8-bit banding without introducing stars.
BAYER8 = (
    (0, 48, 12, 60, 3, 51, 15, 63),
    (32, 16, 44, 28, 35, 19, 47, 31),
    (8, 56, 4, 52, 11, 59, 7, 55),
    (40, 24, 36, 20, 43, 27, 39, 23),
    (2, 50, 14, 62, 1, 49, 13, 61),
    (34, 18, 46, 30, 33, 17, 45, 29),
    (10, 58, 6, 54, 9, 57, 5, 53),
    (42, 26, 38, 22, 41, 25, 37, 21),
)


def chunk(tag: bytes, data: bytes) -> bytes:
    payload = tag + data
    return struct.pack('>I', len(data)) + payload + struct.pack('>I', zlib.crc32(payload) & 0xFFFFFFFF)


def generate(path: Path, dpi: int) -> tuple[int, int]:
    # A4 dimensions, as defined by the source LaTeX document / pdf geometry.
    width = round(210 / 25.4 * dpi)
    height = round(297 / 25.4 * dpi)
    path.parent.mkdir(parents=True, exist_ok=True)
    denom = -math.expm1(-DECAY)
    # Build eight horizontal dither patterns for each row; no lateral glow.
    dither_patterns = [tuple((b + 0.5) / 64 - 0.5 for b in row) for row in BAYER8]

    with path.open('wb') as output:
        output.write(b'\x89PNG\r\n\x1a\n')
        output.write(chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)))
        output.write(chunk(b'sRGB', b'\x00'))  # Explicit standard RGB intent
        density = round(dpi / 0.0254)
        output.write(chunk(b'pHYs', struct.pack('>IIB', density, density, 1)))
        compress = zlib.compressobj(level=9)
        with_idat = bytearray()
        for y in range(height):
            t = y / (height - 1)
            fraction = -math.expm1(-DECAY * t) / denom
            colors = [a + (b - a) * fraction for a, b in zip(TOP, BOTTOM)]
            dither = dither_patterns[y % 8]
            row8 = bytearray()
            for offset in dither:
                for channel in colors:
                    # tiny, symmetrical quantization dither; no added light source
                    row8.append(max(0, min(255, round(channel + offset))))
            full_row = bytes(row8) * (width // 8) + bytes(row8[: (width % 8) * 3])
            with_idat.extend(compress.compress(b'\x00' + full_row))
            if len(with_idat) > 65536:
                output.write(chunk(b'IDAT', bytes(with_idat)))
                with_idat.clear()
        with_idat.extend(compress.flush())
        if with_idat:
            output.write(chunk(b'IDAT', bytes(with_idat)))
        output.write(chunk(b'IEND', b''))
    return width, height


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('assets/cover-background.png'))
    parser.add_argument('--dpi', type=int, default=300)
    args = parser.parse_args()
    if not 72 <= args.dpi <= 600:
        parser.error('--dpi must be between 72 and 600')
    w, h = generate(args.output, args.dpi)
    print(f'Created {args.output}: {w} x {h}, opaque sRGB PNG, {args.dpi} DPI')
