#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from rom_common import digest_bytes, require_clean_rom, validate_internal_header


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify and inspect the canonical Chibi Maruko-chan SNES ROM")
    ap.add_argument("rom", type=Path)
    args = ap.parse_args()

    raw = args.rom.read_bytes()
    ident = digest_bytes(raw)
    print(f"size={ident.size} (0x{ident.size:X})")
    print(f"sha1={ident.sha1}")
    print(f"sha256={ident.sha256}")
    require_clean_rom(args.rom)
    print("clean_rom_contract=PASS")

    h = validate_internal_header(raw)
    for key, value in h.items():
        if isinstance(value, int) and key not in {"rom_size_exp", "ram_size_exp", "region", "maker", "version"}:
            print(f"{key}=0x{value:X}")
        else:
            print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
