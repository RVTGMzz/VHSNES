#!/usr/bin/env python3
"""Checkpoint078: original-pointer-anchored Quiz explanation patch (STATIC ONLY).

Original scanner IDs 0x35A69 and 0x33B8D were classified unsafe in 063/077,
but the *physical* explanation records at 0x35A58 and 0x33B8A have authentic
bank06 LoROM pointer-table references at 0x3136B and 0x31453.

Translate glyphs ONLY within original existing line capacities (13/14/9,3).
Preserve original text-control headers, native 81 6F markers, layout spaces,
pointer words, adjacent stage057/058 translations and original gameplay bytes.
No font ROM or emulator tested. Output cumulative CLEAN-ROM-relative IPS only.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import unicodedata
from pathlib import Path
from build_content_first_040_fortune import make_ips,apply_ips
from build_quiz_relocated_81_jobwait_075 import read_codepage

ROOT=Path(__file__).resolve().parent.parent
CLEAN_SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
MANIFEST="translation/runtime/quiz_nonanswer_reanchored_078.json"
ORIGINAL_SOURCE_SHA="b1ae53c74a04bf69cde9c4aaa708cc6b53d20eea7a3f80c25a81a97a24daf421"
ORIGINAL_SOURCE_IPS_SHA="f560fb8b326b2f4185f7c0b4da149ebe0dee576a40b4ec28d32f375de1241e97"
LINE_SLOTS=(
 (0x35A64,13,"４月１日エイプリルフールに","Cá tháng Tư"),
 (0x35A86,14,"まる子とおじいちゃんは、山田","Maru và ông"),
 (0x35AAA,9,"くんをだまそうとす","lừa cậu."),
 (0x33B94,3,"年生。","đó."),
)
RECORDS=(
 (0x35A58,0x3136B,0xDA58,b"\x0e\x00\x0f\x08",0x35A64),
 (0x33B8A,0x31453,0xBB8A,b"\x0e\x00\x0f\x14",0x33B94),
)

def sha(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()

def validate_manifest(root:Path):
    m=json.loads((root/MANIFEST).read_text(encoding="utf-8"))
    if (m.get("schema")!="chibi.quiz.pointer_reanchored_nonanswers_078.v1" or
        m.get("original_rom_sha256")!=CLEAN_SHA or len(m.get("fields",[]))!=2 or
        m.get("emulator_tested") is not False or
        m.get("approved_for_gameplay") is not False):
        raise AssertionError("078 original-script field lineage or approval flags changed")
    expected=(
        ("0x35A58","0x3136B","0x35A69",[13,14,9],
         ["Cá tháng Tư","Maru và ông","lừa cậu."]),
        ("0x33B8A","0x31453","0x33B8D",[3],["đó."]),
    )
    for data,(record,pointer,scanner,caps,vi) in zip(m["fields"],expected):
        if (data.get("native_record_start")!=record or
            data.get("original_pointer_word_at")!=pointer or
            data.get("scanner_alias")!=scanner or
            data.get("original_glyph_capacities")!=caps or
            data.get("vi_runtime_lines")!=vi):
            raise AssertionError("078 source-to-native field mapping drift")
    return m

def build(clean:bytes,baseline:bytes,root:Path):
    if len(clean)!=0x200000 or sha(clean)!=CLEAN_SHA or len(baseline)!=len(clean):
        raise ValueError("Requires exact original unheadered 2MiB Japanese ROM")
    m=validate_manifest(root)
    mapping=read_codepage(root)
    for start,word,ptr,prefix,first in RECORDS:
        if (clean[start:start+4]!=prefix or
            int.from_bytes(clean[word:word+2],"little")!=ptr or
            baseline[start:start+4]!=prefix or
            baseline[word:word+2]!=clean[word:word+2]):
            raise AssertionError(f"Original explanation pointer/native prefix changed at {start:05X}")
    staged058=json.loads(
        (root/"translation/runtime/quiz_content_first_67_058.json").read_text(
            encoding="utf-8"))["records"]
    previous=[r for r in staged058 if int(r["file_offset"],0)==0x33B3B]
    if len(previous)!=1 or "lớp 3" not in previous[0]["vi_runtime_lines"]:
        raise AssertionError("Existing stage058 translation must include the full grade")
    patched=bytearray(baseline)
    allow=set(range(0x7FDC,0x7FE0))
    fields=[]
    for offset,capacity,japanese,vietnamese in LINE_SLOTS:
        original=japanese.encode("cp932")
        if len(original)!=capacity*2 or clean[offset:offset+len(original)]!=original:
            raise AssertionError(f"Original native Japanese glyph cells drifted: {offset:05X}")
        if baseline[offset:offset+len(original)]!=original:
            raise AssertionError("Already integrated overlay occupies one of the 078 glyph slots")
        if vietnamese!=unicodedata.normalize("NFC",vietnamese):
            raise AssertionError("Vietnamese 078 text must be NFC")
        glyphs=bytearray()
        for character in vietnamese:
            value=mapping.get(character)
            if value is None or len(value)!=4 or not value.startswith("84"):
                raise AssertionError(f"Missing approved V2 glyph {character!r}")
            glyphs.extend(bytes.fromhex(value))
        if len(glyphs)>capacity*2:
            raise AssertionError(f"078 translated explanation overflow at {offset:05X}")
        padding=bytes.fromhex(mapping[" "])*(capacity-len(vietnamese))
        new=bytes(glyphs)+padding
        if len(new)!=len(original):
            raise AssertionError("078 full native glyph cell width changed")
        patched[offset:offset+len(new)]=new
        allow.update(range(offset,offset+len(new)))
        fields.append({"original_glyph_ROM_offset":f"0x{offset:X}",
                       "original_Japanese":japanese,"translated_full_Vietnamese":vietnamese,
                       "fixed_original_glyph_capacity":capacity,
                       "used_Vietnamese_glyphs":len(vietnamese),
                       "padding_space_glyphs":capacity-len(vietnamese)})
    patched[0x7FDC:0x7FE0]=bytes(4)
    checksum=(sum(patched)+0x1FE)&0xFFFF
    patched[0x7FDC:0x7FDE]=(checksum^0xFFFF).to_bytes(2,"little")
    patched[0x7FDE:0x7FE0]=checksum.to_bytes(2,"little")
    final=bytes(patched)
    changed={i for i,(a,b) in enumerate(zip(baseline,final)) if a!=b}
    if changed-allow:
        raise AssertionError("Unexpected binary modified outside 2 native Quiz records")
    ips,records=make_ips(clean,final)
    if apply_ips(clean,ips)!=final:
        raise AssertionError("078 source-relative IPS replay failed")
    if baseline==clean and (len(changed)!=82 or len(ips)!=115 or records!=5 or
                            checksum!=0x0A44 or sha(final)!=ORIGINAL_SOURCE_SHA or
                            sha(ips)!=ORIGINAL_SOURCE_IPS_SHA):
        raise AssertionError("Independent original Japanese ROM 078 byte fingerprint drift")
    return ips,{
        "status":"PASS_TWO_ORIGINAL_POINTER_ANCHORED_QUIZ_EXPLANATIONS_STATIC_ONLY",
        "original_ROM_sha256":CLEAN_SHA,
        "clean_ROM_IPS_sha256":sha(ips),
        "clean_ROM_IPS_bytes":len(ips),
        "clean_ROM_IPS_records":records,
        "final_candidate_ROM_sha256":sha(final),
        "LoROM_checksum":f"0x{checksum:04X}",
        "new_native_explanation_fields_prepared":2,
        "original_offending_scanner_aliases":["0x35A69","0x33B8D"],
        "source_line_details":fields,
        "native_control_bytes_unchanged":True,
        "original_control_flow_and_pointer_bytes_unchanged":True,
        "source_only_candidate_not_gameplay_accepted":True,
        "emulator_tested":False,
        "VN_V2_font_in_original_retail_ROM":False,
        "release_approved":False,
        "copyrighted_ROM_written":False,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("original_clean_Japanese_sfc",type=Path)
    p.add_argument("--baseline-ips",type=Path)
    p.add_argument("--project-root",type=Path,default=ROOT)
    p.add_argument("--ips",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--allow-untested",action="store_true")
    args=p.parse_args()
    if not args.allow_untested:
        p.error("This is untested by a SNES emulator: pass --allow-untested")
    paths=[args.original_clean_Japanese_sfc,args.ips,args.report]
    if args.baseline_ips:paths.append(args.baseline_ips)
    if len({x.resolve() for x in paths})!=len(paths):
        p.error("Do not overwrite source SFC, existing IPS or QA JSON")
    clean=args.original_clean_Japanese_sfc.read_bytes()
    baseline=apply_ips(clean,args.baseline_ips.read_bytes()) if args.baseline_ips else clean
    ips,qa=build(clean,baseline,args.project_root)
    args.ips.parent.mkdir(parents=True,exist_ok=True)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.ips.write_bytes(ips)
    args.report.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(qa,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
