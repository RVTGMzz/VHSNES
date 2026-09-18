#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

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


def main() -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Generate one guarded graphics-manifest entry "
            "from a proven Build 035 span and replacement file"
        )
    )
    ap.add_argument("build035", type=Path)
    ap.add_argument("replacement_file", type=Path)
    ap.add_argument("--id", required=True)
    ap.add_argument("--offset", type=lambda s: int(s, 0), required=True)
    ap.add_argument(
        "--evidence",
        required=True,
        help="short proof note, e.g. G1 pointer/DMA + decoded asset",
    )
    args = ap.parse_args()

    base = require_build035(args.build035)
    replacement = args.replacement_file.read_bytes()
    if not replacement:
        raise SystemExit("replacement file is empty")

    start = args.offset
    end = start + len(replacement)
    if not (0 <= start < end <= len(base)):
        raise SystemExit(
            f"replacement span outside ROM: "
            f"0x{start:X}..0x{end:X}"
        )

    original = base[start:end]
    entry = {
        "id": args.id,
        "offset": f"0x{start:X}",
        "length": f"0x{len(replacement):X}",
        "expected_original_sha256": hashlib.sha256(
            original
        ).hexdigest(),
        "replacement_file": str(args.replacement_file),
        "replacement_sha256": hashlib.sha256(
            replacement
        ).hexdigest(),
        "evidence": args.evidence,
        "runtime_claim": False,
    }

    print(
        json.dumps(
            entry,
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
