#!/usr/bin/env python3
"""Chibi checkpoint078 — two missed native Quiz explanation fields.

ROM-free: assert that scanner aliases 0x35A69 / 0x33B8D are NOT native field
starts, but are re-anchored at 0x35A58 / 0x33B8A with original pointer
words and approved in-place full Vietnamese text.

Optional original ROM: confirm both real LoROM 16-bit pointers, exact
Japanese CP932 glyph cells, native layout/control markers and source SHA.
No copyrighted ROM/IPS output and no SNES emulator acceptance claimed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from audit_quiz_nonanswers_077 import (
    run as audit_077,REANCHORED_UNSAFE_078,
)
from build_quiz_native_explanations_078 import (
    CLEAN_SHA,RECORDS,LINE_SLOTS,validate_manifest,
)

ROOT=Path(__file__).resolve().parent.parent
EXPECTED_ALIASES={0x35A69,0x33B8D}
EXPECTED_078_POINTERS={0x3136B:0x35A58,0x31453:0x33B8A}

def audit(root:Path,clean:bytes|None=None):
    old=audit_077(root)
    if (old["independent_native_fields_across_077_and_078"]!=3
        or old["further_pointer_reanchored_independent_fields_078"]!=2
        or old["unsafe_scanner_aliases_still_requiring_parent_review"]!=8
        or REANCHORED_UNSAFE_078!=EXPECTED_ALIASES):
        raise AssertionError("077/078 original scanner reconciliation drift")
    manifest=validate_manifest(root)
    if len(manifest["fields"])!=2:
        raise AssertionError("Expected exactly 2 legitimate native 078 records")
    total_native_capacity=sum(c for _,c,_,_ in LINE_SLOTS)
    translated_glyphs=sum(len(vi) for _,c,_,vi in LINE_SLOTS)
    if (total_native_capacity!=39 or translated_glyphs!=33):
        raise AssertionError("078 fixed-width original native glyph capacity changed")
    check_binary=False
    if clean is not None:
        if len(clean)!=0x200000 or hashlib.sha256(clean).hexdigest()!=CLEAN_SHA:
            raise ValueError("Exact original unheadered Japanese 2MiB Chibi SFC required")
        for start,word,ptr,prefix,first in RECORDS:
            actual=int.from_bytes(clean[word:word+2],"little")
            if (actual!=ptr or clean[start:start+4]!=prefix
                or 0x30000+actual-0x8000!=start):
                raise AssertionError(f"078 genuine original field pointer mismatch {start:X}")
        for pos,capacity,japanese,vi in LINE_SLOTS:
            if clean[pos:pos+capacity*2]!=japanese.encode("cp932"):
                raise AssertionError(f"Native Japanese record changed at {pos:X}")
            end=pos+capacity*2
            if clean[end:end+2]!=b"\x81\x6f":
                if not (pos==0x33B94 and clean[end+4:end+6]==b"\x81\x6f"):
                    raise AssertionError(f"Native line marker not preserved at {end:X}")
        check_binary=True
    return {
        "status":"PASS_REANCHORED_TWO_MISSED_ORIGINAL_QUIZ_FIELDS_NOT_EMULATOR",
        "original_japanese_ROM_sha256":CLEAN_SHA,
        "original_scanner_nonanswer_source_rows":21,
        "pointer_addressable_native_fields_from_077_plus_078":3,
        "new_independent_078_explanation_fields":2,
        "native_pointer_ROM_addresses":["0x3136B","0x31453"],
        "original_native_record_starts":["0x35A58","0x33B8A"],
        "source_scanner_offsets_not_real_record_starts":["0x35A69","0x33B8D"],
        "existing_native_capacity_glyphs":total_native_capacity,
        "replaced_full_vietnamese_glyphs":translated_glyphs,
        "existing_native_line_caps_all_respected":all(len(v)<=n for _,n,_,v in LINE_SLOTS),
        "native_ROM_byte_verification_ran":check_binary,
        "SNES_emulator_tested":False,
        "independently_emulator_accepted_extra_items":0,
        "writes_ROM_or_IPS":False,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-root",type=Path,default=ROOT)
    p.add_argument("--original-rom",type=Path)
    p.add_argument("--report",type=Path)
    a=p.parse_args()
    if a.report and a.original_rom and a.report.resolve()==a.original_rom.resolve():
        p.error("Refusing to overwrite the source ROM")
    result=audit(a.project_root,a.original_rom.read_bytes() if a.original_rom else None)
    if a.report:
        a.report.parent.mkdir(parents=True,exist_ok=True)
        a.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
