#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from probe_visible_menu_011_fe4_thin import (
    CHECKSUM,
    CHECKSUM_COMPLEMENT,
    LEAD,
    MAP_BASE,
    MAPPING_AUDIT_END,
    MAPPING_AUDIT_START,
    PTR_TABLE,
    assert_blank_cell,
    load_codepage,
    read_u16le,
    require_clean_rom,
    unpack_bitmap_hex,
    write_bitmap,
    write_snes_checksum,
)

FIELDS = (
    (0x181CE, ("Nói thẳng nhé!", "Du học chớ ngại!", "Luyện phản xạ!")),
    (0x18247, ("Nói thẳng nhé!", "Du học chớ ngại!", "Tập khỏi rơi!")),
    (0x182C0, ("Nói thẳng nhé!", "Du học chớ ngại!", "Rèn gu mỹ thuật!")),
)

FIELD_BYTES = 106
LINE_BYTES = (32, 34, 34)
OPEN_QUOTE = bytes.fromhex("8175")
CLOSE_QUOTE = bytes.fromhex("8176")
LINE_BREAK = bytes.fromhex("816F")


def encode_all_2byte(text: str, enc: dict[str, bytes]) -> bytes:
    missing = [ch for ch in text if ch not in enc]
    if missing:
        raise RuntimeError(f"unmapped chars: {missing}")
    out = b"".join(enc[ch] for ch in text)
    if len(out) != len(text) * 2:
        raise RuntimeError("text is not fully encoded as 2-byte units")
    return out


def fixed_line(
    text: str,
    width: int,
    enc: dict[str, bytes],
    *,
    prefix: bytes = b"",
    suffix: bytes = b"",
) -> bytes:
    raw = prefix + encode_all_2byte(text, enc) + suffix
    if len(raw) > width or (width - len(raw)) % 2:
        raise RuntimeError(f"line fit failed: {text!r} {len(raw)}/{width}")
    raw += enc[" "] * ((width - len(raw)) // 2)
    if len(raw) != width:
        raise RuntimeError("fixed line width mismatch")
    return raw


def build_payload(lines: tuple[str, str, str], enc: dict[str, bytes]) -> bytes:
    rows = (
        fixed_line(lines[0], LINE_BYTES[0], enc, prefix=OPEN_QUOTE),
        fixed_line(lines[1], LINE_BYTES[1], enc),
        fixed_line(lines[2], LINE_BYTES[2], enc, suffix=CLOSE_QUOTE),
    )
    payload = rows[0] + LINE_BREAK + rows[1] + LINE_BREAK + rows[2] + LINE_BREAK
    if len(payload) != FIELD_BYTES:
        raise RuntimeError(f"payload length mismatch: {len(payload)}")
    if [i for i in range(len(payload)-1) if payload[i:i+2] == LINE_BREAK] != [32, 68, 104]:
        raise RuntimeError("line-break offsets changed")
    return payload


def main() -> int:
    ap = argparse.ArgumentParser(description="Build G2 direct-text Probe 003 with strict 2-byte Vietnamese units")
    ap.add_argument("clean_rom", type=Path)
    ap.add_argument("output", type=Path)
    here = Path(__file__).resolve().parent
    ap.add_argument("--codepage", type=Path, default=here.parent / "translation" / "codepage" / "vi_codepage_v4_fe4_native.csv")
    ap.add_argument("--glyphs", type=Path, default=here.parent / "translation" / "codepage" / "vi_glyphs_v5_fe4_thin.json")
    args = ap.parse_args()

    data = require_clean_rom(args.clean_rom)
    original = bytes(data)
    enc, char_gid, visual_key, glyph_source = load_codepage(args.codepage)
    glyph_json = json.loads(args.glyphs.read_text(encoding="utf-8"))

    lead_ptr = read_u16le(data, PTR_TABLE + (LEAD - 0x80) * 2)
    if lead_ptr != 0x9A74:
        raise RuntimeError(f"lead pointer mismatch: 0x{lead_ptr:04X}")

    needed = set("".join("".join(lines) for _off, lines in FIELDS))
    if " " not in needed or "!" not in needed:
        raise RuntimeError("probe must exercise 2-byte space and exclamation mappings")

    audit = bytes(data[MAPPING_AUDIT_START:MAPPING_AUDIT_END])
    custom_visual_to_gid: dict[str, int] = {}
    for ch in sorted(needed):
        if ch not in enc:
            raise RuntimeError(f"missing codepage char: {ch!r}")
        if glyph_source[ch] != "custom":
            continue
        key = visual_key[ch]
        gid = char_gid[ch]
        if key not in glyph_json:
            raise RuntimeError(f"missing glyph JSON: {key!r}")
        prior = custom_visual_to_gid.setdefault(key, gid)
        if prior != gid:
            raise RuntimeError(f"visual alias conflict: {key!r}")

    for key, gid in custom_visual_to_gid.items():
        assert_blank_cell(data, gid)
        if audit.count(gid.to_bytes(2, "little")):
            raise RuntimeError(f"custom glyph already referenced: 0x{gid:04X}")

    for ch in sorted(needed):
        code = enc[ch]
        if len(code) != 2 or code[0] != LEAD:
            raise RuntimeError(f"bad Vietnamese code unit for {ch!r}: {code.hex()}")
        entry_off = MAP_BASE + (code[1] - 0x40) * 2
        data[entry_off:entry_off + 2] = char_gid[ch].to_bytes(2, "little")

    for key, gid in custom_visual_to_gid.items():
        meta = glyph_json[key]
        if int(meta["glyph_id"], 16) != gid:
            raise RuntimeError(f"glyph id mismatch: {key!r}")
        write_bitmap(data, gid, unpack_bitmap_hex(meta["bitmap_hex"]))

    for off, lines in FIELDS:
        source = bytes(original[off:off + FIELD_BYTES])
        if source[32:34] != LINE_BREAK or source[68:70] != LINE_BREAK or source[104:106] != LINE_BREAK:
            raise RuntimeError(f"source separator mismatch at 0x{off:06X}")
        if original[off + FIELD_BYTES] != 0x00:
            raise RuntimeError(f"NUL terminator mismatch at 0x{off + FIELD_BYTES:06X}")
        data[off:off + FIELD_BYTES] = build_payload(lines, enc)

    checksum, complement = write_snes_checksum(data)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(data)

    print("clean_rom_contract=PASS")
    print("probe=G2_DIRECT_TEXT_PROBE_003_STRICT_2BYTE")
    print("D038=ORIGINAL")
    print("line_break_offsets=32,68,104 PASS")
    print("all_vi_printable_units=0x84xx PASS")
    print(f"checksum=0x{checksum:04X}")
    print(f"complement=0x{complement:04X}")
    print(f"sha1={hashlib.sha1(data).hexdigest()}")
    print(f"sha256={hashlib.sha256(data).hexdigest()}")
    print(f"diff_bytes={sum(a != b for a, b in zip(original, data))}")
    print(f"output={args.output}")
    print("runtime_claim=NO")


if __name__ == "__main__":
    raise SystemExit(main())
