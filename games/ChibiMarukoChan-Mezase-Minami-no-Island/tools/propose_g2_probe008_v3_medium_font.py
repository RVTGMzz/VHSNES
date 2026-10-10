#!/usr/bin/env python3
"""Generate a V3 MEDIUM-WEIGHT bitmap proposal from exact Probe008 V2 ROM.

PURE DATA: writes UTF-8 JSON + QA report; it NEVER modifies/exports a ROM.
32 originally-native glyphs relocated to page 0x0A are frozen byte-for-byte.
The other 178 physical glyphs receive a single right-hand body pixel where
safe. Stacked accents are unchanged (y<=3), avoiding new tone collisions.
A pairwise test checks 210 x 210 glyph combinations at proposed 9px pitch.
This does NOT prove runtime rendering, DBR, or real-game readability.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANONICAL = ROOT / "translation/codepage/g2_probe008_complete_candidate_v2.json"
SOURCE_ROM_SHA = "2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd"
NATIVE_PAGE = 0x0A
PIXELS = 12 * 12


def points(raw: bytes) -> set[tuple[int,int]]:
    if len(raw) != 18:
        raise ValueError("glyph must have 18 bytes")
    return {(i % 12, i // 12) for i in range(PIXELS)
            if raw[i//8] & (0x80 >> (i%8))}


def packed(coords: set[tuple[int,int]]) -> bytes:
    if any(not (0 <= x < 12 and 0 <= y < 12) for x,y in coords):
        raise ValueError("pixel would escape 12x12 cell")
    return sum(1 << (143-(y*12+x)) for x,y in coords).to_bytes(18,"big")


def medium(raw: bytes, protected_native: bool) -> bytes:
    if protected_native:
        return raw
    old = points(raw)
    # Body only: never widen the isolated tone marks above row y=4.
    new = old | {(x+1,y) for x,y in old if y >= 4 and x <= 8}
    return packed(new)


def read_gid(rom: bytes, code: str) -> int:
    high,low=bytes.fromhex(code)
    if high not in (0x84,0x85) or not (0x40<=low<=0xFC):
        raise ValueError(f"unexpected codepage character {code}")
    off = 0x29756 + (high-0x80)*2
    tab = int.from_bytes(rom[off:off+2],"little")
    if tab < 0x8000:
        raise AssertionError("codepage lead pointer not mapped to ROM")
    absolute = (0x85 & 0x7F)*0x8000 + (tab & 0x7FFF) + (low-0x40)*2
    return int.from_bytes(rom[absolute:absolute+2],"little")


def extract(rom: bytes, gid: int) -> bytes:
    page, cell=gid>>8,gid&255
    if page>10 or cell>=100:
        raise ValueError(f"glyph page/cell invalid: {gid:04X}")
    # Actual font pointer page bank relocated in V2; page A is $A4:D000.
    base=0x125000 if page==10 else 0x128000 + page*0x800
    col=(cell%10)*12
    row=(cell//10)*12
    out=0
    for y in range(12):
        for x in range(12):
            px=col+x
            off=base+(row+y)*16+px//8
            out=(out<<1)|bool(rom[off] & (0x80>>(px%8)))
    return out.to_bytes(18,"big")


def collision(a: set[tuple[int,int]], b: set[tuple[int,int]], pitch: int) -> bool:
    return bool(a & {(x+pitch,y) for x,y in b})


def build(rom: bytes):
    if len(rom)!=0x200000 or hashlib.sha256(rom).hexdigest()!=SOURCE_ROM_SHA:
        raise ValueError("requires exact Probe008 V2 13px FONT ONLY input")
    canon=json.loads(CANONICAL.read_text(encoding="utf-8"))
    if len(canon)!=212:
        raise AssertionError("expected 212 original codepoints")
    output={}
    by_gid={}
    native=0
    for char,row in canon.items():
        code=row["code_hex"]
        gid=read_gid(rom,code)
        original=extract(rom,gid)
        if original.hex()!=row["bitmap_hex"].lower():
            raise AssertionError(f"original V2 bitmap mismatch: {char} {gid:04X}")
        is_original_native=(int(code[:2],16)==0x84 and (gid>>8)==NATIVE_PAGE)
        updated=medium(original,is_original_native)
        if is_original_native:
            native+=1
        if gid in by_gid and by_gid[gid]!=updated:
            raise AssertionError(f"V2 shared glyph ID {gid:04X} must not diverge")
        by_gid[gid]=updated
        output[char]={**row,"bitmap_hex":updated.hex()}
        if output[char]["code_hex"]!=row["code_hex"]:
            raise AssertionError("font revision must preserve code assignments")
    if len(by_gid)!=210 or native!=32:
        raise AssertionError(f"unexpected glyph ownership: {len(by_gid)}, native={native}")
    ink=[points(b) for b in by_gid.values()]
    clash=sum(collision(a,b,9) for a in ink for b in ink)
    if clash:
        raise AssertionError(f"9px bitmap overlap in {clash} ordered glyph pairs")
    if len(output)!=212:
        raise AssertionError("missing codepoint")
    count_changed=sum(
        1 for char,row in canon.items()
        if row["bitmap_hex"].lower()!=output[char]["bitmap_hex"]
    )
    if count_changed != 180:
        # Alias codepoints may duplicate a changed physical glyph.
        raise AssertionError(f"unexpected changed Unicode mappings {count_changed}")
    report={
        "kind":"FONT_DATA_PROTOTYPE_ONLY",
        "status":"PAIRWISE_9PX_BITMAP_STATIC_PASS",
        "source_sha256":SOURCE_ROM_SHA,
        "codepoints":212,"physical_glyphs":210,
        "native_original_glyphs_preserved":32,
        "codepoints_with_changed_bitmap":count_changed,
        "physical_glyphs_modified":178,
        "pairwise_pitch_px":9,
        "ordered_glyph_pairs_checked":210*210,
        "ink_overlap_pairs":clash,
        "source_total_ink_pixels":sum(len(points(extract(rom,g))) for g in by_gid),
        "v3_total_ink_pixels":sum(map(len,ink)),
        "roman_codepage_assignments_changed":False,
        "rom_modified":False,
        "runtime_qa":"NOT_TESTED",
        "checkpoint025":"USER_RUNTIME_VISUAL_FAIL",
        "release_ready":False
    }
    return output,report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("exact_v2_font_only_rom",type=Path)
    p.add_argument("out_v3_candidate_json",type=Path)
    p.add_argument("out_report_json",type=Path)
    a=p.parse_args()
    paths=(a.exact_v2_font_only_rom,a.out_v3_candidate_json,a.out_report_json)
    if len({f.resolve() for f in paths})!=3:
        p.error("inputs/outputs must all be different files")
    candidate, report=build(a.exact_v2_font_only_rom.read_bytes())
    a.out_v3_candidate_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_v3_candidate_json.write_text(
        json.dumps(candidate,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    a.out_report_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_report_json.write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
