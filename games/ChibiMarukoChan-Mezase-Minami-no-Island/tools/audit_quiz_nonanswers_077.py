#!/usr/bin/env python3
"""Checkpoint077 ROM-free audit of exactly 21 original non-answer Quiz source IDs.

After 279 already-staged source IDs and 81 actual still-unstaged three-choice
answer IDs, exactly 21 scanner rows remain. 10 are partially within an
already staged physical script, 10 start at unsafe scanner boundaries, BUT
two of those unsafe scanner aliases were re-anchored to real independently
pointer-addressable native explanation records in checkpoint078. Thus there
are THREE independent native fields: 0x320E8, 0x35A69 and 0x33B8D. This does
NOT imply those 20 aliases are semantically fully localized.

Never double-count fragments as new game strings. Never emit a ROM/IPS.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from audit_quiz_repo_no_rom_070 import (
    check as audit_070,SOURCE_FILES,STAGES
)
from build_quiz_nonanswer_continuation_077 import validate_manifest

ROOT=Path(__file__).resolve().parent.parent
EXPECTED_NESTED={
    0x31E50,0x31E7B,0x31F33,0x3275E,0x32874,
    0x3299F,0x32A96,0x32C15,0x33050,0x33119,
}
EXPECTED_UNSAFE={
    0x34403,0x34A99,0x352AC,0x352C2,0x353F3,
    0x35A69,0x35DB3,0x361A4,0x364B1,0x33B8D,
}
ONE_INDEPENDENT={0x320E8}
REANCHORED_UNSAFE_078={0x35A69,0x33B8D}

def rows(p:Path):
    with p.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def run(root:Path):
    original=audit_070(root,None)
    if (original["canonical_Quiz_sources"]!=381 or
        original["distinct_staged_Quiz_sources"]!=279 or
        original["pending_original_choice_answers"]!=81):
        raise AssertionError("Canonical 070 source inventory drift")
    source={}
    for f in SOURCE_FILES:
        for r in rows(root/"translation/source"/f):
            k=int(r["file_offset"],0)
            if k in source:
                raise AssertionError("Duplicate Quiz source scanner offset")
            source[k]=r
    staged=set()
    for _,name,fmt,_ in STAGES:
        p=root/"translation/runtime"/name
        r=rows(p) if fmt=="csv" else json.loads(p.read_text(encoding="utf-8"))["records"]
        if fmt=="mixed":
            r=[x for x in r if x.get("category")=="quiz"]
        staged.update(int(x["file_offset"],0) for x in r)
    atlas=json.loads((root/"translation/runtime/quiz_answer_pointer_offsets_070.json").read_text(encoding="utf-8"))
    answers={int(x,0) for a in atlas["selection_slot_answer_source_offsets"] for x in a}
    remaining=set(source)-staged-answers
    if remaining!=(EXPECTED_NESTED|EXPECTED_UNSAFE|ONE_INDEPENDENT):
        raise AssertionError("21 original Quiz non-answer source offsets/classifications changed")
    if len(remaining)!=21 or len(EXPECTED_NESTED)!=10 or len(EXPECTED_UNSAFE)!=10:
        raise AssertionError("Expected 10 nested, 10 unsafe and 1 original field")
    manifest=validate_manifest(root)
    if manifest["selected_full_vietnamese_continuation"]!="Mỗi ngày Maru có mấy yên?":
        raise AssertionError("Edited Quiz cash question needs fresh semantic QA")

    records=[]
    for off in sorted(remaining):
        label=("nested_source_alias_review_parent" if off in EXPECTED_NESTED
               else "scanner_unsafe_but_078_reanchored_to_native_pointer_field" if off in REANCHORED_UNSAFE_078
               else "unsafe_scanner_start_needs_parent_review" if off in EXPECTED_UNSAFE
               else "077_independent_full_native_continuation_pending_emulator_QA")
        records.append({
            "original_scanner_offset":f"0x{off:X}",
            "classification":label,
            "canonical_original_source_text":source[off]["source_jp_scanner"],
            "canonical_vi_full_reference":source[off]["vi_full"],
            "independently_count_as_accepted_game_string":False,
        })
    return {
        "status":"PASS_21_NON_ANSWER_SCAN_ROWS_EXACT_UNAPPROVED_SOURCE_TRIAGE",
        "canonical_Quiz_source_IDs":381,
        "preexisting_staged_IDs":279,
        "pending_three_choice_answer_IDs":81,
        "remaining_nonanswer_canonical_scanner_rows":21,
        "already_staged_nested_text_window_aliases":10,
        "unsafe_standalone_scanner_boundaries":10,
        "independent_native_field_recognized_by_077":1,
        "further_pointer_reanchored_independent_fields_078":2,
        "independent_native_fields_across_077_and_078":3,
        "unsafe_scanner_aliases_still_requiring_parent_review":8,
        "unique_unstaged_nonanswer_native_field_original_offset":"0x320E8",
        "unique_unstaged_nonanswer_field_native_pointer_ROM":"0x311AF",
        "candidate_077_full_Vietnamese_line":manifest["selected_full_vietnamese_continuation"],
        "newly_emulator_accepted_localizations":0,
        "gameplay_tested":False,
        "ROM_or_IPS_written":False,
        "records":records,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-root",type=Path,default=ROOT)
    p.add_argument("--report",type=Path)
    a=p.parse_args()
    r=run(a.project_root)
    if a.report:
        a.report.parent.mkdir(parents=True,exist_ok=True)
        a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in r.items() if k!="records"},ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
