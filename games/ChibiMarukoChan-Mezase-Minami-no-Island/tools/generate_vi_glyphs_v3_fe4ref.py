#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import unicodedata
from pathlib import Path

FE4_REFERENCE_SIZE = 4_194_816
FE4_REFERENCE_SHA1 = "2556860f8f51d0895c191a5f614c9088fc8fd98e"
FE4_COPIER_HEADER = 0x200
FE4_FONT_BASE = 0x128000
FE4_FONT_SIZE = 0x3C00

# FE4 Vietnamese reference font layout recovered from the user-supplied ROM.
# A-Z occupy cells 0x00..0x19; a-z occupy 0x1A..0x33.
UPPER = {chr(ord('A') + i): i for i in range(26)}
LOWER = {chr(ord('a') + i): 0x1A + i for i in range(26)}
ACCENTED_LOWER = {
    'á':0x3A,'à':0x3B,'ả':0x3C,'ã':0x3D,'ạ':0x3E,'â':0x3F,
    'ấ':0x40,'ầ':0x41,'ẩ':0x42,'ẫ':0x43,'ậ':0x44,'ă':0x45,
    'ắ':0x46,'ằ':0x47,'ẳ':0x48,'ẵ':0x49,'ặ':0x4A,
    'í':0x4B,'ì':0x4C,'ỉ':0x4D,'ĩ':0x4E,'ị':0x4F,
    'é':0x50,'è':0x51,'ẻ':0x52,'ẽ':0x53,'ẹ':0x54,'ê':0x55,
    'ế':0x56,'ề':0x57,'ể':0x58,'ễ':0x59,'ệ':0x5A,
    'ó':0x5B,'ò':0x5C,'ỏ':0x5D,'õ':0x5E,'ọ':0x5F,'ô':0x60,
    'ố':0x61,'ồ':0x62,'ổ':0x63,'ỗ':0x64,'ộ':0x65,'ơ':0x66,
    'ớ':0x67,'ờ':0x68,'ở':0x69,'ỡ':0x6A,'ợ':0x6B,
    'ú':0x6C,'ù':0x6D,'ủ':0x6E,'ũ':0x6F,'ụ':0x70,'ư':0x71,
    'ứ':0x72,'ừ':0x73,'ử':0x74,'ữ':0x75,'ự':0x76,
    'ý':0x77,'ỳ':0x78,'ỷ':0x79,'ỹ':0x7A,'ỵ':0x7B,
}


def require_reference(path: Path) -> bytes:
    data = path.read_bytes()
    sha1 = hashlib.sha1(data).hexdigest()
    if len(data) != FE4_REFERENCE_SIZE or sha1 != FE4_REFERENCE_SHA1:
        raise RuntimeError(
            f"FE4 reference identity mismatch: size={len(data)} sha1={sha1}; "
            f"expected size={FE4_REFERENCE_SIZE} sha1={FE4_REFERENCE_SHA1}"
        )
    return data[FE4_COPIER_HEADER:]


def decode_2bpp_tile(buf: bytes, tile_index: int) -> list[list[int]]:
    off = tile_index * 16
    out = [[0] * 8 for _ in range(8)]
    for y in range(8):
        p0 = buf[off + y * 2]
        p1 = buf[off + y * 2 + 1]
        for x in range(8):
            bit = 7 - x
            out[y][x] = 1 if (((p0 >> bit) & 1) | (((p1 >> bit) & 1) << 1)) else 0
    return out


def decode_cell(font: bytes, glyph_index: int) -> list[list[int]]:
    # The 2bpp sheet is 16 tiles wide. One logical glyph cell occupies a 2x2
    # tile block (16x16), with the Vietnamese/Latin ink confined to the left
    # 8 pixels. This is the source shape we adapt into Chibi's 12x12 cell.
    cell_row = glyph_index // 8
    cell_col = glyph_index % 8
    tl = cell_row * 32 + cell_col * 2
    out = [[0] * 16 for _ in range(16)]
    for dx, dy, ti in ((0,0,tl),(8,0,tl+1),(0,8,tl+16),(8,8,tl+17)):
        tile = decode_2bpp_tile(font, ti)
        for y in range(8):
            for x in range(8):
                out[dy + y][dx + x] = tile[y][x]
    return out


def source_cell_for_char(font: bytes, ch: str) -> list[list[int]]:
    if ch in UPPER:
        return [row[:8] for row in decode_cell(font, UPPER[ch])]
    if ch in LOWER:
        return [row[:8] for row in decode_cell(font, LOWER[ch])]
    if ch in ACCENTED_LOWER:
        return [row[:8] for row in decode_cell(font, ACCENTED_LOWER[ch])]

    if ch in ('Đ', 'đ'):
        base = 'D' if ch == 'Đ' else 'd'
        src = source_cell_for_char(font, base)
        out = [row[:] for row in src]
        # The reference ROM has no clean standalone Đ/đ cell in the recovered
        # Latin block, so transfer the FE4 D/d body and add a matching 1px bar.
        for x in range(8 if ch == 'Đ' else 7):
            out[10][x] = 1
        return out

    if ch == 'ñ':
        out = [row[:] for row in source_cell_for_char(font, 'n')]
        tilde = source_cell_for_char(font, 'ã')
        for y in range(8):
            for x in range(8):
                out[y][x] |= tilde[y][x]
        return out

    nfd = unicodedata.normalize('NFD', ch)
    if len(nfd) > 1 and nfd[0] in UPPER:
        base = nfd[0]
        lower_equiv = unicodedata.normalize('NFC', base.lower() + ''.join(nfd[1:]))
        if lower_equiv in ACCENTED_LOWER:
            out = [row[:] for row in source_cell_for_char(font, base)]
            ref = source_cell_for_char(font, lower_equiv)
            # Transfer the reference mark area while preserving the uppercase
            # FE4 body. Rows 0..7 contain above/attached marks; 14..15 contain
            # the below-dot family.
            for y in list(range(8)) + [14, 15]:
                for x in range(8):
                    out[y][x] |= ref[y][x]
            return out

    raise RuntimeError(f"FE4 reference has no transferable glyph recipe for {ch!r}")


def resize_nn(src: list[list[int]], width: int = 10, height: int = 12) -> list[list[int]]:
    h0 = len(src)
    w0 = len(src[0])
    out = [[0] * width for _ in range(height)]
    for y in range(height):
        sy = min(h0 - 1, int(y * h0 / height))
        for x in range(width):
            sx = min(w0 - 1, int(x * w0 / width))
            out[y][x] = src[sy][sx]
    return out


def build_chibi_glyph(font: bytes, ch: str) -> list[list[int]]:
    src = source_cell_for_char(font, ch)  # 8x16
    resized = resize_nn(src, 10, 12)
    out = [[0] * 12 for _ in range(12)]
    for y in range(12):
        for x in range(10):
            out[y][x + 1] = resized[y][x]
    return out


def pack_hex(grid: list[list[int]]) -> str:
    bits = [grid[y][x] for y in range(12) for x in range(12)]
    raw = bytearray()
    for i in range(0, 144, 8):
        b = 0
        for bit in bits[i:i+8]:
            b = (b << 1) | (1 if bit else 0)
        raw.append(b)
    return raw.hex()


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate Chibi 12x12 glyph bank from user-supplied FE4 Vietnamese font reference")
    ap.add_argument("reference_rom", type=Path)
    ap.add_argument("--codepage", type=Path, required=True)
    ap.add_argument("--fallback-glyphs", type=Path, required=True, help="V2 glyph JSON used only for non-letter punctuation visuals")
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    body = require_reference(args.reference_rom)
    font = body[FE4_FONT_BASE:FE4_FONT_BASE + FE4_FONT_SIZE]
    if len(font) != FE4_FONT_SIZE:
        raise RuntimeError("FE4 font slice truncated")

    rows = list(csv.DictReader(args.codepage.open("r", encoding="utf-8-sig", newline="")))
    fallback = json.loads(args.fallback_glyphs.read_text(encoding="utf-8"))

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
        if len(key) == 1 and (key.isalpha() or unicodedata.category(key).startswith('L')):
            bitmap = pack_hex(build_chibi_glyph(font, key))
        else:
            if key not in fallback:
                raise RuntimeError(f"non-letter fallback visual missing: {key!r}")
            bitmap = fallback[key]["bitmap_hex"]
        out[key] = {"bitmap_hex": bitmap, "glyph_id": f"{gid:04X}"}

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, separators=(",", ":")), encoding="utf-8")
    print(f"reference_sha1={FE4_REFERENCE_SHA1}")
    print(f"font_body_range=0x{FE4_FONT_BASE:06X}..0x{FE4_FONT_BASE + FE4_FONT_SIZE - 1:06X}")
    print(f"custom_visual_glyphs={len(out)}")
    print(f"output={args.output}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
