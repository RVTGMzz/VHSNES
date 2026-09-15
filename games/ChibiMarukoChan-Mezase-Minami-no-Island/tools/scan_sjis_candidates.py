#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path

from rom_common import require_clean_rom


def is_sjis_lead(x: int) -> bool:
    return 0x81 <= x <= 0x9F or 0xE0 <= x <= 0xFC


def is_sjis_trail(x: int) -> bool:
    return 0x40 <= x <= 0x7E or 0x80 <= x <= 0xFC


def is_japanese_char(ch: str) -> bool:
    o = ord(ch)
    return (
        0x3040 <= o <= 0x30FF
        or 0x3400 <= o <= 0x9FFF
        or ch in "、。・ー〜～…「」『』【】（）［］｛｝！？：；％＋－×÷＝▼"
    )


def is_allowed_char(ch: str) -> bool:
    if ch == " " or "0" <= ch <= "9" or "A" <= ch <= "Z" or "a" <= ch <= "z":
        return True
    return is_japanese_char(ch)


def decode_unit(data: bytes | bytearray, pos: int) -> tuple[str, int] | None:
    x = data[pos]
    if 0x20 <= x <= 0x7E:
        return chr(x), 1
    if is_sjis_lead(x) and pos + 1 < len(data) and is_sjis_trail(data[pos + 1]):
        try:
            ch = bytes(data[pos:pos + 2]).decode("cp932")
        except UnicodeDecodeError:
            return None
        if len(ch) == 1 and is_allowed_char(ch):
            return ch, 2
    return None


def scan(data: bytes | bytearray, min_japanese: int = 3):
    i = 0
    while i < len(data):
        unit = decode_unit(data, i)
        if unit is None:
            i += 1
            continue
        start = i
        chars: list[str] = []
        while i < len(data):
            unit = decode_unit(data, i)
            if unit is None:
                break
            ch, n = unit
            chars.append(ch)
            i += n
        text = "".join(chars)
        jp_count = sum(is_japanese_char(c) for c in text)
        if jp_count >= min_japanese and text.strip():
            yield start, i, text, jp_count


def main() -> int:
    ap = argparse.ArgumentParser(description="Conservative candidate scanner for direct CP932/Shift-JIS text runs")
    ap.add_argument("rom", type=Path)
    ap.add_argument("--csv", type=Path)
    ap.add_argument("--min-japanese", type=int, default=3)
    ap.add_argument("--start", type=lambda x: int(x, 0), default=0)
    ap.add_argument("--end", type=lambda x: int(x, 0))
    args = ap.parse_args()

    data = require_clean_rom(args.rom)
    rows = []
    for start, end, text, jp_count in scan(data, args.min_japanese):
        if start < args.start:
            continue
        if args.end is not None and start >= args.end:
            continue
        rows.append({
            "file_offset": f"0x{start:X}",
            "end_offset": f"0x{end:X}",
            "byte_length": end - start,
            "japanese_chars": jp_count,
            "text": text,
            "status": "candidate_unreviewed",
        })

    print(f"candidates={len(rows)}")
    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=rows[0].keys() if rows else ["file_offset", "end_offset", "byte_length", "japanese_chars", "text", "status"])
            w.writeheader()
            w.writerows(rows)
        print(f"csv={args.csv}")
    else:
        for row in rows:
            print(f"{row['file_offset']}..{row['end_offset']}  {row['text']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
