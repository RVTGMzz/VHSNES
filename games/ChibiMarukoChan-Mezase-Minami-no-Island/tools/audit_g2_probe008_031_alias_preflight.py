#!/usr/bin/env python3
"""Preflight G2-only quote alias 8574/8575 capacity on exact clean + V2 ROM.

Requires zero-valued 85 lead entries, two physically empty 12x12 cells,
exact original quote mapping and precisely structured G2 text. Read-only;
raw byte-pair counts are NOT native parser reachability proof.
"""
import argparse
import hashlib
import json
from pathlib import Path

CLEAN="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
V2="2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd"
FIELDS=(0x181CE,0x18247,0x182C0)

def mapped_id(rom,code):
    high,low=bytes.fromhex(code)
    p=int.from_bytes(rom[0x29756+2*(high-0x80):0x29758+2*(high-0x80)],"little")
    off=0x28000+(p&0x7FFF)+2*(low-0x40)
    return int.from_bytes(rom[off:off+2],"little")

def glyph_pixels(rom,gid):
    page,cell=gid>>8,gid&255
    if page>10 or cell>99:
        raise ValueError("invalid 12x12 bitmap slot")
    pp=rom[0x2F800+3*page:0x2F803+3*page]
    base=(pp[2]&127)*0x8000+(int.from_bytes(pp[:2],"little")&0x7FFF)
    ox=(cell%10)*12
    oy=(cell//10)*12
    return tuple(bool(rom[base+(oy+y)*16+(ox+x)//8]&(0x80>>((ox+x)%8)))
                 for y in range(12) for x in range(12))

def audit(clean,rom):
    for label,data,sha in (("clean",clean,CLEAN),("V2",rom,V2)):
        if len(data)!=0x200000 or hashlib.sha256(data).hexdigest()!=sha:
            raise ValueError(f"exact {label} ROM SHA/size required")
    if [mapped_id(rom,x) for x in ("8175","8176")]!=[0x0159,0x015A]:
        raise AssertionError("original Japanese quote glyph mapping differs")
    if [mapped_id(rom,x) for x in ("8574","8575")]!=[0,0]:
        raise AssertionError("proposed 85 alias map entries are occupied")
    if any(any(glyph_pixels(rom,g)) for g in (0x0A54,0x0A55)):
        raise AssertionError("target quote font cell contains pixels")
    if not all(any(glyph_pixels(rom,g)) for g in (0x0159,0x015A)):
        raise AssertionError("source native quote glyph is empty")
    if rom[0x2FA68:0x2FA6C]!=bytes(4):
        raise AssertionError("quote aliases not mapped to empty zero entries")
    if rom[0x2F81E:0x2F821]!=bytes.fromhex("00D0A4"):
        raise AssertionError("expanded page 0A pointer invalid")
    records=[]
    for off in FIELDS:
        original=clean[off:off+106]
        data=rom[off:off+106]
        pairs=[data[i:i+2].hex().upper() for i in range(0,106,2)]
        if [i for i,c in enumerate(pairs) if c=="816F"] != [16,34,52]:
            raise AssertionError("strict G2 line controls changed")
        if pairs.count("8175")!=1 or pairs.count("8176")!=1:
            raise AssertionError("expected exactly one opening and closing quote")
        if any(c in ("8574","8575") for c in pairs):
            raise AssertionError("alias was already present")
        if original==data:
            raise AssertionError("input V2 contains no restored Vietnamese dialogue")
        records.append({"file_offset":f"0x{off:06X}","quote_pairs_ready":2,
                        "control_indices":[16,34,52]})
    counts={}
    for code in ("8574","8575"):
        b=bytes.fromhex(code)
        total=sum(clean[i:i+2]==b for i in range(len(clean)-1))
        in_story=sum(clean[i:i+2]==b for i in range(0x18000,0x20000-1))
        counts[code]={"all_ROM_raw_byte_pairs":total,"Story_bank_raw_byte_pairs":in_story}
    expected={"8574":{"all_ROM_raw_byte_pairs":13,"Story_bank_raw_byte_pairs":0},
              "8575":{"all_ROM_raw_byte_pairs":6,"Story_bank_raw_byte_pairs":0}}
    if counts!=expected:
        raise AssertionError("original clean ROM alias byte inventory changed")
    return {
        "status":"STATIC_029_ALIAS_PREFLIGHT_PASS",
        "exact_clean_sha256":CLEAN,"exact_v2_font_only_sha256":V2,
        "original_quote_ids":["0159","015A"],
        "target_G2_only_code_pairs":["8574","8575"],
        "target_G2_only_glyph_ids":["0A54","0A55"],
        "original_quote_font_cells_untouched":True,
        "target_alias_font_cells_blank":True,
        "original_records":records,
        "candidate_raw_pair_occurrences":counts,
        "full_game_reachability":"UNPROVEN",
        "029_emulator_test":"NOT_PERFORMED",
        "release_ready":False,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("clean_rom",type=Path)
    p.add_argument("v2_font_only_rom",type=Path)
    p.add_argument("report_json",type=Path)
    a=p.parse_args()
    paths=(a.clean_rom,a.v2_font_only_rom,a.report_json)
    if len({x.resolve() for x in paths})!=3:
        p.error("source and output paths must be distinct")
    result=audit(a.clean_rom.read_bytes(),a.v2_font_only_rom.read_bytes())
    a.report_json.parent.mkdir(parents=True,exist_ok=True)
    a.report_json.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
