#!/usr/bin/env python3
"""Chibi Quiz 052: read-only preflight of all 381 Japanese Quiz source records.

A strict candidate must match exact CP932 bytes at the claimed ROM offset,
have an untouched 816F record delimiter immediately after those bytes,
and remain unchanged in the already translated base. All other records
are BLOCKED for manual layout investigation; never patch scanner aliases.
Does not build a ROM or silently shorten full Vietnamese text.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from audit_quiz_source_050 import run as inventory

CLEAN_SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
ROOT=Path(__file__).resolve().parent.parent

def inspect(clean: bytes, base: bytes, project: Path) -> dict:
    if len(clean)!=0x200000 or hashlib.sha256(clean).hexdigest()!=CLEAN_SHA:
        raise ValueError("Wrong exact headerless Japanese ROM")
    if len(base)!=len(clean):
        raise ValueError("Baseline size mismatch")
    source=inventory(project)
    results=[]
    for row in source["rows"]:
        reasons=list(row["risks"])
        offset=int(row["file_offset"],16)
        jp=row["source_jp_scanner"]
        if row["status"]=="already_integrated_047":
            reasons.append("already_integrated_do_not_overwrite")
        try:
            encoded=jp.encode("cp932")
        except UnicodeEncodeError:
            reasons.append("not_encodable_as_cp932")
            encoded=b""
        if len(encoded)%2:
            reasons.append("odd_byte_length")
        if offset<0 or offset+len(encoded)+2>len(clean):
            reasons.append("outside_rom")
        elif encoded:
            if clean[offset:offset+len(encoded)]!=encoded:
                reasons.append("source_bytes_do_not_match_ROM")
            if clean[offset+len(encoded):offset+len(encoded)+2]!=b"\x81\x6f":
                reasons.append("no_immediate_816F_line_terminator")
            if base[offset:offset+len(encoded)+2]!=clean[offset:offset+len(encoded)+2]:
                reasons.append("base_already_modified_or_delimiter_changed")
        else:
            reasons.append("empty_original_field")
        safe=not reasons
        results.append({
            "file_offset":row["file_offset"],
            "source_file":row["source_file"],
            "original_japanese":jp,
            "canonical_vi_full":row["vi_full"],
            "max_original_two_byte_units":len(encoded)//2 if safe else None,
            "status":"EXACT_SLOT_PREFLIGHT_ONLY_NOT_PATCHED" if safe else "BLOCKED",
            "reasons":reasons,
        })
    approved=sum(r["status"].startswith("EXACT_SLOT") for r in results)
    return {
        "schema":"chibi.quiz.physical_preflight.052.v1",
        "clean_rom_sha256":CLEAN_SHA,
        "base_rom_sha256":hashlib.sha256(base).hexdigest(),
        "canonical_quiz_rows":381,
        "source_exact_slots_for_editor_review":approved,
        "blocked_or_already_integrated":381-approved,
        "editorial_approval":False,
        "physical_patch_created":False,
        "emulator_tested":False,
        "entries":results
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("clean_japanese_rom",type=Path)
    p.add_argument("baseline_vietnamese_rom",type=Path)
    p.add_argument("--project-root",type=Path,default=ROOT)
    p.add_argument("--report",type=Path,required=True)
    a=p.parse_args()
    targets=[a.clean_japanese_rom,a.baseline_vietnamese_rom,a.report]
    if len({p.resolve() for p in targets})!=len(targets):
        p.error("input and output paths must be distinct")
    result=inspect(a.clean_japanese_rom.read_bytes(),
                   a.baseline_vietnamese_rom.read_bytes(),a.project_root)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="entries"},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
