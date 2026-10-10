#!/usr/bin/env python3
"""Read-only Probe008 030 font-renderer stack/atlas audit on exact clean SNES ROM.

Proves code signatures and symbolic call-frame layout only. DOES NOT run
emulator, confirm live M/X flags, certify original quote/85 lead safety,
or claim checkpoint029 gameplay passed. No ROM writes or game assets.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

SHA = "e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
ANCHORS = {
    "parser_lead_dispatch": (0x283D8, "C9 A5 81 D0 04 A6 46 D0 36 EB 85 00 29 FF 00 38 E9 80 00 0A AA BF 56 97 85 85 02 E2 20 A9 85 85 04 C2 20"),
    "parser_glyph_call": (0x28407, "B7 02 AC 9A 1F 84 10 AC 9C 1F 84 12 22 7B 8E 85"),
    "renderer_prologue": (0x28E7B, "8B DA 5A 48 AF B2 1F 00 22 05 8E 85"),
    "helper_prologue": (0x28E05, "DA 5A A8 A5 10 0A AA BF 70 96 85"),
    "renderer_bank_switch": (0x28E87, "68 85 02 29 FF 00 AA BF 0C 96 85 29 FF 00 F4 00 7F AB AB"),
    "page_pointer_lookup": (0x28E9A, "85 00 A5 02 EB 29 0F 00 85 18 0A 65 18 AA BF EE 95 85 85 18 BF EF 95 85 85 19"),
    "atlas_x": (0x28EB4, "A5 00 29 0F 00 0A 0A 85 02 0A 65 02 85 08"),
    "atlas_y": (0x28EC2, "A5 00 29 F0 00 4A 85 00 4A 65 00 85 0A"),
    "shift_lookup": (0x290EC, "A6 10 BF 96 96 85 85 00"),
}


def check_signatures(rom: bytes) -> None:
    for name,(off,hex_bytes) in ANCHORS.items():
        signature=bytes.fromhex(hex_bytes)
        if rom[off:off+len(signature)] != signature:
            raise AssertionError(f"original renderer code differs at {name}: {off:06X}")
    for off,expect in ((0x28E0C,"BF 70 96 85"),(0x290EE,"BF 96 96 85")):
        if rom[off:off+4]!=bytes.fromhex(expect):
            raise AssertionError(f"original 13px lookup changed at {off:06X}")
    bcd=bytes((i//10)*16+(i%10) for i in range(100))
    if rom[0x2960C:0x29670] != bcd:
        raise AssertionError("original packed-decimal atlas lookup changed")
    if rom[0x295F1:0x295F4] != bytes.fromhex("00 88 A5"):
        raise AssertionError("native quote font page pointer unexpectedly changed")


def stack_frame(x_bytes: int) -> dict:
    # Symbolic stack layout derived from code signature:
    # renderer PHB;PHX;PHY;PHA; JSL helper; helper PHX;PHY;
    # word lookup patched JSL; hook PHP. Glyph A saved by renderer PHA.
    stacked=[]
    def push(name, size):
        stacked[:0]=[name+str(n) for n in range(size)]
    for name,n in (("DBR",1),("renderer_X",x_bytes),
                   ("renderer_Y",x_bytes),("glyph_A",2),
                   ("JSL_helper_return",3),("helper_X",x_bytes),
                   ("helper_Y",x_bytes),("JSL_hook_return",3),
                   ("PHP_saved_status",1)):
        push(name,n)
    offsets=[i+1 for i,s in enumerate(stacked) if s.startswith("glyph_A")]
    if len(offsets)!=2 or offsets[1]!=offsets[0]+1:
        raise AssertionError("saved glyph A is not a two-byte stack word")
    return {"X_width_bits":x_bytes*8,
            "assuming_renderer_M_16":True,
            "glyph_low_byte_stack_offset":offsets[0],
            "glyph_high_byte_stack_offset":offsets[1],
            "first_nine_stack_slots":[{"S_offset":i+1,"byte":s}
                                      for i,s in enumerate(stacked[:9])]}


def native_quotes(clean: bytes) -> list[dict]:
    bank,word=0xA5,0x8800
    base=(bank&0x7F)*0x8000+(word&0x7FFF)
    output=[]
    for glyph,cell in ((0x0159,89),(0x015A,90)):
        ox=(cell%10)*12;oy=(cell//10)*12
        dots=set()
        for y in range(12):
            for x in range(12):
                pixel=ox+x
                off=base+(oy+y)*16+pixel//8
                if clean[off]&(0x80>>(pixel%8)):
                    dots.add((x,y))
        output.append({"glyph_id":f"{glyph:04X}","pixels":len(dots),
                       "left":min(x for x,y in dots),
                       "right":max(x for x,y in dots)})
    return output


def audit(data: bytes) -> dict:
    if len(data)!=0x200000 or hashlib.sha256(data).hexdigest()!=SHA:
        raise ValueError("exact 2MiB unheadered clean ROM SHA-256 required")
    check_signatures(data)
    x8=stack_frame(1);x16=stack_frame(2)
    if (x8["glyph_low_byte_stack_offset"],
        x16["glyph_low_byte_stack_offset"]) != (10,12):
        raise AssertionError("unexpected actual glyph PHA stack offset")
    return {"status":"READ_ONLY_STATIC_65816_FRAME_PASS",
            "exact_clean_rom_sha256":SHA,
            "checked_original_code_anchors":len(ANCHORS),
            "word_lookup_rom_offset":"0x28E0C",
            "shift_lookup_rom_offset":"0x290EE",
            "original_call_frames":[x8,x16],
            "native_quote_glyph_shape":native_quotes(data),
            "original_13px_tables_preserved":True,
            "checkpoint025_user_real_typography":"FAIL",
            "checkpoint029_sn es_runtime".replace(" ",""):"NOT_TESTED",
            "runtime_stack_modes_verified":False,
            "emulator_execution":False,"release_ready":False}


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exact_clean_rom",type=Path)
    parser.add_argument("report_json",type=Path)
    parser.add_argument("--negative-tests",action="store_true",
                        help="prove original-code signatures fail on 9 mutated sites")
    args=parser.parse_args()
    if args.exact_clean_rom.resolve()==args.report_json.resolve():
        parser.error("never overwrite ROM with report")
    raw=args.exact_clean_rom.read_bytes()
    result=audit(raw)
    if args.negative_tests:
        for off,_ in ANCHORS.values():
            damaged=bytearray(raw)
            damaged[off]^=1
            try:
                check_signatures(damaged)
            except AssertionError:
                continue
            raise AssertionError(f"mutated code not detected at {off:06X}")
        result["nine_opcode_mutations_rejected"]=len(ANCHORS)
    args.report_json.parent.mkdir(parents=True,exist_ok=True)
    args.report_json.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",
                                encoding="utf-8")
    print(json.dumps(result,indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
