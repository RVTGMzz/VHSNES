#!/usr/bin/env python3
"""Checkpoint077: safely repoint the ONE independent Quiz non-answer continuation.

Original Quiz question/main slot0 about Maruko's daily pocket money has a
continuation text region at PC 0x320DC. The canonical scanner starts INSIDE
that native field at 0x320E8, so byte-editing only the scanner text would
leave the original Japanese 'は' at the beginning. This builder repoints the
WHOLE native continuation record via the exact original pointer at 0x311AF.

An extra 68-byte candidate bank06 record lives immediately AFTER all 81
original answer-candidate reservations 0x36A00..0x37F84. The complete
Vietnamese continuation plus native header+control is 63 bytes, padded to the
conservative 66-byte source-window bound; the final two bytes remain FF.

This is an UNTESTED STATIC PATCH candidate. It does not prove the original
question renderer accepts 25 Vietnamese glyphs. No copyrighted ROM output.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import unicodedata
from pathlib import Path

from build_content_first_040_fortune import apply_ips, make_ips
from build_quiz_relocated_81_jobwait_075 import read_codepage
from plan_quiz_bankcopy_slots_073 import plan as plan_answers

ROOT=Path(__file__).resolve().parent.parent
CLEAN_SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
MANIFEST="translation/runtime/quiz_nonanswer_077_single_continuation.json"
OLD_POINTER_AT=0x311AF
OLD_TEXT_RECORD_AT=0x320DC
SOURCE_SCANNER_AT=0x320E8
NEW_TEXT_RECORD_AT=0x37F84
COPY_BYTES=66
CELL_BYTES=68
ROM_BANK_END=0x38000
PREFIX=bytes.fromhex("0E000F0E202020202020")
END=bytes.fromhex("816F00")
OLD_NATIVE=PREFIX+"は１日いくら？".encode("cp932")+END
PLAIN_CLEAN_IPS_SHA="0deca543c5b7b2b8509766b66c40a0b2f759d94c01a4de83443a7fa9daa6d538"
PLAIN_CLEAN_ROM_SHA="209628345d7fc502dde620ea85a227bfe9ff2c9b538dd551d0a886aabe7bf1aa"

def sha(blob:bytes)->str:
    return hashlib.sha256(blob).hexdigest()

def csv_rows(p:Path):
    with p.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def validate_manifest(root:Path):
    manifest=json.loads((root/MANIFEST).read_text(encoding="utf-8"))
    expected={
        "schema":"chibi.quiz.remaining_nonanswer.077.v1",
        "original_clean_ROM_sha256":CLEAN_SHA,
        "source_offset":"0x320E8",
        "original_physical_record_start":"0x320DC",
        "original_continuation_pointer_word_at":"0x311AF",
        "original_continuation_pointer_16bit":"0xA0DC",
        "staged_context_parent_source_offset":"0x32095",
        "staged_context_parent_stage":"059",
        "selected_full_vietnamese_continuation":"Mỗi ngày Maru có mấy yên?",
        "new_record_glyphs":25,
        "new_record_unpadded_bytes":63,
        "new_record_native_copy_bytes":66,
        "new_record_reserved_cell_bytes":68,
        "experimental_new_record_ROM_at":"0x37F84",
        "experimental_new_pointer_16bit":"0xFF84",
        "original_81_answer_cells_end_exclusive":"0x37F84",
        "remaining_unused_to_bank06_boundary_bytes":56,
    }
    for key,value in expected.items():
        if manifest.get(key)!=value:
            raise AssertionError(f"077 independent Quiz source plan changed: {key}")
    if any(manifest.get(key) is not False for key in (
        "original_one_line_screen_width_tested","emulator_tested",
        "production_or_source_staging_approved")):
        raise AssertionError("077 source-only research may not claim emulator approval")
    canonical=csv_rows(root/manifest["source_csv"])
    selected=[r for r in canonical if int(r["file_offset"],0)==SOURCE_SCANNER_AT]
    if (len(selected)!=1 or
        selected[0]["source_jp_scanner"]!="１日いくら？｛" or
        selected[0]["vi_full"]!="...mỗi ngày là bao nhiêu?"):
        raise AssertionError("Original canonical pocket-money Quiz continuation differs")
    runtime059=json.loads((root/"translation/runtime/quiz_content_first_37_059.json").read_text(encoding="utf-8"))["records"]
    parents=[r for r in runtime059 if int(r["file_offset"],0)==0x32095]
    if (len(parents)!=1 or parents[0]["vi_runtime_lines"]!=
        manifest["staged_parent_runtime_lines"] or
        parents[0]["vi_full_reference"]!=manifest["staged_parent_vi_full_reference"]):
        raise AssertionError("Prior translated Quiz question main/context changed")
    return manifest

def build(clean:bytes,baseline:bytes,root:Path,require_all81:bool):
    if (len(clean)!=0x200000 or sha(clean)!=CLEAN_SHA or
        len(baseline)!=len(clean)):
        raise ValueError("Only original clean 2MiB Japanese SFC / same-sized candidate")
    m=validate_manifest(root)
    cp=read_codepage(root)
    text=m["selected_full_vietnamese_continuation"]
    if text!=unicodedata.normalize("NFC",text):
        raise AssertionError("Vietnamese question continuation not NFC")
    b=bytearray()
    for char in text:
        code=cp.get(char)
        if code is None or len(code)!=4 or not code.startswith("84"):
            raise AssertionError(f"Missing Vietnamese glyph in question: {char!r}")
        b+=bytes.fromhex(code)
    rec=PREFIX+bytes(b)+END
    if len(text)!=25 or len(rec)!=63 or len(OLD_NATIVE)!=27:
        raise AssertionError("Native original/new Quiz question record bounds changed")
    if (clean[OLD_POINTER_AT:OLD_POINTER_AT+2]!=bytes.fromhex("DCA0") or
        clean[OLD_TEXT_RECORD_AT:OLD_TEXT_RECORD_AT+len(OLD_NATIVE)]!=OLD_NATIVE or
        clean[0x37F84:0x37FC8]!=b"\xFF"*68):
        raise AssertionError("Original Quiz question cont/pointer/free bank bytes changed")
    if (baseline[OLD_POINTER_AT:OLD_POINTER_AT+2]!=clean[OLD_POINTER_AT:OLD_POINTER_AT+2] or
        baseline[OLD_TEXT_RECORD_AT:OLD_TEXT_RECORD_AT+len(OLD_NATIVE)]!=OLD_NATIVE or
        baseline[NEW_TEXT_RECORD_AT:NEW_TEXT_RECORD_AT+CELL_BYTES]!=b"\xFF"*CELL_BYTES):
        raise AssertionError("Existing baseline occupies 077 Quiz question slot")
    if require_all81:
        plan=plan_answers(root,clean)
        if len(plan["slots"])!=81 or plan["slots"][-1]["copy_window_end_exclusive"]!=0x37F82:
            raise AssertionError("Complete original Quiz 81-answer allocation changed")
        for option in plan["slots"]:
            off=int(option["pointer_word_ROM"],16)
            expected=int(option["experimental_bank06_CPU_pointer"],16)
            dst=int(option["experimental_dest_ROM"],16)
            if (int.from_bytes(baseline[off:off+2],"little")!=expected or
                baseline[dst:dst+4]!=bytes.fromhex("0E060F12") or
                baseline[dst+COPY_BYTES:dst+CELL_BYTES]!=b"\xFF\xFF"):
                raise AssertionError("77 question candidate requires ALL 81 prior answer pointers already relocated")
    if NEW_TEXT_RECORD_AT+CELL_BYTES>ROM_BANK_END:
        raise AssertionError("077 Quiz question copy would cross LoROM bank06")
    patched=bytearray(baseline)
    patched[OLD_POINTER_AT:OLD_POINTER_AT+2]=bytes.fromhex("84FF")
    patched[NEW_TEXT_RECORD_AT:NEW_TEXT_RECORD_AT+COPY_BYTES]=rec+b"\x00"*(COPY_BYTES-len(rec))
    if patched[NEW_TEXT_RECORD_AT+COPY_BYTES:NEW_TEXT_RECORD_AT+CELL_BYTES]!=b"\xFF\xFF":
        raise AssertionError("77 question copy buffer guard overwritten")
    patched[0x7fdc:0x7fe0]=bytes(4)
    checksum=(sum(patched)+0x1fe)&0xffff
    patched[0x7fdc:0x7fde]=(checksum^0xffff).to_bytes(2,"little")
    patched[0x7fde:0x7fe0]=checksum.to_bytes(2,"little")
    patched=bytes(patched)
    changed={i for i,(a,z) in enumerate(zip(baseline,patched)) if a!=z}
    allowed=(set(range(OLD_POINTER_AT,OLD_POINTER_AT+2))|
             set(range(NEW_TEXT_RECORD_AT,NEW_TEXT_RECORD_AT+COPY_BYTES))|
             set(range(0x7fdc,0x7fe0)))
    if changed-allowed:
        raise AssertionError("077 modifies bytes outside one native source-pointer/record/checksum")
    ips,records=make_ips(clean,patched)
    if apply_ips(clean,ips)!=patched:
        raise AssertionError("077 final clean-source IPS replay failed")
    if baseline==clean:
        if (sha(ips)!=PLAIN_CLEAN_IPS_SHA or sha(patched)!=PLAIN_CLEAN_ROM_SHA or
            len(ips)!=95 or records!=3 or checksum!=0xE9CA or len(changed)!=72):
            raise AssertionError("Independent 077 source-only test fixture SHA drift")
    return ips,{
        "status":"ONE_NEW_INDEPENDENT_QUIZ_QUESTION_CONTINUATION_STATIC_ONLY",
        "original_clean_ROM_sha256":CLEAN_SHA,
        "preexisting_81_full_answer_candidates_verified":require_all81,
        "new_independent_original_Quiz_source_offset":"0x320E8",
        "new_question_main_stage059_source_offset":"0x32095",
        "new_original_pointer_word_repointed":"0x311AF",
        "original_full_Japanese_field_preserved":True,
        "new_full_Vietnamese_question_text":text,
        "new_077_record_ROM":"0x37F84",
        "native_byte_record_unpadded":len(rec),
        "native_question_copy_bytes_reserved":COPY_BYTES,
        "original_bank_bytes_left_to_0x38000":56,
        "SNES_checksum":f"0x{checksum:04X}",
        "candidate_ROM_SHA256":sha(patched),
        "clean_ROM_IPS_SHA256":sha(ips),
        "clean_ROM_IPS_bytes":len(ips),
        "clean_ROM_IPS_records":records,
        "new_byte_differences_vs_input":len(changed),
        "original_Quiz_question_renderer_copy_width_verified":False,
        "original_V2_font_absent_in_clean_retail_ROM":True,
        "SNES_emulator_tested":False,
        "screen_width_or_choice_grading_tested":False,
        "release_approved":False,
        "copyrighted_ROM_written":False,
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("clean_original_Japanese_sfc",type=Path)
    ap.add_argument("--after-81-ips",type=Path,
                    help="Optional cumulative clean-ROM IPS with the full 81-answer relocation")
    ap.add_argument("--project-root",type=Path,default=ROOT)
    ap.add_argument("--ips",type=Path,required=True)
    ap.add_argument("--report",type=Path,required=True)
    ap.add_argument("--allow-untested",action="store_true")
    a=ap.parse_args()
    if not a.allow_untested:
        ap.error("This is an emulator-UNTESTED candidate: pass --allow-untested")
    files=[a.clean_original_Japanese_sfc,a.ips,a.report]
    if a.after_81_ips:files.append(a.after_81_ips)
    if len({p.resolve() for p in files})!=len(files):
        ap.error("Input/output paths must be distinct")
    if a.ips.suffix.lower()!=".ips" or a.report.suffix.lower()!=".json":
        ap.error("Expected IPS + JSON outputs")
    clean=a.clean_original_Japanese_sfc.read_bytes()
    baseline=apply_ips(clean,a.after_81_ips.read_bytes()) if a.after_81_ips else clean
    ips,qa=build(clean,baseline,a.project_root,bool(a.after_81_ips))
    a.ips.parent.mkdir(parents=True,exist_ok=True)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.ips.write_bytes(ips)
    a.report.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(qa,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
