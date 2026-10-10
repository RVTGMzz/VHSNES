#!/usr/bin/env python3
"""Independent byte-level verifier of G2 line-scoped 9px ROM diagnostic.

No builder import. Fails on unexpected byte, checksum, source-framing,
callsite, 65816 stub, source-pointer path or original 13px-table change.
Static proof is NOT emulator compatibility proof.
"""
import argparse
import hashlib
import json
from pathlib import Path

BASE_SHA256 = "2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd"
TARGET_SHA256 = "feb7215a67046128ff67113fd921b6479d956df6018a3ae4e74992d03b0c978a"
WORD_STUB = bytes.fromhex(
    "08 e2 20 8b 68 c9 83 d0 24 c2 20 af 94 1f 00 "
    "c9 ce 81 90 19 c9 38 82 90 1a c9 47 82 90 0f "
    "c9 b1 82 90 10 c9 c0 82 90 05 c9 2a 83 90 06 "
    "28 bf 70 96 85 6b 28 bf 80 fc 85 6b"
)
BYTE_STUB = bytes.fromhex(
    "08 e2 20 8b 68 c9 83 d0 24 c2 20 af 94 1f 00 "
    "c9 ce 81 90 19 c9 38 82 90 1a c9 47 82 90 0f "
    "c9 b1 82 90 10 c9 c0 82 90 05 c9 2a 83 90 06 "
    "28 bf 96 96 85 6b 28 bf c0 fc 85 6b"
)


def verify(original, candidate, check_sha=True):
    if len(original) != 0x200000 or hashlib.sha256(original).hexdigest() != BASE_SHA256:
        raise ValueError("wrong exact Probe008 V2 font-only source")
    if len(candidate) != 0x200000:
        raise ValueError("ROM size changed")
    if len(WORD_STUB) != 57 or len(BYTE_STUB) != 57:
        raise AssertionError("unexpected reference stub length")
    if candidate[0x28E0C:0x28E10] != bytes.fromhex("2280FB85"):
        raise AssertionError("word-table JSL callsite changed")
    if candidate[0x290EE:0x290F2] != bytes.fromhex("2200FC85"):
        raise AssertionError("shift-table JSL callsite changed")
    if candidate[0x2FB80:0x2FB80+57] != WORD_STUB:
        raise AssertionError("word stub differs from reference")
    if candidate[0x2FC00:0x2FC00+57] != BYTE_STUB:
        raise AssertionError("byte stub differs from reference")
    for i in range(19):
        x=4+9*i
        if (int.from_bytes(candidate[0x2FC80+i*2:0x2FC82+i*2],"little") != 16*(x//8)
                or candidate[0x2FCC0+i] != x%8):
            raise AssertionError(f"wrong 9px position {i}")
    for o in (0x181CE,0x18247,0x182C0):
        if candidate[o:o+106] != original[o:o+106]:
            raise AssertionError(f"strict 2-byte G2 payload changed at {o:06X}")
        for sep in (32,68,104):
            if candidate[o+sep:o+sep+2] != bytes.fromhex("816F"):
                raise AssertionError("line delimiter byte pair overwritten")
    for o,z in ((0x29670,0x296A9),(0x28EA8,0x28EB2),(0x29756,0x29776)):
        if candidate[o:z] != original[o:z]:
            raise AssertionError(f"original renderer/mapping state changed at {o:06X}")
    # Verify actual parser sources and line-column transfer into the renderer.
    if original[0x28340:0x28345] != bytes.fromhex("AC941FB900"):
        raise AssertionError("parser no longer reads current source through $1F94/Y")
    if original[0x28409:0x28417] != bytes.fromhex("AC9A1F8410AC9C1F8412227B8E85"):
        raise AssertionError("renderer no longer receives 1F9A/1F9C positions")
    ranges = ((0x81CE,0x8238),(0x8247,0x82B1),(0x82C0,0x832A))
    if any(end-first != 106 for first,end in ranges):
        raise AssertionError("source ranges are no longer each 106 bytes")
    allowed = set(range(0x7FDC,0x7FE0))
    for lo,hi in ((0x28E0C,0x28E10),(0x290EE,0x290F2),
                  (0x2FB80,0x2FC00),(0x2FC00,0x2FC80),
                  (0x2FC80,0x2FCA6),(0x2FCC0,0x2FCD3)):
        allowed.update(range(lo,hi))
    changed = {i for i,(a,b) in enumerate(zip(original,candidate)) if a!=b}
    if changed - allowed:
        raise AssertionError("unexpected ROM changes: " + str(sorted(changed-allowed)[:16]))
    temp=bytearray(candidate)
    temp[0x7FDC:0x7FE0]=bytes(4)
    ck=(sum(temp)+0x1FE)&0xFFFF
    header_ck=int.from_bytes(candidate[0x7FDE:0x7FE0],"little")
    header_comp=int.from_bytes(candidate[0x7FDC:0x7FDE],"little")
    if ck!=header_ck or header_comp!=(ck^0xFFFF):
        raise AssertionError("independent checksum/complement error")
    if len(changed)!=181 or ck!=0xF4D6:
        raise AssertionError("unexpected diff count/checksum")
    digest=hashlib.sha256(candidate).hexdigest()
    if check_sha and digest!=TARGET_SHA256:
        raise AssertionError("ROM not identical to reviewed line-scoped probe")
    return {
        "status":"INDEPENDENT_STATIC_PASS_ONLY",
        "base_sha256":BASE_SHA256,"candidate_sha256":digest,
        "changed_bytes":len(changed),"checksum":f"0x{ck:04X}",
        "complement":f"0x{ck^0xFFFF:04X}",
        "original_13px_tables_preserved":True,
        "G2_3x106_byte_records_preserved":True,
        "65816_stubs_verified":True,
        "runtime":"UNTESTED","release_ready":False
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("probe008_v2_13px",type=Path)
    ap.add_argument("line_scoped_9px_probe",type=Path)
    ap.add_argument("output_report",type=Path)
    ap.add_argument("--negative-tests",action="store_true")
    a=ap.parse_args()
    files=(a.probe008_v2_13px,a.line_scoped_9px_probe,a.output_report)
    if len({p.resolve() for p in files})!=3:
        raise ValueError("input and report must not share path")
    before=a.probe008_v2_13px.read_bytes()
    after=a.line_scoped_9px_probe.read_bytes()
    report=verify(before,after)
    if a.negative_tests:
        for loc in (0x181CE,0x28E0C,0x2FB88,0x2FC81,0x7FDE):
            broken=bytearray(after)
            broken[loc]^=1
            try:
                verify(before,broken)
            except (AssertionError,ValueError):
                continue
            raise AssertionError(f"corruption at 0x{loc:X} undetected")
        report["negative_corruption_tests"]=5
    a.output_report.parent.mkdir(parents=True,exist_ok=True)
    a.output_report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",
                               encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
