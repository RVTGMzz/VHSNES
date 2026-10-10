#!/usr/bin/env python3
"""INDEPENDENT checker for Probe008 V2 FONT-ONLY experimental ROM.

This is intentionally separate from the builder. Static verification is not
emulator validation; game release readiness remains FALSE.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLEAN_SHA256 = "e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
PROBE003_SHA256 = "5208bec10147f478cc17955c4f262a5cde08e5b85708caa2717370f6835fbacd"
FONT = ROOT / "translation/codepage/g2_probe008_complete_candidate_v2.json"
CSV = ROOT / "translation/codepage/vi_codepage_v4_fe4_native.csv"
STAGE_PAGE = 0x125000
STAGE_PTR = 0x2F800
STAGE_MAP = 0x2FA00
MAP84 = 0x29A74


def ink_from_rom(rom: bytes, gid: int) -> bytes:
    page = gid >> 8
    cell = gid & 0xFF
    if not (0 <= page <= 10 and 0 <= cell < 100):
        raise ValueError("invalid page/cell ID")
    base = STAGE_PAGE if page == 10 else 0x128000 + page * 0x800
    bits = 0
    for y in range(12):
        for x in range(12):
            px = 12 * (cell % 10) + x
            py = 12 * (cell // 10) + y
            off = base + py * 16 + (px // 8)
            bits = (bits << 1) | bool(rom[off] & (0x80 >> (px & 7)))
    return bits.to_bytes(18, "big")


def bitmap_allowed_offsets(gid: int) -> set[int]:
    cell = gid & 255
    page = gid >> 8
    base = STAGE_PAGE if page == 10 else 0x128000 + 0x800 * page
    x0 = (cell % 10) * 12
    y0 = (cell // 10) * 12
    return {base + (y0+y)*16 + (x0+x)//8 for y in range(12) for x in range(12)}


def verify(clean: bytes, before: bytes, after: bytes) -> dict:
    if len(clean) != 0x200000 or hashlib.sha256(clean).hexdigest() != CLEAN_SHA256:
        raise ValueError("incorrect clean ROM identity")
    if len(before) != 0x200000 or hashlib.sha256(before).hexdigest() != PROBE003_SHA256:
        raise ValueError("incorrect Probe003 identity")
    if len(after) != 0x200000:
        raise ValueError("ROM length changed")
    cp = list(csv.DictReader(CSV.open(encoding="utf-8", newline="")))
    font = json.loads(FONT.read_text(encoding="utf-8"))
    if len(cp) != 160 or len(font) != 212:
        raise AssertionError("codepage coverage mismatch")
    cp_by_char = {r["unicode"]: r for r in cp}
    extras = sorted(set(font) - set(cp_by_char))
    if len(extras) != 52 or len([r for r in cp if r["glyph_source"] == "native"]) != 32:
        raise AssertionError("expected 52 additions and 32 native copies")
    native_visuals = sorted({r["visual_key"] for r in cp if r["glyph_source"] == "native"})
    if len(native_visuals) != 32:
        raise AssertionError("native glyph alias count changed")
    designated = {ch: 0x0A00 + i for i, ch in enumerate(native_visuals)}
    # Sorting Unicode for the missing 49 uppercase, then appended ằ/ẵ/ỵ.
    additions = [ch for ch in extras if ch not in ("ằ", "ẵ", "ỵ")] + ["ằ", "ẵ", "ỵ"]
    designated.update({ch: 0x0A20 + i for i, ch in enumerate(additions)})
    allow = set(range(STAGE_PAGE, STAGE_PAGE+0x800))
    allow.update(range(STAGE_PTR, STAGE_PTR+33))
    allow.update(range(STAGE_MAP, STAGE_MAP+0x180))
    allow.update(range(0x7FDC,0x7FE0))
    allow.update(range(0x29760,0x29762))
    for address in (0x28EA8, 0x28EAD):
        allow.update(range(address,address+4))
    expected_ptrs = before[0x295EE:0x295EE+30] + bytes.fromhex("00D0A4")
    if after[STAGE_PTR:STAGE_PTR+33] != expected_ptrs:
        raise AssertionError("expanded page pointer array incorrect")
    if after[0x28EA8:0x28EAC] != bytes.fromhex("BF00F885"):
        raise AssertionError("low-word pointer lookup not relocated")
    if after[0x28EAD:0x28EB1] != bytes.fromhex("BF01F885"):
        raise AssertionError("bank-byte pointer lookup not relocated")
    if after[0x29760:0x29762] != bytes.fromhex("00FA"):
        raise AssertionError("new 0x85 lead pointer not relocated")
    if after[0x295EE:0x295EE+30] != before[0x295EE:0x295EE+30]:
        raise AssertionError("original 10-page table overwritten")
    if any(a != b for a,b in zip(before[0x29670:0x296A9], after[0x29670:0x296A9])):
        raise AssertionError("spacing differs from original 13px")
    gid_bitmaps: dict[int, str] = {}
    for row in cp:
        ch = row["unicode"]
        code = font[ch]["code_hex"]
        if code.upper() != row["code_hex"].upper() or not code.upper().startswith("84"):
            raise AssertionError(f"existing codepoint corrupted: {ch!r}")
        gid = (designated[row["visual_key"]] if row["glyph_source"] == "native"
               else int(row["glyph_id_hex"],16))
        off = MAP84 + (int(code[2:],16)-0x40)*2
        allow.update((off,off+1))
        if int.from_bytes(after[off:off+2],"little") != gid:
            raise AssertionError(f"wrong 0x84 mapping: {ch!r}")
        prev = gid_bitmaps.setdefault(gid,font[ch]["bitmap_hex"])
        if prev != font[ch]["bitmap_hex"]:
            raise AssertionError(f"shared cell conflict: {ch!r}")
    for i,ch in enumerate(additions):
        code = font[ch]["code_hex"]
        if code.upper() != f"85{0x40+i:02X}":
            raise AssertionError(f"wrong new unit for {ch}")
        gid = designated[ch]
        off = STAGE_MAP+2*i
        if int.from_bytes(after[off:off+2],"little") != gid:
            raise AssertionError(f"wrong extension mapping: {ch!r}")
        gid_bitmaps[gid] = font[ch]["bitmap_hex"]
    if len(gid_bitmaps) != 210:
        raise AssertionError(f"unexpected physical glyph count: {len(gid_bitmaps)}")
    for gid,hx in gid_bitmaps.items():
        if ink_from_rom(after,gid) != bytes.fromhex(hx):
            raise AssertionError(f"pixel mismatch at glyph ID {gid:04X}")
        if gid >> 8 != 10:
            allow.update(bitmap_allowed_offsets(gid))
    for off in (0x181CE,0x18247,0x182C0):
        old=before[off:off+106]
        if after[off:off+106]!=old:
            raise AssertionError(f"original Probe003 text framing changed at {off:06X}")
        if [i for i in range(0,105) if old[i:i+2]==bytes.fromhex("816F")] != [32,68,104]:
            raise AssertionError(f"strict 2-byte separator offsets corrupted at {off:06X}")
    checksum_data = bytearray(after)
    checksum_data[0x7FDC:0x7FE0] = bytes(4)
    calc = (sum(checksum_data)+0x1FE)&0xFFFF
    ck = int.from_bytes(after[0x7FDE:0x7FE0],"little")
    complement = int.from_bytes(after[0x7FDC:0x7FDE],"little")
    if ck != calc or (ck ^ complement) != 0xFFFF:
        raise AssertionError("independent SNES checksum invalid")
    changes = {i for i,(a,b) in enumerate(zip(before,after)) if a!=b}
    outliers = changes-allow
    if outliers:
        raise AssertionError("unexpected ROM diff bytes: "+str([hex(i) for i in sorted(outliers)[:16]]))
    return {
        "verification": "STATIC_PASS_ONLY",
        "runtime": "UNTESTED", "release_ready": False,
        "clean_sha256": CLEAN_SHA256,
        "probe003_sha256": PROBE003_SHA256,
        "patched_sha256": hashlib.sha256(after).hexdigest(),
        "changed_bytes": len(changes),
        "mapped_codepoints": 212,
        "unique_physical_glyphs": len(gid_bitmaps),
        "new_11th_page_cells": 84,
        "source_text_records_unchanged": True,
        "original_13px_pitch_unchanged": True,
        "both_page_ptr_lookups_relocated": True,
        "checksum": f"0x{ck:04X}",
        "unproven": ["page0x0A emulator path", "0x85 proprietary use", "typography / full gameplay"],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("clean_rom",type=Path)
    ap.add_argument("probe003_rom",type=Path)
    ap.add_argument("probe008_candidate",type=Path)
    ap.add_argument("report_json",type=Path)
    args=ap.parse_args()
    paths=[x.resolve() for x in (
        args.clean_rom,args.probe003_rom,args.probe008_candidate,args.report_json)]
    if len(set(paths))!=4:
        raise ValueError("do not overwrite source or result with verification report")
    report=verify(args.clean_rom.read_bytes(),args.probe003_rom.read_bytes(),
                  args.probe008_candidate.read_bytes())
    args.report_json.parent.mkdir(parents=True,exist_ok=True)
    args.report_json.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
