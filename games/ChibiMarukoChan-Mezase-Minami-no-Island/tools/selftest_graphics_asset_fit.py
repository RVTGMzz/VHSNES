#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


def check(name: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(name)
    print(f"{name}=PASS")


def run(tool: Path, replacement: Path, span: int, extra=None):
    cmd = [
        sys.executable,
        str(tool),
        str(replacement),
        "--span-length",
        hex(span),
    ]
    if extra:
        cmd.extend(extra)
    return subprocess.run(
        cmd,
        check=True,
        capture_output=True,
        text=True,
    )


def main() -> int:
    print("CHIBI GRAPHICS FIT PLANNER SELFTEST")
    tool = Path(__file__).with_name(
        "plan_graphics_asset_fit.py"
    )

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        replacement = td / "r.bin"

        replacement.write_bytes(b"A" * 16)
        result = run(tool, replacement, 16)
        check(
            "exact_fit",
            "status=EXACT_FIT" in result.stdout,
        )

        padded = td / "padded.bin"
        result = run(
            tool,
            replacement,
            32,
            [
                "--padded-output",
                str(padded),
                "--pad-byte",
                "0x00",
            ],
        )
        check(
            "fits_with_padding",
            "status=FITS_WITH_PADDING"
            in result.stdout,
        )
        check(
            "padding_length",
            len(padded.read_bytes()) == 32,
        )

        result = run(tool, replacement, 8)
        check(
            "relocation_required",
            "RELOCATION_OR_LAYOUT_CHANGE_REQUIRED"
            in result.stdout,
        )

    print("selftest=PASS")
    print("commercial_rom_required=NO")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
