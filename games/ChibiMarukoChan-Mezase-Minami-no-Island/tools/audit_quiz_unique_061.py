#!/usr/bin/env python3
"""Audit distinct Quiz source offsets across all staged translation layers.

Guards against inflated progress and re-patching original source fields that
a prior stage already translated. Does NOT claim emulation/runtime QA.
"""
from __future__ import annotations
import csv
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
SOURCE_FILES = (
    "quiz_batch01_part1_vi.csv","quiz_batch01_part2_vi.csv",
    "quiz_batch02_part1_vi.csv","quiz_batch02_part2_vi.csv",
    "quiz_batch02_part3_vi.csv","quiz_batch03_part1_vi.csv",
    "quiz_batch03_part2_vi.csv","quiz_batch03_part3_vi.csv",
)
STAGES = (
    ("041","csv","quiz_answers_exact_fit_041.csv"),
    ("047","quiz_json","quiz_fortune_exactfit_047.json"),
    ("054","json","quiz_content_first_54_054.json"),
    ("057","json","quiz_content_first_50_057.json"),
    ("058","json","quiz_content_first_67_058.json"),
    # Historic name retains '37', but 3 preexisting 047 records were removed.
    ("059","json","quiz_content_first_37_059.json"),
    ("060","json","quiz_content_first_21_060.json"),
    ("061","json","quiz_content_first_19_061.json"),
)
EXPECTED_COUNTS={"041":21,"047":15,"054":54,"057":50,
                 "058":67,"059":34,"060":21,"061":17}
EXPECTED_TOTAL=279
EXPECTED_SOURCE=381

def normalize_offset(raw):
    x=int(raw,0)
    if not 0<=x<0x200000:
        raise AssertionError("Invalid SNES ROM address: "+str(raw))
    return f"0x{x:X}"

def csv_rows(file):
    with file.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def run(root=ROOT):
    source={}
    for name in SOURCE_FILES:
        filename=root/"translation/source"/name
        for row in csv_rows(filename):
            key=normalize_offset(row["file_offset"])
            if key in source:
                raise AssertionError(f"Duplicate canonical Quiz source {key}: {name}")
            source[key]=filename.name
    if len(source)!=EXPECTED_SOURCE:
        raise AssertionError(f"Quiz source inventory expected 381, got {len(source)}")
    owner={}
    report={}
    for stage,typ,filename in STAGES:
        file=root/"translation/runtime"/filename
        if typ=="csv":
            records=csv_rows(file)
        else:
            records=json.loads(file.read_text(encoding="utf-8"))["records"]
        if typ=="quiz_json":
            records=[r for r in records if r["category"]=="quiz"]
        local=set()
        for r in records:
            key=normalize_offset(r["file_offset"])
            if key not in source:
                raise AssertionError(f"Unrecognized original Quiz offset {stage}: {key}")
            if key in local:
                raise AssertionError(f"Duplicate within stage {stage}: {key}")
            if key in owner:
                raise AssertionError(f"Previously patched Quiz offset {key}: "
                                     f"stage {owner[key]} and stage {stage}")
            owner[key]=stage
            local.add(key)
        if len(local)!=EXPECTED_COUNTS[stage]:
            raise AssertionError(f"Stage {stage} expected {EXPECTED_COUNTS[stage]} "
                                 f"distinct Quiz fields; found {len(local)}")
        report[stage]=len(local)
    if len(owner)!=EXPECTED_TOTAL:
        raise AssertionError(f"Quiz unique count should be {EXPECTED_TOTAL}, got {len(owner)}")
    return {
        "status":"PASS_STATIC_DISTINCT_QUIZ_SOURCE_OFFSETS_NO_EMULATOR",
        "canonical_source_records":len(source),
        "staged_unique_Quiz_records":len(owner),
        "remaining_original_Quiz_records":len(source)-len(owner),
        "stage_counts":report,
        "historical_053_duplicate_rows_excluded":True,
        "historical_059_047_overlaps_removed":3,
        "historical_061_ambiguous_abbreviations_deferred":2,
        "emulator_tested":False,
    }

if __name__=="__main__":
    result=run()
    print(json.dumps(result,ensure_ascii=False,indent=2))
