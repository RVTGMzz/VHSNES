#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import struct
import zlib
from pathlib import Path

EXPECTED_SIZE = 0x200000
EXPECTED_BUILD035_SHA1 = "054380f9b452f245471e6309eb33c7486d581462"
EXPECTED_BUILD035_SHA256 = "f8fb662a9e1b8fc5a5ff689f690ceaf332055ed86983e52b476a78852e4fd58d"
FONT_PAGE_TABLE = 0x295EE
GLYPH_SIZE = 12


def lorom_cpu_to_file(cpu: int) -> int:
    bank = (cpu >> 16) & 0xFF
    addr = cpu & 0xFFFF
    if addr < 0x8000:
        raise ValueError(f"not a LoROM ROM address: ${cpu:06X}")
    off = (bank & 0x7F) * 0x8000 + (addr - 0x8000)
    if not 0 <= off < EXPECTED_SIZE:
        raise ValueError(f"mapped file offset outside ROM: 0x{off:X}")
    return off


def load_build035(path: Path) -> bytes:
    data = path.read_bytes()
    sha1 = hashlib.sha1(data).hexdigest()
    sha256 = hashlib.sha256(data).hexdigest()
    if (
        len(data) != EXPECTED_SIZE
        or sha1 != EXPECTED_BUILD035_SHA1
        or sha256 != EXPECTED_BUILD035_SHA256
    ):
        raise RuntimeError(
            "Build 035 contract failed: "
            f"size={len(data)} sha1={sha1} sha256={sha256}"
        )
    return data


def load_glyph_ids(path: Path) -> dict[str, int]:
    out: dict[str, int] = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            out[row["unicode"]] = int(row["glyph_id_hex"], 16)
    return out


def font_page_file(data: bytes, page: int) -> int:
    p = FONT_PAGE_TABLE + page * 3
    cpu = data[p] | (data[p + 1] << 8) | (data[p + 2] << 16)
    return lorom_cpu_to_file(cpu)


def extract_glyph(data: bytes, gid: int) -> list[list[int]]:
    page = (gid >> 8) & 0xFF
    idx = gid & 0xFF
    if idx >= 100:
        raise ValueError(f"glyph index outside 10x10 page: 0x{gid:04X}")

    x0 = (idx % 10) * GLYPH_SIZE
    y0 = (idx // 10) * GLYPH_SIZE
    page_off = font_page_file(data, page)

    out: list[list[int]] = []
    for y in range(GLYPH_SIZE):
        row: list[int] = []
        for x in range(GLYPH_SIZE):
            px = x0 + x
            py = y0 + y
            byte_off = page_off + py * 16 + (px // 8)
            bit = 7 - (px & 7)
            row.append((data[byte_off] >> bit) & 1)
        out.append(row)
    return out


def required_canvas(
    text: str,
    x0: int,
    y0: int,
    advance: int,
    line_height: int,
) -> tuple[int, int]:
    lines = text.split("\n")
    widest = 0
    for line in lines:
        if not line:
            width = 0
        else:
            width = (len(line) - 1) * advance + GLYPH_SIZE
        widest = max(widest, width)
    height = (
        0
        if not lines
        else (len(lines) - 1) * line_height + GLYPH_SIZE
    )
    return x0 + widest, y0 + height


def rasterize(
    data: bytes,
    glyphs: dict[str, int],
    text: str,
    width: int,
    height: int,
    x0: int,
    y0: int,
    advance: int,
    line_height: int,
) -> list[list[int]]:
    canvas = [[0] * width for _ in range(height)]
    x = x0
    y = y0

    for ch in text:
        if ch == "\n":
            x = x0
            y += line_height
            continue

        if ch not in glyphs:
            raise ValueError(f"missing glyph for {ch!r}")

        glyph = extract_glyph(data, glyphs[ch])
        if x + GLYPH_SIZE > width or y + GLYPH_SIZE > height:
            raise ValueError(
                f"text overflow at {ch!r}: x={x} y={y} "
                f"canvas={width}x{height}"
            )

        for gy in range(GLYPH_SIZE):
            for gx in range(GLYPH_SIZE):
                if glyph[gy][gx]:
                    canvas[y + gy][x + gx] = 1

        x += advance

    return canvas


def encode_tile(
    tile: list[list[int]],
    bpp: int,
    ink: int,
) -> bytes:
    if bpp not in (2, 4):
        raise ValueError("bpp must be 2 or 4")
    maxv = (1 << bpp) - 1
    if not 1 <= ink <= maxv:
        raise ValueError(
            f"ink index must be 1..{maxv} for {bpp}bpp"
        )

    out = bytearray(16 if bpp == 2 else 32)
    for y in range(8):
        for x in range(8):
            pix = ink if tile[y][x] else 0
            shift = 7 - x

            if pix & 0x1:
                out[y * 2] |= 1 << shift
            if pix & 0x2:
                out[y * 2 + 1] |= 1 << shift
            if bpp == 4:
                if pix & 0x4:
                    out[16 + y * 2] |= 1 << shift
                if pix & 0x8:
                    out[16 + y * 2 + 1] |= 1 << shift

    return bytes(out)


def encode_canvas(
    canvas: list[list[int]],
    bpp: int,
    ink: int,
) -> bytes:
    height = len(canvas)
    width = len(canvas[0])
    if width % 8 or height % 8:
        raise ValueError("canvas dimensions must be multiples of 8")

    out = bytearray()
    for ty in range(height // 8):
        for tx in range(width // 8):
            tile = [
                [
                    canvas[ty * 8 + y][tx * 8 + x]
                    for x in range(8)
                ]
                for y in range(8)
            ]
            out.extend(encode_tile(tile, bpp, ink))
    return bytes(out)


def encode_tilemap(
    width_tiles: int,
    height_tiles: int,
    tile_base: int,
    palette: int,
    priority: bool,
) -> bytes:
    count = width_tiles * height_tiles
    if tile_base < 0 or tile_base + count > 1024:
        raise ValueError(
            f"tile index range exceeds 10-bit SNES tile field: "
            f"base={tile_base} count={count}"
        )
    if not 0 <= palette <= 7:
        raise ValueError("palette must be 0..7")

    out = bytearray()
    for i in range(count):
        entry = tile_base + i
        entry |= palette << 10
        if priority:
            entry |= 0x2000
        out.extend(entry.to_bytes(2, "little"))
    return bytes(out)


def write_preview_png(
    path: Path,
    canvas: list[list[int]],
    scale: int,
) -> None:
    height = len(canvas)
    width = len(canvas[0])
    out_width = width * scale
    out_height = height * scale

    raw = bytearray()
    for y in range(height):
        for _ in range(scale):
            raw.append(0)
            for x in range(width):
                value = 0 if canvas[y][x] else 255
                raw.extend(bytes([value]) * scale)

    def chunk(tag: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + tag
            + payload
            + struct.pack(
                ">I",
                zlib.crc32(tag + payload) & 0xFFFFFFFF,
            )
        )

    png = bytearray(b"\x89PNG\r\n\x1a\n")
    png += chunk(
        b"IHDR",
        struct.pack(
            ">IIBBBBB",
            out_width,
            out_height,
            8,
            0,
            0,
            0,
            0,
        ),
    )
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Rasterize Build 035 Vietnamese 12x12 glyphs into "
            "raw SNES 2bpp/4bpp graphics"
        )
    )
    ap.add_argument("build035", type=Path)
    ap.add_argument("output_prefix", type=Path)
    ap.add_argument("--codepage", type=Path, required=True)
    ap.add_argument("--text", required=True)
    ap.add_argument("--bpp", type=int, choices=(2, 4), required=True)
    ap.add_argument("--ink-index", type=int, default=1)
    ap.add_argument("--width-tiles", type=int)
    ap.add_argument("--height-tiles", type=int)
    ap.add_argument("--x", type=int, default=0)
    ap.add_argument("--y", type=int, default=0)
    ap.add_argument("--advance", type=int, default=12)
    ap.add_argument("--line-height", type=int, default=12)
    ap.add_argument("--tile-base", type=int, default=0)
    ap.add_argument("--palette", type=int, default=0)
    ap.add_argument("--priority", action="store_true")
    ap.add_argument("--preview-scale", type=int, default=3)
    args = ap.parse_args()

    if args.advance < 1 or args.line_height < 1:
        raise SystemExit("advance and line-height must be positive")
    if args.preview_scale < 1 or args.preview_scale > 16:
        raise SystemExit("preview-scale must be 1..16")

    data = load_build035(args.build035)
    glyphs = load_glyph_ids(args.codepage)

    missing = sorted({
        ch
        for ch in args.text
        if ch != "\n" and ch not in glyphs
    })
    if missing:
        raise SystemExit(
            "missing codepage glyphs: "
            + ", ".join(repr(ch) for ch in missing)
        )

    need_w, need_h = required_canvas(
        args.text,
        args.x,
        args.y,
        args.advance,
        args.line_height,
    )

    width_tiles = (
        args.width_tiles
        if args.width_tiles is not None
        else math.ceil(need_w / 8)
    )
    height_tiles = (
        args.height_tiles
        if args.height_tiles is not None
        else math.ceil(need_h / 8)
    )
    if width_tiles < 1 or height_tiles < 1:
        raise SystemExit("canvas tile dimensions must be positive")

    width = width_tiles * 8
    height = height_tiles * 8
    if need_w > width or need_h > height:
        raise SystemExit(
            f"text needs {need_w}x{need_h} pixels, "
            f"canvas is {width}x{height}"
        )

    canvas = rasterize(
        data,
        glyphs,
        args.text,
        width,
        height,
        args.x,
        args.y,
        args.advance,
        args.line_height,
    )
    tiles = encode_canvas(
        canvas,
        args.bpp,
        args.ink_index,
    )
    tilemap = encode_tilemap(
        width_tiles,
        height_tiles,
        args.tile_base,
        args.palette,
        args.priority,
    )

    prefix = args.output_prefix
    prefix.parent.mkdir(parents=True, exist_ok=True)
    tile_path = Path(str(prefix) + ".tiles.bin")
    map_path = Path(str(prefix) + ".tilemap.bin")
    png_path = Path(str(prefix) + ".png")
    meta_path = Path(str(prefix) + ".json")

    tile_path.write_bytes(tiles)
    map_path.write_bytes(tilemap)
    write_preview_png(
        png_path,
        canvas,
        args.preview_scale,
    )

    used = []
    seen = set()
    for ch in args.text:
        if ch == "\n" or ch in seen:
            continue
        seen.add(ch)
        used.append({
            "char": ch,
            "glyph_id": f"0x{glyphs[ch]:04X}",
        })

    meta = {
        "base": "Build 035",
        "text": args.text,
        "bpp": args.bpp,
        "ink_index": args.ink_index,
        "canvas_pixels": [width, height],
        "canvas_tiles": [width_tiles, height_tiles],
        "origin": [args.x, args.y],
        "advance": args.advance,
        "line_height": args.line_height,
        "tile_base": args.tile_base,
        "palette": args.palette,
        "priority": args.priority,
        "tile_count": width_tiles * height_tiles,
        "tile_bytes": len(tiles),
        "tilemap_bytes": len(tilemap),
        "glyphs": used,
        "outputs": {
            "tiles": str(tile_path),
            "tilemap": str(map_path),
            "preview": str(png_path),
        },
        "runtime_claim": False,
    }
    meta_path.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print("build035_contract=PASS")
    print(f"text={args.text}")
    print(f"canvas={width}x{height}")
    print(
        f"tiles={width_tiles}x{height_tiles} "
        f"count={width_tiles * height_tiles}"
    )
    print(f"tile_bytes=0x{len(tiles):X}")
    print(f"tilemap_bytes=0x{len(tilemap):X}")
    print(f"tiles_output={tile_path}")
    print(f"tilemap_output={map_path}")
    print(f"preview_output={png_path}")
    print(f"metadata_output={meta_path}")
    print("asset_layout_claim=NO")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
