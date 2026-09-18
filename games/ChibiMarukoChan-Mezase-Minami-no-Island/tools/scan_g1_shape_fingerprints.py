#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
from dataclasses import dataclass
from pathlib import Path

EXPECTED_SIZE = 0x200000
EXPECTED_SHA1 = "08a2415362f69788ec76b1a36044dc1f1a5f2ea1"
PTR_TABLE = 0x29756
BANK85_FILE_BASE = 0x28000
FONT_PAGE_TABLE = 0x295EE
FONT_WIDTH = 128
GLYPH_SIZE = 12
PIXELS_PER_GLYPH = GLYPH_SIZE * GLYPH_SIZE

TARGETS = {
    "heading": "どれにする？",
    "start": "はじめから",
    "password": "パスワード",
}


@dataclass(frozen=True)
class GlyphShape:
    ch: str
    gid: int
    rows: tuple[int, ...]
    bits144: int
    ink: int


@dataclass(frozen=True)
class Hit:
    mode: str
    off: int
    ch: str
    score: float


def require_clean(path: Path) -> bytes:
    data = path.read_bytes()
    sha1 = hashlib.sha1(data).hexdigest()
    if len(data) != EXPECTED_SIZE or sha1 != EXPECTED_SHA1:
        raise RuntimeError(f"clean ROM contract failed: size={len(data)} sha1={sha1}")
    return data


def lorom_cpu_to_file(cpu: int) -> int:
    bank = (cpu >> 16) & 0xFF
    addr = cpu & 0xFFFF
    if addr < 0x8000:
        raise ValueError(f"not a LoROM ROM address: ${cpu:06X}")
    off = (bank & 0x7F) * 0x8000 + (addr - 0x8000)
    if not 0 <= off < EXPECTED_SIZE:
        raise ValueError(f"mapped file offset outside ROM: 0x{off:X}")
    return off


def map_base_for_lead(data: bytes, lead: int) -> int:
    ptr_off = PTR_TABLE + (lead - 0x80) * 2
    ptr = int.from_bytes(data[ptr_off:ptr_off + 2], "little")
    return BANK85_FILE_BASE + (ptr - 0x8000)


def glyph_id(data: bytes, ch: str) -> int:
    raw = ch.encode("cp932")
    if len(raw) != 2:
        raise ValueError(f"expected 2-byte CP932 char: {ch!r} -> {raw.hex()}")
    lead, trail = raw
    base = map_base_for_lead(data, lead)
    entry = base + (trail - 0x40) * 2
    return int.from_bytes(data[entry:entry + 2], "little")


def font_page_file(data: bytes, page: int) -> int:
    if not 0 <= page < 10:
        raise ValueError(f"unexpected font page: {page}")
    p = FONT_PAGE_TABLE + page * 3
    cpu = data[p] | (data[p + 1] << 8) | (data[p + 2] << 16)
    return lorom_cpu_to_file(cpu)


def read_bit_1bpp_page(data: bytes, page_off: int, x: int, y: int) -> int:
    byte_off = page_off + y * (FONT_WIDTH // 8) + (x // 8)
    bit = 7 - (x & 7)
    return (data[byte_off] >> bit) & 1


def rows_to_bits144(rows: tuple[int, ...]) -> int:
    bits = 0
    for row in rows:
        bits = (bits << GLYPH_SIZE) | (row & 0xFFF)
    return bits


def extract_glyph(data: bytes, ch: str) -> GlyphShape:
    gid = glyph_id(data, ch)
    page = (gid >> 8) & 0xFF
    idx = gid & 0xFF
    if idx >= 100:
        raise ValueError(f"glyph index outside 10x10 page: {ch!r} gid=0x{gid:04X}")
    col = idx % 10
    row = idx // 10
    x0 = col * GLYPH_SIZE
    y0 = row * GLYPH_SIZE
    page_off = font_page_file(data, page)
    rows: list[int] = []
    for y in range(GLYPH_SIZE):
        bits = 0
        for x in range(GLYPH_SIZE):
            bits = (bits << 1) | read_bit_1bpp_page(data, page_off, x0 + x, y0 + y)
        rows.append(bits)
    row_tuple = tuple(rows)
    packed = rows_to_bits144(row_tuple)
    return GlyphShape(ch, gid, row_tuple, packed, packed.bit_count())


def similarity(bits_a: int, bits_b: int) -> float:
    return 1.0 - ((bits_a ^ bits_b).bit_count() / PIXELS_PER_GLYPH)


def packed_1bpp_bits144(data: bytes, off: int, *, lsb_left: bool = False) -> int | None:
    if off < 0 or off + 24 > len(data):
        return None
    out = 0
    for y in range(12):
        b0 = data[off + y * 2]
        b1 = data[off + y * 2 + 1]
        row = 0
        for x in range(12):
            src = b0 if x < 8 else b1
            pos = x if lsb_left else 7 - (x & 7)
            if lsb_left and x >= 8:
                pos = x - 8
            row = (row << 1) | ((src >> pos) & 1)
        out = (out << 12) | row
    return out


def decode_snes_tile_mask(data: bytes, off: int, bpp: int) -> tuple[int, ...] | None:
    if bpp not in (2, 4):
        raise ValueError(bpp)
    tile_bytes = 16 if bpp == 2 else 32
    if off < 0 or off + tile_bytes > len(data):
        return None
    rows = []
    for y in range(8):
        p0 = data[off + y * 2]
        p1 = data[off + y * 2 + 1]
        p2 = data[off + 16 + y * 2] if bpp == 4 else 0
        p3 = data[off + 16 + y * 2 + 1] if bpp == 4 else 0
        bits = 0
        for x in range(8):
            shift = 7 - x
            pix = (
                ((p0 >> shift) & 1)
                | (((p1 >> shift) & 1) << 1)
                | (((p2 >> shift) & 1) << 2)
                | (((p3 >> shift) & 1) << 3)
            )
            bits = (bits << 1) | (1 if pix else 0)
        rows.append(bits)
    return tuple(rows)


def compose_2x2_bits144(tiles: list[tuple[int, ...]]) -> int:
    tl, tr, bl, br = tiles
    rows = []
    for y in range(12):
        if y < 8:
            left, right = tl[y], tr[y]
        else:
            left, right = bl[y - 8], br[y - 8]
        full16 = (left << 8) | right
        rows.append((full16 >> 4) & 0xFFF)
    return rows_to_bits144(tuple(rows))


def unique_target_chars() -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for text in TARGETS.values():
        for ch in text:
            if ch not in seen:
                seen.add(ch)
                out.append(ch)
    return out


def maybe_add_hits(hits: list[Hit], mode: str, off: int, bits: int, shapes: list[GlyphShape], max_diff: int) -> None:
    ink = bits.bit_count()
    # A cheap density gate eliminates most random/blank data before XOR scoring.
    for shape in shapes:
        if abs(ink - shape.ink) > max_diff:
            continue
        diff = (bits ^ shape.bits144).bit_count()
        if diff <= max_diff:
            hits.append(Hit(mode, off, shape.ch, 1.0 - diff / PIXELS_PER_GLYPH))


def scan_packed_1bpp(data: bytes, shapes: list[GlyphShape], max_diff: int) -> list[Hit]:
    hits: list[Hit] = []
    for off in range(0, len(data) - 24 + 1, 2):
        msb = packed_1bpp_bits144(data, off, lsb_left=False)
        lsb = packed_1bpp_bits144(data, off, lsb_left=True)
        assert msb is not None and lsb is not None
        maybe_add_hits(hits, "1bpp12_msb", off, msb, shapes, max_diff)
        maybe_add_hits(hits, "1bpp12_lsb", off, lsb, shapes, max_diff)
    return hits


def scan_snes_blocks(data: bytes, shapes: list[GlyphShape], bpp: int, max_diff: int) -> list[Hit]:
    hits: list[Hit] = []
    tile_bytes = 16 if bpp == 2 else 32
    block_bytes = tile_bytes * 4
    for off in range(0, len(data) - block_bytes + 1, tile_bytes):
        tiles = [decode_snes_tile_mask(data, off + i * tile_bytes, bpp) for i in range(4)]
        if any(t is None for t in tiles):
            continue
        bits = compose_2x2_bits144(tiles)  # type: ignore[arg-type]
        maybe_add_hits(hits, f"snes{bpp}bpp_2x2_seq", off, bits, shapes, max_diff)
    return hits


def cluster_hits(hits: list[Hit], max_span: int) -> list[list[Hit]]:
    if not hits:
        return []
    ordered = sorted(hits, key=lambda h: h.off)
    clusters: list[list[Hit]] = []
    cur = [ordered[0]]
    for h in ordered[1:]:
        if h.off - cur[-1].off <= max_span:
            cur.append(h)
        else:
            clusters.append(cur)
            cur = [h]
    clusters.append(cur)
    return clusters


def target_coverage(chars: set[str]) -> str:
    parts = []
    for name, text in TARGETS.items():
        unique = set(text)
        covered = len(unique & chars)
        parts.append(f"{name}:{covered}/{len(unique)}")
    return ",".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(description="READ-ONLY G1 bitmap-shape fingerprint scanner")
    ap.add_argument("rom", type=Path)
    ap.add_argument("--max-diff", type=int, default=14, help="max differing pixels out of 144 (default 14 ~= 90.3%% similarity)")
    ap.add_argument("--cluster-span", type=lambda s: int(s, 0), default=0x800)
    ap.add_argument("--top", type=int, default=240)
    args = ap.parse_args()

    if not 0 <= args.max_diff <= 72:
        raise SystemExit("--max-diff must be in 0..72")

    data = require_clean(args.rom)
    chars = unique_target_chars()
    shapes = [extract_glyph(data, ch) for ch in chars]

    print("CHIBI MARUKO G1 SHAPE FINGERPRINT SCAN")
    print("mode=READ_ONLY")
    print("clean_rom_contract=PASS")
    print("runtime_claim=NO")
    print("targets=" + " | ".join(f"{k}:{v}" for k, v in TARGETS.items()))
    print(f"unique_glyphs={len(shapes)} max_diff={args.max_diff} min_similarity={1-args.max_diff/144:.4f}")
    for g in shapes:
        print(f"glyph={g.ch} gid=0x{g.gid:04X} ink={g.ink}")

    hits: list[Hit] = []
    hits.extend(scan_packed_1bpp(data, shapes, args.max_diff))
    hits.extend(scan_snes_blocks(data, shapes, 2, args.max_diff))
    hits.extend(scan_snes_blocks(data, shapes, 4, args.max_diff))

    print(f"raw_hits={len(hits)}")
    for h in sorted(hits, key=lambda x: (-x.score, x.off, x.mode, x.ch))[:args.top]:
        print(f"hit mode={h.mode:20s} off=0x{h.off:06X} ch={h.ch} score={h.score:.4f}")

    clusters = cluster_hits(hits, args.cluster_span)
    ranked = sorted(
        clusters,
        key=lambda c: (-len({h.ch for h in c}), -max(h.score for h in c), c[0].off),
    )
    print(f"clusters={len(clusters)} cluster_span=0x{args.cluster_span:X}")
    for members in ranked[:100]:
        chars_here = {h.ch for h in members}
        chars_s = "".join(ch for ch in chars if ch in chars_here)
        modes = sorted({h.mode for h in members})
        best = max(h.score for h in members)
        print(
            f"cluster 0x{members[0].off:06X}..0x{members[-1].off:06X} "
            f"unique_chars={len(chars_here)} chars={chars_s} hits={len(members)} best={best:.4f} "
            f"coverage={target_coverage(chars_here)} modes={','.join(modes)}"
        )

    print("interpretation=multi-glyph clusters are asset candidates only, not patch offsets")
    print("proof_gate=correlate candidate cluster with trace_g1_render_path screen-setup/DMA/pointer evidence")
    print("do_not_patch=0x286B4..0x287FC descriptor/debug prose")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
