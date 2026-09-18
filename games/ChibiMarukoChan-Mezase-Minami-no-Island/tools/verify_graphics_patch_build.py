#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from apply_graphics_patch_manifest import (
    CHECKSUM_BYTES,
    load_manifest,
    load_patch,
    validate_base,
    validate_patches,
)
from rom_common import EXPECTED_SIZE, validate_internal_header


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Independent verifier for guarded Chibi graphics builds"
    )
    ap.add_argument("base_rom", type=Path)
    ap.add_argument("built_rom", type=Path)
    ap.add_argument("manifest", type=Path)
    args = ap.parse_args()

    manifest = load_manifest(args.manifest)
    base = args.base_rom.read_bytes()
    built = args.built_rom.read_bytes()

    validate_base(base, manifest["base"])
    if len(base) != EXPECTED_SIZE or len(built) != EXPECTED_SIZE:
        raise SystemExit(
            f"size gate failed: base={len(base)} built={len(built)}"
        )

    patches = [
        load_patch(entry, args.manifest.parent)
        for entry in manifest["patches"]
    ]
    validate_patches(base, patches)

    allowed = set(CHECKSUM_BYTES)
    for patch in patches:
        start = patch.offset
        end = start + patch.length
        allowed.update(range(start, end))

        actual = built[start:end]
        if actual != patch.replacement:
            raise SystemExit(
                f"{patch.patch_id}: built span does not equal replacement"
            )

    changed = {
        i
        for i, (before, after) in enumerate(zip(base, built))
        if before != after
    }
    unexpected = sorted(changed - allowed)
    if unexpected:
        raise SystemExit(
            "unexpected diff bytes: "
            + ", ".join(f"0x{x:X}" for x in unexpected[:32])
        )

    header = validate_internal_header(built)
    if not header["checksum_pair_valid"]:
        raise SystemExit("SNES checksum/complement pair invalid")
    if not header["checksum_matches"]:
        raise SystemExit(
            f"SNES checksum mismatch: stored=0x{header['checksum']:04X} "
            f"computed=0x{header['computed_checksum']:04X}"
        )

    print("base_contract=PASS")
    print("manifest_original_span_hashes=PASS")
    print("replacement_spans=PASS")
    print("diff_surface=PASS")
    print("snes_checksum=PASS")
    print(f"patch_count={len(patches)}")
    print(f"changed_bytes={len(changed)}")
    print(f"built_sha1={hashlib.sha1(built).hexdigest()}")
    print(f"built_sha256={hashlib.sha256(built).hexdigest()}")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
