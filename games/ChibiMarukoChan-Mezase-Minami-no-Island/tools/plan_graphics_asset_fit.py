#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Check whether a generated graphics replacement fits "
            "inside a proven existing asset span"
        )
    )
    ap.add_argument("replacement", type=Path)
    ap.add_argument(
        "--span-length",
        type=lambda s: int(s, 0),
        required=True,
    )
    ap.add_argument(
        "--span-offset",
        type=lambda s: int(s, 0),
        help="optional proven ROM span start for reporting",
    )
    ap.add_argument(
        "--padded-output",
        type=Path,
        help=(
            "optional output padded to exact span length; "
            "only allowed when replacement is not larger"
        ),
    )
    ap.add_argument(
        "--pad-byte",
        type=lambda s: int(s, 0),
        default=0,
    )
    ap.add_argument("--json", type=Path)
    args = ap.parse_args()

    if args.span_length <= 0:
        raise SystemExit("span-length must be positive")
    if not 0 <= args.pad_byte <= 0xFF:
        raise SystemExit("pad-byte must be 0..255")

    replacement = args.replacement.read_bytes()
    used = len(replacement)
    capacity = args.span_length

    if used == capacity:
        status = "EXACT_FIT"
    elif used < capacity:
        status = "FITS_WITH_PADDING"
    else:
        status = "RELOCATION_OR_LAYOUT_CHANGE_REQUIRED"

    free = capacity - used
    ratio = used / capacity

    if args.padded_output:
        if used > capacity:
            raise SystemExit(
                "cannot pad: replacement exceeds proven span"
            )
        padded = replacement + bytes(
            [args.pad_byte]
        ) * (capacity - used)
        args.padded_output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        args.padded_output.write_bytes(padded)

    report = {
        "replacement": str(args.replacement),
        "replacement_bytes": used,
        "replacement_sha256": hashlib.sha256(
            replacement
        ).hexdigest(),
        "span_offset": (
            f"0x{args.span_offset:X}"
            if args.span_offset is not None
            else None
        ),
        "span_length": capacity,
        "status": status,
        "free_bytes": free,
        "usage_ratio": ratio,
        "padded_output": (
            str(args.padded_output)
            if args.padded_output
            else None
        ),
        "pad_byte": (
            f"0x{args.pad_byte:02X}"
            if args.padded_output
            else None
        ),
        "runtime_claim": False,
    }

    print(f"status={status}")
    print(f"replacement_bytes=0x{used:X}")
    print(f"span_length=0x{capacity:X}")
    print(f"free_bytes={free}")
    print(f"usage_ratio={ratio:.4f}")
    if args.padded_output:
        print(f"padded_output={args.padded_output}")
    print("runtime_claim=NO")

    if args.json:
        args.json.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        args.json.write_text(
            json.dumps(
                report,
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
