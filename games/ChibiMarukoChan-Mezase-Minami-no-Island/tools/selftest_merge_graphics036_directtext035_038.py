#!/usr/bin/env python3
"""Real-asset, synthetic DIRECT-TEXT-base tests for the 038 safe merger.

Runs the exact clean + graphics036 ROM assets but substitutes two artificial,
disjoint text edits; it DOES NOT pretend to have historical Build035. Tests
five intentionally clashing source locations. No output SNES ROM is written.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from merge_graphics036_directtext035_preflight_038 import (
    CLEAN_SHA,GRAPHICS036_SHA,REGIONS,checksum,merge,preflight
)

def run(clean:bytes,gfx:bytes)->dict:
    if len(clean)!=0x200000 or hashlib.sha256(clean).hexdigest()!=CLEAN_SHA:
        raise ValueError("exact clean ROM required")
    if len(gfx)!=0x200000 or hashlib.sha256(gfx).hexdigest()!=GRAPHICS036_SHA:
        raise ValueError("exact graphics036 experimental ROM required")
    fake=bytearray(clean)
    saved=(0x18300,0x2A000)
    fake[saved[0]] ^= 1
    fake[saved[1]] ^= 4
    checksum(fake)
    report=preflight(clean,bytes(fake),gfx)
    if report["status"]!="SAFE_TO_MERGE":
        raise AssertionError(f"nonoverlap synthetic fixture rejected: {report}")
    merged,more=merge(clean,bytes(fake),gfx)
    for offset in saved:
        if merged[offset]!=fake[offset]:
            raise AssertionError("unrelated user text edit lost")
    if more["status"]!="MERGED_STATIC_ONLY":
        raise AssertionError("static merge status invalid")
    failures={}
    for name,offset in (
        ("g0_bank86_relocated",0x36907),
        ("g0_4bpp_title",0xF6456),
        ("g1_story_choices",0xBF95E),
        ("g1_mode_question",0xC706F),
        ("g0_package_pointer",0x12095),
    ):
        invalid=bytearray(fake)
        invalid[offset] ^= 1
        state=preflight(clean,bytes(invalid),gfx)
        if state["status"]!="BLOCKED_NO_ROM_WRITE":
            raise AssertionError(f"overlap not blocked: {name}")
        if not any(x["asset"]==name for x in state["reserved_asset_region_conflicts"]):
            raise AssertionError(f"overlap misclassified: {name}")
        failures[name]="BLOCKED"
    return {
        "status":"EXACT_REAL_GRAPHICS_SIMULATED_DIRECTTEXT_BASE_SELFTEST_PASS",
        "real_clean_sha256":CLEAN_SHA,
        "real_graphics036_sha256":GRAPHICS036_SHA,
        "synthetic_unrelated_text_edits_preserved":len(saved),
        "conflict_fixtures_blocked":failures,
        "actual_historical_Build035_present":False,
        "actual_combined_release_ROM_built":False,
        "gameplay_tested":False,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("exact_clean_rom",type=Path)
    p.add_argument("exact_graphics036_rom",type=Path)
    p.add_argument("--report",type=Path)
    a=p.parse_args()
    result=run(a.exact_clean_rom.read_bytes(),a.exact_graphics036_rom.read_bytes())
    s=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    print(s)
    if a.report:
        a.report.parent.mkdir(parents=True,exist_ok=True)
        a.report.write_text(s,encoding="utf-8")

if __name__=="__main__":
    main()
