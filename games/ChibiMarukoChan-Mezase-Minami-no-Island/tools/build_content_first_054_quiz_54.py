#!/usr/bin/env python3
"""Checkpoint 054: 54 nonduplicate Quiz records on rebuilt full checkpoint048.

This builder never reads or releases an unauthorized ROM: the user supplies an
exact clean Japanese source and a verified full 048 baseline. It preserves all
native ASCII indentation, spaces, 816F line markers and script stop bytes.
The 54 short-form translations are pending actual SNES gameplay/editorial QA.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import unicodedata
from pathlib import Path
from build_content_first_040_fortune import apply_ips,make_ips

ROOT=Path(__file__).resolve().parent.parent
CLEAN_SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
MANIFEST="translation/runtime/quiz_content_first_54_054.json"
PREVIEW_IPS_SHA="9f5069f7a105e371a71f9cf8bf5fdd38bae099d774c184a272f9abec9c8908ad"

def sha(raw:bytes)->str:
    return hashlib.sha256(raw).hexdigest()

def csv_rows(file:Path):
    with file.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def segments(clean:bytes,offset:int):
    if offset<0x31D00 or offset>=0x37000:
        raise AssertionError(f"Unapproved Quiz bank {offset:X}")
    pos=left=offset
    frames=[]
    markers=[]
    while pos<offset+280:
        first=clean[pos]
        if first<0x20:break
        if clean[pos:pos+2]==b"\x81\x6f":
            frames.append((left,pos))
            markers.append(pos)
            pos+=2
            left=pos
            continue
        if first==0x20:
            pos+=1
            continue
        if (0x81<=first<=0x9f or 0xe0<=first<=0xfc) and clean[pos+1]>=0x40:
            pos+=2
            continue
        raise AssertionError(f"Unsafe native Quiz byte {first:02X} at {pos:X}")
    else:
        raise AssertionError(f"Quiz text frame too long {offset:X}")
    if pos>left:
        frames.append((left,pos))
    if not frames or clean[pos]>=0x20:
        raise AssertionError(f"Missing native script stop {offset:X}")
    return frames,markers,pos

def build(clean:bytes,baseline:bytes,project:Path):
    if len(clean)!=0x200000 or sha(clean)!=CLEAN_SHA:
        raise ValueError("Wrong original Japanese 2MiB ROM")
    if len(baseline)!=len(clean):
        raise ValueError("048 ROM size mismatch")
    if int.from_bytes(baseline[0x2975e:0x29760],"little")!=0x9a74:
        raise AssertionError("Missing established 0x84xx V2 font/codepage root")
    plan=json.loads((project/MANIFEST).read_text(encoding="utf-8"))
    rows=plan["records"]
    if (plan["schema"]!="chibi.quiz.content_first.054.v1" or
        plan["source_clean_sha256"]!=CLEAN_SHA or
        plan["candidate_count"]!=54 or len(rows)!=54 or
        len({r["file_offset"].lower() for r in rows})!=54):
        raise AssertionError("054 editorial source drift")
    used=set()
    for name in ("main_menu_compact_v1.csv","ui_choices_compact_v1.csv",
                 "quiz_answers_exact_fit_041.csv"):
        used.update(r["file_offset"].lower() for r in
                    csv_rows(project/"translation/runtime"/name))
    prior047=json.loads((project/"translation/runtime/quiz_fortune_exactfit_047.json")
                      .read_text(encoding="utf-8"))
    used.update(r["file_offset"].lower() for r in prior047["records"])
    mapped={r["unicode"]:r["code_hex"] for r in
            csv_rows(project/"translation/codepage/vi_codepage_v4_fe4_native.csv")}
    if mapped.get(" ")!="8440":
        raise AssertionError("V2 space glyph code drift")
    out=bytearray(baseline)
    allowed=set()
    markers=set()
    segments_count=0
    for row in rows:
        key=row["file_offset"].lower()
        at=int(key,16)
        if key in used:
            raise AssertionError("Previously integrated Quiz/UI field: "+key)
        captions=row["vi_runtime_lines"]
        frames,breaks,stop=segments(clean,at)
        if (row["status"]!="clean_rom_source_verified_pending_048_merged_ROM_emulator"
            or len(frames)!=len(captions) or not breaks):
            raise AssertionError("Native Quiz frame count/status drift "+key)
        capacities=[]
        for (start,end),caption in zip(frames,captions):
            native=clean[start:end]
            if native.strip(b" ")==b"":
                body_start=body_end=start
            else:
                left=len(native)-len(native.lstrip(b" "))
                right=len(native)-len(native.rstrip(b" "))
                body_start=start+left
                body_end=end-right
            content=clean[body_start:body_end]
            if len(content)%2:
                raise AssertionError("Odd physical text bytes at "+key)
            cap=len(content)//2
            capacities.append(cap)
            if (unicodedata.normalize("NFC",caption)!=caption or
                len(caption)>cap):
                raise AssertionError("054 Vietnamese exceeds native glyph cells: "+key)
            if not content:
                if caption:raise AssertionError("Text in blank physical record "+key)
                continue
            if baseline[start:end]!=native:
                raise AssertionError("048 baseline already edited Quiz text at "+key)
            dst=bytearray()
            for char in caption+" "*(cap-len(caption)):
                code=mapped.get(char)
                if code is None or len(code)!=4 or not code.startswith("84"):
                    raise AssertionError(f"Unsupported old glyph {char!r} at {key}")
                index=int(code[-2:],16)
                ptr=0x28000+0x1a74+2*(index-0x40)
                if index<0x40 or int.from_bytes(baseline[ptr:ptr+2],"little")==0:
                    raise AssertionError(f"Unassigned old glyph {char!r} at {key}")
                dst.extend(bytes.fromhex(code))
            physical=set(range(body_start,body_end))
            if physical&allowed:
                raise AssertionError("Overlapping 054 source spans: "+key)
            allowed.update(physical)
            out[body_start:body_end]=dst
        if capacities!=row["expected_capacities"]:
            raise AssertionError("Native line lengths shifted at "+key)
        if baseline[at:stop]!=clean[at:stop]:
            # By now only permitted glyphs can differ in out, not baseline.
            raise AssertionError("Input baseline premodified source: "+key)
        for i in breaks:
            if out[i:i+2]!=b"\x81\x6f":
                raise AssertionError("Original 816F marker modified "+key)
        markers.update(breaks)
        segments_count+=len(frames)
    if len(allowed)!=2642 or segments_count!=123 or len(markers)!=123:
        raise AssertionError("054 byte/line source inventory changed")
    text_only=bytes(out)
    text_changes={i for i,(x,y) in enumerate(zip(baseline,text_only)) if x!=y}
    if len(text_changes)!=2636 or text_changes-allowed:
        raise AssertionError("054 modified unexpected code/script bytes")
    # All clean ROM text-only changed positions are independent of previous
    # 048 patches, so checking the per-field delta is enough here.
    out[0x7fdc:0x7fe0]=bytes(4)
    ck=(sum(out)+0x1fe)&0xffff
    out[0x7fdc:0x7fde]=(ck^0xffff).to_bytes(2,"little")
    out[0x7fde:0x7fe0]=ck.to_bytes(2,"little")
    full=bytes(out)
    delta={i for i,(a,b) in enumerate(zip(baseline,full)) if a!=b}
    if delta-(allowed|set(range(0x7fdc,0x7fe0))):
        raise AssertionError("Unexpected changed data outside Quiz and checksum")
    ips,record_count=make_ips(clean,full)
    if apply_ips(clean,ips)!=full:
        raise AssertionError("Independent final clean-ROM IPS replay failed")
    return ips,{
        "status":"054_STATIC_ROM_INTEGRATED_NOT_EMULATOR_ACCEPTED",
        "source_clean_sha256":CLEAN_SHA,
        "baseline_048_sha256":sha(baseline),
        "new_Quiz_records":54,
        "new_physical_text_segments":123,
        "native_line_markers_preserved":len(markers),
        "approved_glyph_source_bytes":len(allowed),
        "changed_text_byte_positions":len(text_changes),
        "output_ROM_sha256":sha(full),
        "output_clean_IPS_sha256":sha(ips),
        "IPS_bytes":len(ips),
        "IPS_records":record_count,
        "SNES_checksum":f"0x{ck:04X}",
        "SNES_complement":f"0x{ck^0xffff:04X}",
        "gameplay_tested":False,
        "release_ready":False,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("clean_rom",type=Path)
    p.add_argument("full_verified_048_rom",type=Path)
    p.add_argument("--expected-048-sha",required=True)
    p.add_argument("--project-root",type=Path,default=ROOT)
    p.add_argument("--ips",required=True,type=Path)
    p.add_argument("--report",required=True,type=Path)
    p.add_argument("--allow-untested",action="store_true")
    a=p.parse_args()
    if not a.allow_untested:
        p.error("ROM data only, SNES emulator untested; pass --allow-untested")
    if (len(a.expected_048_sha)!=64 or
        any(ch not in "0123456789abcdef" for ch in a.expected_048_sha)):
        p.error("Expected 048 SHA must be 64 lowercase hex characters")
    base=a.full_verified_048_rom.read_bytes()
    if sha(base)!=a.expected_048_sha:
        p.error("048 baseline does not match expected SHA")
    targets=[a.clean_rom,a.full_verified_048_rom,a.ips,a.report]
    if len({x.resolve() for x in targets})!=len(targets):
        p.error("Inputs and outputs must be distinct")
    ips,report=build(a.clean_rom.read_bytes(),base,a.project_root)
    for dest,payload in ((a.ips,ips),
                         (a.report,(json.dumps(report,ensure_ascii=False,indent=2)+"\n").encode())):
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(payload)
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
