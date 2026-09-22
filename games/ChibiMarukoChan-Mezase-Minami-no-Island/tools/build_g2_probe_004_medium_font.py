#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

EXPECTED_BASE_SHA1 = "d0f7969aea3cad0a167dca3889ee9960be6415e0"
EXPECTED_SIZE = 0x200000
FONT_PAGE_BASES = [0x128000 + i * 0x800 for i in range(10)]
CELL_W = CELL_H = 12
PAGE_STRIDE = 16
CHECKSUM_COMPLEMENT = 0x7FDC
CHECKSUM = 0x7FDE

CUSTOM_GIDS = (
    0x083F, 0x0845, 0x084D, 0x0850, 0x0851, 0x0852, 0x0854, 0x0856,
    0x0857, 0x0858, 0x085A, 0x085C, 0x085E, 0x090F, 0x0910, 0x0916,
    0x0922, 0x0925, 0x0927, 0x092F, 0x0931, 0x093A, 0x093D, 0x093E,
    0x0947, 0x0957, 0x0959,
)


def sha1(data: bytes | bytearray) -> str:
    return hashlib.sha1(data).hexdigest()


def cell_bit_locations(gid: int):
    page = gid >> 8
    index = gid & 0xFF
    x0 = (index % 10) * CELL_W
    y0 = (index // 10) * CELL_H
    base = FONT_PAGE_BASES[page]
    for y in range(CELL_H):
        for x in range(CELL_W):
            px = x0 + x
            py = y0 + y
            off = base + py * PAGE_STRIDE + px // 8
            mask = 1 << (7 - (px % 8))
            yield y, x, off, mask


def read_cell(data: bytes | bytearray, gid: int) -> list[list[int]]:
    grid = [[0] * CELL_W for _ in range(CELL_H)]
    for y, x, off, mask in cell_bit_locations(gid):
        grid[y][x] = 1 if data[off] & mask else 0
    return grid


def thicken_right(grid: list[list[int]]) -> list[list[int]]:
    out = [row[:] for row in grid]
    for y in range(CELL_H):
        for x in range(CELL_W - 1):
            if grid[y][x]:
                out[y][x + 1] = 1
    return out


def write_cell(data: bytearray, gid: int, grid: list[list[int]]) -> set[int]:
    touched: set[int] = set()
    for y, x, off, mask in cell_bit_locations(gid):
        before = data[off]
        if grid[y][x]:
            data[off] |= mask
        else:
            data[off] &= (~mask) & 0xFF
        if data[off] != before:
            touched.add(off)
    return touched


def calc_checksum(data: bytes | bytearray) -> int:
    tmp = bytearray(data)
    tmp[CHECKSUM_COMPLEMENT:CHECKSUM + 2] = b"\x00\x00\x00\x00"
    return (sum(tmp) + 0x1FE) & 0xFFFF


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Build G2 Probe 004 by widening only the custom Probe-003 dialogue glyphs"
    )
    ap.add_argument("probe003_rom", type=Path)
    ap.add_argument("output", type=Path)
    args = ap.parse_args()

    original = args.probe003_rom.read_bytes()
    if len(original) != EXPECTED_SIZE or sha1(original) != EXPECTED_BASE_SHA1:
        raise SystemExit(
            f"Probe003 base contract failed: size={len(original)} sha1={sha1(original)}"
        )

    data = bytearray(original)
    font_touched: set[int] = set()
    for gid in CUSTOM_GIDS:
        font_touched.update(
            write_cell(data, gid, thicken_right(read_cell(data, gid)))
        )

    checksum = calc_checksum(data)
    complement = checksum ^ 0xFFFF
    data[CHECKSUM_COMPLEMENT:CHECKSUM_COMPLEMENT + 2] = complement.to_bytes(2, "little")
    data[CHECKSUM:CHECKSUM + 2] = checksum.to_bytes(2, "little")

    diffs = {i for i, (a, b) in enumerate(zip(original, data)) if a != b}
    allowed = set(font_touched)
    allowed.update(range(CHECKSUM_COMPLEMENT, CHECKSUM + 2))
    unexpected = sorted(diffs - allowed)
    if unexpected:
        raise SystemExit(
            "unexpected diff bytes: " + ", ".join(hex(x) for x in unexpected[:16])
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(data)

    print("base_probe003_contract=PASS")
    print("probe=G2_DIRECT_TEXT_PROBE_004_MEDIUM_FONT")
    print(f"custom_glyphs={len(CUSTOM_GIDS)}")
    print(f"font_diff_bytes={len(font_touched)}")
    print(f"total_diff_vs_probe003={len(diffs)}")
    print(f"checksum=0x{checksum:04X}")
    print(f"complement=0x{complement:04X}")
    print(f"sha1={sha1(data)}")
    print(f"sha256={hashlib.sha256(data).hexdigest()}")
    print(f"output={args.output}")
    print("text_payload=UNCHANGED_FROM_PROBE003")
    print("scene_logic=UNCHANGED_FROM_PROBE003")
    print("runtime_claim=NO")


if __name__ == "__main__":
    raise SystemExit(main())
