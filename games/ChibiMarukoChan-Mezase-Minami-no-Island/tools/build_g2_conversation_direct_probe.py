#!/usr/bin/env python3
from __future__ import annotations

import argparse
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
    (
        0x181CE,
        "bba59fd14eb22e6b1c20b022cc8b5b1deefea805a662060ff4bb969e940f1d1a",
        ("Nói thẳng nhé!", "Du học chớ xấu hổ!", "Luyện phản xạ!"),
    ),
    (
        0x18247,
        "bf7f9ce44005a4dff7807a2028e96030f835dc19247400adfbf293600877c237",
        ("Nói thẳng nhé!", "Du học chớ xấu hổ!", "Tập khỏi rơi!"),
    ),
    (
        0x182C0,
        "ec02dcf7e69d501c99deba14b3e1a954bffb33c9955e2c1e95b4509a3874361f",
        ("Nói thẳng nhé!", "Du học chớ xấu hổ!", "Rèn gu mỹ thuật!"),
    ),
)

FIELD_BYTES = 106
LINE_BYTES = (32, 34, 34)
OPEN_QUOTE = bytes.fromhex("8175")
CLOSE_QUOTE = bytes.fromhex("8176")
LINE_BREAK = bytes.fromhex("816F")
FULLWIDTH_EXCL = bytes.fromhex("8149")


def encode_mixed(text: str, enc: dict[str, bytes]) -> bytes:
    out = bytearray()
    for ch in text:
        if ch == " ":
            out.append(0x20)
        elif ch == "!":
            out += FULLWIDTH_EXCL
        else:
            if ch not in enc:
                raise RuntimeError(f"unmapped runtime character: {ch!r}")
            out += enc[ch]
    return bytes(out)


def fixed_line(
    text: str,
    width: int,
    enc: dict[str, bytes],
    *,
    prefix: bytes = b"",
    suffix: bytes = b"",
) -> bytes:
    row = prefix + encode_mixed(text, enc) + suffix
    if len(row) > width:
        raise RuntimeError(
            f"line exceeds fixed byte width: {text!r} {len(row)} > {width}"
        )
    return row + (b" " * (width - len(row)))


def build_payload(lines: tuple[str, str, str], enc: dict[str, bytes]) -> bytes:
    a = fixed_line(lines[0], LINE_BYTES[0], enc, prefix=OPEN_QUOTE)
    b = fixed_line(lines[1], LINE_BYTES[1], enc)
    c = fixed_line(lines[2], LINE_BYTES[2], enc, suffix=CLOSE_QUOTE)
    payload = a + LINE_BREAK + b + LINE_BREAK + c + LINE_BREAK
    if len(payload) != FIELD_BYTES:
        raise RuntimeError(f"payload length mismatch: {len(payload)}")
    return payload


def required_chars() -> set[str]:
    return {
        ch
        for _off, _sha, lines in FIELDS
        for line in lines
        for ch in line
        if ch not in {" ", "!"}
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Build G2 school-front direct-text Vietnamese probe 002"
    )
    ap.add_argument("clean_rom", type=Path)
    ap.add_argument("output", type=Path)
    here = Path(__file__).resolve().parent
    ap.add_argument(
        "--codepage",
        type=Path,
        default=here.parent / "translation" / "codepage" / "vi_codepage_v4_fe4_native.csv",
    )
    ap.add_argument(
        "--glyphs",
        type=Path,
        default=here.parent / "translation" / "codepage" / "vi_glyphs_v5_fe4_thin.json",
    )
    args = ap.parse_args()

    data = require_clean_rom(args.clean_rom)
    original = bytes(data)
    enc, char_gid, visual_key, glyph_source = load_codepage(args.codepage)
    glyph_json = json.loads(args.glyphs.read_text(encoding="utf-8"))

    ptr_off = PTR_TABLE + (LEAD - 0x80) * 2
    lead_ptr = read_u16le(data, ptr_off)
    if lead_ptr != 0x9A74:
        raise RuntimeError(f"lead 0x84 pointer mismatch: 0x{lead_ptr:04X}")

    needed = required_chars()
    missing = sorted(needed - set(enc))
    if missing:
        raise RuntimeError(f"runtime text contains unmapped chars: {missing}")

    audit = bytes(data[MAPPING_AUDIT_START:MAPPING_AUDIT_END])
    custom_visual_to_gid: dict[str, int] = {}
    for ch in sorted(needed):
        if glyph_source[ch] != "custom":
            continue
        key = visual_key[ch]
        gid = char_gid[ch]
        if key not in glyph_json:
            raise RuntimeError(f"missing glyph JSON entry for {key!r}")
        prior = custom_visual_to_gid.setdefault(key, gid)
        if prior != gid:
            raise RuntimeError(f"visual alias {key!r} maps to multiple glyph IDs")

    for key, gid in custom_visual_to_gid.items():
        assert_blank_cell(data, gid)
        if audit.count(gid.to_bytes(2, "little")):
            raise RuntimeError(f"custom glyph slot 0x{gid:04X} is already referenced")

    payloads = []
    for off, expected_sha256, lines in FIELDS:
        source = bytes(data[off:off + FIELD_BYTES])
        if hashlib.sha256(source).hexdigest() != expected_sha256:
            raise RuntimeError(f"source identity mismatch at 0x{off:06X}")
        if data[off + FIELD_BYTES] != 0x00:
            raise RuntimeError(f"expected NUL terminator missing at 0x{off + FIELD_BYTES:06X}")
        payloads.append((off, build_payload(lines, enc), lines))

    allowed: set[int] = set()

    # Install only the codepage rows required by this probe.
    for ch in sorted(needed):
        code = enc[ch]
        if len(code) != 2 or code[0] != LEAD:
            raise RuntimeError(f"invalid 0x84 code for {ch!r}")
        entry_off = MAP_BASE + (code[1] - 0x40) * 2
        data[entry_off:entry_off + 2] = char_gid[ch].to_bytes(2, "little")
        allowed.update(range(entry_off, entry_off + 2))

    bitmap_touched: set[int] = set()
    for key, gid in custom_visual_to_gid.items():
        meta = glyph_json[key]
        if int(meta["glyph_id"], 16) != gid:
            raise RuntimeError(f"glyph JSON ID mismatch for {key!r}")
        bitmap_touched.update(
            write_bitmap(data, gid, unpack_bitmap_hex(meta["bitmap_hex"]))
        )
    allowed.update(bitmap_touched)

    for off, payload, _lines in payloads:
        data[off:off + FIELD_BYTES] = payload
        allowed.update(range(off, off + FIELD_BYTES))

    checksum, complement = write_snes_checksum(data)
    allowed.update(range(CHECKSUM_COMPLEMENT, CHECKSUM + 2))

    diffs = {i for i, (a, b) in enumerate(zip(original, data)) if a != b}
    unexpected = sorted(diffs - allowed)
    if unexpected:
        raise RuntimeError(
            "unexpected diff bytes: " + ", ".join(hex(x) for x in unexpected[:16])
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(data)

    print("clean_rom_contract=PASS")
    print("probe=G2_DIRECT_TEXT_PROBE_002")
    print(f"lead_pointer=0x{lead_ptr:04X}")
    print(f"required_chars={len(needed)}")
    print(f"custom_visual_glyphs={len(custom_visual_to_gid)}")
    print("field_layout=32/34/34 bytes x 3 records")
    for off, _payload, lines in payloads:
        print(f"field=0x{off:06X} lines={' | '.join(lines)}")
    print(f"bitmap_diff_bytes={len(bitmap_touched)}")
    print(f"total_diff_bytes={len(diffs)}")
    print(f"checksum=0x{checksum:04X}")
    print(f"complement=0x{complement:04X}")
    print(f"sha1={hashlib.sha1(data).hexdigest()}")
    print(f"sha256={hashlib.sha256(data).hexdigest()}")
    print(f"output={args.output}")
    print("D038=ORIGINAL")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
