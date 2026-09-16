#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from rom_common import digest_bytes, require_clean_rom, write_snes_checksum, validate_internal_header

TEXT_OFFSET = 0x28818
SOURCE_TEXT = "ストーリーモード"
PROBE_TEXT = "ＴＥＳＴ１２３４"

MAP_TABLE_82_TRAIL_4F = 0x29880
CODE_E = 0x8264
E_ENTRY = MAP_TABLE_82_TRAIL_4F + ((CODE_E & 0xFF) - 0x4F) * 2
EXPECTED_E_GLYPH_ID = 0x0000

# Static reverse of renderer $85:8E7B:
# glyph high byte = one of ten 128x128 1bpp pages;
# glyph low byte = binary cell index 0..99 in a 10x10 grid of 12x12 cells.
CUSTOM_GLYPH_ID = 0x0963  # page 9, index 99 decimal
FONT_PAGE9_FILE = 0x12C800
CELL_INDEX = 99
CELL_W = 12
CELL_H = 12
PAGE_STRIDE_BYTES = 16
MAPPING_AUDIT_START = 0x29796
MAPPING_AUDIT_END = 0x2B380

CUSTOM_BITMAP = (
    "............",
    "..#####.....",
    "..#....#....",
    "..#.....#...",
    "..#.....#...",
    "#########...",
    "..#.....#...",
    "..#.....#...",
    "..#....#....",
    "..#####.....",
    "............",
    "............",
)


def u16le(data: bytes | bytearray, off: int) -> int:
    return data[off] | (data[off + 1] << 8)


def cell_xy(index: int) -> tuple[int, int]:
    if not 0 <= index < 100:
        raise RuntimeError("cell index must be 0..99")
    return (index % 10) * CELL_W, (index // 10) * CELL_H


def cell_bits(page_base: int, index: int):
    x0, y0 = cell_xy(index)
    for y in range(CELL_H):
        for x in range(CELL_W):
            px = x0 + x
            off = page_base + (y0 + y) * PAGE_STRIDE_BYTES + px // 8
            mask = 1 << (7 - (px % 8))
            yield y, x, off, mask


def assert_blank_cell(data: bytes | bytearray) -> None:
    ink = sum(1 for _y, _x, off, mask in cell_bits(FONT_PAGE9_FILE, CELL_INDEX) if data[off] & mask)
    if ink:
        raise RuntimeError(f"custom slot 0x{CUSTOM_GLYPH_ID:04X} is not blank: {ink} lit pixels")


def write_bitmap(data: bytearray) -> set[int]:
    if len(CUSTOM_BITMAP) != 12 or any(len(row) != 12 for row in CUSTOM_BITMAP):
        raise RuntimeError("CUSTOM_BITMAP must be exactly 12x12")
    x0, y0 = cell_xy(CELL_INDEX)
    touched: set[int] = set()
    for y, row in enumerate(CUSTOM_BITMAP):
        for x, ch in enumerate(row):
            px, py = x0 + x, y0 + y
            off = FONT_PAGE9_FILE + py * PAGE_STRIDE_BYTES + px // 8
            mask = 1 << (7 - px % 8)
            before = data[off]
            if ch == "#":
                data[off] |= mask
            elif ch == ".":
                data[off] &= (~mask) & 0xFF
            else:
                raise RuntimeError("bitmap may contain only . and #")
            if data[off] != before:
                touched.add(off)
    return touched


def main() -> int:
    ap = argparse.ArgumentParser(description="Probe 006: custom Vietnamese Đ glyph through proven two-byte menu path")
    ap.add_argument("rom", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data = require_clean_rom(args.rom)
    original = bytes(data)
    source = SOURCE_TEXT.encode("cp932")
    replacement = PROBE_TEXT.encode("cp932")
    if len(source) != 16 or len(replacement) != 16:
        raise RuntimeError("probe must remain exactly 8 two-byte units")
    if bytes(data[TEXT_OFFSET:TEXT_OFFSET + 16]) != source:
        raise RuntimeError("menu source identity mismatch")
    if u16le(data, E_ENTRY) != EXPECTED_E_GLYPH_ID:
        raise RuntimeError("full-width E mapping identity mismatch")

    assert_blank_cell(data)
    gid_bytes = CUSTOM_GLYPH_ID.to_bytes(2, "little")
    reuse_hits = bytes(data[MAPPING_AUDIT_START:MAPPING_AUDIT_END]).count(gid_bytes)
    if reuse_hits:
        raise RuntimeError(f"candidate glyph 0x{CUSTOM_GLYPH_ID:04X} has {reuse_hits} mapping-region reuse hits")

    print(f"text_offset=0x{TEXT_OFFSET:06X}")
    print(f"E_entry=0x{E_ENTRY:06X} clean_glyph_id=0x0000")
    print(f"custom_glyph_id=0x{CUSTOM_GLYPH_ID:04X}")
    print("custom_cell=page9 index99 x108 y108 12x12")
    print("custom_cell_blank=PASS")
    print("custom_mapping_reuse_hits=0")
    print("expected_runtime_first_line=TĐST1234")
    print("runtime_claim=NO")
    if args.dry_run:
        print("dry_run=PASS")
        return 0

    data[TEXT_OFFSET:TEXT_OFFSET + 16] = replacement
    data[E_ENTRY:E_ENTRY + 2] = gid_bytes
    bitmap_touched = write_bitmap(data)
    checksum, complement = write_snes_checksum(data)
    header = validate_internal_header(data)
    if not header["checksum_matches"] or not header["checksum_pair_valid"]:
        raise RuntimeError("post-build checksum validation failed")

    allowed = set(range(TEXT_OFFSET, TEXT_OFFSET + 16))
    allowed.update(range(E_ENTRY, E_ENTRY + 2))
    allowed.update(bitmap_touched)
    allowed.update(range(0x7FDC, 0x7FE0))
    diffs = {i for i, (a, b) in enumerate(zip(original, data)) if a != b}
    unexpected = sorted(diffs - allowed)
    if unexpected:
        raise RuntimeError(f"unexpected diff bytes: {[hex(x) for x in unexpected[:16]]}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(data)
    ident = digest_bytes(data)
    print(f"bitmap_diff_bytes={len(bitmap_touched)}")
    print(f"total_diff_bytes={len(diffs)}")
    print(f"build_checksum=0x{checksum:04X}")
    print(f"build_complement=0x{complement:04X}")
    print(f"output_sha1={ident.sha1}")
    print(f"output_sha256={ident.sha256}")
    print(f"output={args.output}")
    print("diff_surface=PASS")
    print("build=PASS")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
