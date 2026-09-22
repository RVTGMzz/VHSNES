#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

EXPECTED_BASE_SHA1 = "d0f7969aea3cad0a167dca3889ee9960be6415e0"
EXPECTED_GLYPH_JSON_SHA256 = "5586abea7c33cdc15510a4ac2cf75dbf814c1973e23ddb004b6962b6ff8e57e8"
EXPECTED_SIZE = 0x200000

FONT_PAGE_BASES = [0x128000 + i * 0x800 for i in range(10)]
CELL_W = CELL_H = 12
PAGE_STRIDE = 16
MAP_BASE = 0x29A74
MAPPING_AUDIT_START = 0x29756
MAPPING_AUDIT_END = 0x2B380
CHECKSUM_COMPLEMENT = 0x7FDC
CHECKSUM = 0x7FDE

CODE_TRAILS = {
    "!":0x41,"D":0x5C,"L":0x64,"N":0x66,"R":0x6A,"T":0x6C,
    "c":0x75,"g":0x79,"h":0x7A,"i":0x7B,"k":0x7D,"m":0x80,"n":0x81,
    "p":0x83,"r":0x85,"t":0x87,"u":0x88,"x":0x8B,"y":0x8C,
    "è":0x97,"é":0x98,"ó":0x9E,"ơ":0xAB,"ạ":0xAE,"ả":0xB0,"ậ":0xB8,
    "ẳ":0xBA,"ệ":0xC3,"ọ":0xC6,"ỏ":0xC7,"ớ":0xD0,"ỹ":0xE0,
}

NEW_SLOTS = {0x0960, 0x0961, 0x0962, 0x085F, 0x0860}


def sha1(data: bytes | bytearray) -> str:
    return hashlib.sha1(data).hexdigest()


def cell_bit_locations(gid: int):
    page = gid >> 8
    idx = gid & 0xFF
    if not (0 <= page < 10 and 0 <= idx < 100):
        raise RuntimeError(f"invalid glyph id 0x{gid:04X}")
    x0 = (idx % 10) * CELL_W
    y0 = (idx // 10) * CELL_H
    base = FONT_PAGE_BASES[page]
    for y in range(CELL_H):
        for x in range(CELL_W):
            px = x0 + x
            py = y0 + y
            off = base + py * PAGE_STRIDE + px // 8
            mask = 1 << (7 - (px % 8))
            yield y, x, off, mask


def unpack_bitmap_hex(bitmap_hex: str) -> list[int]:
    raw = bytes.fromhex(bitmap_hex)
    if len(raw) != 18:
        raise RuntimeError("12x12 bitmap must be 18 bytes / 144 bits")
    bits = []
    for b in raw:
        bits.extend((b >> shift) & 1 for shift in range(7, -1, -1))
    return bits


def calc_checksum(data: bytes | bytearray) -> int:
    tmp = bytearray(data)
    tmp[CHECKSUM_COMPLEMENT:CHECKSUM + 2] = b"\x00\x00\x00\x00"
    return (sum(tmp) + 0x1FE) & 0xFFFF


def main() -> int:
    ap = argparse.ArgumentParser(description="Build G2 Probe 005 clean dialogue font on Probe 003 text path")
    ap.add_argument("probe003_rom", type=Path)
    ap.add_argument("output", type=Path)
    here = Path(__file__).resolve().parent
    ap.add_argument("--glyphs", type=Path, default=here.parent / "translation" / "codepage" / "g2_probe005_dialogue_glyphs.json")
    args = ap.parse_args()

    original = args.probe003_rom.read_bytes()
    if len(original) != EXPECTED_SIZE or sha1(original) != EXPECTED_BASE_SHA1:
        raise SystemExit(f"Probe003 base contract failed: size={len(original)} sha1={sha1(original)}")

    glyph_bytes = args.glyphs.read_bytes()
    glyph_sha = hashlib.sha256(glyph_bytes).hexdigest()
    if glyph_sha != EXPECTED_GLYPH_JSON_SHA256:
        raise SystemExit(f"glyph JSON identity mismatch: {glyph_sha}")

    glyphs = json.loads(glyph_bytes.decode("utf-8"))
    if set(glyphs) != set(CODE_TRAILS):
        raise SystemExit("glyph set does not match Probe005 code-map set")

    data = bytearray(original)
    audit = bytes(data[MAPPING_AUDIT_START:MAPPING_AUDIT_END])

    for gid in sorted(NEW_SLOTS):
        ink = sum(1 for _y, _x, off, mask in cell_bit_locations(gid) if data[off] & mask)
        refs = audit.count(gid.to_bytes(2, "little"))
        if ink or refs:
            raise SystemExit(f"new slot 0x{gid:04X} is not clean: ink={ink} refs={refs}")

    mapping_touched: set[int] = set()
    font_touched: set[int] = set()

    for ch, meta in glyphs.items():
        gid = int(meta["glyph_id"], 16)
        trail = CODE_TRAILS[ch]
        entry = MAP_BASE + (trail - 0x40) * 2
        before = bytes(data[entry:entry + 2])
        data[entry:entry + 2] = gid.to_bytes(2, "little")
        if bytes(data[entry:entry + 2]) != before:
            mapping_touched.update(range(entry, entry + 2))

        bits = unpack_bitmap_hex(meta["bitmap_hex"])
        i = 0
        for _y, _x, off, mask in cell_bit_locations(gid):
            before_b = data[off]
            if bits[i]:
                data[off] |= mask
            else:
                data[off] &= (~mask) & 0xFF
            if data[off] != before_b:
                font_touched.add(off)
            i += 1

    checksum = calc_checksum(data)
    complement = checksum ^ 0xFFFF
    data[CHECKSUM_COMPLEMENT:CHECKSUM_COMPLEMENT + 2] = complement.to_bytes(2, "little")
    data[CHECKSUM:CHECKSUM + 2] = checksum.to_bytes(2, "little")

    diffs = {i for i, (a, b) in enumerate(zip(original, data)) if a != b}
    allowed = set(mapping_touched) | set(font_touched) | set(range(CHECKSUM_COMPLEMENT, CHECKSUM + 2))
    unexpected = sorted(diffs - allowed)
    if unexpected:
        raise SystemExit("unexpected diff bytes: " + ", ".join(hex(x) for x in unexpected[:16]))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(data)

    print("base_probe003_contract=PASS")
    print("probe=G2_DIRECT_TEXT_PROBE_005_CLEAN_DIALOGUE_FONT")
    print(f"glyphs={len(glyphs)}")
    print(f"font_diff_bytes={len(font_touched)}")
    print(f"mapping_diff_bytes={len(mapping_touched)}")
    print(f"total_diff_vs_probe003={len(diffs)}")
    print(f"checksum=0x{checksum:04X}")
    print(f"complement=0x{complement:04X}")
    print(f"sha1={sha1(data)}")
    print(f"sha256={hashlib.sha256(data).hexdigest()}")
    print("text_payload=UNCHANGED_FROM_PROBE003")
    print("scene_logic=UNCHANGED_FROM_PROBE003")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
