#!/usr/bin/env python3
"""ROM-free executable simulation of the original three-choice Quiz WRAM copy.

Uses the exact canonical Vietnamese source files + original V2 codepage,
and models the three sequential 65c816 66-byte writes into $7E8000,
$7E8020 and $7E8040. Staged choices not in this experimental batch
receive a short neutral fixture. This is NOT a full SNES emulator. The 075 disassembly shows the game
WAITS between choice copies for the text job to finish. Therefore this
simulation's after-all-three-copies RAM damage cannot be interpreted as
guaranteed *onscreen* corruption.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from build_quiz_relocated_81_074 import (
    read_codepage, encode_full, PREFIX, TERMINATOR,
)
from plan_quiz_bankcopy_slots_073 import plan

ROOT=Path(__file__).resolve().parent.parent
ORIGINAL_DEST_STRIDE=32
NATIVE_COPY_BYTES=66
SHORT_FIXTURE=PREFIX+b"\x82\x60\x82\x61"+TERMINATOR

def run(root:Path):
    source=plan(root)
    choices=source["slots"]
    mapping=read_codepage(root)
    slots={}
    for item in choices:
        key=(int(item["pointer_table_slot"]),int(item["answer_ordinal"])-1)
        if key in slots:
            raise AssertionError("Duplicate original answer table entry")
        original=int(item["source_offset"],16)
        payload,_=encode_full(item["source_full_vietnamese"],mapping,original)
        record=PREFIX+payload+TERMINATOR
        if len(record)!=item["record_size"] or len(record)>NATIVE_COPY_BYTES:
            raise AssertionError("Native Quiz source record drift")
        slots[key]=(original,item["source_full_vietnamese"],record)
    if len(slots)!=81:
        raise AssertionError("Wrong number of original pending choice addresses")

    corrupted=[]
    intact=[]
    for question in range(50):
        ram=bytearray(b"\xff"*160)
        for ordinal in range(3):
            original,caption,record=slots.get(
                (question,ordinal),(None,"fixture",SHORT_FIXTURE))
            if len(record)>NATIVE_COPY_BYTES:
                raise AssertionError("Bad source copy width")
            block=record+b"\x00"*(NATIVE_COPY_BYTES-len(record))
            start=ordinal*ORIGINAL_DEST_STRIDE
            ram[start:start+NATIVE_COPY_BYTES]=block
        for ordinal in range(3):
            if (question,ordinal) not in slots:
                continue
            off,caption,record=slots[(question,ordinal)]
            start=ordinal*ORIGINAL_DEST_STRIDE
            kept=(bytes(ram[start:start+len(record)])==record)
            entry={"original_source_offset":f"0x{off:X}",
                   "pointer_slot":question,"answer_ordinal":ordinal+1,
                   "full_vietnamese":caption,"full_native_record_bytes":len(record)}
            (intact if kept else corrupted).append(entry)
    if (len(intact)!=63 or len(corrupted)!=18 or
        any(i["answer_ordinal"]==3 for i in corrupted) or
        any(x["full_native_record_bytes"]<=ORIGINAL_DEST_STRIDE for x in corrupted)):
        raise AssertionError("Actual WRAM successive 66-byte copy overwrite counts changed")
    # Distinguish 52 truly stride-bounded records vs 11 third-answers
    # that survive the three writes but exceed the assumed 32-byte area.
    stride_safe=[x for x in intact if x["full_native_record_bytes"]<=ORIGINAL_DEST_STRIDE]
    third_long=[x for x in intact if x["full_native_record_bytes"]>ORIGINAL_DEST_STRIDE]
    if len(stride_safe)!=52 or len(third_long)!=11:
        raise AssertionError("Actual safe + third-choice risky record split drift")
    return {"status":"PASS_ROM_FREE_REAL_WRAM_COPY_OVERWRITE_SIMULATION",
            "actual_original_65c816_WRAM_copy_starts":[0,32,64],
            "per_choice_native_copy_bytes":66,
            "canonical_source_choices_simulated":len(choices),
            "truly_stride_safe_texts":len(stride_safe),
            "choice_1_or_2_buffer_bytes_changed_IF_render_deferred":len(corrupted),
            "real_65816_waits_for_text_job_to_complete_before_next_copy":True,
            "choice_3_long_and_not_next_copy_overwritten":len(third_long),
            "release_all_81_full_labels_safe":False,
            "SNES_emulator_executed":False,
            "corrupted_records":corrupted}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-root",type=Path,default=ROOT)
    p.add_argument("--report",type=Path)
    a=p.parse_args()
    result=run(a.project_root)
    if a.report:
        a.report.parent.mkdir(parents=True,exist_ok=True)
        a.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="corrupted_records"},
                     ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
