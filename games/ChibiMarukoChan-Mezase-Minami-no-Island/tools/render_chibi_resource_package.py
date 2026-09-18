#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path

from decompress_chibi_resource import (
    cpu_to_file,
    decompress_resource,
    reorder_flag1_blocks,
)
from rom_common import require_clean_rom


@dataclass(frozen=True)
class Record:
    index: int
    vram_word: int
    source_cpu: int
    source_file: int
    compressed_span: int
    postprocess: bool
    output_size: int


def parse_type0_package(
    rom: bytes | bytearray,
    script_cpu: int,
) -> tuple[int, int, list[Record], bytearray]:
    """Parse one bank-$82 type-0 resource script and reconstruct 64 KiB VRAM."""
    if ((script_cpu >> 16) & 0xFF) != 0x82:
        raise ValueError("type-0 package pointer must be in CPU bank $82")

    script_off = cpu_to_file(script_cpu)
    script_type = rom[script_off]
    flags = rom[script_off + 1]
    if script_type != 0x00:
        raise ValueError(
            f"script ${script_cpu:06X} is type 0x{script_type:02X}, not type 00"
        )

    p = script_off + 2
    records: list[Record] = []
    vram = bytearray(0x10000)

    for index in range(64):
        if p >= len(rom):
            raise ValueError("unterminated type-0 package")
        if rom[p] == 0xFF:
            return script_type, flags, records, vram
        if p + 5 > len(rom):
            raise ValueError("truncated type-0 record")

        dest_word = rom[p] | (rom[p + 1] << 8)
        source_cpu = rom[p + 2] | (rom[p + 3] << 8) | (rom[p + 4] << 16)
        source_file = cpu_to_file(source_cpu)

        raw, header, _stats = decompress_resource(rom, source_file)
        decoded = (
            reorder_flag1_blocks(raw)
            if header.postprocess
            else raw
        )

        dest_byte = dest_word * 2
        end_byte = dest_byte + len(decoded)
        if end_byte > len(vram):
            raise ValueError(
                f"record {index}: VRAM write 0x{dest_byte:X}..0x{end_byte:X} "
                "exceeds 64 KiB"
            )
        vram[dest_byte:end_byte] = decoded

        records.append(
            Record(
                index,
                dest_word,
                source_cpu,
                source_file,
                header.span,
                header.postprocess,
                len(decoded),
            )
        )
        p += 5

    raise ValueError("type-0 package exceeded 64 records without terminator")


def decode_tile(data: bytes | bytearray, off: int, bpp: int) -> list[list[int]]:
    if bpp not in (2, 4):
        raise ValueError("bpp must be 2 or 4")
    need = 16 if bpp == 2 else 32
    if off < 0 or off + need > len(data):
        raise ValueError(f"tile outside VRAM: 0x{off:X}")
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


def render_tilemap(
    vram: bytes | bytearray,
    *,
    map_word: int,
    gfx_word: int,
    bpp: int,
    width_tiles: int,
    height_tiles: int,
    tile_base: int = 0,
    scale: int = 2,
) -> list[bytearray]:
    width = width_tiles * 8 * scale
    height = height_tiles * 8 * scale
    canvas = [bytearray([255] * width) for _ in range(height)]
    map_off = map_word * 2
    gfx_off = gfx_word * 2
    tile_size = 16 if bpp == 2 else 32
    maxv = (1 << bpp) - 1

    for my in range(height_tiles):
        for mx in range(width_tiles):
            ep = map_off + (my * width_tiles + mx) * 2
            if ep + 2 > len(vram):
                raise ValueError("tilemap outside VRAM")
            entry = vram[ep] | (vram[ep + 1] << 8)
            tile_index = (entry & 0x03FF) + tile_base
            hflip = bool(entry & 0x4000)
            vflip = bool(entry & 0x8000)
            toff = gfx_off + tile_index * tile_size
            if toff < 0 or toff + tile_size > len(vram):
                continue
            tile = decode_tile(vram, toff, bpp)

            for oy in range(8):
                sy = 7 - oy if vflip else oy
                for ox in range(8):
                    sx = 7 - ox if hflip else ox
                    idx = tile[sy][sx]
                    gray = 255 - round((idx / maxv) * 255)
                    px = (mx * 8 + ox) * scale
                    py = (my * 8 + oy) * scale
                    for yy in range(scale):
                        row = canvas[py + yy]
                        for xx in range(scale):
                            row[px + xx] = gray
    return canvas


def write_gray_png(path: Path, canvas: list[bytearray]) -> None:
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


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Reconstruct a Chibi type-0 resource package into VRAM and render one BG layer"
    )
    ap.add_argument("rom", type=Path)
    ap.add_argument("output_png", type=Path)
    ap.add_argument("--script-cpu", type=lambda s: int(s, 0), required=True)
    ap.add_argument("--map-vram", type=lambda s: int(s, 0), required=True)
    ap.add_argument("--gfx-vram", type=lambda s: int(s, 0), required=True)
    ap.add_argument("--bpp", type=int, choices=(2, 4), required=True)
    ap.add_argument("--width", type=int, default=32)
    ap.add_argument("--height", type=int, default=32)
    ap.add_argument("--tile-base", type=int, default=0)
    ap.add_argument("--scale", type=int, default=2)
    ap.add_argument("--vram-output", type=Path)
    ap.add_argument("--metadata", type=Path)
    args = ap.parse_args()

    if not 1 <= args.scale <= 8:
        raise SystemExit("--scale must be in 1..8")

    rom = require_clean_rom(args.rom)
    script_type, flags, records, vram = parse_type0_package(rom, args.script_cpu)

    canvas = render_tilemap(
        vram,
        map_word=args.map_vram,
        gfx_word=args.gfx_vram,
        bpp=args.bpp,
        width_tiles=args.width,
        height_tiles=args.height,
        tile_base=args.tile_base,
        scale=args.scale,
    )
    write_gray_png(args.output_png, canvas)

    if args.vram_output:
        args.vram_output.parent.mkdir(parents=True, exist_ok=True)
        args.vram_output.write_bytes(vram)

    meta = {
        "mode": "READ_ONLY_OFFLINE_RENDER",
        "script_cpu": f"0x{args.script_cpu:06X}",
        "script_file": f"0x{cpu_to_file(args.script_cpu):06X}",
        "script_type": script_type,
        "script_flags": f"0x{flags:02X}",
        "record_count": len(records),
        "records": [
            {
                "index": r.index,
                "vram_word": f"0x{r.vram_word:04X}",
                "source_cpu": f"0x{r.source_cpu:06X}",
                "source_file": f"0x{r.source_file:06X}",
                "compressed_span": f"0x{r.compressed_span:X}",
                "postprocess": r.postprocess,
                "output_size": f"0x{r.output_size:X}",
            }
            for r in records
        ],
        "render": {
            "map_vram_word": f"0x{args.map_vram:04X}",
            "gfx_vram_word": f"0x{args.gfx_vram:04X}",
            "bpp": args.bpp,
            "width_tiles": args.width,
            "height_tiles": args.height,
            "tile_base": args.tile_base,
            "scale": args.scale,
            "png": str(args.output_png),
        },
        "vram_sha256": hashlib.sha256(vram).hexdigest(),
        "runtime_claim": False,
    }

    if args.metadata:
        args.metadata.parent.mkdir(parents=True, exist_ok=True)
        args.metadata.write_text(
            json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    print("clean_rom_contract=PASS")
    print(f"script=0x{args.script_cpu:06X}")
    print(f"type0_records={len(records)}")
    for r in records:
        print(
            f"record={r.index:02d} vram=0x{r.vram_word:04X} "
            f"source=0x{r.source_cpu:06X} file=0x{r.source_file:06X} "
            f"span=0x{r.compressed_span:X} post={int(r.postprocess)} "
            f"out=0x{r.output_size:X}"
        )
    print(f"output_png={args.output_png}")
    if args.vram_output:
        print(f"vram_output={args.vram_output}")
    if args.metadata:
        print(f"metadata={args.metadata}")
    print("asset_identity_claim=SCREEN_DEPENDENT")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
