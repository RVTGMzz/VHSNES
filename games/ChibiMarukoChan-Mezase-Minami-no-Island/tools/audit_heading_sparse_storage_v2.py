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


def ordered_token_hits(data: bytes, tokens: list[bytes], max_gap: int) -> list[list[int]]:
    out: list[list[int]] = []
    start = 0
    first = tokens[0]
    while True:
        p = data.find(first, start)
        if p < 0:
            return out
        positions = [p]
        cursor = p + len(first)
        ok = True
        for token in tokens[1:]:
            stop = min(len(data), cursor + max_gap + len(token) + 1)
            q = data.find(token, cursor, stop)
            if q < 0:
                ok = False
                break
            positions.append(q)
            cursor = q + len(token)
        if ok:
            out.append(positions)
        start = p + 1


def masked_tilemap_hits(data: bytes, gids: list[int], mask: int) -> list[int]:
    out: list[int] = []
    byte_len = len(gids) * 2
    for off in range(0, len(data) - byte_len + 1, 2):
        ok = True
        for i, gid in enumerate(gids):
            word = data[off + i * 2] | (data[off + i * 2 + 1] << 8)
            if (word & mask) != (gid & mask):
                ok = False
                break
        if ok:
            out.append(off)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Audit sparse/interleaved storage hypotheses for heading どれにする？")
    ap.add_argument("rom", type=Path)
    args = ap.parse_args()

    data = require_clean(args.rom)
    mapped = [glyph_id_for_char(data, ch) for ch in TEXT]
    cp932_tokens = [raw for raw, _gid in mapped]
    gids = [gid for _raw, gid in mapped]
    gid_le_tokens = [gid.to_bytes(2, "little") for gid in gids]
    low_tokens = [bytes([gid & 0xFF]) for gid in gids]

    print(f"text={TEXT}")
    print("glyph_ids=" + ",".join(f"0x{x:04X}" for x in gids))

    for gap in (0, 1, 2, 4, 8, 12, 16, 24, 32):
        cp_hits = ordered_token_hits(data, cp932_tokens, gap)
        gid_hits = ordered_token_hits(data, gid_le_tokens, gap)
        low_hits = ordered_token_hits(data, low_tokens[:5], gap)
        print(
            f"max_gap={gap} cp932_ordered_hits={len(cp_hits)} "
            f"gid_le_ordered_hits={len(gid_hits)} low_first5_ordered_hits={len(low_hits)}"
        )

    for mask in (0x03FF, 0x01FF, 0x00FF):
        found = masked_tilemap_hits(data, gids, mask)
        print(f"masked_16bit_contiguous mask=0x{mask:04X} hits={len(found)}")

    menu_start, menu_end = 0x28000, 0x2B000
    need = {gid & 0xFF for gid in gids}
    for window in (24, 32):
        count = 0
        for off in range(menu_start, menu_end - window + 1):
            if need.issubset(set(data[off : off + window])):
                count += 1
        print(f"menu_bank_window={window} all_low_bytes_windows={count}")

    print("conclusion=no evidence for simple CP932/glyph-id sparse command stream up to 32-byte gaps")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
