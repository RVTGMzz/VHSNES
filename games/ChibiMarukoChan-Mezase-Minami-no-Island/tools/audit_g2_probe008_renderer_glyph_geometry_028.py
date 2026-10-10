#!/usr/bin/env python3
"""Check actual renderer glyph geometry without altering any ROM.

Rejects the 025 mistake of treating $001FB2 as the actual glyph ID.
At $85:8E7B original glyph ID arrives in A, saved by PHA;
at $85:90EE original renderer has already computed glyph page pointer
and 12px atlas coordinates in direct-page $18/$08/$0A.
This script audits ALL 1,100 valid page/cell combinations and the three
strict-two-byte G2 dialogue fields. It is not SNES CPU execution.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

V2_SHA = "2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd"
RECORDS = (0x181CE, 0x18247, 0x182C0)


def word_select(gid: int) -> bool:
    return (0x083A <= gid <= 0x0863 or 0x090A <= gid <= 0x0963
            or 0x0A00 <= gid <= 0x0A53 or gid in (0x0159, 0x015A))


def shift_select(page_pointer: bytes, atlas_x: int, atlas_y: int,
                 pages: list[bytes]) -> bool:
    if page_pointer == pages[8]:
        return atlas_y > 60 or (atlas_y == 60 and atlas_x >= 96)
    if page_pointer == pages[9]:
        return atlas_y >= 12
    if page_pointer == pages[10]:
        return atlas_y < 96 or (atlas_y == 96 and atlas_x <= 36)
    if page_pointer == pages[1]:
        return ((atlas_y == 96 and atlas_x == 108)
                or (atlas_y == 108 and atlas_x == 0))
    return False


def map_code(rom: bytes, code: bytes) -> int:
    lead, trail = code
    if not (0x80 <= lead <= 0x9F and 0x40 <= trail <= 0xFC):
        raise AssertionError(f"unsupported original code {code.hex()}")
    lead_off = 0x29756 + 2 * (lead - 0x80)
    table = int.from_bytes(rom[lead_off:lead_off+2], "little")
    if table < 0x8000:
        raise AssertionError(f"invalid lead pointer for {code.hex()}")
    glyph_off = 0x28000 + (table & 0x7FFF) + 2*(trail - 0x40)
    return int.from_bytes(rom[glyph_off:glyph_off+2], "little")


def audit(rom: bytes) -> dict:
    if len(rom) != 0x200000 or hashlib.sha256(rom).hexdigest() != V2_SHA:
        raise ValueError("requires EXACT V2 13px font-only ROM, no header")
    expected = (
        (0x28E7B, "8B DA 5A 48 AF B2 1F 00 22 05 8E 85"),
        (0x28E87, "68 85 02 29 FF 00 AA BF 0C 96 85 29 FF 00"),
        (0x28EA8, "BF 00 F8 85"),
        (0x28EAE, "BF 01 F8 85"),
        (0x290EC, "A6 10 BF 96 96 85"),
    )
    for offset, codes in expected:
        token = bytes.fromhex(codes)
        if rom[offset:offset+len(token)] != token:
            raise AssertionError(f"renderer byte signature mismatch at {offset:06X}")

    bcd = rom[0x2960C:0x29670]
    if bcd != bytes(int(f"{v//10}{v%10}", 16) for v in range(100)):
        raise AssertionError("glyph-cell BCD lookup changed")

    pages = [rom[0x2F800+3*i:0x2F803+3*i] for i in range(11)]
    if len(set(pages)) != 11:
        raise AssertionError("font page pointer collisions")

    count9 = 0
    for page in range(11):
        for cell in range(100):
            gid = (page << 8) | cell
            packed = bcd[cell]
            x, y = 12*(packed & 0x0F), 12*(packed >> 4)
            first = word_select(gid)
            second = shift_select(pages[page], x, y, pages)
            if first != second:
                raise AssertionError(
                    f"word/shift disagree gid={gid:04X} atlas=({x},{y})"
                )
            count9 += first
    if count9 != 218:
        raise AssertionError(f"unexpected 9px scope {count9}")

    rows = []
    for offset in RECORDS:
        raw = rom[offset:offset+106]
        if len(raw) != 106:
            raise AssertionError("record too short")
        separators = []
        drawable = 0
        for j in range(53):
            code = raw[2*j:2*j+2]
            if code == bytes.fromhex("816F"):
                separators.append(j)
                continue
            gid = map_code(rom, code)
            if not word_select(gid):
                raise AssertionError(f"G2 code not covered {code.hex()}->{gid:04X}")
            drawable += 1
        if separators != [16, 34, 52] or drawable != 50:
            raise AssertionError("G2 original strict-two-byte record changed")
        rows.append({"file_offset": f"0x{offset:06X}", "code_pairs": 53,
                     "drawable_pairs": drawable, "separators": separators})
    if map_code(rom,bytes.fromhex("8175")) != 0x0159 or \
       map_code(rom,bytes.fromhex("8176")) != 0x015A:
        raise AssertionError("original Japanese quote mapping was changed")

    return {
        "status": "READ_ONLY_STATIC_GLYPH_GEOMETRY_PASS",
        "rom_sha256": V2_SHA,
        "valid_page_cell_ids": 1100,
        "first_vs_second_lookup_disagreements": 0,
        "nine_pixel_glyph_ids": count9,
        "native_13_pixel_glyph_ids": 1100 - count9,
        "quote_glyph_ids": ["0159", "015A"],
        "g2_original_records": rows,
        "glyph_source": "original renderer A saved by PHA, not $001FB2",
        "second_hook_geometry": "original DP $18 font page, $08/$0A atlas coordinates",
        "requires_new_WRAM_flag": False,
        "rom_written": False,
        "previous_025_runtime": "USER_SCREENSHOT_FAIL",
        "SNES_emulator_execution": "NOT_PERFORMED",
        "release_ready": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("exact_probe008_v2_font_only", type=Path)
    p.add_argument("output_report", type=Path)
    args = p.parse_args()
    if args.exact_probe008_v2_font_only.resolve() == args.output_report.resolve():
        p.error("read-only ROM and report paths must differ")
    result = audit(args.exact_probe008_v2_font_only.read_bytes())
    args.output_report.parent.mkdir(parents=True, exist_ok=True)
    args.output_report.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
