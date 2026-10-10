#!/usr/bin/env python3
"""Read-only G2 direct call-graph and M16 glyph provenance audit.

Uses exact clean and recovered V2 ROMs. Counts direct JSL/JSR byte
signatures, validates actual parser M16 reset and renderer entry.
Not a whole-ROM disassembler, no indirect-call reachability proof, and
not a SNES runtime test. Deliberately never writes a ROM.
"""
import argparse
import hashlib
import json
from pathlib import Path

CLEAN="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
V2="2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd"

def hits(blob, needle, first=0, end=None):
    found=[]
    pos=first
    end=len(blob) if end is None else end
    while True:
        pos=blob.find(needle,pos,end)
        if pos<0:
            return found
        found.append(pos)
        pos+=1

def check_core(original, font):
    for name, needle, wanted in (
        ("parser_JSL_renderer", bytes.fromhex("227B8E85"), [0x28413]),
        ("renderer_JSL_helper", bytes.fromhex("22058E85"), [0x28E83]),
    ):
        found=hits(original,needle)
        if found!=wanted or hits(font,needle)!=wanted:
            raise AssertionError(f"unexpected direct callers for {name}: {found}")
    # Only same-bank JSRs in the $85 ROM bank could target $85:8E05 / 8E7B.
    for name, needle in (
        ("JSR_renderer", bytes.fromhex("207B8E")),
        ("JSR_helper", bytes.fromhex("20058E")),
    ):
        found=hits(original,needle,0x28000,0x30000)
        if found:
            raise AssertionError(f"unexpected direct {name}: {found}")
    selector=bytes.fromhex("E220A9858504C220")
    if original[0x283F3:0x283FB]!=selector or font[0x283F3:0x283FB]!=selector:
        raise AssertionError("cannot establish 16-bit A before mapped glyph load")
    code=bytes.fromhex("B702AC9A1F8410AC9C1F8412227B8E85")
    if original[0x28407:0x28417]!=code or font[0x28407:0x28417]!=code:
        raise AssertionError("renderer not reached directly from mapped glyph load")
    for address, expected in (
        (0x28E7B,"8BDA5A48AFB21F0022058E85"),
        (0x28E05,"DA5AA8A5100AAABF709685"),
        (0x290EC,"A610BF969685"),
    ):
        b=bytes.fromhex(expected)
        if original[address:address+len(b)]!=b or font[address:address+len(b)]!=b:
            raise AssertionError(f"renderer machine code altered at {address:06X}")
    if font[0x28EA8:0x28EAC]!=bytes.fromhex("BF00F885"):
        raise AssertionError("V2 font pointer low-word relocation lost")
    if font[0x28EAE:0x28EB2]!=bytes.fromhex("BF01F885"):
        raise AssertionError("V2 font pointer bank-byte relocation lost")

def audit(original, font):
    if len(original)!=len(font) or len(original)!=0x200000:
        raise ValueError("both ROM inputs must have exact unheadered 2MiB length")
    if hashlib.sha256(original).hexdigest()!=CLEAN:
        raise ValueError("incorrect clean ROM SHA-256")
    if hashlib.sha256(font).hexdigest()!=V2:
        raise ValueError("incorrect V2 font-only ROM SHA-256")
    check_core(original,font)
    mutants=(0x28413,0x28E83,0x283F3,0x283F8,0x28407,0x28E7B,0x28E05)
    for address in mutants:
        broken=bytearray(font)
        broken[address]^=1
        try:
            check_core(original,broken)
        except AssertionError:
            continue
        raise AssertionError(f"corruption undetected at {address:06X}")
    return {
        "status":"STATIC_DIRECT_CALL_GRAPH_PASS",
        "clean_rom_sha256":CLEAN,
        "v2_font_only_sha256":V2,
        "parser_direct_renderer_JSL":["0x28413"],
        "renderer_direct_helper_JSL":["0x28E83"],
        "within_bank85_direct_JSR_to_renderer_or_helper":0,
        "glyph_A_16bit_evidence":"REP #$20 in parser before LDA [$02],Y and renderer JSL",
        "negative_instruction_mutations_rejected":len(mutants),
        "limitation":"Bytewise direct call signatures and straight-line M16 proof only; indirect calls and CPU runtime untraced",
        "025_user_runtime_typography":"FAIL",
        "029_emulator_runtime":"NOT_TESTED",
        "release_ready":False,
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("clean_rom",type=Path)
    ap.add_argument("v2_font_only_rom",type=Path)
    ap.add_argument("report_json",type=Path)
    args=ap.parse_args()
    paths=(args.clean_rom,args.v2_font_only_rom,args.report_json)
    if len({p.resolve() for p in paths})!=3:
        ap.error("input/output paths must all be distinct")
    report=audit(args.clean_rom.read_bytes(),args.v2_font_only_rom.read_bytes())
    args.report_json.parent.mkdir(parents=True,exist_ok=True)
    args.report_json.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
