#!/usr/bin/env python3
"""Checkpoint075: prove SNES Quiz copy -> text task -> WAIT for task completion.

Prior 074 incorrectly equated *final WRAM buffer overlap* with guaranteed
visible output corruption. Original 65c816 shows EACH choice's copied WRAM
buffer is passed via JSL $85804B and followed by repeated JSL $858160
and BCC back until the text-job status clears, *before* the next option.
The text handler's exact visual width remains unverified without emulator QA.

This is a read-only disassembly-contract and conditional overlap model.
It never patches the original ROM or declares all 81 choice records playable.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from plan_quiz_bankcopy_slots_073 import plan as plan_choices
from audit_quiz_wram_stride_074 import run as audit_wram

ROOT=Path(__file__).resolve().parent.parent
ROM_SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
NATIVE_COPIER_AT=0x30762
NATIVE_COPIER=bytes.fromhex(
    "A9 20 00 85 08 B9 00 00 9F 00 80 7E E8 E8 C8 C8 C6 08 10 F1 60")
# The three callers COPY (JSR $8762), then initialize the script bank,
# PASS THEIR NEW WRAM BUFFER Y address to JSL $85804B, then return.
# Options 2/3 additionally adjust a display-layout control word at +2
# before calling the script renderer.
CALLER_WINDOWS=(
    (0x30740,0,bytes.fromhex(
        "20 62 87 A9 7E 00 22 2B 80 85 "
        "A0 00 80 22 4B 80 85 22 60 81 85 90 FA")),
    (0x307BA,1,bytes.fromhex(
        "20 62 87 AF 22 80 7E 18 69 00 02 8F 22 80 7E "
        "A9 7E 00 22 2B 80 85 "
        "A0 20 80 22 4B 80 85 22 60 81 85 90 FA")),
    (0x3082B,2,bytes.fromhex(
        "20 62 87 AF 42 80 7E 18 69 00 04 8F 42 80 7E "
        "A9 7E 00 22 2B 80 85 "
        "A0 40 80 22 4B 80 85 22 60 81 85 90 FA")),
)
RENDER_WRAPPER_AT=0x28044
# CPU bank 85 at $8044 = PC 0x28044.
# $85804B is inside this wrapper; it synchronously CALLS three subroutines.
# Do not assume the graphics have actually finished rendering by return.
RENDER_WRAPPER=bytes.fromhex(
    "A9 85 00 22 2B 80 85 DA 5A "
    "22 9D 80 85 22 56 81 85 22 60 81 85 7A FA 6B")
# The render job begins with STA $1F80=2 and STY $1F94.
TEXT_START_AT=0x28156
TEXT_START=bytes.fromhex("A9 02 00 8D 80 1F 8C 94 1F 6B")
# JSL $858160 returns CLC while $1F80 is active, SEC when zero.
# Original three callers BCC -6 to poll this function before continuing.
WAIT_POLL_AT=0x28160
WAIT_POLL=bytes.fromhex(
    "AD 80 1F F0 13 8B DA 5A AF 86 1F 00 48 AB 28 "
    "22 7A 81 85 7A FA AB 18 6B 38 6B")

def check_code(clean:bytes):
    if len(clean)!=0x200000 or hashlib.sha256(clean).hexdigest()!=ROM_SHA:
        raise ValueError("Exact original unheadered Japanese retail Chibi SFC required")
    if clean[NATIVE_COPIER_AT:NATIVE_COPIER_AT+len(NATIVE_COPIER)]!=NATIVE_COPIER:
        raise AssertionError("Original 33*2 byte text copier bytes changed")
    if clean[RENDER_WRAPPER_AT:RENDER_WRAPPER_AT+len(RENDER_WRAPPER)]!=RENDER_WRAPPER:
        raise AssertionError("Original $85804B rendering wrapper bytes changed")
    if clean[TEXT_START_AT:TEXT_START_AT+len(TEXT_START)]!=TEXT_START:
        raise AssertionError("Original $858156 text-job start/pointer changed")
    if clean[WAIT_POLL_AT:WAIT_POLL_AT+len(WAIT_POLL)]!=WAIT_POLL:
        raise AssertionError("Original $858160 text-job status/carry wait routine changed")
    for at,ordinal,source in CALLER_WINDOWS:
        if clean[at:at+len(source)]!=source:
            raise AssertionError(f"Original answer copy/render branch {ordinal+1} changed")
        if source.count(bytes.fromhex("20 62 87"))!=1:
            raise AssertionError("Expected one native answer copy per branch")
        if source.count(bytes.fromhex("22 4B 80 85"))!=1:
            raise AssertionError("Expected one immediate text-processing/render call")
        if not source.endswith(bytes.fromhex("22 60 81 85 90 FA")):
            raise AssertionError("Each answer must poll render job JSL $858160/BCC -6")
        if source.find(bytes.fromhex("20 62 87")) > source.find(bytes.fromhex("22 4B 80 85")):
            raise AssertionError("Native render-before-copy call order is inconsistent")
        if source.find(bytes.fromhex(("A0 00 80","A0 20 80","A0 40 80")[ordinal]))<0:
            raise AssertionError("Original WRAM text-address argument changed")
    return True

def run(root:Path,original_rom:bytes|None):
    candidates=plan_choices(root,original_rom)
    source=audit_wram(root,original_rom)["summary"]
    options=candidates["slots"]
    if (len(options)!=81 or source["canonical_full_answers_exceeding_32_byte_WRAM_stride"]!=29
        or source["original_answer_1_or_2_records_overwritten_by_next_copy"]!=18):
        raise AssertionError("Historical source length/WRAM counts drift")
    verified=check_code(original_rom) if original_rom is not None else False
    # Model two possible consumer strategies. The real code passes the copied
    # address to the text handler IMMEDIATELY; what that handler does is NOT
    # demonstrated by the original answer-copy routine alone.
    per_question={}
    for x in options:
        key=(x["pointer_table_slot"],x["answer_ordinal"])
        per_question[key]=x
    immediate_intact=0
    deferred_intact=0
    late_overwritten=[]
    for q in range(50):
        ram=bytearray(b"\x00"*160)
        start_by_ordinal={1:0,2:32,3:64}
        snapshot={}
        for ordinal in (1,2,3):
            x=per_question.get((q,ordinal))
            # Make *every* slot's synthetic bytes distinct. If all source
            # records use the same filler, an overlapping write can look
            # byte-identical and falsely pass the deferred-copy test.
            token=1+q*3+(ordinal-1)  # 1..150: unique per Quiz slot
            rec=(bytes([token])*x["record_size"]) if x else bytes([token])*11
            source_window=rec+b"\x00"*(66-len(rec))
            start=start_by_ordinal[ordinal]
            ram[start:start+66]=source_window
            # The immediate JSL is sequenced right here, before any next copy:
            if x:
                immediate_intact+=int(ram[start:start+len(rec)]==rec)
                snapshot[ordinal]=(x,rec)
        for ordinal,(x,rec) in snapshot.items():
            start=start_by_ordinal[ordinal]
            if ram[start:start+len(rec)]==rec:
                deferred_intact+=1
            else:
                late_overwritten.append({
                    "original_text_file_offset":x["source_offset"],
                    "answer_ordinal":ordinal,
                    "record_bytes":len(rec)})
    if (immediate_intact!=81 or deferred_intact!=63 or
        len(late_overwritten)!=18 or
        any(row["answer_ordinal"]==3 for row in late_overwritten)):
        raise AssertionError("Immediate-versus-deferred dataflow demonstration changed")
    return {
        "status":"PASS_ORIGINAL_65816_COPY_RENDER_AND_POLL_UNTIL_DONE_NOT_EMULATOR",
        "original_ROM_SHA256":ROM_SHA,
        "actual_65816_caller_bytes_verified":verified,
        "native_66_byte_answer_copies":3,
        "native_WRAM_spacing_bytes":32,
        "records_overlapping_later_WRAM_copies":18,
        "all_81_records_intact_at_renderer_handoff":immediate_intact,
        "original_three_choice_branches_WAIT_for_1F80_to_clear":verified,
        "text_handler_start_state_register":"$1F80",
        "text_handler_source_pointer_register":"$1F94",
        "wait_carry_set_when_task_inactive":True,
        "records_still_intact_if_all_consumption_were_deferred_until_after_three_copies":deferred_intact,
        "runtime_visual_corruption_of_18_ascertained":False,
        "buffer_relocation_required_before_next_answer":False,
        "render_handler_wait_until_job_inactive_code_verified":verified,
        "render_handler_visual_width_acceptance_proven":False,
        "renderer_address":"$85804B",
        "renderer_wrapper_ROM_offset":"0x28044",
        "gameplay_or_emulator_tested":False,
        "safe_to_release_all_81":False,
        "patch_or_ROM_written":False,
        "deferred_scenario_late_overwritten":late_overwritten,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-root",type=Path,default=ROOT)
    p.add_argument("--original-rom",type=Path)
    p.add_argument("--report",type=Path)
    args=p.parse_args()
    if args.report and args.original_rom and args.report.resolve()==args.original_rom.resolve():
        p.error("Never overwrite user's original ROM")
    result=run(args.project_root,args.original_rom.read_bytes() if args.original_rom else None)
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="deferred_scenario_late_overwritten"},
                     ensure_ascii=False,indent=2))

if __name__=="__main__":main()
