#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from rom_common import digest_bytes, require_clean_rom, write_snes_checksum, validate_internal_header

# Diagnostic only. This is NOT a translation pass.
PROBE_OFFSET = 0x2B7C9
SOURCE_TEXT = "メロディーありでスタート"
PROBE_TEXT = "BAT DAU CO NHAC"


def main() -> int:
    ap = argparse.ArgumentParser(description="Guarded ASCII renderer probe on one known menu string")
    ap.add_argument("rom", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data = require_clean_rom(args.rom)
    source = SOURCE_TEXT.encode("cp932")
    replacement = PROBE_TEXT.encode("ascii")
    if len(replacement) > len(source):
        raise RuntimeError("probe replacement exceeds the exact source field")
    expected = bytes(data[PROBE_OFFSET:PROBE_OFFSET + len(source)])
    if expected != source:
        raise RuntimeError(
            f"source identity mismatch at 0x{PROBE_OFFSET:X}: got={expected.hex()} expected={source.hex()}"
        )
    replacement_padded = replacement + b" " * (len(source) - len(replacement))

    print("clean_source=PASS")
    print(f"offset=0x{PROBE_OFFSET:X}")
    print(f"source_bytes={len(source)}")
    print(f"replacement_bytes={len(replacement)}")
    print(f"write_span={len(replacement_padded)}")
    print("overlap_count=0")
    print("runtime_claim=NO")

    if args.dry_run:
        print("dry_run=PASS")
        return 0

    data[PROBE_OFFSET:PROBE_OFFSET + len(source)] = replacement_padded
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
