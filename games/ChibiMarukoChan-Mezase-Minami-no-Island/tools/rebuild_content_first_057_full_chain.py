#!/usr/bin/env python3
"""Rebuild Chibi Vietnamese content-first 043 -> 044..048 -> 054..057.

Requires only exact Japanese clean ROM + original checkpoint043 IPS.
Writes final clean-ROM IPS/report, not copyrighted ROM and not an emulator PASS.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from build_content_first_040_fortune import apply_ips
from rebuild_content_first_056_full_chain import run as build056
from build_content_first_057_quiz_50 import build as build057,sha
ROOT=Path(__file__).resolve().parent.parent

def run(clean:bytes,exact043:bytes,project:Path):
    ips056,qa056=build056(clean,exact043,project)
    rom056=apply_ips(clean,ips056)
    if sha(rom056)!=qa056["final_056_rom_sha256"]:
        raise AssertionError("Earlier checkpoint056 merged ROM SHA mismatch")
    ips057,qa057=build057(clean,rom056,project)
    rom057=apply_ips(clean,ips057)
    if sha(rom057)!=qa057["final_ROM_sha256"]:
        raise AssertionError("Checkpoint057 clean IPS replay mismatch")
    return ips057,{
        "status":"FULL_043_THROUGH_057_STATIC_VERIFIED_NOT_EMULATOR",
        "preexisting_056_source_chain":qa056,
        "quiz057":qa057,
        "result_057_ROM_sha256":sha(rom057),
        "source_integrity":"clean_ROM_original_043_IPS_with_byte_guards",
        "emulator_tested":False,
        "fully_translated_game":False,
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
        p.error("Still no emulator game acceptance test; pass --allow-untested")
    paths=[a.clean_japanese_rom,a.exact_043_clean_ips,a.ips,a.report]
    if len({x.resolve() for x in paths})!=len(paths):
        p.error("Distinct original and output file paths required")
    ips,qa=run(a.clean_japanese_rom.read_bytes(),
               a.exact_043_clean_ips.read_bytes(),a.project_root)
    for target,data in ((a.ips,ips),
                        (a.report,(json.dumps(qa,ensure_ascii=False,indent=2)+"\n").encode())):
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    print(json.dumps(qa,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
