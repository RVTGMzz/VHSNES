#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from rom_common import EXPECTED_SIZE, write_snes_checksum

CHECKSUM_BYTES = {0x7FDC, 0x7FDD, 0x7FDE, 0x7FDF}


@dataclass(frozen=True)
class Patch:
    patch_id: str
    offset: int
    length: int
    expected_sha256: str
    replacement: bytes
    replacement_source: str


def digest(data: bytes | bytearray) -> str:
    return hashlib.sha256(data).hexdigest()


def load_manifest(path: Path) -> dict:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if obj.get("schema") != "chibi.graphics.patch.v1":
        raise ValueError("unsupported manifest schema")
    if not isinstance(obj.get("base"), dict):
        raise ValueError("manifest missing base contract")
    if not isinstance(obj.get("patches"), list) or not obj["patches"]:
        raise ValueError("manifest must contain at least one patch")
    return obj


def load_patch(entry: dict, manifest_dir: Path) -> Patch:
    patch_id = str(entry["id"])
    offset = int(str(entry["offset"]), 0)
    length = int(str(entry["length"]), 0)
    expected = str(entry["expected_original_sha256"]).lower()

    has_file = "replacement_file" in entry
    has_hex = "replacement_hex" in entry
    if has_file == has_hex:
        raise ValueError(
            f"{patch_id}: specify exactly one replacement_file or replacement_hex"
        )

    if has_file:
        p = manifest_dir / str(entry["replacement_file"])
        replacement = p.read_bytes()
        source = str(p)
    else:
        replacement = bytes.fromhex(str(entry["replacement_hex"]))
        source = "inline_hex"

    if len(replacement) != length:
        raise ValueError(
            f"{patch_id}: replacement length {len(replacement)} != declared {length}"
        )
    if len(expected) != 64 or any(
        ch not in "0123456789abcdef" for ch in expected
    ):
        raise ValueError(
            f"{patch_id}: expected_original_sha256 must be 64 lowercase hex chars"
        )

    return Patch(
        patch_id,
        offset,
        length,
        expected,
        replacement,
        source,
    )


def validate_base(data: bytes, base: dict) -> None:
    size = int(str(base["size"]), 0)
    sha1 = str(base["sha1"]).lower()
    sha256 = str(base["sha256"]).lower()
    got1 = hashlib.sha1(data).hexdigest()
    got256 = hashlib.sha256(data).hexdigest()

    problems = []
    if len(data) != size:
        problems.append(f"size {len(data)} != {size}")
    if got1 != sha1:
        problems.append(f"sha1 {got1} != {sha1}")
    if got256 != sha256:
        problems.append(f"sha256 {got256} != {sha256}")
    if problems:
        raise ValueError(
            "base contract failed: " + "; ".join(problems)
        )


def validate_patches(data: bytes, patches: list[Patch]) -> None:
    spans: list[tuple[int, int, str]] = []

    for patch in patches:
        start = patch.offset
        end = patch.offset + patch.length

        if not (0 <= start < end <= len(data)):
            raise ValueError(f"{patch.patch_id}: span outside ROM")

        for other_start, other_end, other_id in spans:
            if max(start, other_start) < min(end, other_end):
                raise ValueError(
                    f"{patch.patch_id}: overlaps {other_id}"
                )
        spans.append((start, end, patch.patch_id))

        actual = digest(data[start:end])
        if actual != patch.expected_sha256:
            raise ValueError(
                f"{patch.patch_id}: original-span hash mismatch "
                f"{actual} != {patch.expected_sha256}"
            )


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Guarded graphics patch builder for Chibi Build 035+"
    )
    ap.add_argument("base_rom", type=Path)
    ap.add_argument("manifest", type=Path)
    ap.add_argument("output_rom", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    manifest = load_manifest(args.manifest)
    original = args.base_rom.read_bytes()
    validate_base(original, manifest["base"])

    if len(original) != EXPECTED_SIZE:
        raise SystemExit(f"unexpected ROM size: {len(original)}")

    patches = [
        load_patch(entry, args.manifest.parent)
        for entry in manifest["patches"]
    ]
    validate_patches(original, patches)

    rom = bytearray(original)
    allowed = set(CHECKSUM_BYTES)

    for patch in patches:
        start = patch.offset
        end = start + patch.length
        rom[start:end] = patch.replacement
        allowed.update(range(start, end))

    checksum, complement = write_snes_checksum(rom)

    changed = {
        i
        for i, (before, after) in enumerate(zip(original, rom))
        if before != after
    }
    unexpected = sorted(changed - allowed)
    if unexpected:
        raise SystemExit(
            "unexpected diff bytes: "
            + ", ".join(f"0x{x:X}" for x in unexpected[:32])
        )

    print("base_contract=PASS")
    print(f"patch_count={len(patches)}")
    print("overlap=0 PASS")
    print("original_span_hashes=PASS")
    print("replacement_lengths=PASS")
    print("diff_surface=PASS")

    for patch in patches:
        print(
            f"patch={patch.patch_id} "
            f"offset=0x{patch.offset:06X} "
            f"length=0x{patch.length:X} "
            f"source={patch.replacement_source}"
        )

    print(f"checksum=0x{checksum:04X}")
    print(f"complement=0x{complement:04X}")
    print(f"output_sha1={hashlib.sha1(rom).hexdigest()}")
    print(f"output_sha256={hashlib.sha256(rom).hexdigest()}")
    print("runtime_claim=NO")

    if not args.dry_run:
        args.output_rom.write_bytes(rom)
        print(f"output={args.output_rom}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
