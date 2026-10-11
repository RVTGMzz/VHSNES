#!/usr/bin/env python3
"""Offline Quiz preflight with no Japanese ROM or proprietary font required.

Validates all 381 canonical Quiz source rows, all approved stages 041..061,
and 150 original answer-pointer source offsets captured from clean ROM.
Optionally rechecks the metadata against a user-owned original 2MiB SFC.

Does not patch any binary, move scripts or certify emulator compatibility.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
ROM_SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
SOURCE_FILES=(
    "quiz_batch01_part1_vi.csv","quiz_batch01_part2_vi.csv",
    "quiz_batch02_part1_vi.csv","quiz_batch02_part2_vi.csv",
    "quiz_batch02_part3_vi.csv","quiz_batch03_part1_vi.csv",
    "quiz_batch03_part2_vi.csv","quiz_batch03_part3_vi.csv",
)
STAGES=(
    ("041","quiz_answers_exact_fit_041.csv","csv",21),
    ("047","quiz_fortune_exactfit_047.json","mixed",15),
    ("054","quiz_content_first_54_054.json","json",54),
    ("057","quiz_content_first_50_057.json","json",50),
    ("058","quiz_content_first_67_058.json","json",67),
    ("059","quiz_content_first_37_059.json","json",34),
    ("060","quiz_content_first_21_060.json","json",21),
    ("061","quiz_content_first_19_061.json","json",17),
)
EXCEPTIONS={0x33ddf:{"一","雄"},0x33dfd:{"和","雄"}}

def rows_from_csv(path:Path):
    with path.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def check(root:Path,original_rom:Path|None):
    source={}
    for filename in SOURCE_FILES:
        for row in rows_from_csv(root/"translation/source"/filename):
            offset=int(row["file_offset"],0)
            if (offset in source or not 0<=offset<0x200000
                or not row.get("source_jp_scanner") or not row.get("vi_full")):
                raise AssertionError("Original Quiz source missing/duplicate at "+str(offset))
            source[offset]=row
    if len(source)!=381:
        raise AssertionError("Expected 381 canonical Quiz source records")
    staged={}
    per={}
    for stage,filename,fmt,expected in STAGES:
        path=root/"translation/runtime"/filename
        lines=rows_from_csv(path) if fmt=="csv" else json.loads(
            path.read_text(encoding="utf-8"))["records"]
        if fmt=="mixed":
            lines=[r for r in lines if r.get("category")=="quiz"]
        if len(lines)!=expected:
            raise AssertionError(f"Unexpected stage {stage} Quiz count")
        for row in lines:
            offset=int(row["file_offset"],0)
            if offset not in source or offset in staged:
                raise AssertionError(f"Unknown/double-localized Quiz source {offset:05X}")
            staged[offset]=stage
        per[stage]=expected
    if len(staged)!=279:
        raise AssertionError("Expected 279 uniquely prepared Quiz sources")

    atlas=json.loads((root/"translation/runtime/quiz_answer_pointer_offsets_070.json").read_text(encoding="utf-8"))
    triplets=atlas["selection_slot_answer_source_offsets"]
    if (atlas["schema"]!="chibi.quiz.answer_pointer_atlas_070.v1"
        or atlas["source_clean_ROM_sha256"]!=ROM_SHA
        or atlas["answer_pointer_table_starts"]!=["0x31217","0x3127F","0x312E7"]
        or atlas["pointer_stride_bytes"]!=2 or len(triplets)!=50
        or any(len(group)!=3 for group in triplets)):
        raise AssertionError("Native Quiz 50x3 address atlas shape drift")
    answers=[]
    for group in triplets:
        for original in group:
            offset=int(original,0)
            if offset in answers or offset not in source:
                raise AssertionError("Unknown/duplicated original Quiz answer address")
            answers.append(offset)
    if len(answers)!=150 or len(set(answers))!=150:
        raise AssertionError("Quiz answer atlas not 150 unique original choices")
    selected=[x for x in answers if x in staged]
    pending=[x for x in answers if x not in staged]
    if len(selected)!=69 or len(pending)!=81:
        raise AssertionError("Real original Quiz answer prepared/pending numbers changed")

    cp_rows=rows_from_csv(root/"translation/codepage/vi_codepage_v4_fe4_native.csv")
    v2={r["unicode"]:r["code_hex"] for r in cp_rows}
    if v2.get(" ")!="8440" or len(v2)!=160:
        raise AssertionError("Vietnamese V2 codepage identity/spacing changed")
    unsupported={}
    for offset in pending:
        text=source[offset]["vi_full"]
        missing={ch for ch in text if ch not in v2}
        if missing:
            unsupported[offset]=missing
    if unsupported!=EXCEPTIONS:
        raise AssertionError("Unrecognized unsupported Vietnamese/kanji choice glyphs")
    for off,letters in EXCEPTIONS.items():
        for glyph in letters:
            if len(glyph.encode("cp932"))!=2:
                raise AssertionError("Original Japanese glyph not native CP932")
    if any(not set(source[x]["vi_full"]).issubset(v2) for x in pending if x not in EXCEPTIONS):
        raise AssertionError("Unexpected unencodable full Vietnamese choice")

    checked_rom=False
    if original_rom is not None:
        original=original_rom.read_bytes()
        if len(original)!=0x200000 or hashlib.sha256(original).hexdigest()!=ROM_SHA:
            raise AssertionError("Not the exact original Japanese 2MiB ROM")
        for index,group in enumerate(triplets):
            for ordinal,original_text in enumerate(group):
                at=int(original_text,0)
                pointer_word=(0x31217,0x3127F,0x312E7)[ordinal]+2*index
                cpu_addr=int.from_bytes(original[pointer_word:pointer_word+2],"little")
                if (not 0x8000<=cpu_addr<=0xffff or
                    0x30000+cpu_addr-0x8000+4!=at or
                    original[at-4:at]!=b"\x0e\x06\x0f\x12"):
                    raise AssertionError(
                        f"Original native answer pointer mismatch: {pointer_word:05X}")
        checked_rom=True
    return {
        "status":"PASS_SOURCE_ONLY_QUIZ_PRELIGHT_NOT_EMULATOR",
        "canonical_Quiz_sources":len(source),
        "distinct_staged_Quiz_sources":len(staged),
        "canonical_Quiz_sources_unstaged":len(source)-len(staged),
        "stage_counts":per,
        "original_Quiz_question_slots":len(triplets),
        "original_three_choice_answers":len(answers),
        "prepared_original_choice_answers":len(selected),
        "pending_original_choice_answers":len(pending),
        "pending_fully_V2_encodable":len(pending)-len(EXCEPTIONS),
        "pending_native_CP932_Kanji_exceptions":len(EXCEPTIONS),
        "optional_exact_original_ROM_pointer_QA_passed":checked_rom,
        "composite_043_061_ROM_built":False,
        "emulator_tested":False,
        "gameplay_approved":False,
        "wrote_ROM_or_IPS":False,
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project-root",type=Path,default=ROOT)
    ap.add_argument("--original-rom",type=Path)
    ap.add_argument("--report",type=Path)
    args=ap.parse_args()
    if args.original_rom and args.report and args.original_rom.resolve()==args.report.resolve():
        ap.error("Refusing to overwrite original ROM with JSON")
    result=check(args.project_root,args.original_rom)
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
