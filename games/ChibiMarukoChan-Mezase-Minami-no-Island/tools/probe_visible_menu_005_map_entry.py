#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from rom_common import digest_bytes, require_clean_rom, write_snes_checksum, validate_internal_header

# Probe 005 proves whether the discovered 0x82xx codepoint->glyph-id table
# controls the visible menu renderer. It keeps the same 8 two-byte units as
# Probe 003, but changes ONLY the mapping entry for full-width E (CP932 0x8264)
# from glyph-id 0x0000 (which visibly renders the same glyph as digit 0) to the
# known glyph-id used by full-width A (0x0517).
TEXT_OFFSET = 0x28818
SOURCE_TEXT = "ストーリーモード"
PROBE_TEXT = "ＴＥＳＴ１２３４"

MAP_TABLE_82_TRAIL_4F = 0x29880
CODE_A = 0x8260
CODE_E = 0x8264
A_ENTRY = MAP_TABLE_82_TRAIL_4F + ((CODE_A & 0xFF) - 0x4F) * 2
E_ENTRY = MAP_TABLE_82_TRAIL_4F + ((CODE_E & 0xFF) - 0x4F) * 2
EXPECTED_A_GLYPH_ID = 0x0517
EXPECTED_E_GLYPH_ID = 0x0000


def u16le(data: bytes | bytearray, off: int) -> int:
    return data[off] | (data[off + 1] << 8)


def main() -> int:
    ap = argparse.ArgumentParser(description="Probe 005: prove the 0x82xx codepoint-to-glyph mapping table")
    ap.add_argument("rom", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data = require_clean_rom(args.rom)

    source = SOURCE_TEXT.encode("cp932")
    replacement = PROBE_TEXT.encode("cp932")
    if len(source) != 16 or len(replacement) != 16:
        raise RuntimeError("probe text must remain exactly 8 two-byte units / 16 bytes")
    actual = bytes(data[TEXT_OFFSET:TEXT_OFFSET + len(source)])
    if actual != source:
        raise RuntimeError(
            f"text source identity mismatch at 0x{TEXT_OFFSET:X}: got={actual.hex()} expected={source.hex()}"
        )

    a_id = u16le(data, A_ENTRY)
    e_id = u16le(data, E_ENTRY)
    if a_id != EXPECTED_A_GLYPH_ID:
        raise RuntimeError(f"A mapping mismatch: got 0x{a_id:04X} expected 0x{EXPECTED_A_GLYPH_ID:04X}")
    if e_id != EXPECTED_E_GLYPH_ID:
        raise RuntimeError(f"E mapping mismatch: got 0x{e_id:04X} expected 0x{EXPECTED_E_GLYPH_ID:04X}")

    print(f"text_offset=0x{TEXT_OFFSET:06X}")
    print(f"probe_text={PROBE_TEXT}")
    print(f"A_entry=0x{A_ENTRY:06X} glyph_id=0x{a_id:04X}")
    print(f"E_entry=0x{E_ENTRY:06X} glyph_id=0x{e_id:04X}")
    print("planned_E_remap=0x0517  # same glyph-id as A")
    print("expected_runtime_first_line=TAST1234 (full-width renderer style)")
    print("clean_source=PASS")
    print("source_identity=PASS")
    print("mapping_identity=PASS")
    print("runtime_claim=NO")

    if args.dry_run:
        print("dry_run=PASS")
        return 0

    data[TEXT_OFFSET:TEXT_OFFSET + len(replacement)] = replacement
    data[E_ENTRY:E_ENTRY + 2] = EXPECTED_A_GLYPH_ID.to_bytes(2, "little")

    checksum, complement = write_snes_checksum(data)
    header = validate_internal_header(data)
    if not header["checksum_matches"] or not header["checksum_pair_valid"]:
        raise RuntimeError("post-write SNES checksum validation failed")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(data)
    ident = digest_bytes(data)
    print(f"build_checksum=0x{checksum:04X}")
    print(f"build_complement=0x{complement:04X}")
    print(f"output_sha1={ident.sha1}")
    print(f"output_sha256={ident.sha256}")
    print(f"output={args.output}")
    print("build=PASS")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
