#!/usr/bin/env python3
"""Exact Japanese clean ROM + historical checkpoint043 IPS -> 060.

Keeps all intermediate images in memory, writes the final clean-ROM IPS only.
Production SNES font rendering and gameplay remain NOT TESTED.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from build_content_first_040_fortune import apply_ips
from rebuild_content_first_059_full_chain import run as rebuild059
from build_content_first_060_quiz_21 import build as integrate060,sha

ROOT = Path(__file__).resolve().parent.parent

def run(clean:bytes,exact043:bytes,project:Path):
    ips059,report059 = rebuild059(clean,exact043,project)
    rom059 = apply_ips(clean,ips059)
    if sha(rom059) != report059["result_059_ROM_sha256"]:
        raise AssertionError("Checkpoint059 source-chain result SHA mismatch")
    ips060,report060 = integrate060(clean,rom059,project)
    rom060 = apply_ips(clean,ips060)
    if sha(rom060) != report060["result_060_ROM_sha256"]:
        raise AssertionError("Checkpoint060 full clean-ROM IPS replay mismatch")
    return ips060,{
        "status":"FULL_043_TO_060_STATIC_ONLY_EMULATOR_UNTESTED",
        "previous_059":report059,"new_060":report060,
        "result_060_ROM_sha256":sha(rom060),
        "release_ready":False,"emulator_tested":False,
        "whole_game_fully_translated":False,
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("original_clean_rom",type=Path)
    ap.add_argument("exact_043_clean_ips",type=Path)
    ap.add_argument("--project-root",type=Path,default=ROOT)
    ap.add_argument("--ips",type=Path,required=True)
    ap.add_argument("--report",type=Path,required=True)
    ap.add_argument("--allow-untested",action="store_true")
    args=ap.parse_args()
    if not args.allow_untested:
        ap.error("Emulator not yet accepted; pass --allow-untested")
    paths=[args.original_clean_rom,args.exact_043_clean_ips,args.ips,args.report]
    if len({p.resolve() for p in paths})!=len(paths):
        ap.error("Input and output paths must be distinct")
    ips,report=run(args.original_clean_rom.read_bytes(),
                   args.exact_043_clean_ips.read_bytes(),args.project_root)
    for target,data in ((args.ips,ips),
                       (args.report,(json.dumps(report,ensure_ascii=False,indent=2)+"\n").encode("utf-8"))):
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
