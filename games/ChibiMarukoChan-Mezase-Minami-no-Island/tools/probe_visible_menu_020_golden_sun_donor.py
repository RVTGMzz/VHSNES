#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path

EXPECTED_SIZE = 0x200000
EXPECTED_SHA1 = "08a2415362f69788ec76b1a36044dc1f1a5f2ea1"
LOROM_HEADER = 0x7FC0
CHECKSUM_COMPLEMENT = LOROM_HEADER + 0x1C
CHECKSUM = LOROM_HEADER + 0x1E
FONT_PAGE_BASES = [0x128000 + i * 0x800 for i in range(10)]
CELL_W = CELL_H = 12
PAGE_STRIDE_BYTES = 16
GS_FONT_BASE = 0x32224

MENU_FIELDS = (
    (0x28818, "ストーリーモード", "Âm thanh"),
    (0x2882E, "対戦モード", "Ước!!"),
    (0x2883C, "チーム対戦モード", "Đấu đội!"),
    (0x28852, "まるこＱ", "Vẽ!!"),
    (0x2885E, "まるこペイント", "Hỏi nhé"),
    (0x28870, "まるこみくじ", "Ổn rồi"),
)

# Golden Sun (VH) donor slots identified from the correctly decoded
# 16-bit-per-scanline font records. ASCII chars use ord(ch).
GS_EXT = {
    "Â": 0xC6,
    "Ư": 0xF4,
    "ớ": 0xA6,
    "Đ": 0xFF,
    "ấ": 0x85,
    "đ": 0xBA,
    "ộ": 0xA3,
    "ẽ": 0x8C,
    "ỏ": 0x9B,
    "é": 0x8A,
    "Ổ": 0xE6,
    "ồ": 0x9F,
}


def sha1(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def require_clean(path: Path) -> bytes:
    data = path.read_bytes()
    if len(data) != EXPECTED_SIZE or sha1(data) != EXPECTED_SHA1:
        raise RuntimeError(f"clean ROM contract failed: size={len(data)} sha1={sha1(data)}")
    return data


def calc_snes_checksum(data: bytes | bytearray) -> int:
    tmp = bytearray(data)
    tmp[CHECKSUM_COMPLEMENT : CHECKSUM + 2] = b"\x00\x00\x00\x00"
    return (sum(tmp) + 0x1FE) & 0xFFFF


def write_snes_checksum(data: bytearray) -> tuple[int, int]:
    checksum = calc_snes_checksum(data)
    complement = checksum ^ 0xFFFF
    data[CHECKSUM_COMPLEMENT : CHECKSUM_COMPLEMENT + 2] = complement.to_bytes(2, "little")
    data[CHECKSUM : CHECKSUM + 2] = checksum.to_bytes(2, "little")
    return checksum, complement


def donor_grid(gba: bytes, ch: str) -> tuple[list[list[int]], int, int]:
    code = ord(ch) if ord(ch) < 128 else GS_EXT[ch]
    off = GS_FONT_BASE + (code - 0x20) * 32
    rec = gba[off : off + 32]
    if len(rec) != 32:
        raise RuntimeError(f"short Golden Sun glyph record for {ch!r}")

    width = int.from_bytes(rec[:2], "little")
    bitmap = rec[2:]

    # Correct record decode: 2-byte metric followed by 15 rows of
    # one little-endian 16-bit 1bpp row mask. Do NOT treat the row bytes
    # as two color planes; doing so folds right-side pixels into artifacts.
    src = [[0] * 16 for _ in range(15)]
    for y in range(15):
        word = int.from_bytes(bitmap[y * 2 : y * 2 + 2], "little")
        for x in range(16):
            src[y][x] = 1 if word & (1 << (15 - x)) else 0

    pts = [(x, y) for y in range(15) for x in range(16) if src[y][x]]
    if not pts:
        raise RuntimeError(f"blank Golden Sun donor glyph for {ch!r} code=0x{code:02X}")

    min_x = min(x for x, _y in pts)
    max_x = max(x for x, _y in pts)
    bbox_w = max_x - min_x + 1
    x_shift = (12 - bbox_w) // 2 - min_x

    out = [[0] * 12 for _ in range(12)]
    for x, y in pts:
        # Most donor ink already fits in 0..11. Under-dot glyphs use row 12;
        # fold only that final dot row into Chibi row 11.
        target_y = y if y <= 11 else 11 if y == 12 else None
        target_x = x + x_shift
        if target_y is not None and 0 <= target_x < 12:
            out[target_y][target_x] = 1

    return out, code, width


def write_chibi_cell(data: bytearray, glyph_id: int, grid: list[list[int]]) -> None:
    page = glyph_id >> 8
    index = glyph_id & 0xFF
    x0 = (index % 10) * CELL_W
    y0 = (index // 10) * CELL_H
    base = FONT_PAGE_BASES[page]

    for y in range(12):
        for x in range(12):
            px = x0 + x
            py = y0 + y
            off = base + py * PAGE_STRIDE_BYTES + px // 8
            mask = 1 << (7 - (px % 8))
            if grid[y][x]:
                data[off] |= mask
            else:
                data[off] &= (~mask) & 0xFF


def main() -> int:
    ap = argparse.ArgumentParser(description="Build Chibi menu Probe 020 using Golden Sun (VH) as a glyph-shape donor")
    ap.add_argument("clean_rom", type=Path)
    ap.add_argument("probe010_rom", type=Path, help="Known Probe 010 baseline artifact; used only as a deterministic overlay source")
    ap.add_argument("golden_sun_vh_gba", type=Path)
    ap.add_argument("codepage_csv", type=Path)
    ap.add_argument("output_rom", type=Path)
    args = ap.parse_args()

    clean = require_clean(args.clean_rom)
    probe010 = args.probe010_rom.read_bytes()
    if len(probe010) != EXPECTED_SIZE:
        raise RuntimeError("Probe 010 size mismatch")
    gba = args.golden_sun_vh_gba.read_bytes()

    # Build always starts from CLEAN. Reapply Probe 010's exact byte overlay,
    # then replace only the selected donor glyph cells and test text.
    out = bytearray(clean)
    for i, (a, b) in enumerate(zip(clean, probe010)):
        if a != b:
            out[i] = b
    if bytes(out) != probe010:
        raise RuntimeError("Probe 010 overlay reconstruction mismatch")

    rows = list(csv.DictReader(args.codepage_csv.open(encoding="utf-8-sig")))
    cp = {
        row["unicode"]: (bytes.fromhex(row["code_hex"]), int(row["glyph_id_hex"], 16), row["glyph_source"])
        for row in rows
    }

    chars: list[str] = []
    for _off, _jp, vi in MENU_FIELDS:
        for ch in vi:
            if ch in cp and ch not in " !?" and ch not in chars:
                chars.append(ch)

    for ch in chars:
        _code, glyph_id, _source = cp[ch]
        grid, _gs_code, _gs_width = donor_grid(gba, ch)
        write_chibi_cell(out, glyph_id, grid)

    for off, jp, vi in MENU_FIELDS:
        source = jp.encode("cp932")
        replacement = b"".join(cp[ch][0] for ch in vi)
        if len(source) != len(replacement):
            raise RuntimeError(f"unit-length mismatch at 0x{off:X}: {vi!r}")
        out[off : off + len(source)] = replacement

    checksum, complement = write_snes_checksum(out)
    args.output_rom.write_bytes(out)

    print(f"checksum=0x{checksum:04X}")
    print(f"complement=0x{complement:04X}")
    print(f"sha1={sha1(out)}")
    print(f"sha256={hashlib.sha256(out).hexdigest()}")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
