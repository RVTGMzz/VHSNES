#!/usr/bin/env python3
"""Proof-of-addressing ONLY: repoint one Quiz choice into FF-padded bank 06.

This creates two in-memory IPS byte probes (native Japanese longer answer and
V2-encoded Vietnamese answer) and independently replays them on exact clean ROM.
It does NOT save ROM/IPS, pass emulator QA, license ROM distribution, or approve
the original FF region for production relocation. Preserve original record.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import unicodedata
from pathlib import Path
from build_content_first_040_fortune import make_ips,apply_ips
from audit_quiz_pointer_tables_066 import analyze as inspect_tables

ROOT=Path(__file__).resolve().parent.parent
ORIGINAL_SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
POINTER_WORD_OFFSET=0x3123D
OLD_ANSWER_ROM_OFFSET=0x32567
UNAPPROVED_FF_PROBE_OFFSET=0x37FE0
NEW_POINTER=b"\xE0\xFF"
HEADER=b"\x0E\x06\x0F\x12"
TERMINATOR=b"\x81\x6F\x00"
EXPECTED={
    "jp":{"record_bytes":21,"changed_bytes":27,"ips_bytes":50,
          "ips_records":3,"ips_sha256":"29575dfce7b27cfdad91fa1647e07f1dc8032a460fe919bcc2052d58580452a4",
          "rom_sha256":"c014ea1aae6b36b137899687ea65b19134610623ec23fa92d8ace6df4a51f221",
          "checksum":"0x072D"},
    "vi":{"record_bytes":19,"changed_bytes":25,"ips_bytes":48,
          "ips_records":3,"ips_sha256":"339f1426a87bba18fdd227f32e1eb32fe43c534cc722d42934efa1e40d565dc6",
          "rom_sha256":"017db9ebc59190c0dd131d6b175b75c8cc98e42bb05483e4decfcfb8a740b05f",
          "checksum":"0x0637"},
}


def sha(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()


def patch_in_memory(clean:bytes,caption_bytes:bytes,name:str):
    expected=EXPECTED[name]
    record=HEADER+caption_bytes+TERMINATOR
    if len(record)!=expected["record_bytes"]:
        raise AssertionError("Translated relocated Quiz option length changed")
    dest=UNAPPROVED_FF_PROBE_OFFSET
    if clean[dest:dest+len(record)]!=b"\xFF"*len(record):
        raise AssertionError("Probe area no longer original all-FF ROM padding")
    result=bytearray(clean)
    result[POINTER_WORD_OFFSET:POINTER_WORD_OFFSET+2]=NEW_POINTER
    result[dest:dest+len(record)]=record
    result[0x7fdc:0x7fe0]=bytes(4)
    checksum=(sum(result)+0x1fe)&0xffff
    result[0x7fdc:0x7fde]=(checksum^0xffff).to_bytes(2,"little")
    result[0x7fde:0x7fe0]=checksum.to_bytes(2,"little")
    full=bytes(result)
    diff={i for i,(a,b) in enumerate(zip(clean,full)) if a!=b}
    whitelist=(set(range(POINTER_WORD_OFFSET,POINTER_WORD_OFFSET+2))|
               set(range(dest,dest+len(record)))|set(range(0x7fdc,0x7fe0)))
    if diff-whitelist:
        raise AssertionError("Probe touched a byte outside one 16-bit pointer, FF and checksum")
    if (full[OLD_ANSWER_ROM_OFFSET:OLD_ANSWER_ROM_OFFSET+17]!=
        clean[OLD_ANSWER_ROM_OFFSET:OLD_ANSWER_ROM_OFFSET+17]):
        raise AssertionError("Original answer/source text unexpectedly edited")
    ips,records=make_ips(clean,full)
    if (len(diff)!=expected["changed_bytes"] or len(ips)!=expected["ips_bytes"]
        or records!=expected["ips_records"] or sha(ips)!=expected["ips_sha256"]
        or sha(full)!=expected["rom_sha256"]
        or f"0x{checksum:04X}"!=expected["checksum"]
        or apply_ips(clean,ips)!=full):
        raise AssertionError("Unapproved relocation byte/IPS fingerprint drift")
    return {
        "prototype":name,
        "SNES_word_at_0x3123D_after_repoint":"0xFFE0",
        "new_ROM_record_at":"0x37FE0",
        "new_record_length":len(record),
        "source_text_retained":True,
        "changed_bytes":len(diff),
        "in_memory_clean_rom_IPS_bytes":len(ips),
        "in_memory_IPS_records":records,
        "unreleased_IPS_SHA256":sha(ips),
        "unreleased_source_ROM_SHA256":sha(full),
        "SNES_checksum":f"0x{checksum:04X}",
        "replayed_to_exact_clean_original":True,
        "emulator_tested":False,
    }


def run(clean:bytes,root:Path):
    if len(clean)!=0x200000 or sha(clean)!=ORIGINAL_SHA:
        raise ValueError("Only exact original headerless 2MiB Japanese ROM accepted")
    audit=inspect_tables(clean,root)
    choices=audit["references"]["answer_1"]
    answer=[r for r in choices if r["question_id"]==6]
    if (len(answer)!=1 or answer[0]["pointer_word_offset"]!="0x3123D" or
        answer[0]["original_ROM_destination"]!="0x32567" or
        clean[POINTER_WORD_OFFSET:POINTER_WORD_OFFSET+2]!=b"\x67\xA5" or
        clean[OLD_ANSWER_ROM_OFFSET:OLD_ANSWER_ROM_OFFSET+4]!=HEADER or
        clean[OLD_ANSWER_ROM_OFFSET+4:OLD_ANSWER_ROM_OFFSET+14].decode("cp932")!="じてんしゃ" or
        clean[OLD_ANSWER_ROM_OFFSET+14:OLD_ANSWER_ROM_OFFSET+17]!=TERMINATOR):
        raise AssertionError("Original question #6 first-choice pointer/content drift")
    if clean[0x36907:0x38000]!=b"\xFF"*5881:
        raise AssertionError("Original Quiz bank FF padding changed")
    with (root/"translation/codepage/vi_codepage_v4_fe4_native.csv").open(
            encoding="utf-8-sig",newline="") as file:
        cp={r["unicode"]:r["code_hex"] for r in csv.DictReader(file)}
    translated="Xe đạp"
    if unicodedata.normalize("NFC",translated)!=translated:
        raise AssertionError("Non-NFC Vietnamese fixture")
    encoded=bytearray()
    for letter in translated:
        hx=cp.get(letter)
        if not hx or len(hx)!=4 or not hx.startswith("84"):
            raise AssertionError(f"Project's V2 Vietnamese glyph absent {letter!r}")
        encoded.extend(bytes.fromhex(hx))
    if len(encoded)!=12:
        raise AssertionError("Vietnamese full word must use six 2-byte glyphs")
    result=[
        patch_in_memory(clean,"じてんしゃです".encode("cp932"),"jp"),
        patch_in_memory(clean,bytes(encoded),"vi"),
    ]
    return {
        "status":"PASS_SOURCE_BYTE_REPOINT_PROTOTYPE_ONLY_NOT_EMULATOR",
        "original_ROM_sha256":ORIGINAL_SHA,
        "question_index":6,
        "answer_ordinal":1,
        "original_Japanese_answer":"じてんしゃ",
        "Vietnamese_full_answer":"Xe đạp",
        "note":"Unapproved FF end-of-bank probe at 0x37FE0 leaves script-end FF padding intact. A pointer can physically target extended bytes; interpreter behavior and menu/text rendering are NOT proven.",
        "production_relocation_approved":False,
        "compatible_with_original_ROM_Vietnamese_font":False,
        "emulator_tested":False,
        "ROM_or_IPS_written":False,
        "byte_only_trials":result,
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("clean_original_japanese_rom",type=Path)
    ap.add_argument("--project-root",type=Path,default=ROOT)
    ap.add_argument("--report",type=Path)
    args=ap.parse_args()
    result=run(args.clean_original_japanese_rom.read_bytes(),args.project_root)
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
