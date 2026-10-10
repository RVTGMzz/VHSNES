#!/usr/bin/env python3
"""Combine medium V3 bitmap proposal with 028 glyph-geometry diagnostic.

LOCAL EXPERIMENT, NOT A GAMEPLAY-PASSED ROM. Original 32 native page-0A
glyphs stay bit-identical; codepage, source text and graphics unchanged.
Allows only custom font atlas cells and checksum writes on top of exact
028 geometry diagnostic. Requires the repository V3 data generator.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from propose_g2_probe008_v3_medium_font import build as propose_v3

BASE_SHA = "2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd"
GEOM_SHA = "a3d2e75da5f9dac36750ef77e249fae7613ffd35f8185c50cd6f6197ca8a8688"
COMBINED_SHA = "59f4c45b14a24e6cf67de1c9c7cbe1d9b862eaa2eb4c6518bbc4bcbd6dd006fb"


def code_to_gid(rom, hx):
    lead, trail = bytes.fromhex(hx)
    if lead not in (0x84,0x85):
        raise ValueError("unknown Vietnamese codepage lead")
    address = int.from_bytes(rom[0x29756+2*(lead-0x80):
                                 0x29758+2*(lead-0x80)], "little")
    off = 0x28000 + (address&0x7FFF)+2*(trail-0x40)
    return int.from_bytes(rom[off:off+2], "little")


def pixels(raw):
    return {(i%12,i//12) for i in range(144)
            if raw[i//8] & (0x80>>(i%8))}


def area(rom, gid):
    page, cell=gid>>8, gid&255
    if not (0<=page<=10 and 0<=cell<100):
        raise ValueError("invalid physical glyph")
    pp=rom[0x2F800+3*page:0x2F803+3*page]
    off=((pp[2]&0x7F)*0x8000 +
         (int.from_bytes(pp[:2], "little")&0x7FFF))
    return off,12*(cell%10),12*(cell//10)


def read_glyph(rom, gid):
    base,x0,y0=area(rom,gid)
    value=0
    for y in range(12):
        for x in range(12):
            px=x0+x
            off=base+(y0+y)*16+px//8
            value=(value<<1) | bool(rom[off]&(0x80>>(px%8)))
    return value.to_bytes(18,"big")


def write_glyph(rom, gid, desired):
    base,x0,y0=area(rom,gid)
    ink=pixels(desired)
    for y in range(12):
        for x in range(12):
            px=x0+x
            off=base+(y0+y)*16+px//8
            mask=0x80>>(px%8)
            if (x,y) in ink:
                rom[off]|=mask
            else:
                rom[off]&=255^mask


def build(source_v2: bytes, geometry_rom: bytes):
    if (len(source_v2)!=0x200000 or
        hashlib.sha256(source_v2).hexdigest()!=BASE_SHA):
        raise ValueError("source must be exact 028 V2 font-only ROM")
    if (len(geometry_rom)!=0x200000 or
        hashlib.sha256(geometry_rom).hexdigest()!=GEOM_SHA):
        raise ValueError("diagnostic must have independently staged 028 geometry hash")

    candidate,proposal_report=propose_v3(source_v2)
    if len(candidate)!=212 or proposal_report["ink_overlap_pairs"]!=0:
        raise AssertionError("V3 font proposal incomplete or colliding")
    original={}
    modified={}
    native=set()
    for char,row in candidate.items():
        gid=code_to_gid(source_v2,row["code_hex"])
        before=read_glyph(source_v2,gid)
        native_glyph=(row["code_hex"].startswith("84") and gid>>8==10)
        new=bytes.fromhex(row["bitmap_hex"])
        if native_glyph:
            native.add(gid)
            if before!=new:
                raise AssertionError("original native glyph altered")
        if gid in modified and modified[gid]!=new:
            raise AssertionError(f"shared glyph ID has conflicting variants: {gid:04X}")
        original[gid]=before
        modified[gid]=new
    if len(modified)!=210 or len(native)!=32:
        raise AssertionError("font ownership expectations changed")
    changed_ids={i for i,b in modified.items() if b!=original[i]}
    if len(changed_ids)!=178:
        raise AssertionError("wrong number of modified physical glyphs")

    out=bytearray(geometry_rom)
    for gid in changed_ids:
        write_glyph(out,gid,modified[gid])
    for gid,bm in modified.items():
        if read_glyph(out,gid)!=bm:
            raise AssertionError(f"ROM atlas bitmap mismatch {gid:04X}")

    for off in (0x181CE,0x18247,0x182C0):
        if out[off:off+106]!=geometry_rom[off:off+106]:
            raise AssertionError("G2 source text changed")
    for lo,hi in ((0x29670,0x296A9),(0x29756,0x29776),
                  (0x28E0C,0x28E10),(0x290EE,0x290F2)):
        if out[lo:hi]!=geometry_rom[lo:hi]:
            raise AssertionError(f"renderer codepage / geometry touched: {lo:06X}")
    out[0x7FDC:0x7FE0]=bytes(4)
    checksum=(sum(out)+0x1FE)&0xFFFF
    out[0x7FDC:0x7FDE]=(checksum^0xFFFF).to_bytes(2,"little")
    out[0x7FDE:0x7FE0]=checksum.to_bytes(2,"little")

    allowed=(set(range(0x125000,0x125800)) |
             set(range(0x12C000,0x12D000)) |
             set(range(0x7FDC,0x7FE0)))
    differences={i for i,(a,b) in enumerate(zip(geometry_rom,out)) if a!=b}
    if differences-allowed:
        raise AssertionError("changed bytes outside font and checksum regions")
    if len(differences)!=1183:
        raise AssertionError("unexpected font atlas diff size")
    digest=hashlib.sha256(out).hexdigest()
    if digest!=COMBINED_SHA:
        raise AssertionError("combined ROM does not match independent experiment")

    # Collision calculation uses physical glyph IDs, excluding aliases.
    glyphs=[pixels(bm) for bm in modified.values()]
    collision_count=sum(bool(a & {(x+9,y) for x,y in b})
                        for a in glyphs for b in glyphs)
    if collision_count:
        raise AssertionError(f"9px collision in {collision_count} physical pairs")
    return bytes(out), {
        "status":"EXPERIMENTAL_COMBINED_ROM_STATIC_ONLY",
        "rom_sha256":digest,
        "geometry_sha256":GEOM_SHA,
        "custom_glyphs_changed":len(changed_ids),
        "native_glyphs_unchanged":len(native),
        "bytes_changed_vs_geometry":len(differences),
        "checksum":f"0x{checksum:04X}",
        "complement":f"0x{checksum^0xFFFF:04X}",
        "ink_pixels":sum(map(len,glyphs)),
        "ordered_pair_checks":len(glyphs)**2,
        "overlaps":collision_count,
        "real_emulator_execution":"NOT_TESTED",
        "release_ready":False,
        "previous_025":"USER_RUNTIME_VISUAL_FAIL",
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("exact_v2_font_only_rom",type=Path)
    p.add_argument("exact_028_geometry_rom",type=Path)
    p.add_argument("output_combined_ROM",type=Path)
    p.add_argument("output_report",type=Path)
    p.add_argument("--allow-untested-diagnostic",action="store_true")
    a=p.parse_args()
    if not a.allow_untested_diagnostic:
        p.error("this ROM has NOT PASSED gameplay; opt in explicitly for static experiments")
    paths=(a.exact_v2_font_only_rom,a.exact_028_geometry_rom,
           a.output_combined_ROM,a.output_report)
    if len({x.resolve() for x in paths})!=4:
        p.error("inputs and outputs must have distinct paths")
    result,report=build(a.exact_v2_font_only_rom.read_bytes(),
                        a.exact_028_geometry_rom.read_bytes())
    a.output_combined_ROM.parent.mkdir(parents=True,exist_ok=True)
    a.output_combined_ROM.write_bytes(result)
    a.output_report.parent.mkdir(parents=True,exist_ok=True)
    a.output_report.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",
                               encoding="utf-8")
    print(json.dumps(report,indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
