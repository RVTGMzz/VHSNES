#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from rom_common import require_clean_rom, write_snes_checksum

GROUP4_SECOND_LIST_FILE = 0x044CF8
EXPECTED = bytes.fromhex("80 CE 38 D0 00 00")
PATCHED = bytes.fromhex("80 CE 00 00 00 00")


def build_probe(clean_rom: Path, output: Path) -> dict:
    data = require_clean_rom(clean_rom)

    actual = bytes(
        data[GROUP4_SECOND_LIST_FILE:GROUP4_SECOND_LIST_FILE + len(EXPECTED)]
    )
    if actual != EXPECTED:
        raise RuntimeError(
            "group-4 second-list signature mismatch at "
            f"0x{GROUP4_SECOND_LIST_FILE:06X}: "
            f"{actual.hex()} != {EXPECTED.hex()}"
        )

    before = bytes(data)
    data[
        GROUP4_SECOND_LIST_FILE:
        GROUP4_SECOND_LIST_FILE + len(PATCHED)
    ] = PATCHED

    checksum, complement = write_snes_checksum(data)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(data)

    changed = [
        i for i, (a, b) in enumerate(zip(before, data))
        if a != b
    ]
    return {
        "changed_bytes": len(changed),
        "changed_offsets": [f"0x{x:06X}" for x in changed],
        "sha1": hashlib.sha1(data).hexdigest(),
        "sha256": hashlib.sha256(data).hexdigest(),
        "checksum": f"0x{checksum:04X}",
        "complement": f"0x{complement:04X}",
        "group4_second_list": bytes(
            data[
                GROUP4_SECOND_LIST_FILE:
                GROUP4_SECOND_LIST_FILE + 6
            ]
        ).hex(" ").upper(),
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Build the narrow G2 group-4 probe that keeps CE80 but "
            "terminates the controller list before D038."
        )
    )
    ap.add_argument("clean_rom", type=Path)
    ap.add_argument("output", type=Path)
    args = ap.parse_args()

    meta = build_probe(args.clean_rom, args.output)

    print("clean_rom_contract=PASS")
    print("probe=G2_D038_DISABLE_PROBE_001")
    print("group4_second_list_before=80 CE 38 D0 00 00")
    print(f"group4_second_list_after={meta['group4_second_list']}")
    print(f"changed_bytes={meta['changed_bytes']}")
    print(f"changed_offsets={','.join(meta['changed_offsets'])}")
    print(f"sha1={meta['sha1']}")
    print(f"sha256={meta['sha256']}")
    print(f"checksum={meta['checksum']}")
    print(f"complement={meta['complement']}")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
