#!/usr/bin/env python3
"""Build a guarded Probe008 V2 FONT-ONLY experimental ROM from exact Probe003.

This does NOT change spacing and is NOT release-ready. Emulator testing remains
mandatory. No commercial ROM is included in this repository.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from audit_g2_probe008_font_expansion import check_clean
from repair_g2_probe008_full_font import extra_chars

ROOT = Path(__file__).resolve().parent.parent
BASE_SHA256 = "5208bec10147f478cc17955c4f262a5cde08e5b85708caa2717370f6835fbacd"
FONT_FILE = ROOT / "translation/codepage/g2_probe008_complete_candidate_v2.json"
PAGE10 = 0x125000
PAGEPTR_STAGE = 0x2F800
NEW_LEAD_MAP = 0x2FA00
EXISTING_PAGE_TABLE = 0x295EE
EXISTING_84_TABLE = 0x29A74
LEAD85_PTR = 0x29760
RENDERER_PAGEPTR_INSN = 0x28EA8
RENDERER_PAGEPTR_BANK_INSN = 0x28EAE
TABLE_MAP_NEXT_START = 0x29BE8
CHECKSUM_OFF = 0x7FDC
TEXT_RECORDS = (0x181CE, 0x18247, 0x182C0)


def slot_bytes(gid: int, page10: bool = False):
    page, cell = gid >> 8, gid & 255
    if cell >= 100 or (page10 and page != 10) or (not page10 and page >= 10):
        raise ValueError(f"out-of-range glyph {gid:04X}")
    start = PAGE10 if page10 else 0x128000 + page * 0x800
    x0, y0 = (cell % 10) * 12, (cell // 10) * 12
    for i in range(144):
        x, y = x0 + (i % 12), y0 + i // 12
        yield start + y * 16 + x // 8, 0x80 >> (x % 8)


def install_cell(rom: bytearray, gid: int, hx: str) -> set[int]:
    raw = bytes.fromhex(hx)
    if len(raw) != 18:
        raise ValueError(f"bad font glyph {gid:04X}")
    locations = list(slot_bytes(gid, gid >> 8 == 10))
    touched = set()
    for i, (off, mask) in enumerate(locations):
        before = rom[off]
        if raw[i // 8] & (0x80 >> (i % 8)):
            rom[off] |= mask
        else:
            rom[off] &= 0xFF ^ mask
        if rom[off] != before:
            touched.add(off)
    return touched


def read_cell(rom: bytes, gid: int) -> bytes:
    n = 0
    for off, mask in slot_bytes(gid, gid >> 8 == 10):
        n = (n << 1) | int(bool(rom[off] & mask))
    return n.to_bytes(18, "big")


def build(clean: bytes, probe003: bytes, font: dict) -> tuple[bytes, dict]:
    static = check_clean(clean)  # validates all original 126 reserved custom cells
    if len(probe003) != 0x200000 or hashlib.sha256(probe003).hexdigest() != BASE_SHA256:
        raise ValueError("exact strict-2-byte Probe003 required")
    for a, z in ((PAGE10, PAGE10+0x800), (PAGEPTR_STAGE, PAGEPTR_STAGE+0x21),
                 (NEW_LEAD_MAP, NEW_LEAD_MAP+0x180)):
        if any(byte != 0xFF for byte in probe003[a:z]):
            raise ValueError(f"reserved stage modified by Probe003: {a:06X}")
    if probe003[RENDERER_PAGEPTR_INSN:RENDERER_PAGEPTR_INSN+4] != bytes.fromhex("BF EE 95 85"):
        raise ValueError("unexpected low-word page pointer lookup")
    if probe003[RENDERER_PAGEPTR_BANK_INSN:RENDERER_PAGEPTR_BANK_INSN+4] != bytes.fromhex("BF EF 95 85"):
        raise ValueError("unexpected shifted high-bank page pointer lookup")
    with (ROOT / "translation/codepage/vi_codepage_v4_fe4_native.csv").open(
            encoding="utf-8", newline="") as f:
        codepage = {r["unicode"]: r for r in csv.DictReader(f)}
    extras = extra_chars(codepage)
    if set(font) != set(codepage) | set(extras) or len(font) != 212:
        raise ValueError("complete font entries do not match canonical 160 + 52")
    native_visual = sorted({r["visual_key"] for r in codepage.values()
                            if r["glyph_source"] == "native"})
    if len(native_visual) != 32:
        raise ValueError("expected exactly 32 new-page native copies")
    new_gid = {visual: 0x0A00+i for i, visual in enumerate(native_visual)}
    for j, ch in enumerate(extras, start=len(native_visual)):
        new_gid[ch] = 0x0A00+j
    if len(native_visual) + len(extras) != 84 or max(new_gid.values()) != 0x0A53:
        raise ValueError("out of one-page glyph capacity")
    old = bytes(probe003)
    data = bytearray(old)
    allowed = set()
    # New bitmap page must be zeroed before drawing.
    data[PAGE10:PAGE10+0x800] = bytes(0x800)
    allowed.update(range(PAGE10, PAGE10+0x800))
    # Expand original ten three-byte pointers through a ROM-internal 11-entry
    # array (no original pointer table or BCD lookup overwrite).
    old_ptrs = bytes(data[EXISTING_PAGE_TABLE:EXISTING_PAGE_TABLE+30])
    if old_ptrs[:3] != bytes.fromhex("00 80 A5"):
        raise ValueError("first native font pointer mismatch")
    data[PAGEPTR_STAGE:PAGEPTR_STAGE+33] = old_ptrs + bytes.fromhex("00 D0 A4")
    allowed.update(range(PAGEPTR_STAGE, PAGEPTR_STAGE+33))
    data[RENDERER_PAGEPTR_INSN:RENDERER_PAGEPTR_INSN+4] = bytes.fromhex("BF 00 F8 85")
    allowed.update(range(RENDERER_PAGEPTR_INSN, RENDERER_PAGEPTR_INSN+4))
    data[RENDERER_PAGEPTR_BANK_INSN:RENDERER_PAGEPTR_BANK_INSN+4] = bytes.fromhex("BF 01 F8 85")
    allowed.update(range(RENDERER_PAGEPTR_BANK_INSN, RENDERER_PAGEPTR_BANK_INSN+4))
    # Dedicated new mapping array, do not reuse 84E1+ native-owned mappings.
    data[NEW_LEAD_MAP:NEW_LEAD_MAP+0x180] = bytes(0x180)
    allowed.update(range(NEW_LEAD_MAP, NEW_LEAD_MAP+0x180))
    data[LEAD85_PTR:LEAD85_PTR+2] = bytes.fromhex("00 FA")
    allowed.update(range(LEAD85_PTR, LEAD85_PTR+2))
    owners = {}
    entries = {}
    for ch, row in codepage.items():
        visual = row["visual_key"]
        gid = (new_gid[visual] if row["glyph_source"] == "native"
               else int(row["glyph_id_hex"], 16))
        code = font[ch]["code_hex"]
        if code.upper() != row["code_hex"].upper() or not code.startswith("84"):
            raise ValueError(f"original 2-byte mapping reassigned: {ch}")
        off = EXISTING_84_TABLE + (int(code[2:], 16)-0x40)*2
        if not EXISTING_84_TABLE <= off < TABLE_MAP_NEXT_START - 1:
            raise ValueError(f"original mapping overlaps other lead: {ch}")
        data[off:off+2] = gid.to_bytes(2, "little")
        allowed.update((off, off+1))
        bitmap = font[ch]["bitmap_hex"]
        prev = owners.setdefault(gid, bitmap)
        if prev != bitmap:
            raise ValueError(f"bitmap collision for aliased gid 0x{gid:04X}")
        entries[ch] = {"code_hex": code, "glyph_id": f"{gid:04X}"}
    for ch in extras:
        code = font[ch]["code_hex"]
        if code != f"85{0x40+extras.index(ch):02X}":
            raise ValueError(f"invalid new 85xx code for {ch}")
        gid = new_gid[ch]
        off = NEW_LEAD_MAP + (int(code[2:],16)-0x40)*2
        data[off:off+2] = gid.to_bytes(2,"little")
        entries[ch] = {"code_hex":code, "glyph_id":f"{gid:04X}"}
        owners[gid] = font[ch]["bitmap_hex"]
    for gid, hx in owners.items():
        allowed.update(install_cell(data, gid, hx))
    for gid, hx in owners.items():
        if read_cell(data, gid) != bytes.fromhex(hx):
            raise AssertionError(f"round-trip glyph bitmap mismatch: {gid:04X}")
    # Fixed Probe003 text framing, D038, scene and audio are all outside whitelist.
    if any(data[o:o+106] != old[o:o+106] for o in TEXT_RECORDS):
        raise AssertionError("2-byte story/demo text changed")
    data[CHECKSUM_OFF:CHECKSUM_OFF+4] = bytes(4)
    checksum = (sum(data)+0x1FE) & 0xFFFF
    data[CHECKSUM_OFF:CHECKSUM_OFF+2] = (checksum ^ 0xFFFF).to_bytes(2,"little")
    data[CHECKSUM_OFF+2:CHECKSUM_OFF+4] = checksum.to_bytes(2,"little")
    allowed.update(range(CHECKSUM_OFF,CHECKSUM_OFF+4))
    changed = {i for i,(a,b) in enumerate(zip(old,data)) if a!=b}
    if changed-allowed:
        raise AssertionError("unauthorized ROM changes: " + str(sorted(changed-allowed)[:12]))
    if ((int.from_bytes(data[CHECKSUM_OFF:CHECKSUM_OFF+2],"little") ^
         int.from_bytes(data[CHECKSUM_OFF+2:CHECKSUM_OFF+4],"little")) != 0xFFFF):
        raise AssertionError("header checksum complement mismatch")
    result = {
        "probe": "G2_PROBE008_V2_FONT_ONLY_EXPERIMENT",
        "input_probe003_sha256": BASE_SHA256,
        "output_sha256": hashlib.sha256(data).hexdigest(),
        "size": len(data), "old_codepage_entries": 160, "new_codepage_entries": 52,
        "unique_written_glyph_ids": len(owners),
        "new_page_cells": len(native_visual)+len(extras),
        "diff_bytes": len(changed), "checksum":f"0x{checksum:04X}",
        "new_85xx_map": entries, "preflight":static["status"],
        "original_story_payloads": "UNCHANGED",
        "spacing": "ORIGINAL 13px (9px is diagnostic only)",
        "runtime_status": "UNTESTED",
        "release_ready": False,
        "unproven": ["0x85 proprietary use", "new page reachability",
                     "font legibility and emulator compatibility"],
    }
    return bytes(data),result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("clean_rom",type=Path)
    ap.add_argument("probe003_rom",type=Path)
    ap.add_argument("output_rom",type=Path)
    ap.add_argument("report_json",type=Path)
    args=ap.parse_args()
    paths=[p.resolve() for p in (args.clean_rom,args.probe003_rom,args.output_rom,args.report_json)]
    if len(set(paths))!=4:
        raise ValueError("source, output and report paths must differ")
    font=json.loads(FONT_FILE.read_text(encoding="utf-8"))
    rom,report=build(args.clean_rom.read_bytes(),args.probe003_rom.read_bytes(),font)
    args.output_rom.parent.mkdir(parents=True,exist_ok=True)
    args.output_rom.write_bytes(rom)
    args.report_json.parent.mkdir(parents=True,exist_ok=True)
    args.report_json.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"STATIC EXPERIMENT ONLY | sha256={report['output_sha256']} | diff={report['diff_bytes']}")
    print("RUNTIME=UNTESTED; NOT RELEASE-READY; NEVER COMMIT ROM")


if __name__=="__main__":
    main()
