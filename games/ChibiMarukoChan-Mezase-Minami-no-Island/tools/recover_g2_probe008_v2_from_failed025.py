#!/usr/bin/env python3
"""Recover exact Probe008 V2 FONT-ONLY from failed 025 diagnostics.

Only removes the 025-specific 65816 hooks and 9px position tables,
restores original 13px lookups and SNES header checksum. Requires an
exact SHA-256 025 ROM, verifies byte whitelist and exact recovered V2
SHA. NEVER use this to mark the font as gameplay-tested; the goal is to
make reproducible static work possible without treating failed025 as base.
No copyrighted ROM bytes are included in this script.
"""
import argparse
import hashlib
import json
from pathlib import Path

OLD_SHA="d4bd629003812578580e7a380e791d87fdf64614441394f1261df3951b9815dc"
V2_SHA="2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd"
STAGES=((0x2FB80,0x2FC00),(0x2FC00,0x2FC80),
        (0x2FC80,0x2FCA6),(0x2FCC0,0x2FCD3))

def recover(raw):
    if len(raw)!=0x200000 or hashlib.sha256(raw).hexdigest()!=OLD_SHA:
        raise ValueError("requires exact previously FAILED checkpoint025 ROM")
    original=bytearray(raw)
    for pos,was,now in (
        (0x28E0C,bytes.fromhex("2280FB85"),bytes.fromhex("BF709685")),
        (0x290EE,bytes.fromhex("2200FC85"),bytes.fromhex("BF969685")),
    ):
        if original[pos:pos+4]!=was:
            raise AssertionError(f"unexpected hook before restoration at {pos:06X}")
        original[pos:pos+4]=now
    for start,end in STAGES:
        original[start:end]=bytes([0xFF])*(end-start)
    original[0x7FDC:0x7FE0]=bytes(4)
    checksum=(sum(original)+0x1FE)&0xFFFF
    original[0x7FDC:0x7FDE]=(checksum^0xFFFF).to_bytes(2,"little")
    original[0x7FDE:0x7FE0]=checksum.to_bytes(2,"little")
    allowed=set(range(0x7FDC,0x7FE0))
    for start,end in STAGES:
        allowed.update(range(start,end))
    allowed.update(range(0x28E0C,0x28E10))
    allowed.update(range(0x290EE,0x290F2))
    changed={i for i,(a,b) in enumerate(zip(raw,original)) if a!=b}
    if changed-allowed:
        raise AssertionError("unexpected out-of-contract byte modifications")
    result=bytes(original)
    digest=hashlib.sha256(result).hexdigest()
    if digest!=V2_SHA or len(changed)!=191 or checksum!=0x622E:
        raise AssertionError("recovered V2 does not match canonical font-only SHA")
    return result,{
        "status":"EXACT_025_TO_V2_RECOVERY_PASS",
        "source_rom_sha256":OLD_SHA,
        "recovered_v2_sha256":V2_SHA,
        "changed_bytes":len(changed),
        "SNES_checksum":f"0x{checksum:04X}",
        "SNES_complement":f"0x{checksum^0xFFFF:04X}",
        "known_bad_025_runtime":"FAIL",
        "recovered_v2_runtime":"NOT_CONFIRMED",
        "release_ready":False
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("exact_failed_025_rom",type=Path)
    p.add_argument("recovered_v2_font_only_rom",type=Path)
    p.add_argument("report_json",type=Path)
    a=p.parse_args()
    files=(a.exact_failed_025_rom,a.recovered_v2_font_only_rom,a.report_json)
    if len({x.resolve() for x in files})!=3:
        p.error("ROM source and output paths must differ")
    result, report=recover(a.exact_failed_025_rom.read_bytes())
    a.recovered_v2_font_only_rom.parent.mkdir(parents=True,exist_ok=True)
    a.recovered_v2_font_only_rom.write_bytes(result)
    a.report_json.parent.mkdir(parents=True,exist_ok=True)
    a.report_json.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
