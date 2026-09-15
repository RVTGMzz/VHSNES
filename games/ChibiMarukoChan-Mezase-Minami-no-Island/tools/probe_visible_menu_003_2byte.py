#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from rom_common import digest_bytes, require_clean_rom, write_snes_checksum, validate_internal_header

# Runtime diagnostic after Probe 002 froze at the Konami screen.
# Hypothesis: raw 1-byte ASCII desynchronizes a 2-byte text/script reader.
# Keep exactly one menu field and exactly 8 two-byte characters.
OFFSET = 0x28818
SOURCE = "ストーリーモード"
REPLACEMENT = "ＴＥＳＴ１２３４"


def main() -> int:
    ap = argparse.ArgumentParser(description="Guarded 2-byte full-width Latin probe on the first visible menu item")
    ap.add_argument("rom", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data = require_clean_rom(args.rom)
    source = SOURCE.encode("cp932")
    replacement = REPLACEMENT.encode("cp932")

    if len(source) != 16 or len(replacement) != 16:
        raise RuntimeError("Probe 003 must remain exactly 16 bytes / 8 two-byte units")
    actual = bytes(data[OFFSET:OFFSET + len(source)])
    if actual != source:
        raise RuntimeError(
            f"source identity mismatch at 0x{OFFSET:X}: got={actual.hex()} expected={source.hex()}"
        )

    print(f"offset=0x{OFFSET:06X}")
    print(f"source={SOURCE!r} source_bytes={len(source)}")
    print(f"replacement={REPLACEMENT!r} replacement_bytes={len(replacement)}")
    print("two_byte_width_preserved=PASS")
    print("surrounding_control_bytes_touched=NO")
    print("runtime_claim=NO")

    if args.dry_run:
        print("dry_run=PASS")
        return 0

    data[OFFSET:OFFSET + len(source)] = replacement
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
