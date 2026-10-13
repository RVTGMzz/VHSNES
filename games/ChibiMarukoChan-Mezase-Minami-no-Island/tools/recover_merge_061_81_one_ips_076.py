#!/usr/bin/env python3
"""Chibi: one 039–043 ZIP/IPS -> 061 +81 choices +3 fields +079–086 QA IPS.

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
from build_quiz_native_explanations_078 import build as integrate_two_explanations
from build_quiz_parent_semantic_restore_079 import build as restore_three_semantic_parents
from build_quiz_parent_semantic_restore_080 import build as restore_080_quiz_context
from build_quiz_parent_semantic_restore_081 import build as restore_081_quiz_context
from build_quiz_parent_semantic_restore_082 import build as restore_082_quiz_context
from build_quiz_sugiyama_ono_083 import build as restore_sugiyama_ono_083
from build_quiz_semantic_context_batch_084 import build as restore_four_context_parents_084
from build_quiz_seven_fact_restore_085 import build as restore_seven_fact_parents_085
from build_quiz_context_semantics_086 import build as restore_seven_stage057_086

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
    continuation_ips,continuation_qa=integrate_one_question(
        clean,choice_rom,root,require_all81=True)
    continuation_rom=apply_ips(clean,continuation_ips)
    if (continuation_qa.get("candidate_ROM_SHA256")!=sha(continuation_rom)
        or continuation_qa.get("clean_ROM_IPS_SHA256")!=sha(continuation_ips)):
        raise AssertionError("077 original full Quiz question continuation failed replay")
    explanation_ips,explanation_qa=integrate_two_explanations(
        clean,continuation_rom,root)
    explanation_rom=apply_ips(clean,explanation_ips)
    if (explanation_qa.get("final_candidate_ROM_sha256")!=sha(explanation_rom) or
        explanation_qa.get("clean_ROM_IPS_sha256")!=sha(explanation_ips)):
        raise AssertionError("078 two original pointer-explanations failed cumulative replay")
    semantic_ips,semantic_qa=restore_three_semantic_parents(
        clean,explanation_rom,root)
    semantic_rom=apply_ips(clean,semantic_ips)
    if (semantic_qa.get("candidate_result_ROM_sha256")!=sha(semantic_rom) or
        semantic_qa.get("cumulative_original_ROM_IPS_sha256")!=sha(semantic_ips)):
        raise AssertionError("079 previous semantic repairs IPS replay failed")
    semantic_080_ips,semantic_080_qa=restore_080_quiz_context(
        clean,semantic_rom,root)
    semantic_080_rom=apply_ips(clean,semantic_080_ips)
    if (semantic_080_qa.get("candidate_ROM_sha256")!=sha(semantic_080_rom)
        or semantic_080_qa.get("cumulative_clean_ROM_IPS_sha256")!=sha(semantic_080_ips)):
        raise AssertionError("080 known contextual Quiz corrections failed exact IPS replay")
    semantic_081_ips,semantic_081_qa=restore_081_quiz_context(
        clean,semantic_080_rom,root)
    semantic_081_rom=apply_ips(clean,semantic_081_ips)
    if (semantic_081_qa.get("candidate_ROM_sha256")!=sha(semantic_081_rom)
        or semantic_081_qa.get("final_cumulative_clean_ROM_IPS_sha256")!=sha(semantic_081_ips)):
        raise AssertionError("081 previous Quiz source contextual edits failed replay")
    semantic_082_ips,semantic_082_qa=restore_082_quiz_context(
        clean,semantic_081_rom,root)
    semantic_082_rom=apply_ips(clean,semantic_082_ips)
    if (semantic_082_qa.get("candidate_ROM_sha256")!=sha(semantic_082_rom)
        or semantic_082_qa.get("cumulative_clean_ROM_IPS_sha256")!=sha(semantic_082_ips)):
        raise AssertionError("082 two previous Quiz narration corrections failed replay")
    semantic_083_ips,semantic_083_qa=restore_sugiyama_ono_083(
        clean,semantic_082_rom,root)
    semantic_083_rom=apply_ips(clean,semantic_083_ips)
    if (semantic_083_qa.get("candidate_ROM_sha256")!=sha(semantic_083_rom)
        or semantic_083_qa.get("cumulative_clean_ROM_IPS_sha256")!=sha(semantic_083_ips)):
        raise AssertionError("083 source-faithful Quiz correction failed cumulative replay")
    semantic_084_ips,semantic_084_qa=restore_four_context_parents_084(
        clean,semantic_083_rom,root)
    semantic_084_rom=apply_ips(clean,semantic_084_ips)
    if (semantic_084_qa.get("candidate_ROM_sha256")!=sha(semantic_084_rom)
        or semantic_084_qa.get("cumulative_clean_IPS_sha256")!=sha(semantic_084_ips)):
        raise AssertionError("084 four original contextual corrections failed cumulative replay")
    semantic_085_ips,semantic_085_qa=restore_seven_fact_parents_085(
        clean,semantic_084_rom,root)
    semantic_085_rom=apply_ips(clean,semantic_085_ips)
    if (semantic_085_qa.get("candidate_ROM_sha256")!=sha(semantic_085_rom)
        or semantic_085_qa.get("cumulative_clean_IPS_sha256")!=sha(semantic_085_ips)):
        raise AssertionError("085 seven original Japanese source fixes failed replay")
    final_ips,semantic_086_qa=restore_seven_stage057_086(
        clean,semantic_085_rom,root)
    final_rom=apply_ips(clean,final_ips)
    if (len(final_rom)!=len(clean) or
        semantic_086_qa.get("candidate_ROM_sha256")!=sha(final_rom) or
        semantic_086_qa.get("cumulative_clean_IPS_sha256")!=sha(final_ips) or
        semantic_086_qa.get("reviewed_prior_stage057_source_records")!=7 or
        semantic_086_qa.get("changed_existing_V2_caption_frames")!=16 or
        semantic_085_qa.get("historical_parent_fields_audited")!=7 or
        semantic_085_qa.get("real_new_caption_frames")!=14 or
        semantic_084_qa.get("historical_parent_fields_audited")!=4 or
        semantic_084_qa.get("real_new_caption_frames")!=6 or
        semantic_083_qa.get("corrected_existing_native_parent_count")!=1 or
        semantic_082_qa.get("existing_native_Quiz_explanation_records")!=2 or
        semantic_081_qa.get("canonical_source_records_covered_by_prior_stages")!=4 or
        semantic_080_qa.get("three_original_Quiz_parents_reviewed")!=3 or
        semantic_qa.get("canonical_parent_fields_reviewed")!=3 or
        explanation_qa.get("new_native_explanation_fields_prepared")!=2 or
        continuation_qa.get("new_independent_original_Quiz_source_offset")!="0x320E8" or
        choice_qa.get("canonical_full_Quiz_answer_records")!=81 or
        choice_qa.get("SNES_emulator_tested") is not False or
        choice_qa.get("release_approved") is not False):
        raise AssertionError("Combined 061 + 81 source patch failed fail-closed QA")
    # Ensure the cumulative output actually retained the original V2 font.
    if final_rom[0x2975e:0x29760]!=original_061[0x2975e:0x29760]:
        raise AssertionError("Quiz relocation altered Vietnamese V2 font pointer")
    return final_ips,{
        "status":"COMBINED_061_PLUS_81_CHOICES_PLUS_3_NATIVE_FIELDS_PLUS_079_080_081_082_083_084_085_086_SEMANTIC_QA_UNTESTED",
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
        "additional_two_pointer_anchored_Quiz_explanations_078_report":explanation_qa,
        "079_restored_existing_3_semantic_parent_fields_report":semantic_qa,
        "080_restored_existing_3_additional_semantic_parents_report":semantic_080_qa,
        "081_restored_existing_4_more_semantic_parents_report":semantic_081_qa,
        "082_restored_two_additional_semantic_parent_records_report":semantic_082_qa,
        "083_restored_Sugiyama_named_in_Ono_quiz_report":semantic_083_qa,
        "084_restored_four_more_contextually_correct_native_parents_report":semantic_084_qa,
        "085_restored_seven_missing_original_Quiz_facts_report":semantic_085_qa,
        "086_restored_seven_existing_057_Quiz_contexts_report":semantic_086_qa,
        "original_remaining_Quiz_native_field_candidates_added":3,
        "independent_Quiz_077_candidate_added":1,
        "original_remaining_scanner_aliases_not_independently_patched":18,
        "source_one_archive_rebuild_passed":True,
        "newly_emulator_accepted_Quiz_source_strings":0,
        "079_newly_created_physical_records":0,
        "079_existing_original_semantic_omissions_restored":3,
        "080_existing_original_semantic_omissions_restored":3,
        "081_existing_original_semantic_omissions_restored":4,
        "082_existing_original_semantic_omissions_restored":2,
        "083_existing_original_semantic_omissions_restored":1,
        "084_existing_original_semantic_omissions_restored":4,
        "085_existing_original_semantic_omissions_restored":7,
        "086_existing_original_semantic_omissions_restored":7,
        "recomputed_SNES_checksum":semantic_086_qa["final_SNES_checksum"],
        "font_V2_present_in_combined_candidate":True,
        "all_84_original_independent_remaining_Quiz_fields_have_source_byte_prototypes":True,
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
