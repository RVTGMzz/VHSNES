#!/usr/bin/env python3
"""Audit original Quiz pointer atlas for native fixed-window overlaps.

An overlapping read window is NORMAL for this game's original adjacent
answers; the 68-byte relocation cells in checkpoint073 are conservative.
This source-only check does not run a game emulator or build a patch.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent.parent
ATLAS=ROOT/"translation/runtime/quiz_answer_pointer_offsets_070.json"
COPY_WINDOW_BYTES=66

def audit(path=ATLAS):
    atlas=json.loads(Path(path).read_text(encoding="utf-8"))
    if (atlas["schema"]!="chibi.quiz.answer_pointer_atlas_070.v1"
        or atlas["answer_choices_total"]!=150
        or atlas["selection_slots_total"]!=50):
        raise AssertionError("Unexpected Quiz atlas version or size")
    triples=atlas["selection_slot_answer_source_offsets"]
    if len(triples)!=50 or any(len(t)!=3 for t in triples):
        raise AssertionError("Expected 50 original triples")
    seen=set()
    gaps=[]
    for row in triples:
        x=[int(value,0) for value in row]
        if not (0x31d00<=x[0]<x[1]<x[2]<0x36907):
            raise AssertionError("Original question choices out of order")
        if any(v in seen for v in x):
            raise AssertionError("Duplicate original answer pointer")
        seen.update(x)
        gaps.extend((x[1]-x[0],x[2]-x[1]))
    if (len(seen)!=150 or len(gaps)!=100 or
        min(gaps)!=11 or max(gaps)!=31 or
        not all(g<COPY_WINDOW_BYTES for g in gaps)):
        raise AssertionError("Original native overlapping copy geometry drift")
    return {
        "status":"PASS_NATIVE_QUIZ_SOURCE_OVERLAP_IS_ORIGINAL_GAME_BEHAVIOR",
        "original_choice_records":150,
        "same_question_adjacent_pairs":100,
        "same_question_pairs_with_66_byte_read_overlap":100,
        "minimum_source_spacing":min(gaps),
        "maximum_source_spacing":max(gaps),
        "native_read_window_bytes":COPY_WINDOW_BYTES,
        "checkpoint073_disjoint_slots_conservative_not_required_by_original":True,
        "overlap_alone_proves_emulator_failure":False,
        "emulator_tested":False,
        "ROM_or_IPS_written":False,
    }

if __name__=="__main__":
    print(json.dumps(audit(),ensure_ascii=False,indent=2))
