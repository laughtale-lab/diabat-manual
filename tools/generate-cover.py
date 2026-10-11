import argparse, zlib, struct

def clamp(x):
    return 0 if x < 0 else 255 if x > 255 else int(x)


def write_png(path, width, height, rows):
    def chunk(tag, data):
        return (struct.pack('!I', len(data)) + tag + data +
                struct.pack('!I', zlib.crc32(tag + data) & 0xffffffff))

    raw = bytearray()
    for row in rows:
        raw.append(0)  # filter type 0
        raw.extend(row)

    ihdr = struct.pack('!IIBBBBB', width, height, 8, 2, 0, 0, 0)
    idat = zlib.compress(bytes(raw), 9)
    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) + chunk(b'IDAT', idat) + chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)


def smoothstep(t):
    return t * t * (3 - 2 * t)


def interp(a, b, t):
    return tuple(a[i] * (1 - t) + b[i] * t for i in range(3))


def ordered_dither(x, y, amount=0.35):
    # 4x4 Bayer matrix, centered around 0.
    bayer = [
        [0, 8, 2, 10],
        [12, 4, 14, 6],
        [3, 11, 1, 9],
        [15, 7, 13, 5],
    ]
    v = bayer[y % 4][x % 4] / 15.0 - 0.5
    return v * amount


def make_rows(width, height):
    # Refined palette:
    # Keep top brightness close to previous acceptable version,
    # but reduce the gray/steel quality by shifting slightly toward indigo.
    top = (44, 58, 97)       # #2C3A61  -- cool indigo-leaning midnight blue
    mid = (18, 28, 48)       # #121C30  -- logo region: slightly deeper
    bottom = (4, 7, 14)      # #04070E  -- blue-black, not dead neutral black

    # Logo sits around upper-middle. We want relatively quick early descent.
    knee = 0.29  # by 29% page height, we are already near the logo-zone depth
    rows = []
    for y in range(height):
        p = y / (height - 1)
        if p <= knee:
            t = p / knee
            # faster early darkening while keeping top brightness intact
            t = t ** 0.78
            rgb = interp(top, mid, t)
        else:
            t = (p - knee) / (1 - knee)
            # slower deepening afterwards for a long descent into deep space
            t = smoothstep(t)
            rgb = interp(mid, bottom, t)

        row = bytearray()
        for x in range(width):
            d = ordered_dither(x, y)
            row.extend([clamp(c + d) for c in rgb])
        rows.append(bytes(row))
    return rows


def main():
    parser = argparse.ArgumentParser(description='Generate atmospheric cover background PNG.')
    parser.add_argument('--output', default='assets/cover-background.png')
    parser.add_argument('--dpi', type=int, default=300)
    parser.add_argument('--width-mm', type=float, default=210.0)
    parser.add_argument('--height-mm', type=float, default=297.0)
    args = parser.parse_args()

    width = round(args.width_mm / 25.4 * args.dpi)
    height = round(args.height_mm / 25.4 * args.dpi)
    rows = make_rows(width, height)
    write_png(args.output, width, height, rows)
    print(f'Wrote {args.output} ({width}x{height})')


if __name__ == '__main__':
    main()
