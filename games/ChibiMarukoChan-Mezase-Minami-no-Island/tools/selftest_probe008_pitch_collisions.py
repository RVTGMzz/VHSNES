#!/usr/bin/env python3
"""All-pairs 12x12 bitmap ink collision audit for Probe008 V2 (ROM-free).

This tests only literal adjacent-pixel overlaps, not the game's renderer,
VRAM/WRAM behavior, wrapping, typography or hardware runtime.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / "translation/codepage/g2_probe008_complete_candidate_v2.json"


def points(bmp: str) -> frozenset[tuple[int, int]]:
    data = bytes.fromhex(bmp)
    if len(data) != 18:
        raise AssertionError("expected exactly 18 bytes / 144 pixels")
    return frozenset((i % 12, i // 12) for i in range(144)
                     if data[i // 8] & (0x80 >> (i % 8)))


def count_adjacent_collisions(bitmap_rows, pitch: int) -> tuple[int, int]:
    """Return (ordered pair count with overlap, max ink pixels overwritten)."""
    pt = [points(row["bitmap_hex"]) for row in bitmap_rows]
    rights = [frozenset((x+pitch,y) for x,y in glyph) for glyph in pt]
    count, max_ink = 0, 0
    for left in pt:
        for shifted in rights:
            n = len(left & shifted)
            if n:
                count += 1
                max_ink = max(max_ink, n)
    return count, max_ink


def main():
    entries = json.loads(FONT.read_text(encoding="utf-8"))
    if len(entries) != 212 or len({v["bitmap_hex"] for v in entries.values()}) != 210:
        raise AssertionError("unexpected Probe008 V2 character/bitmap count")
    rows = list(entries.values())
    assert len({v["code_hex"] for v in rows}) == 212
    counts = {}
    for pitch in (13, 12, 10, 9, 8, 7):
        pairs, max_ink = count_adjacent_collisions(rows, pitch)
        counts[pitch] = {"overlapping_ordered_pairs": pairs, "maximum_overlap_pixels": max_ink}
    if counts[9]["overlapping_ordered_pairs"] != 0:
        raise AssertionError("9px causes unexpected adjacent bitmap collision")
    if counts[7]["overlapping_ordered_pairs"] == 0:
        raise AssertionError("7px negative-control no longer exposes collisions")
    print(json.dumps({
        "status": "OFFLINE_BITMAP_ALL_PAIRS_PASS",
        "glyph_entries": len(rows), "ordered_pairs_tested_per_pitch": len(rows)**2,
        "results": counts, "emulator_runtime": "UNTESTED",
        "release_ready": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
