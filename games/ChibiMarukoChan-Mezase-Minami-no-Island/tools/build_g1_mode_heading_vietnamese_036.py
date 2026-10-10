#!/usr/bin/env python3
"""036: replace main-menu sprite heading with Vietnamese, NO font hack.

Real main-mode initializer at ROM file 0x20047 loads graphics package
$82:A213; its record6 loads $98:F06F (file 0xC706F) into VRAM $7000.
This decoded 8192-byte 4bpp sprite sheet has 256 8x8 tiles. Only tiles
192..255 are changed (Japanese two-line 'ゲームを...どれにする？' header).

Input: exact 035 G0 title + Story Start/Password GRAPHICS-ONLY ROM,
built separately from the original Japanese clean ROM. Output is still
NOT full Story/Quiz/Fortune translation and not SNES emulator-tested.
Uses locally installed font by path; do not check font or ROM into GitHub.
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

CLEAN_SHA = "e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
BASE_035_SHA = "77a207589857d2886059057151eaf3d47530032b726744fe739e991ff81a5b80"
OUT_036_SHA = "2c8beee73e985c9a2690cc36ace335f05115c1a3e81b369e09d0cfb132117090"
MAIN_MENU_CALL_OFF = 0x20047
MAIN_MENU_CALL = bytes.fromhex("A2 13 A2 22 55 E2 80")
G1_HEADING_PACKAGE = 0x12213
G1_HEADING_ENTRY = G1_HEADING_PACKAGE + 2 + 6 * 5
HEADING_ENTRY_BYTES = bytes.fromhex("00 70 6F F0 98")
SOURCE = 0xC706F
OLD_SPAN = 3485
BPP4_TILE_BYTES = 32
FIRST_HEADING_TILE = 192
HEADING_TILES = 64
PIXELS_WIDE = 128
PIXELS_TALL = 32


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def snes_tile(pixels: bytes) -> bytes:
    if len(pixels) != 64 or max(pixels) > 15:
        raise AssertionError("tile pixels must be 8x8 native 4bpp")
    result = bytearray()
    for shift in (0, 2):
        for yy in range(8):
            lo = hi = 0
            for xx in range(8):
                value = pixels[8 * yy + xx]
                lo |= ((value >> shift) & 1) << (7-xx)
                hi |= ((value >> (shift+1)) & 1) << (7-xx)
            result.extend((lo, hi))
    return bytes(result)


def draw_heading(font_path: Path) -> Image.Image:
    if not font_path.is_file():
        raise ValueError(f"local font not found: {font_path}")
    result = Image.new("P", (PIXELS_WIDE, PIXELS_TALL), 0)
    d = ImageDraw.Draw(result)
    face = ImageFont.truetype(str(font_path), 14)
    # The retail text sprite is two stacked 16px rows; preserve structure.
    for line_index, text in ((0, "Chọn gì"), (1, "đây?")):
        left, top, right, bottom = d.textbbox((0,0), text, font=face)
        width, height = right-left, bottom-top
        if width > 120 or height > 16:
            raise AssertionError(f"Vietnamese heading clips sprite row: {text}")
        xx = (PIXELS_WIDE - width)//2 - left
        yy = 16*line_index + (16-height)//2 - top
        # Original sprite palette index 2; avoid thick shadow/outline, which
        # blurred Vietnamese accents at the game's native 128px width.
        d.text((xx, yy), text, font=face, fill=2)
    return result


def build(clean: bytes, previous: bytes, font: Path):
    if len(clean) != 0x200000 or digest(clean) != CLEAN_SHA:
        raise ValueError("requires exact 2MiB clean Japanese ROM")
    if len(previous) != 0x200000 or digest(previous) != BASE_035_SHA:
        raise ValueError("requires exact G0+G1 graphics-only checkpoint035 ROM")
    for img in (clean, previous):
        if img[MAIN_MENU_CALL_OFF:MAIN_MENU_CALL_OFF+len(MAIN_MENU_CALL)] != MAIN_MENU_CALL:
            raise AssertionError("main-menu resource execution call unexpectedly changed")
        if img[G1_HEADING_ENTRY:G1_HEADING_ENTRY+5] != HEADING_ENTRY_BYTES:
            raise AssertionError("main-menu G1 resource no longer points to $98:F06F")
    if clean[SOURCE:SOURCE+OLD_SPAN] != previous[SOURCE:SOURCE+OLD_SPAN]:
        raise AssertionError("heading resource changed in checkpoint035 base")

    raw, header, _ = decompress_resource(clean, SOURCE)
    if header.span != OLD_SPAN or header.postprocess or len(raw) != 8192:
        raise AssertionError("original heading sprite resource differs")
    pixels = draw_heading(font)
    content = bytearray(raw)
    for tile_id in range(FIRST_HEADING_TILE, FIRST_HEADING_TILE+HEADING_TILES):
        tx = (tile_id%16)*8
        ty = (tile_id//16-12)*8
        pix = bytes(pixels.getpixel((tx+x,ty+y))
                    for y in range(8) for x in range(8))
        content[tile_id*BPP4_TILE_BYTES:(tile_id+1)*BPP4_TILE_BYTES] = snes_tile(pix)
    if content[:FIRST_HEADING_TILE*BPP4_TILE_BYTES] != raw[:FIRST_HEADING_TILE*BPP4_TILE_BYTES]:
        raise AssertionError("unrelated menu words/icons were changed")
    packed = encode_chibi(bytes(content))
    span = len(packed)+2
    if span > OLD_SPAN:
        raise RuntimeError(f"new heading resource overflow: {span}>{OLD_SPAN}")
    result = bytearray(previous)
    result[SOURCE:SOURCE+OLD_SPAN] = (span.to_bytes(2,"little")+packed+
                                     bytes([0xFF])*(OLD_SPAN-span))
    decoded, recovered_header, _ = decompress_resource(result,SOURCE)
    if recovered_header.span != span or recovered_header.postprocess or decoded != bytes(content):
        raise AssertionError("game codec decompression of modified heading FAILED")
    checksum, complement = write_snes_checksum(result)
    allowed = set(range(SOURCE,SOURCE+OLD_SPAN)) | set(range(0x7FDC,0x7FE0))
    different = {i for i,(a,b) in enumerate(zip(previous,result)) if a != b}
    if different-allowed:
        raise AssertionError(f"modified outside heading resource: {sorted(different-allowed)[:6]}")
    output=bytes(result)
    actual_sha=digest(output)
    if actual_sha != OUT_036_SHA:
        raise AssertionError(f"font or codec differs from reviewed 036 candidate: {actual_sha}")
    ips, records = make_ips(clean, output)
    if (len(ips),records)!=(14452,263):
        raise AssertionError("IPS differs from reviewed 036 candidate")
    report = {
        "status":"EXPERIMENTAL_STATIC_G1_MODE_HEADING_PATCH_PASS",
        "clean_rom_sha256":CLEAN_SHA,
        "graphics_035_sha256":BASE_035_SHA,
        "graphics_036_sha256":OUT_036_SHA,
        "main_menu_initializer_file":"0x20047",
        "asset_package_cpu":"$82:A213",
        "resource_file":"0xC706F","resource_cpu":"$98:F06F","VRAM_word":"0x7000",
        "old_compressed_bytes":OLD_SPAN,"new_compressed_bytes":span,
        "decoded_bytes":8192,
        "protected_first_192_tiles":True,
        "heading_tiles_modified":"192..255",
        "Vietnamese_two_line_heading":["Chọn gì","đây?"],
        "IPS_bytes":len(ips),"IPS_records":records,
        "ROM_changed_bytes_vs_035":len(different),
        "checksum":f"0x{checksum:04X}","complement":f"0x{complement:04X}",
        "shared_resource_13_packages":"REGRESSION_SMOKE_TEST_REQUIRED",
        "runtime_SNES_emulator":"NOT_TESTED",
        "full_story_quiz_vietnamese":"NOT_INCLUDED",
        "release_ready":False
    }
    return output,ips,pixels,report


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("original_clean_rom",type=Path)
    p.add_argument("graphics_035_rom",type=Path)
    p.add_argument("out_036_rom",type=Path)
    p.add_argument("--font",type=Path,required=True)
    p.add_argument("--ips",type=Path,required=True)
    p.add_argument("--preview",type=Path)
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--allow-untested",action="store_true")
    a=p.parse_args()
    if not a.allow_untested:
        p.error("G1 graphics diagnostic not emulator-tested, explicit --allow-untested required")
    paths=[a.original_clean_rom,a.graphics_035_rom,a.out_036_rom,a.ips,a.report]
    if a.preview:paths.append(a.preview)
    if len({x.resolve() for x in paths})!=len(paths):
        p.error("input and output paths cannot overlap")
    clean=bytes(require_clean_rom(a.original_clean_rom))
    out,ips,preview,report=build(clean,a.graphics_035_rom.read_bytes(),a.font)
    a.out_036_rom.parent.mkdir(parents=True,exist_ok=True)
    a.out_036_rom.write_bytes(out)
    a.ips.parent.mkdir(parents=True,exist_ok=True)
    a.ips.write_bytes(ips)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if a.preview:
        a.preview.parent.mkdir(parents=True,exist_ok=True)
        preview.resize((1024,256),Image.Resampling.NEAREST).save(a.preview)
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
