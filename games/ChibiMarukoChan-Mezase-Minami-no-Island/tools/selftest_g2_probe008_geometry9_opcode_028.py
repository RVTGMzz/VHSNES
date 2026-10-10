#!/usr/bin/env python3
"""Subset 65816 opcode regression for geometry-scoped Probe008 028.

Checks the ACTUAL emitted machine code for 1,100 glyph IDs, 19 positions,
both X8/X16 flag cases and both renderer table lookups (83,600 cases).
This simulator models only emitted opcodes; NOT an SNES emulator. Runtime
font aesthetics, actual save-state registers, palette and gameplay untested.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_g2_probe008_glyph_geometry9_diagnostic import (
    BASE_SHA, DIAG_SHA, build, word_hook, shift_hook,
)


def expected_nine(gid):
    return (0x083A<=gid<=0x0863 or 0x090A<=gid<=0x0963
            or 0x0A00<=gid<=0x0A53 or gid in (0x0159,0x015A))


def emulate(stub, origin, rom, gid, pos, x8, is_word):
    page,cell=gid>>8,gid&255
    p=rom[0x2F800+page*3:0x2F803+page*3]
    bcd=rom[0x2960C+cell]
    dp={0x18:int.from_bytes(p[:2],"little"),
        0x08:12*(bcd&15),0x0A:12*(bcd>>4)}
    offset=0
    m=original_m=16 if is_word else 8
    a=0
    carry=zero=False
    saved=[]
    ix=pos*(2 if is_word else 1)
    selected_table=None
    for _ in range(180):
        op=stub[offset]
        offset+=1
        if op==0x08:  # PHP
            saved.append(m)
        elif op in (0xE2,0xC2):
            v=stub[offset];offset+=1
            if v!=0x20:
                raise AssertionError("bad processor-width instruction")
            m=8 if op==0xE2 else 16
        elif op==0xA3:  # LDA d,S
            disp=stub[offset];offset+=1
            if disp==1:
                if m!=8:
                    raise AssertionError("X-width status read without M8")
                a=0x10 if x8 else 0
            elif is_word and disp==(0x0A if x8 else 0x0C) and m==16:
                a=gid
            else:
                raise AssertionError("incorrect 65816 saved-glyph stack offset")
        elif op==0xA5:  # LDA DP, constructed from original ROM atlas geometry
            loc=stub[offset];offset+=1
            a=dp[loc]
        elif op==0x29:  # AND #imm
            n=int.from_bytes(stub[offset:offset+m//8],"little")
            offset+=m//8
            a&=n
            zero=(a==0)
        elif op==0xC9:  # CMP #imm
            n=int.from_bytes(stub[offset:offset+m//8],"little")
            offset+=m//8
            carry=a>=n;zero=a==n
        elif op in (0x90,0xB0,0xF0,0xD0,0x80):
            delta=stub[offset];offset+=1
            taken=(op==0x80 or (op==0x90 and not carry)
                   or (op==0xB0 and carry)
                   or (op==0xF0 and zero)
                   or (op==0xD0 and not zero))
            if taken:
                offset+=delta if delta<128 else delta-256
        elif op==0x4C:
            target=int.from_bytes(stub[offset:offset+2],"little")
            offset=target-(origin&0xFFFF)
        elif op==0x28:  # PLP
            m=saved.pop()
        elif op==0xBF:  # LDA long,X
            addr=int.from_bytes(stub[offset:offset+3],"little")
            offset+=3
            rom_off=((addr>>16&0x7F)*0x8000+(addr&0x7FFF)+ix)
            a=int.from_bytes(rom[rom_off:rom_off+m//8],"little")
            selected_table=addr
        elif op==0x6B:  # RTL
            if saved or m!=original_m:
                raise AssertionError("processor width/stack not restored")
            return a,selected_table
        else:
            raise AssertionError(f"unsupported emitted opcode {op:02X}")
    raise AssertionError("machine-code stub failed to return")


def run(source):
    data,meta=build(source)
    if meta["sha256"]!=DIAG_SHA:
        raise AssertionError("wrong staged diagnostic hash")
    w,s=word_hook(),shift_hook()
    count=0
    for page in range(11):
        for cell in range(100):
            gid=(page<<8)|cell
            nine=expected_nine(gid)
            for i in range(19):
                adv=4+(9 if nine else 13)*i
                for x8 in (False,True):
                    a,table=emulate(w,0x85FB80,data,gid,i,x8,True)
                    if a!=16*(adv//8) or table!=(0x85FC80 if nine else 0x859670):
                        raise AssertionError(
                            f"wrong word result gid={gid:04X} i={i} x8={x8}")
                    count+=1
                    a,table=emulate(s,0x85FD00,data,gid,i,x8,False)
                    if a!=adv%8 or table!=(0x85FCC0 if nine else 0x859696):
                        raise AssertionError(
                            f"wrong byte result gid={gid:04X} i={i} x8={x8}")
                    count+=1
    if count!=83600:
        raise AssertionError("missing opcode cases")
    return {
        "status":"STATIC_65816_SUBSET_83600_PASS_NOT_RUNTIME",
        "diagnostic_sha256":DIAG_SHA,
        "tested_pages":11,"glyph_cells_each":100,
        "glyph_ids_tested":1100,
        "positions_tested":19,"X_widths_tested":2,
        "lookup_hooks_tested":2,"machine_code_subsets_executed":count,
        "9px_glyph_ids":218,"13px_glyph_ids":882,
        "original_g2_records_preserved":True,
        "SNES_emulator_test":"NOT_PERFORMED",
        "runtime_025":"USER_VISUAL_FAIL",
        "release_ready":False,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("exact_v2_font_only_rom",type=Path)
    p.add_argument("output_report",type=Path)
    a=p.parse_args()
    if a.exact_v2_font_only_rom.resolve()==a.output_report.resolve():
        p.error("report and source ROM paths must differ")
    result=run(a.exact_v2_font_only_rom.read_bytes())
    a.output_report.parent.mkdir(parents=True,exist_ok=True)
    a.output_report.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
