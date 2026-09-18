#!/usr/bin/env python3
from __future__ import annotations

import argparse
import struct
import zlib
from pathlib import Path

from rom_common import require_clean_rom


def decode_tile(data: bytes | bytearray, off: int, bpp: int) -> list[list[int]]:
    if bpp not in (2, 4):
        raise ValueError("bpp must be 2 or 4")
    need = 16 if bpp == 2 else 32
    if off < 0 or off + need > len(data):
        raise ValueError(f"tile outside ROM: off=0x{off:X}")
    out = [[0] * 8 for _ in range(8)]
    for y in range(8):
        p0 = data[off + y * 2]
        p1 = data[off + y * 2 + 1]
        p2 = data[off + 16 + y * 2] if bpp == 4 else 0
        p3 = data[off + 16 + y * 2 + 1] if bpp == 4 else 0
        for x in range(8):
            sh = 7 - x
            out[y][x] = (
                ((p0 >> sh) & 1)
                | (((p1 >> sh) & 1) << 1)
                | (((p2 >> sh) & 1) << 2)
                | (((p3 >> sh) & 1) << 3)
            )
    return out


def tile_bytes(bpp: int) -> int:
    return 16 if bpp == 2 else 32


def make_canvas(width: int, height: int, bg: int = 255) -> list[bytearray]:
    return [bytearray([bg] * width) for _ in range(height)]


def gray_for_index(idx: int, bpp: int, mask: bool) -> int:
    if mask:
        return 0 if idx else 255
    maxv = (1 << bpp) - 1
    return 255 - round((idx / maxv) * 255)


def blit_tile(
    canvas: list[bytearray],
    tile: list[list[int]],
    x0: int,
    y0: int,
    bpp: int,
    *,
    mask: bool = False,
    hflip: bool = False,
    vflip: bool = False,
    scale: int = 1,
) -> None:
    for oy in range(8):
        sy = 7 - oy if vflip else oy
        for ox in range(8):
            sx = 7 - ox if hflip else ox
            val = gray_for_index(tile[sy][sx], bpp, mask)
            for yy in range(scale):
                row = canvas[y0 + oy * scale + yy]
                for xx in range(scale):
                    row[x0 + ox * scale + xx] = val


def write_gray_png(path: Path, canvas: list[bytearray]) -> None:
    if not canvas or not canvas[0]:
        raise ValueError("empty canvas")
    height = len(canvas)
    width = len(canvas[0])
    raw = b"".join(b"\x00" + bytes(row) for row in canvas)

    def chunk(tag: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + tag
            + payload
            + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF)
        )

    png = bytearray(b"\x89PNG\r\n\x1a\n")
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)


def render_contact_sheet(
    data: bytes | bytearray,
    gfx_off: int,
    bpp: int,
    count: int,
    cols: int,
    scale: int,
    mask: bool,
) -> list[bytearray]:
    rows = (count + cols - 1) // cols
    canvas = make_canvas(cols * 8 * scale, rows * 8 * scale)
    step = tile_bytes(bpp)
    for i in range(count):
        tile = decode_tile(data, gfx_off + i * step, bpp)
        cx = (i % cols) * 8 * scale
        cy = (i // cols) * 8 * scale
        blit_tile(canvas, tile, cx, cy, bpp, mask=mask, scale=scale)
    return canvas


def render_tilemap(
    data: bytes | bytearray,
    gfx_off: int,
    map_off: int,
    bpp: int,
    width_tiles: int,
    height_tiles: int,
    scale: int,
    mask: bool,
    tile_base: int,
) -> list[bytearray]:
    canvas = make_canvas(width_tiles * 8 * scale, height_tiles * 8 * scale)
    step = tile_bytes(bpp)
    for my in range(height_tiles):
        for mx in range(width_tiles):
            p = map_off + (my * width_tiles + mx) * 2
            if p + 2 > len(data):
                raise ValueError(f"tilemap outside ROM at 0x{p:X}")
            entry = data[p] | (data[p + 1] << 8)
            tile_index = (entry & 0x03FF) + tile_base
            hflip = bool(entry & 0x4000)
            vflip = bool(entry & 0x8000)
            toff = gfx_off + tile_index * step
            if toff + step > len(data):
                continue
            tile = decode_tile(data, toff, bpp)
            blit_tile(
                canvas,
                tile,
                mx * 8 * scale,
                my * 8 * scale,
                bpp,
                mask=mask,
                hflip=hflip,
                vflip=vflip,
                scale=scale,
            )
    return canvas


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Render candidate SNES 2bpp/4bpp graphics from the canonical clean Chibi ROM"
    )
    ap.add_argument("rom", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--bpp", type=int, choices=(2, 4), required=True)
    ap.add_argument("--gfx-offset", type=lambda s: int(s, 0), required=True)
    ap.add_argument("--scale", type=int, default=3)
    ap.add_argument("--mask", action="store_true", help="render nonzero pixels as black for shape inspection")
    sub = ap.add_subparsers(dest="mode", required=True)

    p_tiles = sub.add_parser("tiles", help="render sequential tiles as a contact sheet")
    p_tiles.add_argument("--count", type=int, required=True)
    p_tiles.add_argument("--cols", type=int, default=16)

    p_map = sub.add_parser("tilemap", help="render a raw SNES 16-bit tilemap using candidate graphics")
    p_map.add_argument("--map-offset", type=lambda s: int(s, 0), required=True)
    p_map.add_argument("--width", type=int, required=True)
    p_map.add_argument("--height", type=int, required=True)
    p_map.add_argument("--tile-base", type=int, default=0)

    args = ap.parse_args()
    if args.scale < 1 or args.scale > 16:
        raise SystemExit("--scale must be in 1..16")

    data = require_clean_rom(args.rom)

    if args.mode == "tiles":
        if args.count < 1 or args.cols < 1:
            raise SystemExit("--count and --cols must be positive")
        canvas = render_contact_sheet(
            data,
            args.gfx_offset,
            args.bpp,
            args.count,
            args.cols,
            args.scale,
            args.mask,
        )
        detail = f"tiles count={args.count} cols={args.cols}"
    else:
        if args.width < 1 or args.height < 1:
            raise SystemExit("--width and --height must be positive")
        canvas = render_tilemap(
            data,
            args.gfx_offset,
            args.map_offset,
            args.bpp,
            args.width,
            args.height,
            args.scale,
            args.mask,
            args.tile_base,
        )
        detail = (
            f"tilemap map=0x{args.map_offset:X} "
            f"size={args.width}x{args.height} tile_base={args.tile_base}"
        )

    write_gray_png(args.output, canvas)
    print("clean_rom_contract=PASS")
    print("mode=READ_ONLY")
    print(f"bpp={args.bpp} gfx_offset=0x{args.gfx_offset:X} {detail}")
    print(f"output={args.output}")
    print("asset_identity_claim=NO")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
