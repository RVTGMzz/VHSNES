#!/usr/bin/env python3
"""Probe008 V2 font: crossbar-safe A, centered stacked marks, full Vietnamese set.

Pure data/preview generator. It NEVER changes a ROM or claims runtime PASS.
Requires the hand-drawn custom face from customize_g2_probe008_font.py.
"""
from __future__ import annotations

import csv
import json
import unicodedata as ud
from pathlib import Path

import customize_g2_probe008_font as original
import generate_g2_probe008_font as base

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "translation/codepage/g2_probe008_complete_candidate_v2.json"
COMBINING_TONES = tuple(base.TONES)
STACKING_MODS = {"\u0302", "\u0306"}
NEW_LEAD = 0x85
START_TRAIL = 0x40


def extra_chars(codepage: dict[str, dict]) -> list[str]:
    vowels = "aăâeêioôơuưy"
    tone_set = ("", "\u0301", "\u0300", "\u0309", "\u0303", "\u0323")
    uppers = {ud.normalize("NFC", letter + tone).upper()
              for letter in vowels for tone in tone_set} | {"Đ"}
    missing_upper = sorted(uppers - set(codepage))
    if len(missing_upper) != 49:
        raise AssertionError(f"expected 49 missing Vietnamese capitals, got {len(missing_upper)}")
    extras = missing_upper + ["ằ", "ẵ", "ỵ"]
    if len(extras) != 52 or len(set(extras)) != 52:
        raise AssertionError("unexpected extended codepoint set")
    return extras


def repaired_points(ch: str) -> set[tuple[int, int]]:
    seq = ud.normalize("NFD", ch)
    letter = seq[0]
    marks = set(seq[1:])
    if not marks or letter not in original.LOWER | original.UPPER:
        # Unmarked Latin/punctuation and đ/Đ retain hand-drawn original outlines.
        return glyph_points(original.glyph(ch))
    old_rows = (original.LOWER | original.UPPER)[letter].split("/")
    stacked = bool(marks & STACKING_MODS and marks & set(COMBINING_TONES))
    # The accented A body is EXPLICIT: the complete horizontal crossbar is row 2.
    if letter == "A":
        rows = ["0011100", "0100010", "1111111", "1000001", "1000001"]
    elif letter.isupper():
        # Other capitals preserve both their structural centre and near-base rows.
        rows = [old_rows[i] for i in (0, 1, 3, 4, 6)]
    else:
        rows = old_rows
    # Keep a dot-below row and avoid the hardware-clipped final row (11).
    body_y = 5 if stacked else 4
    if letter == "y" and "\u0323" in marks:
        rows = ["1000010", "1000010", "0111110", "0000010", "0000010", "0000110"]
        body_y = 4
    if body_y + len(rows) > 10:
        body_y = 10 - len(rows)
    result = base.points("/".join(rows), 2, body_y)
    mod_y = 3 if stacked else 1
    if "\u0302" in marks:
        result |= base.points("00100/01010", 3, mod_y)
    if "\u0306" in marks:
        result |= base.points("10001/01110", 3, mod_y)
    if "\u031b" in marks:
        result |= {(9, 2), (9, 3), (8, 4), (7, 4)}
    for mark, pattern in base.TONES.items():
        if mark in marks:
            # Compare with V1's x=7 for stacked marks. This uses centered x=3..7.
            x = 3 if mark in ("\u0300", "\u0303") else (4 if mark == "\u0309" else 5)
            result |= base.points(pattern, x, 0)
    if "\u0323" in marks:
        result.add((5, 10))
    if any(not (0 <= x < 12 and 0 <= y < 11) for x, y in result):
        raise ValueError(f"out-of-range glyph {ch!r}: {sorted(result)}")
    return result


def glyph_points(bitmap_hex: str) -> set[tuple[int, int]]:
    raw = bytes.fromhex(bitmap_hex)
    if len(raw) != 18:
        raise ValueError("12x12 bitmap must have 18 bytes")
    return {(i % 12, i // 12) for i in range(144)
            if raw[i // 8] & (1 << (7 - (i % 8)))}


def bitmap_hex(pts: set[tuple[int, int]]) -> str:
    value = sum(1 << (143 - (y * 12 + x)) for x, y in pts)
    return value.to_bytes(18, "big").hex()


def generate_complete() -> dict[str, dict]:
    with (ROOT / "translation/codepage/vi_codepage_v4_fe4_native.csv").open(
            encoding="utf-8", newline="") as file:
        codepage = {row["unicode"]: row for row in csv.DictReader(file)}
    extras = extra_chars(codepage)
    combined = {}
    for ch, row in codepage.items():
        visual = row["visual_key"]
        combined[ch] = {"code_hex": row["code_hex"], "visual_key": visual,
                        "bitmap_hex": bitmap_hex(repaired_points(visual))}
    for i, ch in enumerate(extras):
        combined[ch] = {"code_hex": f"{NEW_LEAD:02X}{START_TRAIL+i:02X}",
                        "visual_key": ch, "bitmap_hex": bitmap_hex(repaired_points(ch))}
    if len(combined) != 212 or len({r["code_hex"] for r in combined.values()}) != 212:
        raise AssertionError("duplicate code or incomplete full Vietnamese set")
    # Preserve all 160 existing 84xx assignments exactly; the 52 additions
    # are a PROPOSAL for a separate new 85xx table, not yet proven native-safe.
    for ch, row in codepage.items():
        if combined[ch]["code_hex"] != row["code_hex"]:
            raise AssertionError(f"reassigned existing codepoint: {ch}")
    # Accented capitals A MUST have a full 7-pixel horizontal crossbar.
    for ch in combined:
        seq = ud.normalize("NFD", ch)
        if seq[0] == "A" and len(seq) > 1:
            pts = glyph_points(combined[ch]["bitmap_hex"])
            ys = {y for y in range(11) if all((x, y) in pts for x in range(2, 9))}
            if not ys:
                raise AssertionError(f"uppercase A crossbar missing: {ch}")
    # Stacked hỏi/ngã must never use V1's far-right x=7 tone origin.
    for ch in combined:
        seq = ud.normalize("NFD", ch)
        if any(m in seq for m in STACKING_MODS) and any(
                m in seq for m in ("\u0309", "\u0303")):
            pts = glyph_points(combined[ch]["bitmap_hex"])
            upper_tone = {x for x, y in pts if y <= 2}
            if not upper_tone or max(upper_tone) > 7:
                raise AssertionError(f"stacked mark too far right: {ch}")
    return combined


def main() -> None:
    output = generate_complete()
    OUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    print(f"complete_unicode_entries={len(output)}")
    print("missing_capitals_added=49; lowercase_added=3")
    print("accent_A_crossbar=PASS; stacked_tone_centering=PASS")
    print("mapping/allocation=PROPOSED; runtime=UNTESTED; ROM=UNCHANGED")


if __name__ == "__main__":
    main()
