#!/usr/bin/env python3
"""Chibi SNES Quiz nine parallel 50-question pointer tables — READ ONLY.

Proves source bank 06 has nine 50-word LoROM tables, each with two question-50
sentinels. Tags the 50 question groups, 150 answer pointers, and explanation
references. Never writes a game image, IPS, or claims runtime relocation QA.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from bisect import bisect_right
from collections import Counter
from pathlib import Path
from build_quiz_answer_atlas_065 import analyze as quiz_atlas

ROOT=Path(__file__).resolve().parent.parent
SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
FIRST=0x310DF
STRIDE=0x68
TAGS=("footer_metadata","question_main","question_continuation",
      "answer_1","answer_2","answer_3",
      "explanation_start","explanation_middle","explanation_end")
PREFIX_COUNTS={
    "question_main":{"0e000f0a":50},
    "question_continuation":{"0e000f0e":50},
    "answer_1":{"0e060f12":50},
    "answer_2":{"0e060f12":50},
    "answer_3":{"0e060f12":50},
    "explanation_start":{"0e000f08":49,"0e000f0a":1},
    "explanation_middle":{"0e000f0e":49,"0e000f10":1},
    "explanation_end":{"0e000f14":49,"0e000f16":1},
}


def analyze(clean:bytes,root:Path):
    if len(clean)!=0x200000 or hashlib.sha256(clean).hexdigest()!=SHA:
        raise ValueError("Exact original headerless 2MiB Chibi Japanese ROM required")
    prior=quiz_atlas(clean,root)
    if (prior["summary"]["original_question_blocks"]!=50 or
        prior["summary"]["genuine_three_choice_fields"]!=150):
        raise AssertionError("Native Quiz 065 question inventory drift")
    blocks=prior["blocks"]
    starts=[int(x["original_question_region_start"],16) for x in blocks]
    ends=[int(x["original_footer_at"],16) for x in blocks]
    lookup={}
    groups={}
    headers=Counter()
    reference_rows={}
    reference_order=None
    for ti,kind in enumerate(TAGS):
        table=FIRST+STRIDE*ti
        pointer_values=[]
        references=[]
        ids=[]
        for slot in range(50):
            ptraddr=table+slot*2
            snes=int.from_bytes(clean[ptraddr:ptraddr+2],"little")
            if not 0x8000<=snes<=0xFFFF:
                raise AssertionError(f"Pointer in Quiz table {kind} not bank06 LoROM")
            dest=0x30000+(snes-0x8000)
            qid=bisect_right(starts,dest)-1
            if qid<0 or dest>ends[qid]+23:
                raise AssertionError(f"Quiz table {kind} pointer 0x{dest:X} out of source group")
            qid+=1
            block=blocks[qid-1]
            if ti==0:
                expected=int(block["original_footer_at"],16)+3
                if dest!=expected or clean[dest+5]!=0xC6:
                    raise AssertionError(f"Quiz metadata footer pointer mismatch: {qid}")
            elif ti==1:
                expected=0x31D43 if qid==1 else starts[qid-1]
                if dest!=expected:
                    raise AssertionError(f"Main question entrypoint mismatch: {qid}")
            elif 3<=ti<=5:
                original=int(block["answer_choices"][ti-3]["original_file_offset"],16)
                if dest+4!=original or clean[dest:dest+4]!=b"\x0e\x06\x0f\x12":
                    raise AssertionError(f"Question {qid} original answer choice {ti-2} pointer wrong")
            if ti:
                prefix=clean[dest:dest+4].hex()
                headers[(kind,prefix)]+=1
            pointer_values.append(snes)
            ids.append(qid)
            references.append({
                "question_id":qid,"ordered_slot":slot,
                "pointer_word_offset":f"0x{ptraddr:X}",
                "bank06_CPU_addr":f"0x{snes:04X}",
                "original_ROM_destination":f"0x{dest:X}",
                "native_prefix":clean[dest:dest+4].hex() if ti else "metadata_not_0E_0F",
            })
        if sorted(ids)!=list(range(1,51)):
            raise AssertionError(f"Quiz table {kind} not a permutation of 50 question groups")
        if reference_order is None:
            reference_order=ids
        elif ids!=reference_order:
            raise AssertionError("Parallel question pointer tables are NOT aligned by question")
        if len(set(pointer_values))!=50:
            raise AssertionError(f"Duplicate unsanctioned pointer in table {kind}")
        sentinel_1=int.from_bytes(clean[table+100:table+102],"little")
        sentinel_2=int.from_bytes(clean[table+102:table+104],"little")
        question_50_value=pointer_values[ids.index(50)]
        if sentinel_1!=sentinel_2 or sentinel_1!=question_50_value:
            raise AssertionError(f"Question-50 sentinel bytes differ for table {kind}")
        reference_rows[kind]=references
        groups[kind]={
            "pointer_array_start":f"0x{table:X}",
            "array_end_exclusive":f"0x{table+100:X}",
            "two_16bit_sentinels_at":[f"0x{table+100:X}",f"0x{table+102:X}"],
            "both_sentinels_repeat_question_50":True,
            "pointer_count":50,
            "semantics_confirmed_by_prefix":ti>0,
        }
    for kind,expected in PREFIX_COUNTS.items():
        actual={prefix:c for (label,prefix),c in headers.items() if label==kind}
        if actual!=expected:
            raise AssertionError(f"Original Quiz {kind} presentation code distribution drift: {actual}")
    return {"summary":{
        "status":"PASS_REAL_CLEAN_ROM_NINE_50_WORD_POINTER_ARRAY_SOURCE_QA_ONLY",
        "original_clean_rom_sha256":SHA,
        "pointer_tables":len(TAGS),
        "words_per_table":50,
        "two_tail_sentinel_words_per_table":2,
        "total_16bit_question_entry_references":450,
        "total_verified_question_50_sentinels":18,
        "table_start":"0x310DF",
        "last_table_end_including_two_sentinels":"0x31487",
        "table_stride_bytes":STRIDE,
        "all_nine_orderings_match":True,
        "question_permutation_in_table_order":reference_order,
        "presentation_header_frequencies":dict((t,dict(v)) for t,v in PREFIX_COUNTS.items()),
        "source_answer_choice_refs_verified":150,
        "source_footer_metadata_refs_verified":50,
        "pointer_update_safety_in_emulator_proven":False,
        "relocated_text_rendering_tested":False,
        "gameplay_tested":False,
        "writes_ROM_or_IPS":False,
    },"tables":groups,"references":reference_rows}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("clean_original_japanese_rom",type=Path)
    p.add_argument("--project-root",type=Path,default=ROOT)
    p.add_argument("--report",type=Path)
    args=p.parse_args()
    report=analyze(args.clean_original_japanese_rom.read_bytes(),args.project_root)
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report["summary"],ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
