#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from rom_common import digest_bytes, require_clean_rom, write_snes_checksum, validate_internal_header

# Diagnostic glyph-map probe. It preserves the exact number of two-byte CP932
# code units in each source field so the menu parser's stride/field size does
# not change. This is NOT a translation build.
PROBES = [
    (0x28818, "ストーリーモード", "ＡＢＣＤＥＦＧＨ"),
    (0x2882E, "対戦モード", "ＩＪＫＬＭ"),
    (0x2883C, "チーム対戦モード", "ＮＯＰＱＲＳＴＵ"),
    (0x28852, "まるこＱ", "ＶＷＸＹ"),
    (0x2885E, "まるこペイント", "Ｚ０１２３４５"),
    (0x28870, "まるこみくじ", "６７８９ＡＢ"),
]


def main() -> int:
    ap = argparse.ArgumentParser(description="Guarded two-byte full-width glyph map probe on visible menu")
    ap.add_argument("rom", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data = require_clean_rom(args.rom)
    spans: list[tuple[int, int]] = []

    for offset, jp, probe in PROBES:
        source = jp.encode("cp932")
        replacement = probe.encode("cp932")
        if len(source) != len(replacement):
            raise RuntimeError(
                f"two-byte length mismatch at 0x{offset:X}: source={len(source)} replacement={len(replacement)}"
            )
        if len(source) % 2:
            raise RuntimeError(f"unexpected odd source byte count at 0x{offset:X}")
        actual = bytes(data[offset:offset + len(source)])
        if actual != source:
            raise RuntimeError(
                f"source identity mismatch at 0x{offset:X}: got={actual.hex()} expected={source.hex()}"
            )
        span = (offset, offset + len(source))
        for prev in spans:
            if not (span[1] <= prev[0] or span[0] >= prev[1]):
                raise RuntimeError(f"overlapping write: {span} vs {prev}")
        spans.append(span)
        print(
            f"0x{offset:06X} units={len(source)//2} source={jp} probe={probe} "
            f"bytes={replacement.hex()}"
        )

    print("clean_source=PASS")
    print(f"source_identity={len(PROBES)}/{len(PROBES)} PASS")
    print("two_byte_length_preservation=PASS")
    print("overlap_count=0")
    print("runtime_claim=NO")

    if args.dry_run:
        print("dry_run=PASS")
        return 0

    for offset, jp, probe in PROBES:
        source = jp.encode("cp932")
        replacement = probe.encode("cp932")
        data[offset:offset + len(source)] = replacement

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
