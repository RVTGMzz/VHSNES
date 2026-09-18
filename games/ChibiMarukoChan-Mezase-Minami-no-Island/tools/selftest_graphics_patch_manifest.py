#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from apply_graphics_patch_manifest import Patch, validate_base, validate_patches


def check(name: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(name)
    print(f"{name}=PASS")


def main() -> int:
    print("CHIBI GRAPHICS PATCH MANIFEST SELFTEST")

    base = bytes([0]) * 0x200000
    base_sha1 = hashlib.sha1(base).hexdigest()
    base_sha256 = hashlib.sha256(base).hexdigest()

    validate_base(
        base,
        {
            "size": "0x200000",
            "sha1": base_sha1,
            "sha256": base_sha256,
        },
    )
    check("base_contract", True)

    p1 = Patch(
        "g0",
        0x1000,
        4,
        hashlib.sha256(base[0x1000:0x1004]).hexdigest(),
        b"ABCD",
        "synthetic",
    )
    p2 = Patch(
        "g1",
        0x2000,
        4,
        hashlib.sha256(base[0x2000:0x2004]).hexdigest(),
        b"EFGH",
        "synthetic",
    )
    validate_patches(base, [p1, p2])
    check("non_overlapping_span_validation", True)

    try:
        validate_patches(
            base,
            [
                p1,
                Patch(
                    "overlap",
                    0x1002,
                    4,
                    hashlib.sha256(base[0x1002:0x1006]).hexdigest(),
                    b"WXYZ",
                    "synthetic",
                ),
            ],
        )
    except ValueError:
        check("overlap_rejected", True)
    else:
        raise AssertionError("overlap_rejected")

    try:
        validate_patches(
            base,
            [
                Patch(
                    "bad_hash",
                    0x3000,
                    4,
                    "0" * 64,
                    b"1234",
                    "synthetic",
                )
            ],
        )
    except ValueError:
        check("original_span_hash_mismatch_rejected", True)
    else:
        raise AssertionError("original_span_hash_mismatch_rejected")

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        base_path = td / "base.sfc"
        out_path = td / "out.sfc"
        manifest_path = td / "manifest.json"
        base_path.write_bytes(base)

        replacement = b"VIET"
        off = 0x12340
        manifest = {
            "schema": "chibi.graphics.patch.v1",
            "base": {
                "size": "0x200000",
                "sha1": base_sha1,
                "sha256": base_sha256,
            },
            "patches": [
                {
                    "id": "synthetic_graphics",
                    "offset": hex(off),
                    "length": hex(len(replacement)),
                    "expected_original_sha256": hashlib.sha256(
                        base[off:off + len(replacement)]
                    ).hexdigest(),
                    "replacement_hex": replacement.hex(),
                }
            ],
        }
        manifest_path.write_text(
            json.dumps(manifest, indent=2) + "\n",
            encoding="utf-8",
        )

        tool = Path(__file__).with_name(
            "apply_graphics_patch_manifest.py"
        )
        result = subprocess.run(
            [
                sys.executable,
                str(tool),
                str(base_path),
                str(manifest_path),
                str(out_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        check("builder_reports_diff_surface_pass", "diff_surface=PASS" in result.stdout)
        out = out_path.read_bytes()
        check("builder_writes_replacement", out[off:off + 4] == replacement)

        verifier = Path(__file__).with_name(
            "verify_graphics_patch_build.py"
        )
        verify_result = subprocess.run(
            [
                sys.executable,
                str(verifier),
                str(base_path),
                str(out_path),
                str(manifest_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        check(
            "independent_verifier_pass",
            "snes_checksum=PASS" in verify_result.stdout
            and "diff_surface=PASS" in verify_result.stdout,
        )

        changed = {
            i
            for i, (before, after) in enumerate(zip(base, out))
            if before != after
        }
        allowed = {
            off,
            off + 1,
            off + 2,
            off + 3,
            0x7FDC,
            0x7FDD,
            0x7FDE,
            0x7FDF,
        }
        check("builder_changed_only_allowed_bytes", changed <= allowed)

    print("selftest=PASS")
    print("commercial_rom_required=NO")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
