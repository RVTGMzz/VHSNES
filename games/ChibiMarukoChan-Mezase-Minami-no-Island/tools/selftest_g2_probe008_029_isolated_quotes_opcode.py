#!/usr/bin/env python3
"""Independent opcode-subset QA for 029 G2-only quote aliases.

Tests 1,100 valid glyph IDs × 19 columns × 2 X widths × 2 font
lookup hooks = 83,600 executions of actual generated 65816 stubs.
Static only, NOT a SNES emulator. Protect original 8175/8176 as 13px.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from build_g2_probe008_029_isolated_quotes_diagnostic import (
    BASE_SHA, OUTPUT_SHA, G2_STARTS, build,
    compact_word_hook, compact_shift_hook,
)
from build_g2_probe008_v3_medium_geometry9_experiment import code_to_gid
from selftest_g2_probe008_geometry9_opcode_028 import emulate


def compact(gid):
    return (0x083A <= gid < 0x0864 or
            0x090A <= gid < 0x0964 or
            0x0A00 <= gid < 0x0A56)


def audit(raw):
    if len(raw) != 0x200000 or hashlib.sha256(raw).hexdigest() != BASE_SHA:
        raise ValueError("exact 028 combined input required")
    output, build_report = build(raw)
    if hashlib.sha256(output).hexdigest() != OUTPUT_SHA:
        raise AssertionError("unexpected 029 identity")
    word, shift = compact_word_hook(), compact_shift_hook()
    if output[0x2FB80:0x2FB80+len(word)] != word:
        raise AssertionError("word stub not identical to generated code")
    if output[0x2FD00:0x2FD00+len(shift)] != shift:
        raise AssertionError("shift stub not identical to generated code")
    count = 0
    for page in range(11):
        for cell in range(100):
            gid = (page<<8) | cell
            use9 = compact(gid)
            for col in range(19):
                x = 4 + (9 if use9 else 13)*col
                for is_x8 in (False,True):
                    got, addr = emulate(word,0x85FB80,output,gid,col,is_x8,True)
                    if (got,addr) != (16*(x//8),0x85FC80 if use9 else 0x859670):
                        raise AssertionError(f"WORD mismatch {gid:04X} {col} {is_x8}")
                    count += 1
                    got, addr = emulate(shift,0x85FD00,output,gid,col,is_x8,False)
                    if (got,addr) != (x%8,0x85FCC0 if use9 else 0x859696):
                        raise AssertionError(f"SHIFT mismatch {gid:04X} {col} {is_x8}")
                    count += 1
    if count != 83600:
        raise AssertionError("incomplete 65816 subset coverage")
    for code,gid in (("8175",0x0159),("8176",0x015A)):
        if code_to_gid(output,code)!=gid or compact(gid):
            raise AssertionError("Japanese original quotation glyph accidentally compact")
    for code,gid in (("8574",0x0A54),("8575",0x0A55)):
        if code_to_gid(output,code)!=gid or not compact(gid):
            raise AssertionError("G2-only quote alias missing 9px treatment")
    for first in G2_STARTS:
        original=raw[first:first+106]
        current=output[first:first+106]
        if len(current)!=106:
            raise AssertionError("G2 length changed")
        expected=bytearray(original)
        expected=expected.replace(bytes.fromhex("8175"),bytes.fromhex("8574"))
        expected=expected.replace(bytes.fromhex("8176"),bytes.fromhex("8575"))
        if expected!=current:
            raise AssertionError("modified G2 content beyond exactly the two quote codepairs")
        for i in (32,68,104):
            if current[i:i+2]!=bytes.fromhex("816F"):
                raise AssertionError("G2 line controls changed")
    return {
        "status":"029_OPCODE_SUBSET_PASS_NOT_EMULATOR",
        "source_sha256":BASE_SHA,"rom_sha256":OUTPUT_SHA,
        "opcode_cases":count, "original_native_quote_ids_13px":["0159","015A"],
        "G2_alias_quote_ids_9px":["0A54","0A55"],
        "G2_original_strict_two_byte_record_size":106,
        "G2_two_quote_codepairs_per_record":True,
        "G2_control_816F_preserved":True,
        "checkpoint025_user_runtime":"FAIL",
        "SNES_runtime":"NOT_TESTED","release_ready":False,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("exact_028_combined_rom",type=Path)
    p.add_argument("out_report",type=Path)
    a=p.parse_args()
    if a.exact_028_combined_rom.resolve()==a.out_report.resolve():
        p.error("never overwrite source ROM")
    result=audit(a.exact_028_combined_rom.read_bytes())
    a.out_report.parent.mkdir(parents=True,exist_ok=True)
    a.out_report.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
