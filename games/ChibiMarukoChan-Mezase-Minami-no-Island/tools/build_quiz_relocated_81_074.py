#!/usr/bin/env python3
"""Build complete 81-choice Quiz relocation IPS (EXPERIMENT, NOT PLAYABLE).

Uses true original ROM byte-verified 65c816 66-byte answer copy contract and
full canonical source Vietnamese text. Each answer gets a separate 68-byte
bank06 cell: 4-byte native header + 2-byte V2/CP932 glyphs + 81 6F 00 end,
then zero padding to cover ALL 66 bytes the original engine reads. The two
extra FF bytes per cell are an untouched guard.

Accepts clean original source only, or a previously cumulative Vietnamese
checkpoint061 IPS + its verified QA report. Rebuilds a CLEAN-ROM-based IPS
without distributing copyrighted original ROM/font bytes.

This is static byte-level integration only: the game is NOT emulator-tested.
Never call it a release or assume wide Quiz options fit the visual menu.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import unicodedata
from pathlib import Path

from build_content_first_040_fortune import apply_ips, make_ips
from plan_quiz_bankcopy_slots_073 import (
    plan as plan_073, START, END, CELL_BYTES, NATIVE_COPY_BYTES,
)

ROOT=Path(__file__).resolve().parent.parent
ORIGINAL_SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
EXPECT_CLEAN_ONLY_IPS_SHA="58f284de922c3e44d2616c0de73918f6a2a86ee552c19cdc4e2cc51643f5f109"
EXPECT_CLEAN_ONLY_ROM_SHA="5b8ed66e2ed43936703b99393607c552b5e3697d59eb22e4b3cb6ee94ed23aaa"
PREFIX=bytes.fromhex("0E 06 0F 12")
TERMINATOR=bytes.fromhex("81 6F 00")
EXPECTED_COUNT=81
KANJI={"一","和","雄"}

def sha(blob:bytes)->str:
    return hashlib.sha256(blob).hexdigest()

def read_codepage(project:Path):
    with (project/"translation/codepage/vi_codepage_v4_fe4_native.csv").open(
        encoding="utf-8-sig",newline="") as f:
        records=list(csv.DictReader(f))
    result={row["unicode"]:row["code_hex"] for row in records}
    if len(records)!=160 or len(result)!=160 or result.get(" ")!="8440":
        raise AssertionError("The reviewed 160-V2-glyph codepage has changed")
    for ch,code in result.items():
        if len(code)!=4 or not code.startswith("84") or len(bytes.fromhex(code))!=2:
            raise AssertionError(f"Unexpected V2 glyph byte value {ch!r}: {code!r}")
    return result

def encode_full(text:str,mapping:dict[str,str],source:int)->tuple[bytes,int]:
    if not text or text!=unicodedata.normalize("NFC",text):
        raise AssertionError("Non-NFC or blank full Vietnamese Quiz label")
    out=bytearray()
    native_count=0
    for ch in text:
        if ch in mapping:
            out+=bytes.fromhex(mapping[ch])
        else:
            if ch not in KANJI or source not in (0x33DDF,0x33DFD):
                raise AssertionError(f"Unexpected unsupported glyph {ch!r} at 0x{source:X}")
            cp=ch.encode("cp932")
            if len(cp)!=2:
                raise AssertionError("Native Kanji must be exact 2-byte CP932")
            out+=cp
            native_count+=1
    return bytes(out),native_count

def build(clean:bytes,baseline:bytes,project:Path,stage:str):
    if len(clean)!=0x200000 or sha(clean)!=ORIGINAL_SHA:
        raise ValueError("Exact original headerless Japanese 2MiB SFC is required")
    if len(baseline)!=len(clean):
        raise ValueError("Baseline ROM must remain exactly 2MiB")
    if stage not in ("clean_source_only","cumulative_V2_061"):
        raise ValueError("Unknown baseline lineage; never mix unrelated ROMs")

    source_qa=plan_073(project,clean)
    slots=source_qa["slots"]
    if (len(slots)!=EXPECTED_COUNT or
        source_qa["summary"]["original_rom_copier_and_pointer_contract_checked"] is not True
        or source_qa["summary"]["max_payload_record_size"]!=53
        or source_qa["summary"]["remaining_bank_end_bytes"]!=124):
        raise AssertionError("81 original source records or bank06 copy contract changed")
    mapping=read_codepage(project)

    patched=bytearray(baseline)
    allowed=set(range(0x7fdc,0x7fe0))
    table_entries=[]
    kanji_count=0
    for index,row in enumerate(slots):
        off=int(row["source_offset"],16)
        pointer_off=int(row["pointer_word_ROM"],16)
        dst=int(row["experimental_dest_ROM"],16)
        text=row["source_full_vietnamese"]
        expected_ptr=0x8000+(off-4-0x30000)
        destination_ptr=0x8000+(dst-0x30000)
        if (dst!=START+index*CELL_BYTES or
            not 0x8000<=destination_ptr<=0xFFFF or
            not 0x8000<=expected_ptr<=0xFFFF):
            raise AssertionError("Wrong ordered original source or destination")
        if (clean[pointer_off:pointer_off+2]!=expected_ptr.to_bytes(2,"little")
            or baseline[pointer_off:pointer_off+2]!=clean[pointer_off:pointer_off+2]
            or clean[off-4:off]!=PREFIX
            or baseline[off-4:off]!=clean[off-4:off]):
            raise AssertionError(f"Previous baseline changed original pointer at 0x{off:X}")
        old_terminal=clean.find(TERMINATOR,off,off+160)
        if (old_terminal<0 or
            baseline[off-4:old_terminal+len(TERMINATOR)]!=
                clean[off-4:old_terminal+len(TERMINATOR)]):
            raise AssertionError("Previous localization rewrote one of the 81 independent sources")
        if baseline[dst:dst+CELL_BYTES]!=b"\xFF"*CELL_BYTES:
            raise AssertionError("Previous localization occupied reserved bank06 source cell")
        if len(text)!=row["record_size"]//2:
            # A record has 7 fixed control bytes and 2 bytes per character:
            # use a direct guard below rather than infer from record length.
            if 7+2*len(text)!=row["record_size"]:
                raise AssertionError("Full Vietnamese glyph count/source records changed")
        payload,native=encode_full(text,mapping,off)
        kanji_count+=native
        record=PREFIX+payload+TERMINATOR
        if len(record)!=row["record_size"] or len(record)>NATIVE_COPY_BYTES:
            raise AssertionError("Full choice does not fit reserved original 66-byte copy window")
        full_copied=record+b"\x00"*(NATIVE_COPY_BYTES-len(record))
        if len(full_copied)!=66 or patched[dst:dst+CELL_BYTES]!=b"\xFF"*CELL_BYTES:
            raise AssertionError("Source memory bank must be unused full 68-byte cell")
        patched[dst:dst+NATIVE_COPY_BYTES]=full_copied
        patched[pointer_off:pointer_off+2]=destination_ptr.to_bytes(2,"little")
        allowed.update(range(dst,dst+NATIVE_COPY_BYTES))
        allowed.update(range(pointer_off,pointer_off+2))
        table_entries.append({
            "original_Japanese_source_offset":f"0x{off:X}",
            "original_answer_pointer_word_ROM":f"0x{pointer_off:X}",
            "translated_word_bank06_CPU_pointer":f"0x{destination_ptr:04X}",
            "full_canonical_Vietnamese":text,
            "native_copy_source_ROM":f"0x{dst:X}",
            "native_COPIED_bytes":NATIVE_COPY_BYTES,
            "record_glyph_count":len(text),
            "record_bytes_before_zero_padding":len(record),
        })
    if kanji_count!=4:
        raise AssertionError("Distinct original Kazuo Kanji alternatives no longer intact")
    if not all(patched[START+i*CELL_BYTES+NATIVE_COPY_BYTES:
                       START+(i+1)*CELL_BYTES]==b"\xFF\xFF"
               for i in range(EXPECTED_COUNT)):
        raise AssertionError("Two-byte FF guard after a 66-byte copy cell modified")

    patched[0x7fdc:0x7fe0]=bytes(4)
    checksum=(sum(patched)+0x1fe)&0xFFFF
    patched[0x7fdc:0x7fde]=(checksum^0xFFFF).to_bytes(2,"little")
    patched[0x7fde:0x7fe0]=checksum.to_bytes(2,"little")
    final_rom=bytes(patched)
    changed={i for i,(a,b) in enumerate(zip(baseline,final_rom)) if a!=b}
    if changed-allowed:
        raise AssertionError("Quiz builder touched byte outside 81 private copies/pointers/checksum")
    ips,nrecords=make_ips(clean,final_rom)
    if apply_ips(clean,ips)!=final_rom:
        raise AssertionError("Clean original ROM IPS cannot reproduce the full result")

    if stage=="clean_source_only":
        if (checksum!=0x1C5D or
            len(changed)!=5511 or len(ips)!=6139 or nrecords!=124 or
            sha(ips)!=EXPECT_CLEAN_ONLY_IPS_SHA or
            sha(final_rom)!=EXPECT_CLEAN_ONLY_ROM_SHA):
            raise AssertionError("Independent 81-option clean Japanese ROM fingerprint drift")
    report={
        "status":"SOURCE_BYTE_81_FULL_QUIZ_RELOCATION_STATIC_ONLY",
        "baseline_stage":stage,
        "clean_original_ROM_sha256":ORIGINAL_SHA,
        "baseline_ROM_sha256":sha(baseline),
        "candidate_ROM_sha256":sha(final_rom),
        "cumulative_clean_ROM_IPS_sha256":sha(ips),
        "cumulative_clean_ROM_IPS_bytes":len(ips),
        "cumulative_clean_ROM_IPS_records":nrecords,
        "canonical_full_Quiz_answer_records":len(slots),
        "native_Japanese_Kanji_2byte_glyph_occurrences":kanji_count,
        "independent_disjoint_source_cell_size":CELL_BYTES,
        "engine_fixed_copy_window_bytes":NATIVE_COPY_BYTES,
        "changed_byte_count_vs_baseline":len(changed),
        "recomputed_SNES_checksum":f"0x{checksum:04X}",
        "original_Japanese_answer_string_records_preserved":True,
        "V2_font_present_in_original_clean_ROM":False,
        "mixed_Japanese_Vietnamese_rendering_tested":False,
        "SNES_emulator_tested":False,
        "80_plus_visual_width_acceptance_passed":False,
        "release_approved":False,
        "already_staged_Quiz_source_progress_changed":False,
        "no_commercial_ROM_written":True,
        "candidate_choices":table_entries,
    }
    return ips,report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("original_clean_sfc",type=Path)
    p.add_argument("--baseline-ips",type=Path,
        help="Optional known-good cumulative 061 IPS (requires --baseline-qa-json)")
    p.add_argument("--baseline-qa-json",type=Path)
    p.add_argument("--project-root",type=Path,default=ROOT)
    p.add_argument("--ips",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--allow-untested",action="store_true")
    a=p.parse_args()
    if not a.allow_untested:
        p.error("Real SNES gameplay NOT tested: explicitly pass --allow-untested")
    if bool(a.baseline_ips)!=bool(a.baseline_qa_json):
        p.error("Cumulative 061 IPS and its SHA-bearing QA JSON must be provided together")
    all_paths=[a.original_clean_sfc,a.ips,a.report]
    if a.baseline_ips:all_paths.extend([a.baseline_ips,a.baseline_qa_json])
    if len({x.resolve() for x in all_paths})!=len(all_paths):
        p.error("Never overwrite original ROM, IPS source or report inputs")
    if a.ips.suffix.lower()!=".ips" or a.report.suffix.lower()!=".json":
        p.error("Outputs must be IPS and JSON only")
    clean=a.original_clean_sfc.read_bytes()
    baseline=clean
    stage="clean_source_only"
    if a.baseline_ips:
        baseline=apply_ips(clean,a.baseline_ips.read_bytes())
        official_qa=json.loads(a.baseline_qa_json.read_text(encoding="utf-8"))
        if (official_qa.get("result_061_ROM_sha256")!=sha(baseline) or
            official_qa.get("emulator_tested") is True):
            raise AssertionError("Missing/incorrect 061 lineage or unverified report")
        stage="cumulative_V2_061"
    ips,report=build(clean,baseline,a.project_root,stage)
    # Outputs only after full byte, source, pointer, checksum and replay QA.
    a.ips.parent.mkdir(parents=True,exist_ok=True)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.ips.write_bytes(ips)
    a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:report[k] for k in (
        "status","baseline_stage","candidate_ROM_sha256",
        "cumulative_clean_ROM_IPS_sha256","cumulative_clean_ROM_IPS_bytes",
        "SNES_emulator_tested","release_approved")},ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
