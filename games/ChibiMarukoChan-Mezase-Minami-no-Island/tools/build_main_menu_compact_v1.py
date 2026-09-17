#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path

EXPECTED_SIZE = 0x200000
EXPECTED_BASE_SHA1 = "a1cdd19934ec59cf9cc1142e69730bd27efe7820"  # Build 023 / Probe 019
CHECKSUM_COMPLEMENT = 0x7FDC
CHECKSUM = 0x7FDE

FIELDS = [
    (0x28818, 8, "Truyện"),
    (0x2882E, 5, "Đấu"),
    (0x2883C, 8, "Đấu đội"),
    (0x28852, 4, "M.Q"),
    (0x2885E, 7, "Tập vẽ"),
    (0x28870, 6, "Bói"),
    (0x28880, 6, "Hát"),
    (0x28892, 4, "Âm"),
    (0x288A2, 4, "ST"),
    (0x288B2, 4, "Mono"),
]


def sha1(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def load_codepage(path: Path) -> dict[str, bytes]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    out: dict[str, bytes] = {}
    for row in rows:
        out[row["unicode"]] = bytes.fromhex(row["code_hex"])
    return out


def calc_checksum(data: bytes | bytearray) -> int:
    tmp = bytearray(data)
    tmp[CHECKSUM_COMPLEMENT:CHECKSUM + 2] = b"\x00\x00\x00\x00"
    return (sum(tmp) + 0x1FE) & 0xFFFF


def main() -> int:
    ap = argparse.ArgumentParser(description="Build compact Vietnamese main menu on Build 023 / Probe 019 baseline")
    ap.add_argument("base_rom", type=Path)
    ap.add_argument("output_rom", type=Path)
    ap.add_argument("--codepage", type=Path, required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    original = args.base_rom.read_bytes()
    if len(original) != EXPECTED_SIZE or sha1(original) != EXPECTED_BASE_SHA1:
        raise SystemExit(
            f"base contract failed: size={len(original)} sha1={sha1(original)}; "
            f"expected size={EXPECTED_SIZE} sha1={EXPECTED_BASE_SHA1}"
        )

    enc = load_codepage(args.codepage)
    if " " not in enc:
        raise SystemExit("codepage is missing the 2-byte space glyph")

    spans = []
    for off, units, _text in FIELDS:
        spans.append((off, off + units * 2))
    for i, (a0, a1) in enumerate(spans):
        for b0, b1 in spans[i + 1:]:
            if max(a0, b0) < min(a1, b1):
                raise SystemExit(f"overlap: {hex(a0)}..{hex(a1)} vs {hex(b0)}..{hex(b1)}")

    rom = bytearray(original)
    for off, units, text in FIELDS:
        missing = [ch for ch in text if ch not in enc]
        if missing:
            raise SystemExit(f"missing codepage glyph(s) for {text!r}: {missing!r}")
        raw = b"".join(enc[ch] for ch in text)
        if len(raw) % 2:
            raise SystemExit(f"odd encoded length for {text!r}")
        used_units = len(raw) // 2
        if used_units > units:
            raise SystemExit(f"field overflow for {text!r}: {used_units}>{units}")
        replacement = raw + enc[" "] * (units - used_units)
        if len(replacement) != units * 2:
            raise SystemExit(f"bad replacement length for {text!r}")
        rom[off:off + units * 2] = replacement

    checksum = calc_checksum(rom)
    complement = checksum ^ 0xFFFF
    rom[CHECKSUM_COMPLEMENT:CHECKSUM_COMPLEMENT + 2] = complement.to_bytes(2, "little")
    rom[CHECKSUM:CHECKSUM + 2] = checksum.to_bytes(2, "little")

    allowed = {CHECKSUM_COMPLEMENT, CHECKSUM_COMPLEMENT + 1, CHECKSUM, CHECKSUM + 1}
    for start, end in spans:
        allowed.update(range(start, end))
    changed = {i for i, (a, b) in enumerate(zip(original, rom)) if a != b}
    unexpected = sorted(changed - allowed)
    if unexpected:
        raise SystemExit(f"unexpected diff bytes: {[hex(x) for x in unexpected[:32]]}")

    print("base_contract=PASS")
    print("field_fit=10/10 PASS")
    print("overlap=0 PASS")
    print("diff_surface=PASS")
    print(f"checksum=0x{checksum:04X}")
    print(f"complement=0x{complement:04X}")
    print(f"output_sha1={sha1(bytes(rom))}")
    print(f"output_sha256={hashlib.sha256(rom).hexdigest()}")

    if not args.dry_run:
        args.output_rom.write_bytes(rom)
        print(f"output={args.output_rom}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
