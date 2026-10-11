#!/usr/bin/env python3
"""Rebuild guarded Chibi 043->044->045->046->047->048->054 in one command.

Accept exact clean Japanese game ROM and historical 043 clean-ROM IPS.
No interim ROM files, no copyrighted bytes committed, and no emulator PASS.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from build_content_first_040_fortune import apply_ips
from rebuild_content_first_048_full_chain import run as rebuild_048
from build_content_first_054_quiz_54 import build as integrate_054,sha

ROOT=Path(__file__).resolve().parent.parent

def run(clean:bytes,ips043:bytes,project:Path):
    ips048,qa048=rebuild_048(clean,ips043,project)
    base048=apply_ips(clean,ips048)
    expected=qa048["final_048"]["new_combined_ROM_sha256"]
    if sha(base048)!=expected:
        raise AssertionError("Rebuilt 048 mismatch after clean-ROM IPS replay")
    ips054,qa054=integrate_054(clean,base048,project)
    end054=apply_ips(clean,ips054)
    if sha(end054)!=qa054["output_ROM_sha256"]:
        raise AssertionError("054 final IPS replay SHA mismatch")
    return ips054,{
        "status":"FULL_043_TO_054_STATIC_PASS_EMULATOR_UNTESTED",
        "source_048_stages":qa048["stages"],
        "combined_048_sha256":expected,
        "final_054":qa054,
        "historical_053_duplicate_QA":"15 previously counted Quiz rows already in 041; 054 contains only the single new 053 field (0x340C0) once",
        "emulator_tested":False,
        "release_ready":False,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("clean_rom",type=Path)
    p.add_argument("exact_043_clean_ips",type=Path)
    p.add_argument("--project-root",type=Path,default=ROOT)
    p.add_argument("--ips",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--allow-untested",action="store_true")
    a=p.parse_args()
    if not a.allow_untested:
        p.error("Gameplay emulator validation not done; pass --allow-untested")
    paths=[a.clean_rom,a.exact_043_clean_ips,a.ips,a.report]
    if len({x.resolve() for x in paths})!=len(paths):
        p.error("Inputs and outputs must be distinct")
    final,report=run(a.clean_rom.read_bytes(),
                     a.exact_043_clean_ips.read_bytes(),a.project_root)
    for dst,content in ((a.ips,final),
                        (a.report,(json.dumps(report,ensure_ascii=False,indent=2)+"\n").encode())):
        dst.parent.mkdir(parents=True,exist_ok=True)
        dst.write_bytes(content)
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
