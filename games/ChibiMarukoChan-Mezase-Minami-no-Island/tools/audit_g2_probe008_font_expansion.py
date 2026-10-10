#!/usr/bin/env python3
"""Read-only expansion and codepage feasibility audit for Chibi Probe008.

A blank FF range is NOT proof of no banked/indirect references.
This script must never be used alone to authorize a ROM write.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from repair_g2_probe008_full_font import extra_chars

ROOT = Path(__file__).resolve().parent.parent
CLEAN_SHA256 = "e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
ROM_SIZE = 0x200000
FONT_PAGE = (0x125000, 0x125800)    # potential 11th page at $A4:D000
PTR_STAGING = (0x2F800, 0x2F821)  # 11 * 3-byte pointers, $85:F800
LEAD_STAGING = (0x2FA00, 0x2FA68) # 52 * 2 bytes, $85:FA00


def check_clean(rom: bytes) -> dict:
    if len(rom) != ROM_SIZE or hashlib.sha256(rom).hexdigest() != CLEAN_SHA256:
        raise ValueError("exact verified clean ROM required")
    with (ROOT / "translation/codepage/vi_codepage_v4_fe4_native.csv").open(
            encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    cp = {r["unicode"]: r for r in rows}
    if len(rows) != 160 or len(cp) != 160:
        raise ValueError("expected exactly 160 existing codepage entries")
    additions = extra_chars(cp)
    custom = {int(r["glyph_id_hex"], 16)
              for r in rows if r["glyph_source"] == "custom"}
    native = {r["visual_key"] for r in rows if r["glyph_source"] == "native"}
    if len([r for r in rows if r["glyph_source"] == "native"]) != 32:
        raise ValueError("unexpected native row count")
    if len(custom) != 126:
        raise ValueError("unexpected custom-cell count")
    # Verify every existing custom cell on CLEAN source is blank and unused
    # in the original ROM's mapping region. These cells are RESERVED, not free.
    audit = rom[0x29756:0x2B380]
    for gid in sorted(custom):
        if gid >> 8 >= 10 or gid & 255 >= 100:
            raise ValueError(f"out-of-range custom gid {gid:04X}")
        if gid.to_bytes(2, "little") in audit:
            raise ValueError(f"native mapping references custom gid {gid:04X}")
        ix = gid & 255
        for y in range(12):
            for x in range(12):
                px = 12 * (ix % 10) + x
                py = 12 * (ix // 10) + y
                offset = 0x128000 + (gid >> 8) * 0x800 + py * 16 + px // 8
                if rom[offset] & (0x80 >> (px & 7)):
                    raise ValueError(f"native ink in custom gid {gid:04X}")
    for a, z in (FONT_PAGE, PTR_STAGING, LEAD_STAGING):
        if any(x != 0xFF for x in rom[a:z]):
            raise ValueError(f"candidate storage not all FF at {a:06X}..{z:06X}")
    if rom[0x28EA8:0x28EAC] != bytes.fromhex("BF EE 95 85"):
        raise ValueError("font pointer table consumer changed")
    if rom[0x29760:0x29762] != bytes.fromhex("74 9A"):
        raise ValueError("original lead 0x85 was not a 0x84 alias")
    if rom[0x295EE:0x295F1] != bytes.fromhex("00 80 A5"):
        raise ValueError("first font page pointer changed")
    # 32 native codepage ROWS + 52 new characters = at most 84 cells.
    # The other 128 custom rows occupy their own existing reserved cells.
    needed = len(native) + len(additions)
    if needed > 100:
        raise ValueError("more than one 100-cell page required")
    extension = {ch: f"85{0x40+i:02X}" for i, ch in enumerate(additions)}
    if len(set(extension.values())) != 52 or any(len(bytes.fromhex(v)) != 2 for v in extension.values()):
        raise ValueError("invalid two-byte extension")
    return {
        "status": "READ_ONLY_FEASIBILITY_PASS_NOT_A_ROM_BUILD",
        "rom_unchanged": True, "runtime_status": "UNTESTED", "build_ready": False,
        "existing_entries": 160, "reserved_custom_rows": 128,
        "reserved_custom_unique_slots": 126, "native_rows": 32,
        "new_capitals": 49, "new_lowercase": 3,
        "new_glyphs": 52, "page10_needed_max": needed,
        "page10_cell_capacity": 100,
        "candidate_blank_font_page": "0x125000..0x1257FF ($A4:D000)",
        "candidate_blank_pointer_stage": "0x2F800..0x2F820 ($85:F800)",
        "candidate_blank_lead_map": "0x2FA00..0x2FA67 ($85:FA00)",
        "new_85xx_codepoints": extension,
        "blockers": [
            "No proof that original Japanese text never uses 0x85xx lead",
            "FF-only storage check does not prove indirect pointer reachability safety",
            "Page 0x0A glyph access not yet tested in emulator",
            "Proposed table relocation and 9px diagnostic require runtime testing",
            "9px must be enabled only for suitable Vietnamese glyphs before release",
        ],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("clean_rom", type=Path)
    ap.add_argument("report", type=Path)
    args = ap.parse_args()
    if args.clean_rom.resolve() == args.report.resolve():
        raise ValueError("report must not overwrite input ROM")
    rom = args.clean_rom.read_bytes()
    report = check_clean(rom)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items()
                      if k != "new_85xx_codepoints"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
