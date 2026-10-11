#!/usr/bin/env python3
"""Content-first static rebuild from 043 to 055; never publishes a game ROM.

Requires the exact user-owned Japanese clean ROM and clean-ROM-based
checkpoint043 IPS. Stage 048 and 054 preserve all previous patches; stage
055 adds the three verified G2 rules. Emulator gameplay QA remains pending.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from build_content_first_040_fortune import apply_ips
from rebuild_content_first_054_full_chain import run as rebuild054
from build_content_first_055_g2_rules import build as integrate055, sha

ROOT=Path(__file__).resolve().parent.parent

def run(clean:bytes,ips043:bytes,project:Path):
    ips054,qa054=rebuild054(clean,ips043,project)
    base054=apply_ips(clean,ips054)
    expected=qa054["final_054"]["output_ROM_sha256"]
    if sha(base054)!=expected:
        raise AssertionError("054 chain source replay mismatch")
    ips055,qa055=integrate055(clean,base054,project)
    target=apply_ips(clean,ips055)
    if sha(target)!=qa055["final_055_ROM_sha256"]:
        raise AssertionError("055 chain IPS replay mismatch")
    return ips055,{
        "status":"FULL_043_TO_055_STATIC_VERIFIED_EMULATOR_UNTESTED",
        "verified_054_chain":qa054,
        "verified_055_rules":qa055,
        "final_055_ROM_sha256":sha(target),
        "emulator_tested":False,
        "finished_whole_game_translation":False,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("clean_japanese_rom",type=Path)
    p.add_argument("exact_043_clean_ips",type=Path)
    p.add_argument("--project-root",type=Path,default=ROOT)
    p.add_argument("--ips",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--allow-untested",action="store_true")
    a=p.parse_args()
    if not a.allow_untested:
        p.error("Emulator gameplay has not been tested; pass --allow-untested")
    paths=[a.clean_japanese_rom,a.exact_043_clean_ips,a.ips,a.report]
    if len({x.resolve() for x in paths})!=len(paths):
        p.error("Inputs and outputs must not share a path")
    final,report=run(a.clean_japanese_rom.read_bytes(),a.exact_043_clean_ips.read_bytes(),a.project_root)
    for file,blob in ((a.ips,final),
                      (a.report,(json.dumps(report,ensure_ascii=False,indent=2)+"\n").encode("utf-8"))):
        file.parent.mkdir(parents=True,exist_ok=True)
        file.write_bytes(blob)
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
