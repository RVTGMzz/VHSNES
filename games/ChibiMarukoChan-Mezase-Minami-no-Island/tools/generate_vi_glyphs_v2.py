#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import unicodedata
from pathlib import Path

UP = {
"A":[".###.","#...#","#...#","#####","#...#","#...#","#...#"],
"B":["####.","#...#","#...#","####.","#...#","#...#","####."],
"C":[".####","#....","#....","#....","#....","#....",".####"],
"D":["####.","#...#","#...#","#...#","#...#","#...#","####."],
"E":["#####","#....","#....","####.","#....","#....","#####"],
"F":["#####","#....","#....","####.","#....","#....","#...."],
"G":[".###.","#...#","#....","#.###","#...#","#...#",".###."],
"H":["#...#","#...#","#...#","#####","#...#","#...#","#...#"],
"I":[".###.","..#..","..#..","..#..","..#..","..#..",".###."],
"J":["..###","...#.","...#.","...#.","#..#.","#..#.",".##.."],
"K":["#...#","#..#.","#.#..","##...","#.#..","#..#.","#...#"],
"L":["#....","#....","#....","#....","#....","#....","#####"],
"M":["#...#","##.##","#.#.#","#.#.#","#...#","#...#","#...#"],
"N":["#...#","##..#","##..#","#.#.#","#..##","#..##","#...#"],
"O":[".###.","#...#","#...#","#...#","#...#","#...#",".###."],
"P":["####.","#...#","#...#","####.","#....","#....","#...."],
"Q":[".###.","#...#","#...#","#...#","#.#.#","#..#.",".##.#"],
"R":["####.","#...#","#...#","####.","#.#..","#..#.","#...#"],
"S":[".####","#....","#....",".###.","....#","....#","####."],
"T":["#####","..#..","..#..","..#..","..#..","..#..","..#.."],
"U":["#...#","#...#","#...#","#...#","#...#","#...#",".###."],
"V":["#...#","#...#","#...#","#...#","#...#",".#.#.","..#.."],
"W":["#...#","#...#","#...#","#...#","#.#.#","##.##","#...#"],
"X":["#...#",".#.#.","..#..","..#..","..#..",".#.#.","#...#"],
"Y":["#...#",".#.#.","..#..","..#..","..#..","..#..","..#.."],
"Z":["#####","....#","...#.","..#..",".#...","#....","#####"],
}

LO = {
"a":[".....",".....",".###.","....#",".####","#...#",".####"],
"b":["#....","#....","#.##.","##..#","#...#","#...#","####."],
"c":[".....",".....",".###.","#...#","#....","#...#",".###."],
"d":["....#","....#",".##.#","#..##","#...#","#...#",".####"],
"e":[".....",".....",".###.","#...#","#####","#....",".####"],
"f":["..##.",".#...",".###.",".#...",".#...",".#...",".#..."],
"g":[".....",".....",".####","#...#",".####","....#",".###."],
"h":["#....","#....","#.##.","##..#","#...#","#...#","#...#"],
"i":["..#..",".....",".##..","..#..","..#..","..#..",".###."],
"j":["...#.",".....","..##.","...#.","...#.","#..#.",".##.."],
"k":["#....","#....","#..#.","#.#..","##...","#.#..","#..#."],
"l":[".##..","..#..","..#..","..#..","..#..","..#..",".###."],
"m":[".....",".....","##.#.","#.#.#","#.#.#","#...#","#...#"],
"n":[".....",".....","#.##.","##..#","#...#","#...#","#...#"],
"o":[".....",".....",".###.","#...#","#...#","#...#",".###."],
"p":[".....",".....","####.","#...#","####.","#....","#...."],
"q":[".....",".....",".####","#...#",".####","....#","....#"],
"r":[".....",".....","#.##.","##...","#....","#....","#...."],
"s":[".....",".....",".####","#....",".###.","....#","####."],
"t":[".#...",".#...","###..",".#...",".#...",".#.#.","..#.."],
"u":[".....",".....","#...#","#...#","#...#","#..##",".##.#"],
"v":[".....",".....","#...#","#...#","#...#",".#.#.","..#.."],
"w":[".....",".....","#...#","#...#","#.#.#","##.##","#...#"],
"x":[".....",".....","#...#",".#.#.","..#..",".#.#.","#...#"],
"y":[".....",".....","#...#","#...#",".####","....#",".###."],
"z":[".....",".....","#####","...#.","..#..",".#...","#####"],
}

PROBE6_D_HEX = "0003e0210208208ff82082082103e0000000"


def blank() -> list[list[int]]:
    return [[0 for _ in range(12)] for _ in range(12)]


def setpx(g: list[list[int]], x: int, y: int, v: int = 1) -> None:
    if 0 <= x < 12 and 0 <= y < 12:
        g[y][x] = v


def line_h(g: list[list[int]], x0: int, x1: int, y: int) -> None:
    for x in range(x0, x1 + 1):
        setpx(g, x, y)


def pattern_5_to_7(pat: list[str]) -> list[list[int]]:
    out = [[0 for _ in range(7)] for _ in range(7)]
    for y in range(7):
        for x in range(7):
            src_x = (x * 5) // 7
            out[y][x] = 1 if pat[y][src_x] == "#" else 0
    return out


def unpack_hex(bitmap_hex: str) -> list[list[int]]:
    raw = bytes.fromhex(bitmap_hex)
    if len(raw) != 18:
        raise RuntimeError("expected 18-byte packed 12x12 bitmap")
    bits: list[int] = []
    for b in raw:
        bits.extend((b >> shift) & 1 for shift in range(7, -1, -1))
    g = blank()
    for y in range(12):
        for x in range(12):
            g[y][x] = bits[y * 12 + x]
    return g


def punctuation(key: str) -> list[list[int]]:
    g = blank()
    if key == '"':
        for y in range(2, 5):
            setpx(g, 3, y); setpx(g, 4, y)
            setpx(g, 7, y); setpx(g, 8, y)
    elif key == "'":
        for y in range(2, 5):
            setpx(g, 5, y); setpx(g, 6, y)
    elif key == "-":
        line_h(g, 3, 8, 6)
    elif key == ":":
        for y in (4, 5, 8, 9):
            setpx(g, 5, y); setpx(g, 6, y)
    else:
        raise KeyError(key)
    return g


def build_glyph(ch: str) -> list[list[int]]:
    if ch in {'"', "'", "-", ":"}:
        return punctuation(ch)
    if ch == "Đ":
        return unpack_hex(PROBE6_D_HEX)

    special_bar = False
    if ch == "đ":
        base = "d"
        marks: list[int] = []
        special_bar = True
    else:
        nfd = unicodedata.normalize("NFD", ch)
        base = nfd[0]
        marks = [ord(c) for c in nfd[1:]]

    pat = (UP if base.isupper() else LO).get(base)
    if pat is None:
        raise RuntimeError(f"no base pattern for {ch!r} -> {base!r}")

    g = blank()
    body = pattern_5_to_7(pat)
    for y in range(7):
        for x in range(7):
            if body[y][x]:
                setpx(g, x + 2, y + 4)

    if 0x031B in marks:
        for x, y in ((9,4),(10,3),(10,4),(9,5)):
            setpx(g, x, y)

    if special_bar:
        line_h(g, 1, 9, 7)

    if 0x0302 in marks:
        for x, y in ((3,3),(4,2),(5,2),(6,2),(7,3)):
            setpx(g, x, y)
    if 0x0306 in marks:
        for x, y in ((3,2),(4,3),(5,3),(6,3),(7,2)):
            setpx(g, x, y)

    if 0x0301 in marks:
        for x, y in ((5,1),(6,0),(7,0)):
            setpx(g, x, y)
    if 0x0300 in marks:
        for x, y in ((3,0),(4,0),(5,1)):
            setpx(g, x, y)
    if 0x0309 in marks:
        for x, y in ((4,0),(5,0),(6,1),(5,2),(4,2)):
            setpx(g, x, y)
    if 0x0303 in marks:
        for x, y in ((3,1),(4,0),(5,0),(6,1),(7,1),(8,0)):
            setpx(g, x, y)
    if 0x0323 in marks:
        setpx(g, 5, 11); setpx(g, 6, 11)

    return g


def pack_hex(g: list[list[int]]) -> str:
    bits: list[int] = []
    for y in range(12):
        for x in range(12):
            bits.append(1 if g[y][x] else 0)
    raw = bytearray()
    for i in range(0, 144, 8):
        b = 0
        for bit in bits[i:i+8]:
            b = (b << 1) | bit
        raw.append(b)
    return raw.hex()


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate deterministic 12x12 handcrafted Vietnamese font V2")
    here = Path(__file__).resolve().parent
    ap.add_argument("--codepage", type=Path, default=here.parent / "translation" / "codepage" / "vi_codepage_v2.csv")
    ap.add_argument("--output", type=Path, default=here.parent / "translation" / "codepage" / "vi_glyphs_v2.json")
    args = ap.parse_args()

    rows = list(csv.DictReader(args.codepage.open("r", encoding="utf-8-sig", newline="")))
    visual_to_gid: dict[str, int] = {}
    for row in rows:
        if row["glyph_source"] != "custom":
            continue
        key = row["visual_key"]
        gid = int(row["glyph_id_hex"], 16)
        prior = visual_to_gid.setdefault(key, gid)
        if prior != gid:
            raise RuntimeError(f"visual alias {key!r} maps to multiple glyph IDs")

    out: dict[str, dict[str, str]] = {}
    for key, gid in sorted(visual_to_gid.items(), key=lambda kv: kv[1]):
        out[key] = {"bitmap_hex": pack_hex(build_glyph(key)), "glyph_id": f"{gid:04X}"}

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, separators=(",", ":")), encoding="utf-8")
    print(f"custom_visual_glyphs={len(out)}")
    print(f"output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
