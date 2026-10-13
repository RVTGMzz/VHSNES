#!/usr/bin/env python3
"""Checkpoint085: seven original Quiz omissions restored in existing 054/058/059 native slots.

ROM-free source QA is suitable for CI. The optional actual-ROM builder refuses
anything except the SHA-pinned user-owned Japanese ROM and genuine post084 V2
baseline; it derives REAL native source slots at build time instead of inventing
offsets, validates CP932 and original pointers, and never touches historical
054/058/059 manifests. No emulator/gameplay acceptance is implied.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from build_content_first_040_fortune import apply_ips, make_ips
from build_content_first_054_quiz_54 import segments
from build_quiz_parent_semantic_restore_080 import encode, read_codepage

ROOT=Path(__file__).resolve().parent.parent
CLEAN_SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
MANIFEST="translation/runtime/quiz_seven_fact_restore_085.json"
OLD_STAGE={
    "054":"translation/runtime/quiz_content_first_54_054.json",
    "058":"translation/runtime/quiz_content_first_67_058.json",
    "059":"translation/runtime/quiz_content_first_37_059.json",
}
TARGETS={
    0x32095:("059",[14,13]),
    0x32303:("059",[14,8,9]),
    0x3259A:("059",[12,14,11]),
    0x31FA6:("059",[12,13,13]),
    0x3394B:("058",[9,11,14]),
    0x33C6C:("058",[11,12,12]),
    0x350AD:("054",[14,9,9]),
}
JP_REQUIRED={
    0x32095:"ハンバーグとアイスクリーム",
    0x32303:"なかよし。時に",
    0x3259A:"目立たない",
    0x31FA6:"ウキウキのおたんじょうび",
    0x3394B:"杉浦とくぞう",
    0x33C6C:"富田とみ子",
    0x350AD:"チョコ",
}

def sha(blob:bytes)->str:
    return hashlib.sha256(blob).hexdigest()

def read_csv(path:Path):
    with path.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def audit(root:Path)->dict:
    data=json.loads((root/MANIFEST).read_text(encoding="utf-8"))
    records=data.get("records",[])
    if (data.get("schema")!="chibi.quiz.seven_fact_repair.085.v1"
        or data.get("clean_sha256")!=CLEAN_SHA
        or data.get("apply_after")!="084 cumulative V2 Quiz source candidate"
        or data.get("stage_manifests_immutable") is not True
        or data.get("emulator_tested") is not False
        or data.get("release_approved") is not False
        or data.get("prior_original_parent_records_corrected")!=7
        or data.get("original_physical_glyph_frames")!=20
        or data.get("changed_caption_frames")!=14
        or data.get("new_canonical_source_ids")!=0
        or len(records)!=7):
        raise AssertionError("084 source contract/status drift")
    old_stages={
        name:{int(r["file_offset"],0):r
              for r in json.loads((root/path).read_text(encoding="utf-8"))["records"]}
        for name,path in OLD_STAGE.items()
    }
    mapping=read_codepage(root)
    covered=set()
    changed=0
    lines=0
    original_cells=0
    qa=[]
    for rec in records:
        addr=int(rec["source"],0)
        if addr in covered or addr not in TARGETS:
            raise AssertionError("Duplicate/unreviewed original Quiz source")
        covered.add(addr)
        stage,capacities=TARGETS[addr]
        if (rec["historical_stage"]!=stage
            or rec["original_capacities"]!=capacities
            or len(rec["old_lines"])!=len(capacities)
            or len(rec["new_lines"])!=len(capacities)
            or not rec.get("why")
            or JP_REQUIRED[addr] not in rec["jp_scanner"]):
            raise AssertionError("084 physical native stage/cell contract mismatch")
        original=old_stages[stage].get(addr)
        if original is None or original["vi_runtime_lines"]!=rec["old_lines"]:
            raise AssertionError("Historical 054/058/059 earlier captions modified")
        if (original.get("source_file")!=rec["source_file"]
            or original.get("source_jp_scanner")!=rec["jp_scanner"]
            or original.get("vi_full_reference")!=rec["canonical_vi_full"]):
            raise AssertionError("Historical source and manifest mismatch")
        csv_rows=[row for row in read_csv(root/rec["source_file"])
                  if int(row["file_offset"],0)==addr]
        if (len(csv_rows)!=1 or csv_rows[0]["source_jp_scanner"]!=rec["jp_scanner"]
            or csv_rows[0]["vi_full"]!=rec["canonical_vi_full"]):
            raise AssertionError("Current full natural JP/VI source changed")
        for cap,old,new in zip(capacities,rec["old_lines"],rec["new_lines"]):
            oldbytes=encode(old,cap,mapping)
            newbytes=encode(new,cap,mapping)
            changed+=int(oldbytes!=newbytes)
            lines+=1
            original_cells+=cap
        qa.append({"original_scanner_offset":f"0x{addr:X}","historical_stage":stage,
                   "before":rec["old_lines"],"after":rec["new_lines"]})
    if covered!=set(TARGETS) or lines!=20 or changed!=14 or original_cells!=234:
        raise AssertionError("085 seven parents/fourteen captions/234 cells not satisfied")
    if data["original_fixed_glyph_cells"]!=original_cells:
        raise AssertionError("085 fixed native glyph-cell budget changed")
    return {
        "status":"PASS_085_SEVEN_QUIZ_OMITTED_FACTS_RESTORED_SOURCE_QA",
        "historical_parent_fields_audited":7,
        "original_two_byte_glyph_frames":11,
        "real_new_caption_frames":changed,
        "original_fixed_width_glyph_cells_preserved":original_cells,
        "new_distinct_Quiz_source_IDs":0,
        "original_054_058_manifests_untouched":True,
        "original_japanese_rom_read":False,
        "emulator_tested":False,
        "changes":qa,
    }

def build(clean:bytes,baseline:bytes,root:Path):
    if len(clean)!=0x200000 or sha(clean)!=CLEAN_SHA or len(baseline)!=len(clean):
        raise ValueError("Requires exact user-owned Japanese 2 MiB retail SFC")
    report=audit(root)
    if int.from_bytes(baseline[0x2975E:0x29760],"little")!=0x9A74:
        raise AssertionError("Cannot overwrite without installed 061 V2 font")
    mapping=read_codepage(root)
    m=json.loads((root/MANIFEST).read_text(encoding="utf-8"))
    edited=bytearray(baseline)
    writable=set(range(0x7FDC,0x7FE0))
    changed_frame_count=0
    verified_markers=0
    native_pointers=[]
    for record in m["records"]:
        address=int(record["source"],0)
        stage,caps=TARGETS[address]
        native_start=address-4
        if (clean[native_start:native_start+2]!=b"\x0e\x00"
            or baseline[native_start:address]!=clean[native_start:address]):
            raise AssertionError("Original Quiz native record opcode/header altered")
        raw_ptr=(0x8000+native_start-0x30000).to_bytes(2,"little")
        ptr_hits=[p for p in range(0x31100,0x31500) if clean[p:p+2]==raw_ptr]
        if not ptr_hits or any(baseline[p:p+2]!=raw_ptr for p in ptr_hits):
            raise AssertionError(f"Original native Quiz pointer not retained for 0x{address:X}")
        native_pointers.extend(ptr_hits)
        frames,markers,stop=segments(clean,address)
        if len(frames)!=len(caps) or len(markers)<len(caps)-1:
            raise AssertionError("Original separate text frame layout differs")
        actual_jp=[]
        for (left,right) in frames:
            actual_jp.append(clean[left:right].decode("cp932").replace(" ",""))
        source_jp=record["jp_scanner"].replace("｛","").replace(" ","")
        if source_jp not in "".join(actual_jp):
            raise AssertionError("Exact source ROM Japanese narrative does not match canonical scanner")
        for marker in markers:
            if (clean[marker:marker+2]!=b"\x81\x6f"
                or baseline[marker:marker+2]!=b"\x81\x6f"):
                raise AssertionError("Original 816F Quiz line separator overwritten")
        verified_markers+=len(markers)
        for ((left,right),cap,old,new) in zip(frames,caps,record["old_lines"],record["new_lines"]):
            original=clean[left:right]
            lead=len(original)-len(original.lstrip(b" "))
            tail=(len(original)-len(original.rstrip(b" "))) if lead<len(original) else 0
            start=left+lead
            end=right-tail
            if len(clean[start:end])!=2*cap:
                raise AssertionError("Original native physical 2-byte glyph capacity changed")
            previous=encode(old,cap,mapping)
            if baseline[start:end]!=previous:
                raise AssertionError("Missing exact post083 stage054/058 old V2 caption")
            nextv2=encode(new,cap,mapping)
            if nextv2==previous:
                continue
            region=set(range(start,end))
            if region & writable:
                raise AssertionError("Overlapping reviewed writable Quiz sources")
            for ch in set(new+" "):
                idx=int(mapping[ch][-2:],16)
                loc=0x28000+0x1A74+2*(idx-0x40)
                if int.from_bytes(baseline[loc:loc+2],"little")==0:
                    raise AssertionError(f"Required actual V2 font glyph missing for {ch!r}")
            writable.update(region)
            edited[start:end]=nextv2
            changed_frame_count+=1
    if changed_frame_count!=14:
        raise AssertionError("Expected 14 changed existing 085 Quiz captions")
    edited[0x7FDC:0x7FE0]=bytes(4)
    checksum=(sum(edited)+0x1FE)&0xFFFF
    edited[0x7FDC:0x7FDE]=(checksum^0xFFFF).to_bytes(2,"little")
    edited[0x7FDE:0x7FE0]=checksum.to_bytes(2,"little")
    final=bytes(edited)
    diff={i for i,(a,b) in enumerate(zip(baseline,final)) if a!=b}
    if diff-writable:
        raise AssertionError("085 wrote outside seven original fields/checksum")
    ips,n=make_ips(clean,final)
    if apply_ips(clean,ips)!=final:
        raise AssertionError("085 cumulative clean-ROM IPS replay mismatch")
    report.update({
        "status":"085_SEVEN_EXISTING_QUIZ_OMISSIONS_SOURCE_CANDIDATE_EMULATOR_UNTESTED",
        "original_japanese_rom_read":True,
        "canonical_original_source_ROM_sha256":CLEAN_SHA,
        "validated_original_16bit_pointer_word_candidates":[f"0x{x:X}" for x in sorted(set(native_pointers))],
        "unchanged_original_816F_markers":verified_markers,
        "candidate_ROM_sha256":sha(final),
        "cumulative_clean_IPS_sha256":sha(ips),
        "cumulative_IPS_bytes":len(ips),
        "cumulative_IPS_records":n,
        "modified_ROM_bytes_including_checksum":len(diff),
        "final_SNES_checksum":f"0x{checksum:04X}",
        "emulator_tested":False,
        "ROM_or_IPS_written_by_build_function":False,
        "release_approved":False,
    })
    return ips,report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--audit-only",action="store_true")
    p.add_argument("--project-root",type=Path,default=ROOT)
    p.add_argument("--original-sfc",type=Path)
    p.add_argument("--post083-ips",type=Path)
    p.add_argument("--ips",type=Path)
    p.add_argument("--report",type=Path)
    p.add_argument("--allow-untested",action="store_true")
    a=p.parse_args()
    if a.audit_only:
        print(json.dumps(audit(a.project_root),ensure_ascii=False,indent=2))
        return
    paths=[a.original_sfc,a.post083_ips,a.ips,a.report]
    if not a.allow_untested or any(v is None for v in paths):
        p.error("Need exact original SFC, cumulative post083 IPS and --allow-untested")
    if len({x.resolve() for x in paths})!=4:
        p.error("Never overwrite original SFC or previous IPS")
    clean=a.original_sfc.read_bytes()
    base=apply_ips(clean,a.post083_ips.read_bytes())
    patch,qa=build(clean,base,a.project_root)
    qa["IPS_file_written"]=True
    a.ips.parent.mkdir(parents=True,exist_ok=True)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.ips.write_bytes(patch)
    a.report.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(qa,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
