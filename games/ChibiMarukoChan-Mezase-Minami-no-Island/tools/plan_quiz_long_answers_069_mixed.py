#!/usr/bin/env python3
"""Checkpoint 069: in-memory, NON-PLAYABLE hybrid CP932/V2 Quiz proof.

Repack all canonical Vietnamese choices retaining original native Kanji into an
unapproved 4KiB end-of-bank FF region. Rigorously verify all 81 16-bit pointer
changes, original text/control preservation, checksum and clean-ROM IPS replay.

This is a planning/research proof only. Never write the copyrighted ROM or an
unreviewed playable-patch claim; optional output is JSON diagnostics only.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,unicodedata
from pathlib import Path
from build_content_first_040_fortune import make_ips,apply_ips
from build_quiz_answer_atlas_065 import analyze as quiz_atlas
from audit_quiz_pointer_tables_066 import analyze as inspect_tables

ROOT=Path(__file__).resolve().parent.parent
CLEAN_SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
RELOCATION_START,RELOCATION_END=0x37000,0x38000
EXPECTED_IPS_SHA="3777df4895046d8342d421f8da5d2ccabdfd01cec7b5f8e567759ba1d4e5c213"
EXPECTED_ROM_SHA="c61471d70f0025e075d6dd94366940bc8990e1cfc910cf99f421dc15ff47f184"
RECORD_PREFIX=b"\x0e\x06\x0f\x12"
RECORD_END=b"\x81\x6f\x00"

def sha(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()

def load_csv(p:Path):
    with p.open(encoding="utf-8-sig",newline="") as file:
        return list(csv.DictReader(file))

def plan(clean:bytes,root:Path):
    if len(clean)!=0x200000 or sha(clean)!=CLEAN_SHA:
        raise ValueError("Requires exact original Japanese 2MiB Chibi SFC ROM")
    if clean[0x36907:RELOCATION_END]!=b"\xff"*(RELOCATION_END-0x36907):
        raise AssertionError("Original end-of-bank FF region changed")
    verified=inspect_tables(clean,root)
    atlas=quiz_atlas(clean,root)
    refs={}
    for field in ("answer_1","answer_2","answer_3"):
        for record in verified["references"][field]:
            header=int(record["original_ROM_destination"],16)
            p=int(record["pointer_word_offset"],16)
            if clean[header:header+4]!=RECORD_PREFIX:
                raise AssertionError("Original answer prefix differs from native source")
            answer_addr=header+4
            if answer_addr in refs:
                raise AssertionError("Quiz answer source address in multiple pointer tables")
            refs[answer_addr]={"pointer_word":p,"question":record["question_id"],
                               "ordinal":int(field[-1])}
    if len(refs)!=150:
        raise AssertionError("Did not establish all 150 original answer references")
    all_choices={}
    for block in atlas["blocks"]:
        for opt in block["answer_choices"]:
            addr=int(opt["original_file_offset"],16)
            if addr in all_choices:
                raise AssertionError("Duplicate original Quiz answer source record")
            all_choices[addr]=opt
    if set(all_choices)!=set(refs):
        raise AssertionError("Canonical Quiz atlas differs from nine pointer arrays")
    with (root/"translation/codepage/vi_codepage_v4_fe4_native.csv").open(
        encoding="utf-8-sig",newline="") as file:
        glyph_map={x["unicode"]:x["code_hex"] for x in csv.DictReader(file)}
    if glyph_map.get(" ")!="8440":
        raise AssertionError("Existing Vietnamese 0x84 codepage changed")

    pending={addr:r for addr,r in all_choices.items()
             if r["already_prepared_stage"] is None}
    if len(pending)!=81:
        raise AssertionError("Expected exactly 81 yet-unprepared original Quiz answers")
    out=bytearray(clean)
    cursor=RELOCATION_START
    expected_writes=set(range(0x7fdc,0x7fe0))
    planned=[]
    deferred=[]
    native_kanji_char_count=0
    native_kanji_choices=set()
    for original_addr,opt in sorted(pending.items()):
        full=opt["canonical_full_vietnamese"]
        if unicodedata.normalize("NFC",full)!=full:
            raise AssertionError(f"Non-NFC canonical Vietnamese {original_addr:X}")
        missing=sorted(set(c for c in full if c not in glyph_map))
        # Two quiz alternatives differ ONLY in their original Japanese Kanji.
        # The original ROM demonstrably contains these native CP932 pairs.
        # A future real Vietnamese V2 font ROM still must be checked to ensure
        # native Japanese CP932 glyphs survive alongside 0x84xx Vietnamese.
        allowed_native={"一","和","雄"}
        if missing and (set(missing)-allowed_native or original_addr not in (0x33DDF,0x33DFD)):
            deferred.append({"original_answer_file_offset":f"0x{original_addr:X}",
                             "canonical_full_vietnamese":full,
                             "unsupported_not_approved_for_mixed_encoding":missing})
            continue
        if missing:
            native_kanji_choices.add(original_addr)
        payload=bytearray()
        for char in full:
            code=glyph_map.get(char)
            if code is not None:
                if len(code)!=4 or not code.startswith("84"):
                    raise AssertionError(f"Invalid Vietnamese glyph code for {char!r}")
                payload.extend(bytes.fromhex(code))
            else:
                if char not in allowed_native:
                    raise AssertionError(f"Non-whitelisted CP932 character {char!r}")
                native=char.encode("cp932")
                if (len(native)!=2 or clean[0x31c00:0x36907].count(native)<3):
                    raise AssertionError(f"Native Quiz source Kanji unconfirmed {char!r}")
                payload.extend(native)
                native_kanji_char_count+=1
        record=RECORD_PREFIX+bytes(payload)+RECORD_END
        if cursor & 1:
            cursor+=1
        if cursor+len(record)>RELOCATION_END or (
            clean[cursor:cursor+len(record)]!=b"\xff"*len(record)):
            raise AssertionError("Experimental bank06 relocation capacity overflow")
        source=refs[original_addr]
        pointer_off=source["pointer_word"]
        old_pointer=int.from_bytes(clean[pointer_off:pointer_off+2],"little")
        source_header=0x30000+old_pointer-0x8000
        if source_header+4!=original_addr:
            raise AssertionError("Original answer pointer/source relationship changed")
        new_snes=0x8000+(cursor-0x30000)
        if not 0x8000<=new_snes<=0xffff:
            raise AssertionError("Relocation crosses a bank06 16-bit pointer boundary")
        out[pointer_off:pointer_off+2]=new_snes.to_bytes(2,"little")
        out[cursor:cursor+len(record)]=record
        expected_writes.update(range(pointer_off,pointer_off+2))
        expected_writes.update(range(cursor,cursor+len(record)))
        planned.append({
            "question_index_original_ROM":source["question"],
            "answer_ordinal":source["ordinal"],
            "original_file_offset":f"0x{original_addr:X}",
            "original_16bit_pointer_word_at":f"0x{pointer_off:X}",
            "new_bank06_CPU_pointer":f"0x{new_snes:04X}",
            "unapproved_new_record_ROM_offset":f"0x{cursor:X}",
            "full_canonical_vietnamese":full,
            "v2_glyph_count":len(full),
            "full_new_record_bytes":len(record),
            "original_choice_text_preserved":True,
            "emulator_rendering_approved":False,
        })
        cursor+=len(record)
    if len(planned)!=81 or len(deferred)!=0:
        raise AssertionError("Missing original answer, unsupported glyph or candidate count drift")
    expected_native={0x33DDF,0x33DFD}
    if (native_kanji_choices!=expected_native or native_kanji_char_count!=4):
        raise AssertionError("Two Japanese-original names/4 distinctive CP932 Kanji not retained")
    if cursor!=0x3797F or cursor-RELOCATION_START!=2431:
        raise AssertionError("Original clean-ROM 79-answer packing layout changed")
    if out[0x36907:RELOCATION_START]!=clean[0x36907:RELOCATION_START]:
        raise AssertionError("Reassigned previously reserved script-end padding")
    for r in planned:
        addr=int(r["original_file_offset"],16)
        if out[addr:addr+8]!=clean[addr:addr+8]:
            raise AssertionError("Original in-place Japanese answer was overwritten")
    # Recompute standard SNES LoROM checksum while preserving all other bytes.
    out[0x7fdc:0x7fe0]=bytes(4)
    checksum=(sum(out)+0x1fe)&0xffff
    out[0x7fdc:0x7fde]=(checksum^0xffff).to_bytes(2,"little")
    out[0x7fde:0x7fe0]=checksum.to_bytes(2,"little")
    preview=bytes(out)
    changed={i for i,(a,b) in enumerate(zip(clean,preview)) if a!=b}
    if len(changed)!=2517 or changed-expected_writes:
        raise AssertionError("Unapproved changed ROM bytes in experimental Quiz batch")
    patch,count=make_ips(clean,preview)
    if (count!=124 or len(patch)!=3145 or sha(patch)!=EXPECTED_IPS_SHA
        or sha(preview)!=EXPECTED_ROM_SHA or checksum!=0xc3bc
        or apply_ips(clean,patch)!=preview):
        raise AssertionError("Exact original clean-ROM 79-answer IPS replay/QA drift")
    return {"summary":{
        "status":"PASS_SOURCE_ROM_81_CHOICE_HYBRID_REPACK_NO_EMULATOR",
        "source_clean_ROM_sha256":CLEAN_SHA,
        "unprepared_native_Quiz_answers":len(pending),
        "full_Vietnamese_and_native_Kanji_byte_encoded":len(planned),
        "two_names_with_distinct_original_CP932_kanji":len(native_kanji_choices),
        "original_CP932_kanji_2byte_glyphs":native_kanji_char_count,
        "mixed_V2_CP932_renderer_compatibility_tested":False,
        "full_Vietnamese_blocked_by_legacy_codepage":len(deferred),
        "unapproved_4KiB_storage_start":f"0x{RELOCATION_START:X}",
        "unapproved_used_through_exclusive":f"0x{cursor:X}",
        "unapproved_storage_used_bytes":cursor-RELOCATION_START,
        "unapproved_storage_remaining_bytes":RELOCATION_END-cursor,
        "exact_original_16bit_pointer_updates":len(planned),
        "source_only_rom_byte_differences":len(changed),
        "in_memory_IPS_records":count,"in_memory_IPS_bytes":len(patch),
        "in_memory_IPS_sha256":sha(patch),
        "in_memory_full_ROM_sha256":sha(preview),
        "recomputed_SNES_checksum":f"0x{checksum:04X}",
        "all_source_records_retained":True,
        "production_quiz_entry_approved":False,
        "original_clean_japanese_ROM_has_Vietnamese_font":False,
        "integrated_with_missing_043_IPS":False,
        "gameplay_or_renderer_tested":False,
        "binary_ROM_or_IPS_file_written":False,
    },"unapproved_relocation_candidates":planned,
      "blocked_by_missing_glyphs":deferred}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("original_clean_japanese_ROM",type=Path)
    ap.add_argument("--project-root",type=Path,default=ROOT)
    ap.add_argument("--json-report",type=Path)
    args=ap.parse_args()
    report=plan(args.original_clean_japanese_ROM.read_bytes(),args.project_root)
    if args.json_report:
        args.json_report.parent.mkdir(parents=True,exist_ok=True)
        args.json_report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",
                                   encoding="utf-8")
    print(json.dumps(report["summary"],ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
