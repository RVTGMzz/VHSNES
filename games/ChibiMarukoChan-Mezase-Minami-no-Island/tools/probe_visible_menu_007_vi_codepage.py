#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

EXPECTED_SIZE = 0x200000
EXPECTED_SHA1 = "08a2415362f69788ec76b1a36044dc1f1a5f2ea1"
EXPECTED_SHA256 = "e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
LOROM_HEADER = 0x7FC0
CHECKSUM_COMPLEMENT = LOROM_HEADER + 0x1C
CHECKSUM = LOROM_HEADER + 0x1E
EXPECTED_TITLE = b"RS051 CHIBIMARUKOCHAN"
EXPECTED_MAP_MODE = 0x30

# Dedicated Vietnamese codepage: valid Shift-JIS lead 0x84, unused by the
# currently extracted direct-text corpus. The visible renderer's lead pointer
# for 0x84 resolves to CPU $85:9A74 -> file 0x29A74.
LEAD = 0x84
PTR_TABLE = 0x29756
EXPECTED_LEAD_PTR = 0x9A74
MAP_BASE = 0x29A74
MAPPING_AUDIT_START = 0x29796
MAPPING_AUDIT_END = 0x2B380

FONT_PAGE_BASES = [0x128000 + i * 0x800 for i in range(10)]
CELL_W = 12
CELL_H = 12
PAGE_STRIDE_BYTES = 16

MENU_FIELDS = (
    (0x28818, "ストーリーモード", "ĐẦY ĐỦ!!"),
    (0x2882E, "対戦モード", "được!"),
    (0x2883C, "チーム対戦モード", "CÓ DẤU!!"),
    (0x28852, "まるこＱ", "Việt"),
    (0x2885E, "まるこペイント", "Maruko?"),
    (0x28870, "まるこみくじ", "Ổn rồi"),
)


def digest(data: bytes | bytearray) -> tuple[str, str]:
    return hashlib.sha1(data).hexdigest(), hashlib.sha256(data).hexdigest()


def require_clean_rom(path: Path) -> bytearray:
    data = path.read_bytes()
    sha1, sha256 = digest(data)
    problems: list[str] = []
    if len(data) != EXPECTED_SIZE:
        problems.append(f"size {len(data)} != expected {EXPECTED_SIZE}")
    if sha1 != EXPECTED_SHA1:
        problems.append(f"SHA1 {sha1} != expected {EXPECTED_SHA1}")
    if sha256 != EXPECTED_SHA256:
        problems.append(f"SHA256 {sha256} != expected {EXPECTED_SHA256}")
    if data[LOROM_HEADER:LOROM_HEADER + 21] != EXPECTED_TITLE:
        problems.append("internal title mismatch")
    if data[LOROM_HEADER + 0x15] != EXPECTED_MAP_MODE:
        problems.append("map mode mismatch")
    if problems:
        raise RuntimeError("CLEAN ROM contract failed:\n- " + "\n- ".join(problems))
    return bytearray(data)


def read_u16le(data: bytes | bytearray, off: int) -> int:
    return data[off] | (data[off + 1] << 8)


def calc_snes_checksum(data: bytes | bytearray) -> int:
    if len(data) != EXPECTED_SIZE:
        raise RuntimeError("checksum helper scoped to exact 2 MiB ROM")
    tmp = bytearray(data)
    tmp[CHECKSUM_COMPLEMENT:CHECKSUM + 2] = b"\x00\x00\x00\x00"
    return (sum(tmp) + 0x1FE) & 0xFFFF


def write_snes_checksum(data: bytearray) -> tuple[int, int]:
    checksum = calc_snes_checksum(data)
    complement = checksum ^ 0xFFFF
    data[CHECKSUM_COMPLEMENT:CHECKSUM_COMPLEMENT + 2] = complement.to_bytes(2, "little")
    data[CHECKSUM:CHECKSUM + 2] = checksum.to_bytes(2, "little")
    return checksum, complement


def cell_xy(index: int) -> tuple[int, int]:
    if not 0 <= index < 100:
        raise RuntimeError(f"glyph cell index out of range: {index}")
    return (index % 10) * CELL_W, (index // 10) * CELL_H


def cell_bit_locations(gid: int):
    page = gid >> 8
    index = gid & 0xFF
    if not 0 <= page < 10:
        raise RuntimeError(f"glyph page out of range for 0x{gid:04X}")
    x0, y0 = cell_xy(index)
    base = FONT_PAGE_BASES[page]
    for y in range(CELL_H):
        for x in range(CELL_W):
            px = x0 + x
            py = y0 + y
            off = base + py * PAGE_STRIDE_BYTES + px // 8
            mask = 1 << (7 - (px % 8))
            yield y, x, off, mask


def assert_blank_cell(data: bytes | bytearray, gid: int) -> None:
    ink = sum(1 for _y, _x, off, mask in cell_bit_locations(gid) if data[off] & mask)
    if ink:
        raise RuntimeError(f"custom glyph slot 0x{gid:04X} is not blank: {ink} lit pixels")


def unpack_bitmap_hex(bitmap_hex: str) -> list[str]:
    raw = bytes.fromhex(bitmap_hex)
    if len(raw) != 18:
        raise RuntimeError(f"packed glyph bitmap must be 18 bytes / 144 bits, got {len(raw)}")
    bits: list[int] = []
    for b in raw:
        bits.extend((b >> shift) & 1 for shift in range(7, -1, -1))
    rows = []
    for y in range(12):
        rows.append("".join("#" if bits[y * 12 + x] else "." for x in range(12)))
    return rows


def write_bitmap(data: bytearray, gid: int, rows: list[str]) -> set[int]:
    if len(rows) != 12 or any(len(row) != 12 for row in rows):
        raise RuntimeError(f"glyph 0x{gid:04X} bitmap must be exactly 12x12")
    touched: set[int] = set()
    locs = {(y, x): (off, mask) for y, x, off, mask in cell_bit_locations(gid)}
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch not in ".#":
                raise RuntimeError("glyph bitmap accepts only '.' and '#'")
            off, mask = locs[(y, x)]
            before = data[off]
            if ch == "#":
                data[off] |= mask
            else:
                data[off] &= (~mask) & 0xFF
            if data[off] != before:
                touched.add(off)
    return touched


def load_codepage(path: Path) -> tuple[dict[str, bytes], dict[str, int], dict[str, str]]:
    enc: dict[str, bytes] = {}
    gid: dict[str, int] = {}
    visual: dict[str, str] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            ch = row["unicode"]
            code = bytes.fromhex(row["code_hex"])
            if len(ch) != 1 or len(code) != 2 or code[0] != LEAD:
                raise RuntimeError(f"invalid codepage row: {row}")
            if ch in enc:
                raise RuntimeError(f"duplicate Unicode char: {ch!r}")
            enc[ch] = code
            gid[ch] = int(row["glyph_id_hex"], 16)
            visual[ch] = row["visual_key"]
    return enc, gid, visual


def encode_text(text: str, enc: dict[str, bytes]) -> bytes:
    missing = sorted(set(text) - set(enc))
    if missing:
        raise RuntimeError(f"text contains unmapped characters: {missing}")
    return b"".join(enc[ch] for ch in text)


def main() -> int:
    ap = argparse.ArgumentParser(description="Probe 007: corpus-derived Vietnamese 2-byte codepage + 12x12 glyph bank")
    ap.add_argument("rom", type=Path)
    ap.add_argument("output", type=Path)
    here = Path(__file__).resolve().parent
    ap.add_argument("--codepage", type=Path, default=here.parent / "translation" / "codepage" / "vi_codepage_v1.csv")
    ap.add_argument("--glyphs", type=Path, default=here.parent / "translation" / "codepage" / "vi_glyphs_v1.json")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data = require_clean_rom(args.rom)
    original = bytes(data)
    enc, char_gid, visual_key = load_codepage(args.codepage)
    glyph_json = json.loads(args.glyphs.read_text(encoding="utf-8"))

    ptr_off = PTR_TABLE + (LEAD - 0x80) * 2
    lead_ptr = read_u16le(data, ptr_off)
    if lead_ptr != EXPECTED_LEAD_PTR:
        raise RuntimeError(f"lead 0x84 pointer mismatch: 0x{lead_ptr:04X} != 0x{EXPECTED_LEAD_PTR:04X}")

    custom_visual_to_gid: dict[str, int] = {}
    for ch, key in visual_key.items():
        if key in glyph_json:
            g = char_gid[ch]
            prior = custom_visual_to_gid.setdefault(key, g)
            if prior != g:
                raise RuntimeError(f"visual alias {key!r} maps to multiple glyph IDs")

    audit = bytes(data[MAPPING_AUDIT_START:MAPPING_AUDIT_END])
    for key, gid in sorted(custom_visual_to_gid.items(), key=lambda kv: kv[1]):
        assert_blank_cell(data, gid)
        hits = audit.count(gid.to_bytes(2, "little"))
        if hits:
            raise RuntimeError(f"custom glyph 0x{gid:04X} reuse audit failed: {hits} hit(s)")

    encoded_replacements: list[tuple[int, bytes, bytes, str]] = []
    for off, source_jp, vi in MENU_FIELDS:
        source = source_jp.encode("cp932")
        repl = encode_text(vi, enc)
        if len(repl) != len(source):
            raise RuntimeError(f"field 0x{off:X} unit mismatch: source={len(source)//2}, vi={len(repl)//2}, text={vi!r}")
        if bytes(data[off:off + len(source)]) != source:
            raise RuntimeError(f"source identity mismatch at 0x{off:X}")
        encoded_replacements.append((off, source, repl, vi))

    print(f"codepage_entries={len(enc)}")
    print(f"custom_visual_glyphs={len(custom_visual_to_gid)}")
    print("lead_0x84_direct_text_use_in_current_scanner=0  # audited outside builder")
    print(f"lead_pointer=0x{lead_ptr:04X} PASS")
    print("custom_slot_blank_and_reuse_audit=PASS")
    print("source_identity_and_exact_units=PASS")
    for off, _src, _repl, vi in encoded_replacements:
        print(f"probe_row 0x{off:06X}: {vi}")
    print("expected_runtime_rows=ĐẦY ĐỦ!! / được! / CÓ DẤU!! / Việt / Maruko? / Ổn rồi")
    print("runtime_claim=NO")

    if args.dry_run:
        print("dry_run=PASS")
        return 0

    allowed: set[int] = set()

    for ch, code in enc.items():
        trail = code[1]
        entry_off = MAP_BASE + (trail - 0x40) * 2
        gid = char_gid[ch]
        data[entry_off:entry_off + 2] = gid.to_bytes(2, "little")
        allowed.update(range(entry_off, entry_off + 2))

    bitmap_touched: set[int] = set()
    for key, gid in custom_visual_to_gid.items():
        meta = glyph_json[key]
        if int(meta["glyph_id"], 16) != gid:
            raise RuntimeError(f"glyph JSON ID mismatch for {key!r}")
        rows = unpack_bitmap_hex(meta["bitmap_hex"])
        bitmap_touched.update(write_bitmap(data, gid, rows))
    allowed.update(bitmap_touched)

    for off, source, repl, _vi in encoded_replacements:
        data[off:off + len(source)] = repl
        allowed.update(range(off, off + len(source)))

    checksum, complement = write_snes_checksum(data)
    allowed.update(range(CHECKSUM_COMPLEMENT, CHECKSUM + 2))

    stored_checksum = read_u16le(data, CHECKSUM)
    stored_complement = read_u16le(data, CHECKSUM_COMPLEMENT)
    computed = calc_snes_checksum(data)
    if stored_checksum != computed or ((stored_checksum + stored_complement) & 0xFFFF) != 0xFFFF:
        raise RuntimeError("post-build checksum validation failed")

    diffs = {i for i, (a, b) in enumerate(zip(original, data)) if a != b}
    unexpected = sorted(diffs - allowed)
    if unexpected:
        raise RuntimeError(f"unexpected diff bytes: {[hex(x) for x in unexpected[:16]]}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(data)
    sha1, sha256 = digest(data)
    print(f"bitmap_diff_bytes={len(bitmap_touched)}")
    print(f"total_diff_bytes={len(diffs)}")
    print(f"build_checksum=0x{checksum:04X}")
    print(f"build_complement=0x{complement:04X}")
    print(f"output_sha1={sha1}")
    print(f"output_sha256={sha256}")
    print(f"output={args.output}")
    print("diff_surface=PASS")
    print("build=PASS")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
