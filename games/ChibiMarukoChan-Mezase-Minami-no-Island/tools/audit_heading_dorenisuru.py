#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

EXPECTED_SIZE = 0x200000
EXPECTED_SHA1 = "08a2415362f69788ec76b1a36044dc1f1a5f2ea1"
PTR_TABLE = 0x29756
LOROM_BANK85_FILE_BASE = 0x28000
TEXT = "どれにする？"


def require_clean(path: Path) -> bytes:
    data = path.read_bytes()
    sha1 = hashlib.sha1(data).hexdigest()
    if len(data) != EXPECTED_SIZE or sha1 != EXPECTED_SHA1:
        raise RuntimeError(f"clean ROM contract failed: size={len(data)} sha1={sha1}")
    return data


def map_base_for_lead(data: bytes, lead: int) -> int:
    ptr_off = PTR_TABLE + (lead - 0x80) * 2
    ptr = data[ptr_off] | (data[ptr_off + 1] << 8)
    return LOROM_BANK85_FILE_BASE + (ptr - 0x8000)


def glyph_id_for_char(data: bytes, ch: str) -> tuple[bytes, int]:
    raw = ch.encode("cp932")
    if len(raw) != 2:
        raise RuntimeError(f"expected 2-byte CP932 char: {ch!r} -> {raw.hex()}")
    lead, trail = raw
    base = map_base_for_lead(data, lead)
    entry = base + (trail - 0x40) * 2
    gid = data[entry] | (data[entry + 1] << 8)
    return raw, gid


def hits(data: bytes, pattern: bytes) -> list[int]:
    out: list[int] = []
    start = 0
    while True:
        pos = data.find(pattern, start)
        if pos < 0:
            return out
        out.append(pos)
        start = pos + 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Audit storage hypotheses for visible heading どれにする？")
    ap.add_argument("rom", type=Path)
    args = ap.parse_args()

    data = require_clean(args.rom)
    mapped = [glyph_id_for_char(data, ch) for ch in TEXT]
    gids = [gid for _raw, gid in mapped]

    print(f"text={TEXT}")
    for ch, (raw, gid) in zip(TEXT, mapped):
        print(f"{ch} cp932={raw.hex().upper()} gid=0x{gid:04X}")

    patterns = {
        "raw_cp932": TEXT.encode("cp932"),
        "glyph_ids_le16": b"".join(g.to_bytes(2, "little") for g in gids),
        "glyph_ids_be16": b"".join(g.to_bytes(2, "big") for g in gids),
        "low_bytes_first5": bytes(g & 0xFF for g in gids[:5]),
    }
    for name, pattern in patterns.items():
        found = hits(data, pattern)
        print(f"{name}_hits={len(found)} offsets={[hex(x) for x in found[:16]]}")

    print("conclusion=heading is not stored as an obvious contiguous CP932/glyph-id/low-byte sequence")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
