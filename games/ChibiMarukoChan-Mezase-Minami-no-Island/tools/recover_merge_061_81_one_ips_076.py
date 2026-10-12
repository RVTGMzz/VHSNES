#!/usr/bin/env python3
"""Chibi: one user-owned 039–043 ZIP/IPS -> 061+81 answers+1 question IPS.

End-to-end combines checkpoint071 guarded recovery and checkpoint075 complete
Quiz 81-choice source/LoROM pointer relocation plus one independently
recoverable non-answer question continuation, so the user does NOT have to
manually apply a stack of incomplete historical patch files.

Outputs one CLEAN-original-ROM-relative IPS plus an audit JSON. Does NOT write
copyrighted ROM data or claim emulator, font, screen or answer selection QA.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from build_content_first_040_fortune import apply_ips
from recover_from_any_039_to_043_archive_071 import (
    CLEAN_SHA, select_historical_ips, rebuild as rebuild_061_from_archive,
)
from build_quiz_relocated_81_jobwait_075 import (
    build as integrate_full_81,
    validate_061_baseline_report,
)
from build_quiz_nonanswer_continuation_077 import build as integrate_one_question

ROOT=Path(__file__).resolve().parent.parent

def sha(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()

def rebuild_one_patch(clean:bytes,archive_file:Path,root:Path):
    if len(clean)!=0x200000 or sha(clean)!=CLEAN_SHA:
        raise ValueError("Only the exact original unheadered Japanese 2MiB SFC is allowed")
    selected,previous_ips,provenance=select_historical_ips(archive_file)
    ips061,qa061=rebuild_061_from_archive(clean,selected,previous_ips,root)
    original_061=apply_ips(clean,ips061)
    if len(original_061)!=len(clean):
        raise AssertionError("Reconstructed 061 ROM length unexpectedly changed")
    qa_contract=validate_061_baseline_report(
        qa061,sha(original_061),sha(ips061),sha(clean))
    if int.from_bytes(original_061[0x2975e:0x29760],"little")!=0x9a74:
        raise AssertionError("Actual reconstructed 061 is missing required V2 glyph pointer")
    choice_ips,choice_qa=integrate_full_81(
        clean,original_061,root,"cumulative_V2_061")
    choice_rom=apply_ips(clean,choice_ips)
    if (choice_qa.get("canonical_full_Quiz_answer_records")!=81 or
        choice_qa.get("candidate_ROM_sha256")!=sha(choice_rom)):
        raise AssertionError("Full 81-answer intermediate source IPS failed static QA")
    final_ips,continuation_qa=integrate_one_question(
        clean,choice_rom,root,require_all81=True)
    final_rom=apply_ips(clean,final_ips)
    if (len(final_rom)!=len(clean) or
        continuation_qa.get("candidate_ROM_SHA256")!=sha(final_rom) or
        continuation_qa.get("clean_ROM_IPS_SHA256")!=sha(final_ips) or
        continuation_qa.get("new_independent_original_Quiz_source_offset")!="0x320E8" or
        choice_qa.get("canonical_full_Quiz_answer_records")!=81 or
        choice_qa.get("SNES_emulator_tested") is not False or
        choice_qa.get("release_approved") is not False):
        raise AssertionError("Combined 061 + 81 source patch failed fail-closed QA")
    # Ensure the cumulative output actually retained the original V2 font.
    if final_rom[0x2975e:0x29760]!=original_061[0x2975e:0x29760]:
        raise AssertionError("Quiz relocation altered Vietnamese V2 font pointer")
    return final_ips,{
        "status":"COMBINED_061_PLUS_81_CHOICES_PLUS_1_QUESTION_STATIC_UNTESTED",
        "original_clean_ROM_sha256":CLEAN_SHA,
        "recovered_historical_stage":selected,
        "user_archive":provenance,
        "validated_061_input_SHA_contract":qa_contract,
        "original_061_ROM_sha256":sha(original_061),
        "final_candidate_ROM_sha256":sha(final_rom),
        "final_clean_ROM_IPS_sha256":sha(final_ips),
        "final_clean_ROM_IPS_bytes":len(final_ips),
        "physical_ROM_size":len(final_rom),
        "quiz_81_choice_relocation_report":choice_qa,
        "additional_independent_Quiz_question_continuation_077_report":continuation_qa,
        "independent_Quiz_077_candidate_added":1,
        "original_remaining_scanner_aliases_not_independently_patched":20,
        "source_one_archive_rebuild_passed":True,
        "newly_emulator_accepted_Quiz_source_strings":0,
        "recomputed_SNES_checksum":choice_qa["recomputed_SNES_checksum"],
        "font_V2_present_in_combined_candidate":True,
        "all_82_original_independent_remaining_Quiz_fields_have_source_byte_prototypes":True,
        "emulator_visual_text_tested":False,
        "quiz_answer_highlight_and_grading_tested":False,
        "mixed_native_Kanji_glyphs_verified_in_emulator":False,
        "whole_game_Vietnamese_translation_complete":False,
        "released_as_playable":False,
        "copyrighted_ROM_or_font_written":False,
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("original_clean_Japanese_SFC",type=Path)
    ap.add_argument("historical_user_owned_039_to_043_zip_or_ips",type=Path)
    ap.add_argument("--project-root",type=Path,default=ROOT)
    ap.add_argument("--ips",type=Path,required=True)
    ap.add_argument("--report",type=Path,required=True)
    ap.add_argument("--allow-untested",action="store_true")
    a=ap.parse_args()
    if not a.allow_untested:
        ap.error("Not SNES emulator approved; pass --allow-untested for static test IPS")
    paths=(a.original_clean_Japanese_SFC,
           a.historical_user_owned_039_to_043_zip_or_ips,a.ips,a.report)
    if len({p.resolve() for p in paths})!=len(paths):
        ap.error("Inputs/output paths must differ; never overwrite source ROM")
    if a.ips.suffix.lower()!=".ips" or a.report.suffix.lower()!=".json":
        ap.error("Patch must be .ips and audit report must be .json")
    data=a.original_clean_Japanese_SFC.read_bytes()
    ips,report=rebuild_one_patch(data,a.historical_user_owned_039_to_043_zip_or_ips,a.project_root)
    # Write only after all source/identity/historical/byte/IPS QA checks pass.
    a.ips.parent.mkdir(parents=True,exist_ok=True)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.ips.write_bytes(ips)
    a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":report["status"],
        "recovered_stage":report["recovered_historical_stage"],
        "final_IPS_SHA256":report["final_clean_ROM_IPS_sha256"],
        "patch_bytes":report["final_clean_ROM_IPS_bytes"],
        "emulator_tested":False},ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
