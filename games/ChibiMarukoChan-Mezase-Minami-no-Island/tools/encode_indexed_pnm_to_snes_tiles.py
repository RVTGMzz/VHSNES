#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import re
import struct
import zlib
from pathlib import Path


def parse_ascii_pnm(path: Path) -> tuple[int, int, int, list[list[int]]]:
    data = path.read_bytes()
    data = re.sub(rb"#.*?(?:\r?\n|$)", b" ", data)
    tokens = data.split()
    if not tokens:
        raise ValueError("empty PNM")

    magic = tokens[0]
    if magic not in (b"P1", b"P2"):
        raise ValueError(
            "only ASCII PBM/PGM P1/P2 are supported"
        )

    if len(tokens) < 3:
        raise ValueError("incomplete PNM header")

    width = int(tokens[1])
    height = int(tokens[2])
    if width <= 0 or height <= 0:
        raise ValueError("invalid PNM dimensions")

    pos = 3
    if magic == b"P1":
        max_value = 1
    else:
        if len(tokens) < 4:
            raise ValueError("missing P2 max value")
        max_value = int(tokens[3])
        pos = 4

    values = [int(x) for x in tokens[pos:]]
    if len(values) != width * height:
        raise ValueError(
            f"pixel count {len(values)} != "
            f"{width}*{height}"
        )

    if any(v < 0 or v > max_value for v in values):
        raise ValueError("pixel outside declared PNM range")

    pixels = [
        values[y * width:(y + 1) * width]
        for y in range(height)
    ]
    return width, height, max_value, pixels


def pad_pixels(
    pixels: list[list[int]],
    width: int,
    height: int,
    out_width: int,
    out_height: int,
) -> list[list[int]]:
    if out_width < width or out_height < height:
        raise ValueError("output canvas smaller than source")

    out = [
        [0] * out_width
        for _ in range(out_height)
    ]
    for y in range(height):
        out[y][0:width] = pixels[y]
    return out


def encode_tile(
    tile: list[list[int]],
    bpp: int,
) -> bytes:
    if bpp not in (2, 4):
        raise ValueError("bpp must be 2 or 4")

    max_index = (1 << bpp) - 1
    out = bytearray(16 if bpp == 2 else 32)

    for y in range(8):
        for x in range(8):
            pix = tile[y][x]
            if not 0 <= pix <= max_index:
                raise ValueError(
                    f"pixel index {pix} exceeds {bpp}bpp"
                )

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
    pixels: list[list[int]],
    bpp: int,
) -> bytes:
    height = len(pixels)
    width = len(pixels[0])
    if width % 8 or height % 8:
        raise ValueError(
            "canvas dimensions must be multiples of 8"
        )

    out = bytearray()
    for ty in range(height // 8):
        for tx in range(width // 8):
            tile = [
                [
                    pixels[ty * 8 + y][tx * 8 + x]
                    for x in range(8)
                ]
                for y in range(8)
            ]
            out.extend(
                encode_tile(tile, bpp)
            )
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
            "tile range exceeds 10-bit SNES tile field"
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
    pixels: list[list[int]],
    max_index: int,
    scale: int,
) -> None:
    height = len(pixels)
    width = len(pixels[0])
    out_width = width * scale
    out_height = height * scale

    raw = bytearray()
    for y in range(height):
        for _ in range(scale):
            raw.append(0)
            for x in range(width):
                pix = pixels[y][x]
                gray = (
                    255
                    if max_index == 0
                    else 255 - round(
                        (pix / max_index) * 255
                    )
                )
                raw.extend(
                    bytes([gray]) * scale
                )

    def chunk(tag: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + tag
            + payload
            + struct.pack(
                ">I",
                zlib.crc32(tag + payload)
                & 0xFFFFFFFF,
            )
        )

    png = bytearray(
        b"\x89PNG\r\n\x1a\n"
    )
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
    png += chunk(
        b"IDAT",
        zlib.compress(
            bytes(raw),
            9,
        ),
    )
    png += chunk(b"IEND", b"")
    path.write_bytes(png)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Encode indexed P1/P2 pixel art into "
            "raw SNES 2bpp/4bpp tiles for G0/custom graphics"
        )
    )
    ap.add_argument("input_pnm", type=Path)
    ap.add_argument("output_prefix", type=Path)
    ap.add_argument(
        "--bpp",
        type=int,
        choices=(2, 4),
        required=True,
    )
    ap.add_argument(
        "--pad-to-tiles",
        action="store_true",
    )
    ap.add_argument(
        "--tile-base",
        type=int,
        default=0,
    )
    ap.add_argument(
        "--palette",
        type=int,
        default=0,
    )
    ap.add_argument(
        "--priority",
        action="store_true",
    )
    ap.add_argument(
        "--preview-scale",
        type=int,
        default=3,
    )
    args = ap.parse_args()

    if not 1 <= args.preview_scale <= 16:
        raise SystemExit(
            "preview-scale must be 1..16"
        )

    width, height, declared_max, pixels = (
        parse_ascii_pnm(args.input_pnm)
    )
    max_index = (1 << args.bpp) - 1

    actual_max = max(
        max(row)
        for row in pixels
    )
    if actual_max > max_index:
        raise SystemExit(
            f"pixel index {actual_max} exceeds "
            f"{args.bpp}bpp max {max_index}"
        )

    if width % 8 or height % 8:
        if not args.pad_to_tiles:
            raise SystemExit(
                f"source {width}x{height} is not tile aligned; "
                "use --pad-to-tiles"
            )
        out_width = math.ceil(width / 8) * 8
        out_height = math.ceil(height / 8) * 8
        pixels = pad_pixels(
            pixels,
            width,
            height,
            out_width,
            out_height,
        )
        width = out_width
        height = out_height

    width_tiles = width // 8
    height_tiles = height // 8

    tiles = encode_canvas(
        pixels,
        args.bpp,
    )
    tilemap = encode_tilemap(
        width_tiles,
        height_tiles,
        args.tile_base,
        args.palette,
        args.priority,
    )

    prefix = args.output_prefix
    prefix.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    tiles_path = Path(
        str(prefix) + ".tiles.bin"
    )
    map_path = Path(
        str(prefix) + ".tilemap.bin"
    )
    png_path = Path(
        str(prefix) + ".png"
    )
    meta_path = Path(
        str(prefix) + ".json"
    )

    tiles_path.write_bytes(tiles)
    map_path.write_bytes(tilemap)
    write_preview_png(
        png_path,
        pixels,
        max_index,
        args.preview_scale,
    )

    meta = {
        "source": str(args.input_pnm),
        "source_declared_max": declared_max,
        "actual_max_index": actual_max,
        "bpp": args.bpp,
        "canvas_pixels": [width, height],
        "canvas_tiles": [
            width_tiles,
            height_tiles,
        ],
        "tile_count": (
            width_tiles * height_tiles
        ),
        "tile_base": args.tile_base,
        "palette": args.palette,
        "priority": args.priority,
        "tile_bytes": len(tiles),
        "tilemap_bytes": len(tilemap),
        "outputs": {
            "tiles": str(tiles_path),
            "tilemap": str(map_path),
            "preview": str(png_path),
        },
        "palette_note": (
            "pixel indices only; actual SNES palette colors "
            "must come from the proven target screen palette"
        ),
        "runtime_claim": False,
    }
    meta_path.write_text(
        json.dumps(
            meta,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print("pnm_parse=PASS")
    print(
        f"canvas={width}x{height} "
        f"tiles={width_tiles}x{height_tiles}"
    )
    print(
        f"tile_bytes=0x{len(tiles):X}"
    )
    print(
        f"tilemap_bytes=0x{len(tilemap):X}"
    )
    print(f"tiles_output={tiles_path}")
    print(f"tilemap_output={map_path}")
    print(f"preview_output={png_path}")
    print(f"metadata_output={meta_path}")
    print("palette_identity_claim=NO")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
