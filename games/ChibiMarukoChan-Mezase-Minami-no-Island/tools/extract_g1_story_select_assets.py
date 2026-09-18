#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import zlib
from pathlib import Path

from render_chibi_resource_package import (
    decode_tile,
    parse_type0_package,
    render_tilemap,
    write_gray_png,
)
from rom_common import require_clean_rom

G1_STAGE_SCRIPT = 0x82AF23
G1_ACTOR_A_SCRIPT = 0x82AA30
G1_ACTOR_B_SCRIPT = 0x82AA50

EXPECTED_STAGE_RECORDS = {
    0x2000: (0x90A1C8, 0x380),
    0x21C0: (0x92E3C9, 0x220),
    0x22D0: (0x92DCAC, 0x980),
    0x5000: (0x92E391, 0x50),
    0x0000: (0x92E50D, 0x800),
    0x1000: (0x92E5F0, 0x800),
    0x1400: (0x9C821C, 0x800),
    0x4000: (0x9D8615, 0x800),
    0x7800: (0x97F95E, 0x3E0),
}


def render_tile_sheet(
    vram: bytes | bytearray,
    *,
    start_word: int,
    byte_length: int,
    bpp: int,
    cols: int = 16,
    scale: int = 3,
) -> list[bytearray]:
    tile_bytes = 16 if bpp == 2 else 32
    if byte_length % tile_bytes:
        raise ValueError(
            f"byte length 0x{byte_length:X} is not aligned to {bpp}bpp tiles"
        )
    tile_count = byte_length // tile_bytes
    rows = math.ceil(tile_count / cols)
    width = cols * 8 * scale
    height = rows * 8 * scale
    canvas = [bytearray([255] * width) for _ in range(height)]
    maxv = (1 << bpp) - 1
    base = start_word * 2

    for i in range(tile_count):
        tile = decode_tile(vram, base + i * tile_bytes, bpp)
        tx = i % cols
        ty = i // cols
        for y in range(8):
            for x in range(8):
                gray = 255 - round((tile[y][x] / maxv) * 255)
                px = (tx * 8 + x) * scale
                py = (ty * 8 + y) * scale
                for yy in range(scale):
                    row = canvas[py + yy]
                    for xx in range(scale):
                        row[px + xx] = gray
    return canvas


def crop_nonwhite(
    canvas: list[bytearray],
    *,
    margin: int = 4,
) -> list[bytearray]:
    h = len(canvas)
    w = len(canvas[0])
    xs: list[int] = []
    ys: list[int] = []
    for y, row in enumerate(canvas):
        for x, value in enumerate(row):
            if value < 250:
                xs.append(x)
                ys.append(y)
    if not xs:
        return canvas
    x0 = max(0, min(xs) - margin)
    x1 = min(w, max(xs) + margin + 1)
    y0 = max(0, min(ys) - margin)
    y1 = min(h, max(ys) + margin + 1)
    return [bytearray(row[x0:x1]) for row in canvas[y0:y1]]


def package_metadata(script_cpu: int, records) -> dict:
    return {
        "script_cpu": f"0x{script_cpu:06X}",
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
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Extract the proven Story Start/Password G1 assets from canonical Chibi ROM"
    )
    ap.add_argument("rom", type=Path)
    ap.add_argument(
        "out_dir",
        type=Path,
        nargs="?",
        default=Path("reports/generated/g1_story_select"),
    )
    args = ap.parse_args()

    rom = require_clean_rom(args.rom)
    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)

    _t, stage_flags, stage_records, stage_vram = parse_type0_package(
        rom, G1_STAGE_SCRIPT
    )
    by_dest = {r.vram_word: r for r in stage_records}
    if set(EXPECTED_STAGE_RECORDS) - set(by_dest):
        missing = sorted(set(EXPECTED_STAGE_RECORDS) - set(by_dest))
        raise RuntimeError(f"stage package is missing expected VRAM records: {missing}")

    for dest, (source_cpu, out_size) in EXPECTED_STAGE_RECORDS.items():
        rec = by_dest[dest]
        if rec.source_cpu != source_cpu or rec.output_size != out_size:
            raise RuntimeError(
                f"stage package identity mismatch at VRAM 0x{dest:04X}: "
                f"source=0x{rec.source_cpu:06X}/0x{rec.output_size:X}, "
                f"expected=0x{source_cpu:06X}/0x{out_size:X}"
            )

    stage_png = out / "g1_stage_bg.png"
    write_gray_png(
        stage_png,
        render_tilemap(
            stage_vram,
            map_word=0x0000,
            gfx_word=0x2000,
            bpp=4,
            width_tiles=32,
            height_tiles=32,
            scale=2,
        ),
    )

    options_sheet = render_tile_sheet(
        stage_vram,
        start_word=0x7800,
        byte_length=0x3E0,
        bpp=4,
        cols=16,
        scale=4,
    )
    options_png = out / "g1_start_password_tiles.png"
    write_gray_png(options_png, crop_nonwhite(options_sheet, margin=6))

    actor_exports = []
    for script_cpu, label, start_word in (
        (G1_ACTOR_A_SCRIPT, "actor_a", 0x6000),
        (G1_ACTOR_B_SCRIPT, "actor_b", 0x7000),
    ):
        _type, flags, records, vram = parse_type0_package(rom, script_cpu)
        if len(records) != 1:
            raise RuntimeError(
                f"{label}: expected one resource record, got {len(records)}"
            )
        rec = records[0]
        png_path = out / f"g1_{label}_tiles.png"
        write_gray_png(
            png_path,
            crop_nonwhite(
                render_tile_sheet(
                    vram,
                    start_word=start_word,
                    byte_length=rec.output_size,
                    bpp=4,
                    cols=16,
                    scale=3,
                ),
                margin=4,
            ),
        )
        actor_exports.append(
            {
                **package_metadata(script_cpu, records),
                "png": str(png_path),
            }
        )

    options_rec = by_dest[0x7800]
    metadata = {
        "mode": "READ_ONLY_ASSET_PROOF",
        "clean_rom_sha1": hashlib.sha1(rom).hexdigest(),
        "stage_package": {
            **package_metadata(G1_STAGE_SCRIPT, stage_records),
            "script_flags": f"0x{stage_flags:02X}",
            "stage_png": str(stage_png),
        },
        "start_password_graphics": {
            "vram_word": "0x7800",
            "source_cpu": f"0x{options_rec.source_cpu:06X}",
            "source_file": f"0x{options_rec.source_file:06X}",
            "compressed_span": f"0x{options_rec.compressed_span:X}",
            "postprocess": options_rec.postprocess,
            "decompressed_size": f"0x{options_rec.output_size:X}",
            "tile_count_4bpp": options_rec.output_size // 32,
            "png": str(options_png),
            "visible_labels": ["はじめから", "パスワード"],
            "asset_identity_claim": "STATIC_PASS",
        },
        "actor_packages": actor_exports,
        "heading_dorenisuru": {
            "status": "UNPROVEN",
            "note": "Do not assume どれにする？ lives in the Start/Password stream.",
        },
        "rom_write": False,
        "runtime_claim": False,
    }
    meta_path = out / "g1_story_select_proof.json"
    meta_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print("clean_rom_contract=PASS")
    print("story_select_execution_asset=STATIC_PASS")
    print(f"stage_script=0x{G1_STAGE_SCRIPT:06X}")
    print(
        "options_source="
        f"cpu=0x{options_rec.source_cpu:06X} "
        f"file=0x{options_rec.source_file:06X} "
        f"span=0x{options_rec.compressed_span:X} "
        f"out=0x{options_rec.output_size:X}"
    )
    print(f"stage_png={stage_png}")
    print(f"options_png={options_png}")
    print(f"metadata={meta_path}")
    print("heading_dorenisuru=UNPROVEN")
    print("rom_write=NO")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
