#!/usr/bin/env python3
"""Checkpoint080: restore 3 Quiz semantic details in verified original V2 glyph slots.

Corrects "Sang đợt ba" -> "Học kỳ 3" (school term), restores actual
"Bộ ba hạng B / Hamaji Buutaro" trivia, and describes Maruo's mother as
"rất hiền lành" per original やさしい, NOT an invented mother/son affection.

Overlay must apply to 061+075+077+078+079 combined V2-font candidate,
NEVER alter old original 054/058 stage manifests or their pinned SHA hashes.
No SNES gameplay/rendering acceptance is implied by original-ROM byte QA.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import unicodedata
from pathlib import Path

from build_content_first_040_fortune import apply_ips, make_ips

ROOT = Path(__file__).resolve().parent.parent
ORIGINAL_SHA = "e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
MANIFEST = "translation/runtime/quiz_parent_semantic_restore_080.json"
STAGE_MANIFESTS = {
    "054": "translation/runtime/quiz_content_first_54_054.json",
    "057": "translation/runtime/quiz_content_first_50_057.json",
    "058": "translation/runtime/quiz_content_first_67_058.json",
    "059": "translation/runtime/quiz_content_first_37_059.json",
}
NATIVE = {
    0x32C09: (0x32C05, 0x313BD, "058", [(0x32C0F,13),(0x32C31,8),(0x32C49,6)]),
    0x330E9: (0x330E5, 0x3114F, "058", [(0x330EF,13),(0x33111,14)]),
    0x353D6: (0x353D2, 0x313A7, "054", [(0x353DC,14),(0x35400,14),(0x35424,13)]),
}
EXPECTED_PATCHED_SOURCE_ALIASES = {0x32C15,0x33119,0x353F3}

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def read_codepage(root: Path) -> dict[str,str]:
    with (root/"translation/codepage/vi_codepage_v4_fe4_native.csv").open(
        encoding="utf-8-sig",newline="") as stream:
        rows=list(csv.DictReader(stream))
    values={row["unicode"]:row["code_hex"] for row in rows}
    if len(values)!=160 or len(rows)!=160 or values.get(" ")!="8440":
        raise AssertionError("Unapproved version of existing V2 font codepage")
    return values

def encode(text: str, capacity: int, mapping: dict[str,str]) -> bytes:
    if not isinstance(text,str) or text!=unicodedata.normalize("NFC",text):
        raise AssertionError("Quiz caption is not normalized NFC Vietnamese")
    if len(text)>capacity:
        raise AssertionError(f"Quiz caption ({text!r}) exceeds {capacity} glyph cells")
    result=bytearray()
    for char in text+" "*(capacity-len(text)):
        hx=mapping.get(char)
        if hx is None or len(hx)!=4 or not hx.startswith("84"):
            raise AssertionError(f"Missing official V2 glyph for {char!r}")
        result.extend(bytes.fromhex(hx))
    if len(result)!=2*capacity:
        raise AssertionError("Unchanged original caption-cell width violated")
    return bytes(result)

def audit(root: Path) -> dict:
    plan=json.loads((root/MANIFEST).read_text(encoding="utf-8"))
    if (plan.get("schema")!="chibi.quiz.parent_semantic_restore.080.v1" or
        plan.get("original_clean_ROM_sha256")!=ORIGINAL_SHA or
        len(plan.get("records",[]))!=3 or
        plan.get("change_original_054_058_manifests") is not False or
        plan.get("SNES_emulator_tested") is not False or
        plan.get("release_approved") is not False):
        raise AssertionError("Checkpoint080 canonical provenance or release flag drift")
    actual={r["historical_stage"] for r in plan["records"]}
    if actual!={"054","058"}:
        raise AssertionError("Wrong previous stage dependencies")
    older={}
    for stage,path in STAGE_MANIFESTS.items():
        records=json.loads((root/path).read_text(encoding="utf-8"))["records"]
        older[stage]={int(r["file_offset"],0):r for r in records}
    prior_lookup=older
    # All 12 remaining scanner aliases must have a reviewed parent;
    # 11 key facts are in old text, one age-nine fact remains missing.
    remaining=json.loads((root/"translation/runtime/quiz_remaining_fact_qa_080.json").read_text(encoding="utf-8"))
    tail=remaining.get("audit_remaining",[])
    if (remaining.get("schema")!="chibi.quiz.remaining_scanner_fact_qa.080.v1"
        or len(tail)!=12
        or len({int(x["scanner"],0) for x in tail})!=12
        or set(remaining.get("new_semantic_parent_repairs_080",[]))!=
           {"0x32C15","0x33119","0x353F3"}
        or remaining.get("source_inventory_marked_completed") is not False):
        raise AssertionError("Incomplete 12 Quiz scanner alias source QA ledger")
    outstanding=[]
    for fact in tail:
        stage=fact["stage"]
        if stage not in prior_lookup:
            raise AssertionError("Missing original stage for Quiz scanner alias")
        parent=prior_lookup[stage].get(int(fact["parent"],0))
        if parent is None:
            raise AssertionError("Quiz scanner alias has no approved parent")
        lines=parent["vi_runtime_lines"]
        if any(e not in lines for e in fact["evidence_in_staged_lines"]):
            raise AssertionError("Supposed translated Quiz fact not present in earlier parent")
        if fact["disposition"].startswith("needs_"):
            outstanding.append(int(fact["scanner"],0))
    if outstanding!=[0x31F33]:
        raise AssertionError("Known original Maruko age-nine clue still requires a natural fit")

    cp=read_codepage(root)
    changed=0;checked=0;writable=0;previous_bytes=0
    for record in plan["records"]:
        source=int(record["parent_source_offset"],0)
        if source not in NATIVE:
            raise AssertionError("Unapproved original source field")
        at,ptr,stage,lines=NATIVE[source]
        if (record["historical_stage"]!=stage or
            int(record["original_native_record"],0)!=at or
            int(record["original_pointer_word_at"],0)!=ptr or
            len(record.get("original_japanese",[]))!=len(lines)):
            raise AssertionError("Unexpected original source to Quiz table mapping")
        if bytes.fromhex(record["original_pointer_word_hex"])!=(
            0x8000+at-0x30000).to_bytes(2,"little"):
            raise AssertionError("Original pointer hex bytes mismatch LoROM address")
        previous=older[stage].get(source)
        if previous is None or previous["vi_runtime_lines"]!=record["old_lines"]:
            raise AssertionError("Old stage 054/058 approved caption was changed")
        if len(lines)!=len(record["new_lines"]) or len(lines)!=len(record["old_lines"]):
            raise AssertionError("Unexpected physical native Quiz line count")
        if set(record["source_fact"] for _ in [0])=={""}:
            raise AssertionError("Empty editorial issue")
        for i,(off,cap) in enumerate(lines):
            if (int(record["original_line_offsets"][i],0)!=off or
                record["original_line_caps"][i]!=cap):
                raise AssertionError("Wrong native glyph span offset/capacity")
            jp=record["original_japanese"][i]
            if len(jp.encode("cp932"))!=2*cap:
                raise AssertionError("Original Japanese CP932 physical glyph width changed")
            old,new=record["old_lines"][i],record["new_lines"][i]
            old_bytes=encode(old,cap,cp)
            new_bytes=encode(new,cap,cp)
            previous_bytes+=len(old_bytes)
            checked+=1;writable+=2*cap
            changed+=int(old_bytes!=new_bytes)
    if (checked!=8 or changed!=4 or writable!=2*(13+8+6+13+14+14+14+13)
        or {int(r["scanner_alias"],0) for r in plan["records"]}!=
             EXPECTED_PATCHED_SOURCE_ALIASES):
        raise AssertionError("Wrong original 8 caption spans / four intended repairs")
    if (len(plan.get("records",[]))!=3 or
        len(plan.get("records",[]))>len(NATIVE)):
        raise AssertionError("Duplicate or missing native Quiz source")
    return {
        "status":"PASS_080_ORIGINAL_QUIZ_SEMANTIC_PARENT_QA_NOT_EMULATOR",
        "historical_ROM_SHA256":ORIGINAL_SHA,
        "three_original_Quiz_parents_reviewed":3,
        "native_original_caption_frames_verified":checked,
        "native_existing_caption_frames_changed":changed,
        "native_original_glyph_storage_bytes_preserved":writable,
        "old_054_058_manifest_byte_signatures_preserved":True,
        "newly_counted_canonical_Quiz_strings":0,
        "source_aliases_with_fact_repair":[f"0x{x:X}" for x in sorted(EXPECTED_PATCHED_SOURCE_ALIASES)],
        "other_original_scanner_aliases_pending_context_QA":12,
        "remaining_alias_parent_facts_verified":11,
        "remaining_age_9_clue_unresolved":"0x31F33",
        "SNES_emulator_tested":False,
        "ROM_or_IPS_written_by_audit":False,
    }

def build(clean:bytes,baseline:bytes,root:Path):
    if len(clean)!=0x200000 or sha(clean)!=ORIGINAL_SHA or len(baseline)!=len(clean):
        raise ValueError("Exact original headerless Japanese 2MiB ROM required")
    proof=audit(root)
    if int.from_bytes(baseline[0x2975E:0x29760],"little")!=0x9A74:
        raise AssertionError("Cannot apply Vietnamese Quiz overlay without stage061 V2 font")
    cp=read_codepage(root)
    plan=json.loads((root/MANIFEST).read_text(encoding="utf-8"))
    out=bytearray(baseline)
    allowed=set(range(0x7FDC,0x7FE0))
    for record in plan["records"]:
        source=int(record["parent_source_offset"],0)
        orig,pointer,stage,slots=NATIVE[source]
        expected=(0x8000+orig-0x30000).to_bytes(2,"little")
        if clean[pointer:pointer+2]!=expected or baseline[pointer:pointer+2]!=expected:
            raise AssertionError("Real original Quiz pointer must not be relocated")
        if clean[orig:orig+4]!=baseline[orig:orig+4] or clean[orig:orig+2]!=b"\x0e\x00":
            raise AssertionError("Original native Quiz script header/control changed")
        for (off,cap),old,new,jp in zip(
            slots,record["old_lines"],record["new_lines"],record["original_japanese"]
        ):
            if clean[off:off+2*cap]!=jp.encode("cp932"):
                raise AssertionError("Original Japanese native text span modified")
            oldbytes=encode(old,cap,cp)
            newbytes=encode(new,cap,cp)
            if baseline[off:off+2*cap]!=oldbytes:
                raise AssertionError("Existing old 054/058 V2 translations not in baseline")
            if oldbytes==newbytes:
                continue
            for char in set(new+" "):
                index=int(cp[char][-2:],16)
                glyph_pointer=0x28000+0x1A74+2*(index-0x40)
                if int.from_bytes(baseline[glyph_pointer:glyph_pointer+2],"little")==0:
                    raise AssertionError(f"Required V2 glyph lookup missing: {char!r}")
            out[off:off+2*cap]=newbytes
            allowed.update(range(off,off+2*cap))
    out[0x7FDC:0x7FE0]=bytes(4)
    checksum=(sum(out)+0x1FE)&0xFFFF
    out[0x7FDC:0x7FDE]=(checksum^0xFFFF).to_bytes(2,"little")
    out[0x7FDE:0x7FE0]=checksum.to_bytes(2,"little")
    result=bytes(out)
    modified={i for i,(a,b) in enumerate(zip(baseline,result)) if a!=b}
    if modified-allowed:
        raise AssertionError("080 modified bytes outside original native glyphs/checksum")
    for orig,pointer,_,_ in NATIVE.values():
        if result[pointer:pointer+2]!=baseline[pointer:pointer+2]:
            raise AssertionError("080 touched LoROM question/answer pointer")
    ips,nrecords=make_ips(clean,result)
    if apply_ips(clean,ips)!=result:
        raise AssertionError("Combined checkpoint080 original source-ROM IPS replay failed")
    return ips,{
        **proof,
        "status":"PASS_080_SEMANTIC_CORRECTIONS_MERGED_STATIC_EMULATOR_UNTESTED",
        "candidate_ROM_sha256":sha(result),
        "cumulative_clean_ROM_IPS_sha256":sha(ips),
        "cumulative_clean_ROM_IPS_bytes":len(ips),
        "cumulative_clean_ROM_IPS_records":nrecords,
        "changed_existing_V2_ROM_bytes":len(modified),
        "SNES_checksum":f"0x{checksum:04X}",
        "SNES_emulator_tested":False,
        "VN_font_visible_in_gameplay_tested":False,
        "release_approved":False,
        "copyrighted_ROM_written":False,
    }

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original_japanese_SFC",type=Path)
    parser.add_argument("--baseline-ips",type=Path,required=True)
    parser.add_argument("--project-root",type=Path,default=ROOT)
    parser.add_argument("--ips",type=Path,required=True)
    parser.add_argument("--report",type=Path,required=True)
    parser.add_argument("--allow-untested",action="store_true")
    args=parser.parse_args()
    if not args.allow_untested:
        parser.error("Emulator untested; explicitly pass --allow-untested")
    paths=[args.original_japanese_SFC,args.baseline_ips,args.ips,args.report]
    if len({p.resolve() for p in paths})!=4:
        parser.error("Input/output paths must all differ")
    if args.ips.suffix.lower()!=".ips" or args.report.suffix.lower()!=".json":
        parser.error("Only one original-SFC IPS + JSON report are emitted")
    clean=args.original_japanese_SFC.read_bytes()
    baseline=apply_ips(clean,args.baseline_ips.read_bytes())
    ips,report=build(clean,baseline,args.project_root)
    args.ips.parent.mkdir(parents=True,exist_ok=True)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.ips.write_bytes(ips)
    args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
