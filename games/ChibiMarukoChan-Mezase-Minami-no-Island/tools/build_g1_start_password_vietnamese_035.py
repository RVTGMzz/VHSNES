#!/usr/bin/env python3
"""Build G1 Story choice sprites Bắt đầu / Mật khẩu in the REAL game resource.

Exact clean SNES ROM -> modified sprite stream $97:F95E (file 0xBF95E).
Original G1 menu package $82:AF23 loads this 992-byte 4bpp graphics
stream to VRAM word $7800, containing the two original Japanese labels
and a 2-tile icon. Only label tiles are changed, icon29-30 and blank
tile15 remain byte-identical. Recompress in-place only (source slot 436
bytes). Optionally merge with exact 034 G0 title-only ROM and create an
IPS from the exact clean source. This is NOT a gameplay-tested build.
Local font path required; DO NOT commit commercial ROM or TTF font data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from build_g0_first_boot_title_votri_experimental import encode_chibi, make_ips
from decompress_chibi_resource import decompress_resource
from rom_common import require_clean_rom, write_snes_checksum

SOURCE = 0xBF95E
SOURCE_SPAN = 436
DECODED = 992
G1_PACKAGE = 0x12F23
PACKAGE_GFX_ENTRY = G1_PACKAGE + 2 + 8 * 5
ENTRY_ORIGINAL = bytes.fromhex("00 78 5E F9 97")
CLEAN_SHA = "e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
G0_ONLY_SHA = "012cdfb87eae1b7c5a9feada4e1c322541e3c91ba45ba0b857e08a2465f47ce0"
G1_ONLY_SHA = "9a7bddb9afb7062a63c775e647c9ee04c226202bd16d23a7d5aadf091ea1bdaf"
COMBINED_SHA = "77a207589857d2886059057151eaf3d47530032b726744fe739e991ff81a5b80"
LABELS = (("Bắt đầu", 0, 0, 120, 88), ("Mật khẩu", 0, 8, 104, 92))


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encode_tile(tile: bytes) -> bytes:
    if len(tile) != 64 or max(tile) > 15:
        raise ValueError("requires exact 8x8 4bpp tile")
    result = bytearray()
    for offset in (0, 2):
        for row in range(8):
            low = high = 0
            for x in range(8):
                val = tile[8 * row + x]
                low |= ((val >> offset) & 1) << (7 - x)
                high |= ((val >> (offset + 1)) & 1) << (7 - x)
            result.extend((low, high))
    return bytes(result)


def draw_labels(font: str) -> Image.Image:
    canvas = Image.new("P", (128, 16), 0)
    face = ImageFont.truetype(font, 12)
    for label, origin_x, origin_y, allowed_width, render_width in LABELS:
        tmp = Image.new("L", (150, 32), 0)
        d = ImageDraw.Draw(tmp)
        bbox = d.textbbox((0, 0), label, font=face)
        d.text((-bbox[0], -bbox[1]), label, font=face, fill=255)
        art = tmp.crop((0, 0, bbox[2] - bbox[0], bbox[3] - bbox[1]))
        art = art.resize((render_width, 8), Image.Resampling.LANCZOS)
        left = origin_x + (allowed_width - render_width) // 2
        for y in range(8):
            for x in range(render_width):
                if art.getpixel((x, y)) >= 94:
                    canvas.putpixel((left + x, origin_y + y), 1)
        # Extra right-hand palette-index 2 shade, within the original
        # sprite slot; G1 palette indices 1/2 were already in use.
        for y in range(8):
            for x in range(allowed_width - 1):
                sx = origin_x + x
                if (canvas.getpixel((sx, origin_y + y)) == 1
                        and canvas.getpixel((sx + 1, origin_y + y)) == 0):
                    canvas.putpixel((sx + 1, origin_y + y), 2)
    return canvas


def create_g1(clean: bytes, font: str) -> tuple[bytes, dict]:
    if sha(clean) != CLEAN_SHA or len(clean) != 0x200000:
        raise ValueError("requires exact original Chibi Japanese 2MiB ROM")
    if clean[PACKAGE_GFX_ENTRY:PACKAGE_GFX_ENTRY + 5] != ENTRY_ORIGINAL:
        raise AssertionError("Story G1 package no longer loads source $97:F95E")
    raw, hdr, _ = decompress_resource(clean, SOURCE)
    if hdr.span != SOURCE_SPAN or len(raw) != DECODED or hdr.postprocess:
        raise AssertionError("G1 option resource shape unexpectedly changed")

    image = draw_labels(font)
    replacement = bytearray(raw)
    for tile_index in range(29):
        if tile_index == 15:
            continue
        x0, y0 = tile_index % 16 * 8, tile_index // 16 * 8
        pixels = bytes(image.getpixel((x0 + x, y0 + y))
                       for y in range(8) for x in range(8))
        replacement[tile_index * 32:tile_index * 32 + 32] = encode_tile(pixels)

    if (replacement[15*32:16*32] != raw[15*32:16*32]
            or replacement[29*32:] != raw[29*32:]):
        raise AssertionError("one of the original icons/spacing tile was changed")
    packed = encode_chibi(bytes(replacement))
    span = len(packed) + 2
    if span > SOURCE_SPAN:
        raise RuntimeError(f"G1 graphics would overflow original slot {span}/{SOURCE_SPAN}")
    out = bytearray(clean)
    out[SOURCE:SOURCE + SOURCE_SPAN] = (span.to_bytes(2, "little") +
                                      packed + b"\xFF" * (SOURCE_SPAN - span))
    roundtrip, newhdr, _ = decompress_resource(out, SOURCE)
    if roundtrip != replacement or newhdr.span != span or newhdr.postprocess:
        raise AssertionError("patched G1 graphic does not decompress byte-exactly")
    ck, cp = write_snes_checksum(out)
    allowed = (set(range(SOURCE, SOURCE + SOURCE_SPAN))
               | set(range(0x7FDC, 0x7FE0)))
    changed = {i for i,(a,b) in enumerate(zip(clean, out)) if a != b}
    if changed - allowed:
        raise AssertionError("G1 touched a ROM byte outside its original resource")
    result = bytes(out)
    if sha(result) != G1_ONLY_SHA:
        raise AssertionError("G1 bytes disagree with local exact-resource experiment")
    return result, {
        "scope": "G1 actual Story Start / Password resource only",
        "source_cpu": "$97:F95E", "source_file": f"0x{SOURCE:X}",
        "original_compressed_span": SOURCE_SPAN,
        "new_compressed_span": span,
        "uncompressed_bytes": len(replacement),
        "native_icon_tiles_29_30_unchanged": True,
        "blank_tile15_unchanged": True,
        "labels": [item[0] for item in LABELS],
        "g1_only_sha256": sha(result),
        "SNES_checksum": f"0x{ck:04X}",
        "SNES_complement": f"0x{cp:04X}",
        "SNES_runtime": "NOT_TESTED",
        "release_ready": False,
    }


def combine(clean: bytes, g1: bytes, g0: bytes) -> tuple[bytes, dict]:
    if sha(g0) != G0_ONLY_SHA:
        raise ValueError("exact G0 title-only checkpoint034 ROM required")
    edit_g0 = {i for i,(a,b) in enumerate(zip(clean, g0)) if a != b}
    edit_g1 = {i for i,(a,b) in enumerate(zip(clean, g1)) if a != b}
    overlap = (edit_g0 & edit_g1) - set(range(0x7FDC, 0x7FE0))
    if overlap:
        raise AssertionError(f"ROM collision between G0 and G1: {sorted(overlap)[:10]}")
    output = bytearray(g0)
    output[SOURCE:SOURCE+SOURCE_SPAN] = g1[SOURCE:SOURCE+SOURCE_SPAN]
    ck, cp = write_snes_checksum(output)
    if (output[0x12095:0x12098] != bytes.fromhex("07 E9 86")
            or output[0x36907:0x36907+3420] != g0[0x36907:0x36907+3420]):
        raise AssertionError("G0 title asset relocation damaged during merge")
    digest = sha(output)
    if digest != COMBINED_SHA:
        raise AssertionError("unexpected G0+G1 combined ROM hash")
    patch, records = make_ips(clean, output)
    if len(patch) != 10880 or records != 225:
        raise AssertionError("IPS patch binary changed from independent proof")
    return bytes(output), {
        "status": "STATIC_G0_G1_MERGE_PASS_NOT_RUNTIME",
        "base_clean_sha256": CLEAN_SHA,
        "g0_sha256": G0_ONLY_SHA, "g1_sha256": G1_ONLY_SHA,
        "combined_sha256": digest, "G0_G1_collision_bytes": 0,
        "SNES_checksum": f"0x{ck:04X}", "SNES_complement": f"0x{cp:04X}",
        "ips_bytes": len(patch), "ips_records": records,
        "g1_heading_chon_gi_day": "NOT_PATCHED",
        "full_game_translation": False, "SNES_runtime": "NOT_TESTED",
        "release_ready": False,
    }, patch


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("clean_rom", type=Path)
    parser.add_argument("g0_title_only_rom", type=Path)
    parser.add_argument("out_combined_rom", type=Path)
    parser.add_argument("--font-bold", required=True)
    parser.add_argument("--ips", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--allow-untested", action="store_true")
    args = parser.parse_args()
    if not args.allow_untested:
        parser.error("experimental graphics-only build; pass --allow-untested")
    paths = (args.clean_rom, args.g0_title_only_rom, args.out_combined_rom,
             args.ips, args.report)
    if len({p.resolve() for p in paths}) != len(paths):
        parser.error("input/output files must all be different")
    clean = bytes(require_clean_rom(args.clean_rom))
    g1, qa = create_g1(clean, args.font_bold)
    result, joint, patch = combine(clean, g1, args.g0_title_only_rom.read_bytes())
    args.out_combined_rom.parent.mkdir(parents=True, exist_ok=True)
    args.out_combined_rom.write_bytes(result)
    args.ips.parent.mkdir(parents=True, exist_ok=True)
    args.ips.write_bytes(patch)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps({"G1": qa, "joint": joint},
                                      ensure_ascii=False, indent=2)+"\n",
                           encoding="utf-8")
    print(json.dumps(joint, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
