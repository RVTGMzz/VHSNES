#!/usr/bin/env python3
"""Independent static verifier for the Probe008 glyph-selective spacing probe."""
import argparse
import hashlib
import json
from pathlib import Path

BASE_SHA256 = "2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd"
TARGET_SHA256 = "dffdec30af4c3ef4d02c58414a25fa8312dcffdd168691ed4add755de1582328"
WORD_BYTES = bytes.fromhex(
    "98 c9 3a 08 90 19 c9 64 08 90 19 c9 0a 09 90 0f "
    "c9 64 09 90 0f c9 00 0a 90 05 c9 54 0a 90 05 "
    "bf 70 96 85 6b bf 80 fc 85 6b")
BYTE_BYTES = bytes.fromhex(
    "08 c2 20 af b2 1f 00 c9 3a 08 90 19 c9 64 08 "
    "90 1a c9 0a 09 90 0f c9 64 09 90 10 c9 00 0a "
    "90 05 c9 54 0a 90 06 28 bf 96 96 85 6b 28 bf c0 fc 85 6b")


def verify(before, after):
    if len(before) != 0x200000 or hashlib.sha256(before).hexdigest() != BASE_SHA256:
        raise ValueError("base must be exact Probe008 V2 font-only ROM")
    if len(after) != 0x200000 or hashlib.sha256(after).hexdigest() != TARGET_SHA256:
        raise ValueError("candidate has unexpected identity (update expected checksum only after audit)")
    assert len(WORD_BYTES) == 41 and len(BYTE_BYTES) == 49
    if after[0x28E0C:0x28E10] != bytes.fromhex("2280FB85"):
        raise AssertionError("word-table callsite differs")
    if after[0x290EE:0x290F2] != bytes.fromhex("2200FC85"):
        raise AssertionError("shift-table callsite differs")
    if after[0x2FB80:0x2FB80+41] != WORD_BYTES:
        raise AssertionError("glyph-selective word stub differs")
    if after[0x2FC00:0x2FC00+49] != BYTE_BYTES:
        raise AssertionError("glyph-selective byte stub differs")
    for i in range(19):
        x = 4 + 9*i
        if (int.from_bytes(after[0x2FC80+i*2:0x2FC82+i*2],"little") != 16*(x//8)
            or after[0x2FCC0+i] != x%8):
            raise AssertionError(f"9px table entry {i} differs")
    if before[0x29670:0x296A9] != after[0x29670:0x296A9]:
        raise AssertionError("original 13px Japanese tables altered")
    for off,payload in ((0x181CE,106),(0x18247,106),(0x182C0,106)):
        if before[off:off+payload] != after[off:off+payload]:
            raise AssertionError("original strict 2-byte text changed")
    for off,expected in ((0x28EA8,"BF00F885"),(0x28EAE,"BF01F885")):
        if after[off:off+4] != before[off:off+4] or after[off:off+4] != bytes.fromhex(expected):
            raise AssertionError("font page pointer relocation damaged")
    allowed = set(range(0x7FDC,0x7FE0))
    for start,end in ((0x2FB80,0x2FC00),(0x2FC00,0x2FC80),
                      (0x2FC80,0x2FCA6),(0x2FCC0,0x2FCD3),
                      (0x28E0C,0x28E10),(0x290EE,0x290F2)):
        allowed.update(range(start,end))
    changed = {i for i,(a,b) in enumerate(zip(before,after)) if a!=b}
    if changed - allowed:
        raise AssertionError("unexpected changed bytes: " + str(sorted(changed-allowed)[:12]))
    tmp=bytearray(after)
    tmp[0x7FDC:0x7FE0]=bytes(4)
    c=(sum(tmp)+0x1FE)&0xFFFF
    stored=int.from_bytes(after[0x7FDE:0x7FE0],"little")
    complement=int.from_bytes(after[0x7FDC:0x7FDE],"little")
    if c!=stored or (c^complement)!=0xFFFF:
        raise AssertionError("bad SNES checksum/complement")
    if len(changed)!=157 or stored!=0xF9AF:
        raise AssertionError("unexpected diff count or checksum")
    return {"status":"INDEPENDENT_STATIC_PASS",
            "rom_sha256":TARGET_SHA256,
            "changed_bytes":len(changed),
            "checksum":f"0x{stored:04X}",
            "native_13px_tables_unchanged":True,
            "runtime":"UNTESTED",
            "release_ready":False,
            "caveat":"Mixed native-Japanese quotation marks in Vietnamese lines may have 13px spacing"}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("font_only_rom",type=Path)
    ap.add_argument("selective_probe_rom",type=Path)
    ap.add_argument("report",type=Path)
    a=ap.parse_args()
    if len({p.resolve() for p in (a.font_only_rom,a.selective_probe_rom,a.report)})!=3:
        raise ValueError("input/output file paths must differ")
    result=verify(a.font_only_rom.read_bytes(),a.selective_probe_rom.read_bytes())
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
