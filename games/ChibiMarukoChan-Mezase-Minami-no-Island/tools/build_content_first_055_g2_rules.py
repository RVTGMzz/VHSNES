#!/usr/bin/env python3
"""Guarded G2 rules insertion after integrated 054. ROM byte QA, not emulator QA.

The two native bullet glyphs at 0x1E323/0x1E337 are editable CP932
punctuation (middle dots), NOT control bytes. They become Vietnamese
text so "Thắng 2" remains complete and readable; 816F markers, script
control and ASCII indentation remain byte-identical.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import unicodedata
from pathlib import Path
from build_content_first_040_fortune import make_ips,apply_ips

ROOT=Path(__file__).resolve().parent.parent
CLEAN_SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
MANIFEST="translation/runtime/g2_rules_content_first_055.json"
PREVIEW_IPS_SHA="b2372df59679573167cd82f0c95b2c30de24eb088b323d91a2b4a8d72f494f04"
PREVIEW_SHA="1da12b5de13f06e1902690274709111bcfd0a510c2170a5bd0abd994ea362569"

def sha(blob:bytes)->str:
    return hashlib.sha256(blob).hexdigest()

def read_csv(path:Path):
    with path.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def build(clean:bytes,base054:bytes,root:Path):
    if len(clean)!=0x200000 or sha(clean)!=CLEAN_SHA:
        raise ValueError("Exact original 2MiB Japanese ROM required")
    if len(base054)!=len(clean):
        raise ValueError("Expected full 054 ROM, size mismatch")
    if int.from_bytes(base054[0x2975e:0x29760],"little")!=0x9a74:
        raise AssertionError("Existing V2 font table missing")
    plan=json.loads((root/MANIFEST).read_text(encoding="utf-8"))
    rows=plan["records"]
    if (plan["schema"]!="chibi.g2.rules.content_first.055.v1" or
        plan["clean_original_sha256"]!=CLEAN_SHA or
        plan["translation_count"]!=3 or len(rows)!=3 or
        plan["experimental_clean_overlay_ips_sha256"]!=PREVIEW_IPS_SHA or
        plan["experimental_clean_overlay_sha256"]!=PREVIEW_SHA or
        {r["file_offset"].upper() for r in rows}!={"0X1E307","0X1E323","0X1E337"}):
        raise AssertionError("Unexpected G2 rule source data")
    mapping={r["unicode"]:r["code_hex"] for r in
             read_csv(root/"translation/codepage/vi_codepage_v4_fe4_native.csv")}
    if mapping.get(" ")!="8440":
        raise AssertionError("Unexpected V2 space glyph")
    out=bytearray(base054)
    preview=bytearray(clean)
    allowed=set()
    markers=[]
    for row in rows:
        at=int(row["file_offset"],16)
        marker=int(row["marker_offset"],16)
        source=row["source_jp"].encode("cp932")
        cap=int(row["capacity"])
        caption=row["vi_runtime"]
        if (len(source)!=2*cap or marker!=at+len(source) or
            not caption or unicodedata.normalize("NFC",caption)!=caption or
            len(caption)>cap):
            raise AssertionError("Unexpected G2 glyph count or source punctuation")
        if clean[at:marker]!=source or base054[at:marker]!=source:
            raise AssertionError(f"Existing 054 baseline changed G2 rule {at:X}")
        if (clean[marker:marker+2]!=b"\x81\x6f" or
            base054[marker:marker+2]!=b"\x81\x6f"):
            raise AssertionError("Original G2 line marker missing")
        prefix=8 if at==0x1e307 else 4
        # Real ROM: first field has eight indent spaces; next two each have four.\n        if clean[at-prefix:at]!=b" "*prefix or base054[at-prefix:at]!=b" "*prefix:
            raise AssertionError("Native G2 layout padding missing")
        data=bytearray()
        for char in caption+" "*(cap-len(caption)):
            code=mapping.get(char)
            if not code or len(code)!=4 or not code.startswith("84"):
                raise AssertionError(f"Vietnamese font V2 glyph missing {char!r}")
            idx=int(code[-2:],16)
            ptr=0x28000+0x1a74+2*(idx-0x40)
            if idx<0x40 or int.from_bytes(base054[ptr:ptr+2],"little")==0:
                raise AssertionError("Mapped G2 glyph is not backed by an existing V2 glyph")
            data.extend(bytes.fromhex(code))
        if len(data)!=len(source):
            raise AssertionError("G2 translated byte length drift")
        spans=set(range(at,marker))
        if spans&allowed:
            raise AssertionError("Overlapping G2 source regions")
        allowed|=spans
        out[at:marker]=data
        preview[at:marker]=data
        markers.append(marker)
    if len(allowed)!=64 or len(set(markers))!=3:
        raise AssertionError("G2 physical source coverage drift")
    for marker in markers:
        if out[marker:marker+2]!=b"\x81\x6f" or preview[marker:marker+2]!=b"\x81\x6f":
            raise AssertionError("One G2 line control overwritten")
    probe=bytes(preview)
    probe_ips,probe_count=make_ips(clean,probe)
    if (sha(probe)!=PREVIEW_SHA or sha(probe_ips)!=PREVIEW_IPS_SHA or
        len(probe_ips)!=87 or probe_count!=3 or apply_ips(clean,probe_ips)!=probe):
        raise AssertionError("G2 source byte QA fingerprint drift")
    out[0x7fdc:0x7fe0]=bytes(4)
    checksum=(sum(out)+0x1fe)&0xffff
    out[0x7fdc:0x7fde]=(checksum^0xffff).to_bytes(2,"little")
    out[0x7fde:0x7fe0]=checksum.to_bytes(2,"little")
    complete=bytes(out)
    delta={i for i,(a,b) in enumerate(zip(base054,complete)) if a!=b}
    if delta-(allowed|set(range(0x7fdc,0x7fe0))):
        raise AssertionError("G2 builder touched data beyond approved text/checksum")
    ips,count=make_ips(clean,complete)
    if apply_ips(clean,ips)!=complete:
        raise AssertionError("Final G2 IPS replay failed")
    return ips,{
        "status":"055_G2_STATIC_PASS_EMULATOR_NOT_TESTED",
        "input_clean_sha256":CLEAN_SHA,
        "input_054_sha256":sha(base054),
        "translated_G2_rules":3,
        "G2_source_glyph_bytes":len(allowed),
        "original_G2_line_markers_preserved":len(markers),
        "source_only_IPS_fingerprint":PREVIEW_IPS_SHA,
        "source_only_ROM_fingerprint":PREVIEW_SHA,
        "final_055_ROM_sha256":sha(complete),
        "final_clean_IPS_sha256":sha(ips),
        "final_IPS_bytes":len(ips),
        "final_IPS_records":count,
        "SNES_checksum":f"0x{checksum:04X}",
        "SNES_complement":f"0x{checksum^0xffff:04X}",
        "emulator_tested":False,
        "release_ready":False
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("clean_original_rom",type=Path)
    p.add_argument("full_054_rom",type=Path)
    p.add_argument("--expected-054-sha",required=True)
    p.add_argument("--project-root",type=Path,default=ROOT)
    p.add_argument("--ips",required=True,type=Path)
    p.add_argument("--report",required=True,type=Path)
    p.add_argument("--allow-untested",action="store_true")
    a=p.parse_args()
    if not a.allow_untested:
        p.error("Only binary source QA, not runtime gameplay; pass --allow-untested")
    if len(a.expected_054_sha)!=64 or any(c not in "0123456789abcdef" for c in a.expected_054_sha):
        p.error("Expected 054 SHA needs 64 lowercase hex characters")
    base=a.full_054_rom.read_bytes()
    if sha(base)!=a.expected_054_sha:
        p.error("Full 054 ROM SHA differs from requested baseline")
    paths=[a.clean_original_rom,a.full_054_rom,a.ips,a.report]
    if len({x.resolve() for x in paths})!=4:
        p.error("Input/output paths must differ")
    final,report=build(a.clean_original_rom.read_bytes(),base,a.project_root)
    for dest,payload in ((a.ips,final),(a.report,(json.dumps(report,ensure_ascii=False,indent=2)+"\n").encode())):
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(payload)
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
