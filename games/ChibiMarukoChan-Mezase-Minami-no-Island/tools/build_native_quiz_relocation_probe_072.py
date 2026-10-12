#!/usr/bin/env python3
"""Native-Japanese Quiz relocation smoke test; requires NO Vietnamese font/043 IPS.

Creates a 70-byte IPS from the user's exact original Japanese 2MiB SNES ROM.
It moves 2 answer choices in the first two POINTER-TABLE SLOTS, not guaranteed
the first two questions shown in gameplay. This is a non-release emulator test,
NOT a Vietnamese translation and NOT proof that the game follows pointers.
ROM bytes are NEVER written to disk.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from build_content_first_040_fortune import make_ips, apply_ips

CLEAN_SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
EXPECTED_ROM_SHA="fae23a8f7744313e5977b44eaeaeaf6177bdcd7312c78b671a30851b6599e2ee"
EXPECTED_IPS_SHA="3d29135ff3712b4d8ee74b0afb690ec852a1537b3a713ac22866a734f8cc44ea"
PREFIX=b"\x0e\x06\x0f\x12"
END=b"\x81\x6f\x00"
CASES=(
    (0,0x31217,0x320fb,"３０円","３０円です",0x37000),
    (1,0x31219,0x32273,"７６才","７６才です",0x37040),
)

def digest(blob:bytes)->str:
    return hashlib.sha256(blob).hexdigest()

def build(clean:bytes):
    if len(clean)!=0x200000 or digest(clean)!=CLEAN_SHA:
        raise ValueError("Exact clean unheadered Japanese 2MiB Chibi SFC required")
    if clean[0x36907:0x38000]!=b"\xff"*5881:
        raise AssertionError("Original end-of-bank Quiz padding changed")

    data=bytearray(clean)
    whitelist=set(range(0x7fdc,0x7fe0))
    choices=[]
    for slot,pointer,source,old,new,relocated in CASES:
        old_cp=old.encode("cp932")
        new_cp=new.encode("cp932")
        if not new.startswith(old) or len(new_cp)<=len(old_cp):
            raise AssertionError("Diagnostic must truly expand native Japanese choice")
        original_pointer=0x8000+(source-4-0x30000)
        new_pointer=0x8000+(relocated-0x30000)
        if not (0x8000<=original_pointer<=0xffff and 0x8000<=new_pointer<=0xffff):
            raise AssertionError("Original/new locations do not fit bank06 pointer")
        if (clean[pointer:pointer+2]!=original_pointer.to_bytes(2,"little")
            or clean[source-4:source]!=PREFIX
            or clean[source:source+len(old_cp)]!=old_cp
            or clean[source+len(old_cp):source+len(old_cp)+3]!=END):
            raise AssertionError(f"Original Quiz pointer/answer changed at {source:05X}")
        record=PREFIX+new_cp+END
        target=set(range(relocated,relocated+len(record)))
        if (target & whitelist or
            clean[relocated:relocated+len(record)]!=b"\xff"*len(record)):
            raise AssertionError("Probe would overwrite original bank data")
        whitelist.update(target)
        whitelist.update(range(pointer,pointer+2))
        data[pointer:pointer+2]=new_pointer.to_bytes(2,"little")
        data[relocated:relocated+len(record)]=record
        choices.append({"pointer_slot_zero_based":slot,
            "original_text_ROM":f"0x{source:X}",
            "pointer_word_ROM":f"0x{pointer:X}",
            "new_record_ROM":f"0x{relocated:X}",
            "original_native_choice":old,"longer_native_choice":new,
            "emulator_render_accepted":False})
    data[0x7fdc:0x7fe0]=bytes(4)
    checksum=(sum(data)+0x1fe)&0xffff
    data[0x7fdc:0x7fde]=(checksum^0xffff).to_bytes(2,"little")
    data[0x7fde:0x7fe0]=checksum.to_bytes(2,"little")
    result=bytes(data)
    diff={i for i,(a,b) in enumerate(zip(clean,result)) if a!=b}
    if diff-whitelist or len(diff)!=42:
        raise AssertionError("Unexpected changed bytes outside two Quiz choices, pointers and checksum")
    for _,_,source,old,_,_ in CASES:
        beg=source-4
        original_len=4+len(old.encode("cp932"))+3
        if result[beg:beg+original_len]!=clean[beg:beg+original_len]:
            raise AssertionError("Original inline Japanese text was not preserved")
    patch,records=make_ips(clean,result)
    if (len(patch)!=70 or records!=4 or checksum!=0xFBAC or
        digest(result)!=EXPECTED_ROM_SHA or digest(patch)!=EXPECTED_IPS_SHA or
        apply_ips(clean,patch)!=result):
        raise AssertionError("Exact original retail ROM/IPS SHA or checksum no longer matches")

    return patch,{"status":"NATIVE_JAPANESE_QUIZ_POINTER_RELOCATION_STATIC_ONLY",
        "original_ROM_SHA256":CLEAN_SHA,"result_ROM_SHA256_if_applied":EXPECTED_ROM_SHA,
        "IPS_SHA256":EXPECTED_IPS_SHA,"IPS_bytes":len(patch),
        "IPS_records":records,"changed_original_ROM_bytes":len(diff),
        "SNES_checksum":f"0x{checksum:04X}","choices":choices,
        "original_inplace_choice_text_preserved":True,
        "all_changes_whitelisted":True,"exact_IPS_replay":True,
        "uses_original_Japanese_game_only":True,
        "pointer_slots_not_guaranteed_to_match_initial_gameplay_question_order":True,
        "emulator_tested":False,"vietnamese_translation_complete":False,
        "release_approved":False}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("original_clean_Japanese_sfc",type=Path)
    ap.add_argument("--ips",type=Path,required=True)
    ap.add_argument("--report",type=Path,required=True)
    ap.add_argument("--allow-untested",action="store_true")
    args=ap.parse_args()
    if not args.allow_untested:
        ap.error("No emulator test yet: explicitly pass --allow-untested")
    if args.ips.suffix.lower()!=".ips" or args.report.suffix.lower()!=".json":
        ap.error("Outputs must be .ips and .json")
    paths=(args.original_clean_Japanese_sfc,args.ips,args.report)
    if len({p.resolve() for p in paths})!=len(paths):
        ap.error("Input and output files must differ")
    ips,report=build(args.original_clean_Japanese_sfc.read_bytes())
    args.ips.parent.mkdir(parents=True,exist_ok=True)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.ips.write_bytes(ips)
    args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
