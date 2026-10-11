#!/usr/bin/env python3
"""056 guarded two-Fortune exception overlay, after real combined checkpoint055.

Requires exact 2MiB clean Japanese ROM and full integrated 055 baseline.
Reads immutable canonical Vietnamese for two short, semantically reviewed
Fortune cases. Does NOT abbreviate yellow/white/week/Heaven's voice as
unintelligible text: these four cases require safe longer text layout.
This builder produces clean-source IPS only; emulator gameplay is untested.
"""
from __future__ import annotations

import argparse,csv,hashlib,json,unicodedata
from pathlib import Path
from build_content_first_040_fortune import make_ips,apply_ips

ROOT=Path(__file__).resolve().parent.parent
CLEAN_SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
MANIFEST="translation/runtime/fortune_exceptions_2_056.json"
PREVIEW_IPS_SHA="84e30fe4f1bad5621934de99dcc9e0c3a11efd64152f36af676b42e56eca31be"
PREVIEW_ROM_SHA="d308a8a4b9b87a2c496fda3409398df6803c98381424a2a3a253f274d0491071"

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()

def csv_rows(p:Path):
    with p.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))

def build(clean:bytes,base055:bytes,project:Path):
    if len(clean)!=0x200000 or sha(clean)!=CLEAN_SHA:
        raise ValueError("Exact headerless Japanese 2MiB game ROM required")
    if len(base055)!=len(clean):
        raise ValueError("055 ROM has wrong size")
    if int.from_bytes(base055[0x2975e:0x29760],"little")!=0x9a74:
        raise AssertionError("Existing V2 0x84 glyph mapping absent")
    plan=json.loads((project/MANIFEST).read_text(encoding="utf-8"))
    rows=plan["records"]
    if (plan["schema"]!="chibi.fortune.exceptions.056.v1" or
        plan["clean_original_sha256"]!=CLEAN_SHA or len(rows)!=2 or
        plan["translated_additional_fortune"]!=2 or
        {r["file_offset"].upper() for r in rows}!={"0X2C413","0X2C601"} or
        plan["preview_IPS_sha256"]!=PREVIEW_IPS_SHA or
        plan["preview_source_ROM_sha256"]!=PREVIEW_ROM_SHA):
        raise AssertionError("056 manifest identity or previously verified QA drift")
    canonical={}
    for filename in ("fortune_batch01_part2_vi.csv","fortune_batch01_part3_vi.csv"):
        source_file="translation/source/"+filename
        for row in csv_rows(project/source_file):
            key=row["file_offset"].upper()
            if key in canonical:raise AssertionError("Duplicate source address "+key)
            canonical[key]=(source_file,row)
    mapped={r["unicode"]:r["code_hex"] for r in
            csv_rows(project/"translation/codepage/vi_codepage_v4_fe4_native.csv")}
    if mapped.get(" ")!="8440":
        raise AssertionError("Unexpected existing Vietnamese V2 font map")
    output=bytearray(base055)
    preview=bytearray(clean)
    allowed=set()
    markers=set()
    for row in rows:
        key=row["file_offset"].upper();off=int(key,16)
        original=canonical.get(key)
        if (original is None or row["source_file"]!=original[0]
            or row["source_jp"]!=original[1]["source_jp"]
            or row["vi_full"]!=original[1]["vi_full"]):
            raise AssertionError("Original Japanese/full Vietnamese source mismatch "+key)
        raw=row["source_jp"].encode("cp932")
        count=int(row["capacity"]);vi=row["vi_runtime"]
        if (len(raw)!=2*count or len(vi)>count or
            unicodedata.normalize("NFC",vi)!=vi):
            raise AssertionError("Original source glyph count / normalized VI overflow "+key)
        end=off+len(raw)
        if clean[off:end]!=raw or base055[off:end]!=raw:
            raise AssertionError("056 original Japanese slot not untouched by 055 "+key)
        if (clean[end:end+2]!=b"\x81\x6f" or
            base055[end:end+2]!=b"\x81\x6f"):
            raise AssertionError("Original Fortune 816F script marker missing "+key)
        span=set(range(off,end))
        if span&allowed:raise AssertionError("Overlapping two Fortune fields "+key)
        allowed|=span;markers.add(end)
        encoded=bytearray()
        for ch in vi+" "*(count-len(vi)):
            code=mapped.get(ch)
            if not code or len(code)!=4 or not code.startswith("84"):
                raise AssertionError("Vietnamese codepoint not available "+repr(ch))
            index=int(code[-2:],16)
            ptr=0x28000+0x1a74+2*(index-0x40)
            if index<0x40 or int.from_bytes(base055[ptr:ptr+2],"little")==0:
                raise AssertionError("Unassigned existing V2 font glyph "+repr(ch))
            encoded.extend(bytes.fromhex(code))
        if len(encoded)!=len(raw):raise AssertionError("Translated Fortune glyph byte length mismatch")
        output[off:end]=encoded
        preview[off:end]=encoded
        if output[end:end+2]!=b"\x81\x6f":raise AssertionError("Fortune 816F overwritten")
    if len(allowed)!=36 or len(markers)!=2:raise AssertionError("Approved 056 slot budget changed")
    probe=bytes(preview)
    patch_preview,n_preview=make_ips(clean,probe)
    if (sha(probe)!=PREVIEW_ROM_SHA or sha(patch_preview)!=PREVIEW_IPS_SHA
        or len(patch_preview)!=54 or n_preview!=2 or
        apply_ips(clean,patch_preview)!=probe):
        raise AssertionError("056 original-clean ROM physical experiment replay drift")
    text_only=bytes(output)
    text_change={i for i,(x,y) in enumerate(zip(base055,text_only)) if x!=y}
    if len(text_change)!=36 or text_change-allowed:
        raise AssertionError("Unexpected 056 modifications outside two Fortune records")
    output[0x7fdc:0x7fe0]=bytes(4)
    checksum=(sum(output)+0x1fe)&0xffff
    output[0x7fdc:0x7fde]=(checksum^0xffff).to_bytes(2,"little")
    output[0x7fde:0x7fe0]=checksum.to_bytes(2,"little")
    full=bytes(output)
    diff={i for i,(x,y) in enumerate(zip(base055,full)) if x!=y}
    if diff-(allowed|set(range(0x7fdc,0x7fe0))):
        raise AssertionError("Attempted overwrite outside 056 or checksum")
    ips,ips_count=make_ips(clean,full)
    if apply_ips(clean,ips)!=full:
        raise AssertionError("Combined 056 clean ROM IPS replay failed")
    return ips,{
        "status":"056_TWO_FORTUNE_RECORDS_STATIC_INTEGRATED_EMULATOR_UNTESTED",
        "input_055_rom_sha256":sha(base055),
        "added_fortune_records":2,
        "unchanged_original_816F_markers":len(markers),
        "approved_source_bytes":36,
        "modified_text_bytes":len(text_change),
        "unchanged_canonical_full_translations":True,
        "remaining_fortune_exceptions":plan["unresolved_source_offsets"],
        "clean_overlay_preview_SHA256":PREVIEW_IPS_SHA,
        "output_056_ROM_sha256":sha(full),
        "final_clean_IPS_sha256":sha(ips),
        "final_clean_IPS_bytes":len(ips),
        "final_clean_IPS_records":ips_count,
        "checksum":f"0x{checksum:04X}",
        "complement":f"0x{checksum^0xffff:04X}",
        "emulator_tested":False,
        "release_ready":False,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("clean_rom",type=Path)
    p.add_argument("verified_full_055_rom",type=Path)
    p.add_argument("--expected-055-sha",required=True)
    p.add_argument("--project-root",type=Path,default=ROOT)
    p.add_argument("--ips",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--allow-untested",action="store_true")
    a=p.parse_args()
    if not a.allow_untested:
        p.error("Emulator not yet verified; pass --allow-untested to create a static patch")
    if (len(a.expected_055_sha)!=64 or
        any(c not in "0123456789abcdef" for c in a.expected_055_sha)):
        p.error("Expected baseline 055 SHA must be 64 lowercase hex characters")
    paths=[a.clean_rom,a.verified_full_055_rom,a.ips,a.report]
    if len({x.resolve() for x in paths})!=len(paths):
        p.error("Inputs/outputs must be different files")
    baseline=a.verified_full_055_rom.read_bytes()
    if sha(baseline)!=a.expected_055_sha:p.error("055 SHA mismatches supplied verified base")
    ips,report=build(a.clean_rom.read_bytes(),baseline,a.project_root)
    for path,data in ((a.ips,ips),
                      (a.report,(json.dumps(report,ensure_ascii=False,indent=2)+"\n").encode())):
        path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
