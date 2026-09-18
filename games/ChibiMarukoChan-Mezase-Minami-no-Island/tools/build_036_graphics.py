#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from rom_common import validate_internal_header

EXPECTED_SIZE = 0x200000
EXPECTED_BUILD035_SHA1 = "054380f9b452f245471e6309eb33c7486d581462"
EXPECTED_BUILD035_SHA256 = "f8fb662a9e1b8fc5a5ff689f690ceaf332055ed86983e52b476a78852e4fd58d"


def require_build035(path: Path) -> bytes:
    data = path.read_bytes()
    sha1 = hashlib.sha1(data).hexdigest()
    sha256 = hashlib.sha256(data).hexdigest()
    if (
        len(data) != EXPECTED_SIZE
        or sha1 != EXPECTED_BUILD035_SHA1
        or sha256 != EXPECTED_BUILD035_SHA256
    ):
        raise RuntimeError(
            "Build 035 contract failed: "
            f"size={len(data)} sha1={sha1} sha256={sha256}"
        )
    return data


def load_ready_manifest(path: Path) -> dict:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if obj.get("schema") != "chibi.graphics.patch.v1":
        raise RuntimeError("unsupported manifest schema")
    if obj.get("ready") is not True:
        raise RuntimeError(
            "graphics manifest is not marked ready=true"
        )
    patches = obj.get("patches")
    if not isinstance(patches, list) or not patches:
        raise RuntimeError("ready manifest has no patches")
    return obj


def run_capture(cmd: list[str]) -> str:
    result = subprocess.run(
        cmd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def main() -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Build and independently verify Chibi Build 036 "
            "graphics layer on exact Build 035"
        )
    )
    ap.add_argument("build035", type=Path)
    ap.add_argument("manifest", type=Path)
    ap.add_argument("output_rom", type=Path)
    ap.add_argument(
        "--report",
        type=Path,
        default=Path(
            "reports/generated/build036_graphics_static.json"
        ),
    )
    args = ap.parse_args()

    require_build035(args.build035)
    manifest = load_ready_manifest(args.manifest)

    base = manifest.get("base", {})
    if (
        str(base.get("sha1", "")).lower()
        != EXPECTED_BUILD035_SHA1
        or str(base.get("sha256", "")).lower()
        != EXPECTED_BUILD035_SHA256
    ):
        raise RuntimeError(
            "manifest base contract is not exact Build 035"
        )

    tool_dir = Path(__file__).resolve().parent
    py = sys.executable

    builder_output = run_capture(
        [
            py,
            str(
                tool_dir
                / "apply_graphics_patch_manifest.py"
            ),
            str(args.build035),
            str(args.manifest),
            str(args.output_rom),
        ]
    )

    verifier_output = run_capture(
        [
            py,
            str(tool_dir / "verify_graphics_patch_build.py"),
            str(args.build035),
            str(args.output_rom),
            str(args.manifest),
        ]
    )

    built = args.output_rom.read_bytes()
    header = validate_internal_header(built)

    report = {
        "build": "036 graphics candidate",
        "base": {
            "name": args.build035.name,
            "sha1": EXPECTED_BUILD035_SHA1,
            "sha256": EXPECTED_BUILD035_SHA256,
        },
        "manifest": str(args.manifest),
        "patch_ids": [
            str(entry.get("id"))
            for entry in manifest["patches"]
        ],
        "output": {
            "path": str(args.output_rom),
            "size": len(built),
            "sha1": hashlib.sha1(built).hexdigest(),
            "sha256": hashlib.sha256(built).hexdigest(),
            "checksum": f"0x{header['checksum']:04X}",
            "complement": f"0x{header['complement']:04X}",
        },
        "static_validation": {
            "builder": "PASS",
            "independent_verifier": "PASS",
            "checksum_pair": bool(
                header["checksum_pair_valid"]
            ),
            "checksum_matches": bool(
                header["checksum_matches"]
            ),
        },
        "builder_output": builder_output.splitlines(),
        "verifier_output": verifier_output.splitlines(),
        "runtime_status": "UNTESTED",
        "runtime_claim": False,
    }

    args.report.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    args.report.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print("build035_contract=PASS")
    print("manifest_ready=PASS")
    print("graphics_builder=PASS")
    print("independent_verifier=PASS")
    print("snes_checksum=PASS")
    print(f"patch_count={len(manifest['patches'])}")
    print(f"output={args.output_rom}")
    print(f"report={args.report}")
    print(
        f"output_sha1={report['output']['sha1']}"
    )
    print(
        f"output_sha256={report['output']['sha256']}"
    )
    print("runtime_status=UNTESTED")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
