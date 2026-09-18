#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def check(name: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(name)
    print(f"{name}=PASS")


def main() -> int:
    print("CHIBI GRAPHICS MANIFEST ASSEMBLER SELFTEST")
    tool = Path(__file__).with_name(
        "assemble_graphics_manifest.py"
    )

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        template = root / "template.json"
        out_dir = root / "manifest"
        output = out_dir / "build036.json"
        f1_dir = root / "f1"
        f2_dir = root / "f2"
        f1_dir.mkdir()
        f2_dir.mkdir()

        template.write_text(
            json.dumps(
                {
                    "schema": "chibi.graphics.patch.v1",
                    "ready": False,
                    "base": {
                        "size": "0x200000",
                        "sha1": "x",
                        "sha256": "y",
                    },
                    "patches": [],
                }
            ),
            encoding="utf-8",
        )

        (f1_dir / "a.bin").write_bytes(b"AAAA")
        (f2_dir / "b.bin").write_bytes(b"BBBB")

        f1 = f1_dir / "a.json"
        f2 = f2_dir / "b.json"
        f1.write_text(
            json.dumps(
                {
                    "schema": "chibi.graphics.patch.fragment.v1",
                    "id": "g1_start",
                    "evidence": "synthetic proof A",
                    "patches": [
                        {
                            "id": "g1_start_gfx",
                            "offset": "0x1000",
                            "length": "0x4",
                            "expected_original_sha256": "0" * 64,
                            "replacement_file": "a.bin",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        f2.write_text(
            json.dumps(
                {
                    "schema": "chibi.graphics.patch.fragment.v1",
                    "id": "g3_win",
                    "evidence": "synthetic proof B",
                    "patches": [
                        {
                            "id": "g3_win_gfx",
                            "offset": "0x2000",
                            "length": "0x4",
                            "expected_original_sha256": "1" * 64,
                            "replacement_file": "b.bin",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        result = subprocess.run(
            [
                sys.executable,
                str(tool),
                str(template),
                str(output),
                str(f1),
                str(f2),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        check(
            "assembler_reports_ready",
            "manifest_ready=true"
            in result.stdout,
        )

        manifest = json.loads(
            output.read_text(encoding="utf-8")
        )
        check(
            "manifest_ready",
            manifest["ready"] is True,
        )
        check(
            "manifest_patch_count",
            len(manifest["patches"]) == 2,
        )
        for patch in manifest["patches"]:
            replacement = (
                output.parent
                / patch["replacement_file"]
            )
            check(
                "rewritten_path_resolves_"
                + patch["id"],
                replacement.is_file(),
            )

        overlap = f2_dir / "overlap.json"
        overlap.write_text(
            json.dumps(
                {
                    "schema": "chibi.graphics.patch.fragment.v1",
                    "id": "overlap",
                    "evidence": "synthetic overlap",
                    "patches": [
                        {
                            "id": "overlap_gfx",
                            "offset": "0x1002",
                            "length": "0x4",
                            "expected_original_sha256": "2" * 64,
                            "replacement_file": "b.bin",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        bad = subprocess.run(
            [
                sys.executable,
                str(tool),
                str(template),
                str(root / "bad.json"),
                str(f1),
                str(overlap),
            ],
            capture_output=True,
            text=True,
        )
        check(
            "overlap_rejected",
            bad.returncode != 0,
        )

    print("selftest=PASS")
    print("commercial_rom_required=NO")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
