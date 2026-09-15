#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from rom_common import digest_bytes, require_clean_rom, write_snes_checksum, validate_internal_header

# Diagnostic visible-menu probe only. Not a final Vietnamese translation pass.
# Keep every surrounding control/terminator byte untouched.
PROBES = [
    (0x28818, "ストーリーモード", "COT TRUYEN"),
    (0x2882E, "対戦モード", "DOI KHANG"),
    (0x2883C, "チーム対戦モード", "DAU DOI"),
    (0x28852, "まるこＱ", "MARUKO Q"),
    (0x2885E, "まるこペイント", "VE MARUKO"),
    (0x28870, "まるこみくじ", "BOI MARUKO"),
    (0x28880, "針切カラオケ", "KARAOKE"),
    (0x28892, "サウンド", "AM THANH"),
    (0x288A2, "ステレオ", "STEREO"),
    (0x288B2, "モノラル", "MONO"),
]


def main() -> int:
    ap = argparse.ArgumentParser(description="Guarded ASCII probe on the immediately visible main menu")
    ap.add_argument("rom", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data = require_clean_rom(args.rom)
    spans: list[tuple[int, int]] = []

    for offset, jp, ascii_text in PROBES:
        source = jp.encode("cp932")
        replacement = ascii_text.encode("ascii")
        if len(replacement) > len(source):
            raise RuntimeError(f"replacement too long at 0x{offset:X}: {ascii_text!r}")
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
        print(f"0x{offset:06X} source={jp} source_bytes={len(source)} probe={ascii_text!r} probe_bytes={len(replacement)}")

    print("clean_source=PASS")
    print(f"source_identity={len(PROBES)}/{len(PROBES)} PASS")
    print("overlap_count=0")
    print("runtime_claim=NO")

    if args.dry_run:
        print("dry_run=PASS")
        return 0

    for offset, jp, ascii_text in PROBES:
        source = jp.encode("cp932")
        replacement = ascii_text.encode("ascii")
        data[offset:offset + len(source)] = replacement + b" " * (len(source) - len(replacement))

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
