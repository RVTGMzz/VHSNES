#!/usr/bin/env python3
"""Audit 65c816 SNES Quiz WRAM destination overlap BEFORE 81-choice patch.

Bank06 65c816 source copy reads 66 bytes, but the original three answer
destination buffers begin at WRAM $7E8000, $7E8020 and $7E8040:
ONLY 32 bytes between answer starts. Option 2 overwrites bytes 32..65 of
option 1; option 3 overwrites bytes 32..65 of option 2. This is distinct
from original-ROM BANK padding safety established in checkpoint073.

The full Vietnamese answers are left unchanged in canonical CSVs. This tool
does not shorten names, write binaries, or claim emulator-visible QA.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from plan_quiz_bankcopy_slots_073 import plan as plan_source

ROOT=Path(__file__).resolve().parent.parent
COPIED_BYTES=66
WRAM_STRIDE=0x20
DESTINATIONS=("0x7E8000","0x7E8020","0x7E8040")

def run(root:Path,clean:bytes|None=None):
    source=plan_source(root,clean)
    options=source["slots"]
    if len(options)!=81:
        raise AssertionError("Original pending answer count drift")
    risky=[]
    for item in options:
        length=int(item["record_size"])
        ordinal=int(item["answer_ordinal"])
        if length>WRAM_STRIDE:
            overrun=length-WRAM_STRIDE
            risky.append({
                "original_text_ROM":item["source_offset"],
                "pointer_table_slot":item["pointer_table_slot"],
                "answer_ordinal":ordinal,
                "full_canonical_Vietnamese":item["source_full_vietnamese"],
                "native_record_bytes":length,
                "extra_bytes_past_32_byte_slot":overrun,
                "next_choice_copy_guaranteed_to_overwrite":ordinal in (1,2),
            })
    overwritten=[x for x in risky if x["next_choice_copy_guaranteed_to_overwrite"]]
    last_choice=[x for x in risky if x["answer_ordinal"]==3]
    if (len(risky)!=29 or len(overwritten)!=18 or len(last_choice)!=11
        or max(x["native_record_bytes"] for x in risky)!=53):
        raise AssertionError("Canonical Quiz native 32-byte WRAM spill count changed")

    # Original SNES 65c816 answer routines, verified by 073 in exact SFC,
    # render text from buffers with start pointers 0x8000, 0x8020, 0x8040.
    # A long option 1/2 cannot retain its entire record after following copy.
    # Option 3 has no following overwrite, but its >32B width / memory
    # safety is still untested in the real SNES renderer.
    return {"summary":{
        "status":"FAIL_CLOSED_ROM_SOURCE_SAFE_BUT_WRAM_STRIDE_UNSAFE_FOR_ALL_81",
        "pending_full_answer_candidates":len(options),
        "native_fixed_copy_bytes":COPIED_BYTES,
        "native_WRAM_stride_bytes":WRAM_STRIDE,
        "native_WRAM_destination_starts":DESTINATIONS,
        "source_66_byte_windows_nonoverlap_in_ROM":True,
        "canonical_full_answers_exceeding_32_byte_WRAM_stride":len(risky),
        "original_answer_1_or_2_records_overwritten_by_next_copy":len(overwritten),
        "original_answer_3_records_larger_than_32_byte_stride":len(last_choice),
        "largest_full_answer_record_bytes":53,
        "safe_to_release_81_full_answer_patch":False,
        "requires_WRAM_buffer_layout_or_engine_change":True,
        "actual_SNES_emulator_tested":False,
        "patch_or_ROM_emitted":False,
    },"definite_choice_1_or_2_buffer_overwrites":overwritten,
      "long_choice_3_additional_visual_width_risks":last_choice}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project-root",type=Path,default=ROOT)
    ap.add_argument("--original-rom",type=Path)
    ap.add_argument("--report",type=Path)
    a=ap.parse_args()
    if a.original_rom and a.report and a.original_rom.resolve()==a.report.resolve():
        ap.error("Do not overwrite original Japanese ROM")
    report=run(a.project_root,a.original_rom.read_bytes() if a.original_rom else None)
    if a.report:
        a.report.parent.mkdir(parents=True,exist_ok=True)
        a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",
                            encoding="utf-8")
    print(json.dumps(report["summary"],ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
