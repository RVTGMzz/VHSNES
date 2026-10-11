#!/usr/bin/env python3
"""Chibi SNES read-only source QA suite (064–069) plus canonical Quiz inventory.

Run with the user's exact unheadered Japanese ROM and a full local checkout:
    python tools/verify_quiz_technical_069.py clean.sfc --report qa069.json

Checks 279 staged sources, 102 remaining, 409 original script transitions,
50 questions/150 answers, 9x50 pointers, original single answer relocation
and all 81 full-label dry-run relocations. Generates JSON only. The original
retail ROM does NOT contain Vietnamese font V2. NEVER marks emulator success.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from audit_quiz_unique_061 import run as audit_unique
from audit_quiz_remaining_063 import run as audit_remaining
from probe_quiz_script_grammar_064 import analyze as audit_grammar
from build_quiz_answer_atlas_065 import analyze as audit_atlas
from audit_quiz_pointer_tables_066 import analyze as audit_pointers
from probe_quiz_relocation_067 import run as audit_one_repoint
from plan_quiz_long_answers_068 import plan as audit_79_legacy
from plan_quiz_long_answers_069_mixed import plan as audit_81_mixed

ROOT=Path(__file__).resolve().parent.parent
CLEAN_SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
FINAL_81_IPS_SHA="3777df4895046d8342d421f8da5d2ccabdfd01cec7b5f8e567759ba1d4e5c213"
FINAL_81_ROM_SHA="c61471d70f0025e075d6dd94366940bc8990e1cfc910cf99f421dc15ff47f184"

def run(clean:bytes,root:Path):
    if len(clean)!=0x200000 or hashlib.sha256(clean).hexdigest()!=CLEAN_SHA:
        raise ValueError("Exact original clean user-owned Japanese 2MiB SFC required")
    stages=audit_unique(root)
    remaining=audit_remaining(clean,root)["summary"]
    grammar=audit_grammar(clean)
    atlas=audit_atlas(clean,root)["summary"]
    pointers=audit_pointers(clean,root)["summary"]
    single=audit_one_repoint(clean,root)
    batch79=audit_79_legacy(clean,root)["summary"]
    batch81=audit_81_mixed(clean,root)["summary"]
    if (stages["staged_unique_Quiz_records"]!=279 or
        stages["remaining_original_Quiz_records"]!=102 or
        remaining["independent_original_text_regions_not_yet_staged"]!=82 or
        remaining["staged_original_text_byte_overlaps"]!=0 or
        grammar["native_816F_then_00_control_boundaries"]!=409 or
        atlas["original_question_blocks"]!=50 or
        atlas["genuine_three_choice_fields"]!=150 or
        atlas["answer_choices_remaining_unstaged"]!=81 or
        pointers["total_16bit_question_entry_references"]!=450 or
        pointers["source_answer_choice_refs_verified"]!=150 or
        len(single["byte_only_trials"])!=2 or
        batch79["full_Vietnamese_encodable_without_font_changes"]!=79 or
        batch81["full_Vietnamese_and_native_Kanji_byte_encoded"]!=81 or
        batch81["original_CP932_kanji_2byte_glyphs"]!=4 or
        batch81["exact_original_16bit_pointer_updates"]!=81 or
        batch81["unapproved_storage_used_bytes"]!=2431 or
        batch81["source_only_rom_byte_differences"]!=2517 or
        batch81["in_memory_IPS_bytes"]!=3145 or
        batch81["in_memory_IPS_records"]!=124 or
        batch81["in_memory_IPS_sha256"]!=FINAL_81_IPS_SHA or
        batch81["in_memory_full_ROM_sha256"]!=FINAL_81_ROM_SHA or
        batch81["recomputed_SNES_checksum"]!="0xC3BC"):
        raise AssertionError("Original ROM/source/PTR/069 integrity regression")
    # No experimental relocation has ever received emulator acceptance:
    if (batch81["production_quiz_entry_approved"] or
        batch81["gameplay_or_renderer_tested"] or
        batch81["integrated_with_missing_043_IPS"]):
        raise AssertionError("Unsafe/unsupported emulator acceptance claim")
    return {
        "status":"PASS_EXACT_ORIGINAL_ROM_ALL_SOURCE_BYTE_GUARDS_ONLY",
        "original_japanese_ROM_sha256":CLEAN_SHA,
        "staged_Quiz_unique_canonical_entries":279,
        "canonical_Quiz_rows_remaining_unstaged":102,
        "independent_original_ROM_text_regions_remaining":82,
        "original_Quiz_script_terminals":409,
        "original_Quiz_question_groups":50,
        "original_Quiz_answer_choices":150,
        "original_Quiz_choice_pointer_references":150,
        "original_Quiz_question_table_pointer_references":450,
        "pending_full_answer_candidates_total":81,
        "V2_only_unmodified_codepage_candidates":79,
        "hybrid_V2_original_CP932_Kanji_byte_encodable_candidates":81,
        "experimental_reloco_81_proposal_IPS_SHA256":FINAL_81_IPS_SHA,
        "experimental_reloco_81_proposal_ROM_SHA256":FINAL_81_ROM_SHA,
        "experimental_81_answer_pointer_update_count":81,
        "real_043_IPS_available_to_this_source_only_test":False,
        "SNES_game_emulator_tested":False,
        "hybrid_CP932_with_V2_in_game_verified":False,
        "relocation_production_approved":False,
        "ROM_or_IPS_written_to_disk":False,
    }

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original_clean_japanese_rom",type=Path)
    parser.add_argument("--project-root",type=Path,default=ROOT)
    parser.add_argument("--report",type=Path)
    args=parser.parse_args()
    paths=[args.original_clean_japanese_rom]
    if args.report:
        paths.append(args.report)
    if len({p.resolve() for p in paths})!=len(paths):
        parser.error("JSON report must not overwrite user-owned ROM")
    result=run(args.original_clean_japanese_rom.read_bytes(),args.project_root)
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
