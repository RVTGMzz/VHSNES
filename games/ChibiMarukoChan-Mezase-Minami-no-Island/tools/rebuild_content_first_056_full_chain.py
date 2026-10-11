#!/usr/bin/env python3
"""Exact Chibi localization replay: 043 -> 044/045/046/047/048/054/055/056.

Only input assets: verified clean user-owned Japanese game ROM and exact
previously published 043 clean IPS. All intermediate ROMs live in memory.
Output final clean-ROM IPS and a static QA report; not emulator acceptance.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from build_content_first_040_fortune import apply_ips
from rebuild_content_first_055_full_chain import run as rebuild055
from build_content_first_056_fortune_2 import build as build056,sha

ROOT=Path(__file__).resolve().parent.parent

def run(clean:bytes,ips043:bytes,root:Path):
    ips055,report055=rebuild055(clean,ips043,root)
    base=apply_ips(clean,ips055)
    if sha(base)!=report055["final_055_ROM_sha256"]:
        raise AssertionError("The earlier 055 combined ROM SHA verification failed")
    ips056,report056=build056(clean,base,root)
    merged=apply_ips(clean,ips056)
    if sha(merged)!=report056["output_056_ROM_sha256"]:
        raise AssertionError("Final 056 clean IPS replay returned different 2MiB ROM")
    return ips056,{
        "status":"056_FULL_CHAIN_STATIC_VERIFIED_NO_EMULATOR_PASS",
        "prior_chain":report055,
        "new_fortune":report056,
        "final_056_rom_sha256":sha(merged),
        "remaining_exception_source_offsets":["0x2BD5E","0x2C86B","0x2CA7D","0x2CADD"],
        "emulator_tested":False,
        "finished_whole_game_translation":False,
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("original_clean_rom",type=Path)
    ap.add_argument("exact_043_clean_ips",type=Path)
    ap.add_argument("--project-root",type=Path,default=ROOT)
    ap.add_argument("--ips",type=Path,required=True)
    ap.add_argument("--report",type=Path,required=True)
    ap.add_argument("--allow-untested",action="store_true")
    a=ap.parse_args()
    if not a.allow_untested:
        ap.error("Real emulator gameplay is NOT TESTED: pass --allow-untested")
    paths=[a.original_clean_rom,a.exact_043_clean_ips,a.ips,a.report]
    if len({p.resolve() for p in paths})!=len(paths):
        ap.error("Input/output paths must be different")
    patch,report=run(a.original_clean_rom.read_bytes(),
                     a.exact_043_clean_ips.read_bytes(),a.project_root)
    for out,data in ((a.ips,patch),(a.report,(json.dumps(report,ensure_ascii=False,indent=2)+"\n").encode())):
        out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
