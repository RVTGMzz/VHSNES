#!/usr/bin/env python3
"""Checkpoint048 — guarded 103 Fortune glyph-field overlay on full checkpoint047.

The complete natural Vietnamese vi_full remains in canonical source CSVs;
compact in-game display forms are in translation/runtime/fortune_content_first_103_048.json.

This builder has TWO consciously distinct modes:
* default: require exact FULL 047 ROM; reject collisions; recompute checksum;
  write exact CLEAN-ROM-based combined 048 IPS, optional local-only ROM.
* --static-check-043: use exact 043 ROM already independently verified, create
  and SHA-pin an IPS containing the 103 text changes ONLY (no checksum). This
  proves original CP932 bytes, fixed glyph budgets and non-overlap with 043,
  but explicitly DOES NOT claim full 047+048 ROM exists.

Never publish copyrighted ROM or font files. Actual SNES gameplay UNTESTED.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import unicodedata
from pathlib import Path

from build_content_first_040_fortune import make_ips, apply_ips

PROJECT = Path(__file__).resolve().parent.parent
CLEAN_SHA = "e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
BASE_043_SHA = "45ffca7db5db83bc2734e885ee90c77f33746e2c4a54d1c99f1502f3e992a6ae"
BASE_047_SHA = "1f6430064b70671a4f3ba94f0fd256764db54690950519c22d9e03ec74230dd9"
PREVIEW_043_PLUS_TEXT_SHA = "4f461333d171fc21c3541ae29393056f0c9234ea0f5c4de46f97589afd20378b"
TEXT_OVERLAY_SHA = "3eb7dcc55d0c0b585beb4b27d6d2ca08c5facd39196042756eae0cf0dc68379c"
SOURCE_ROOT = "translation/source/"
SOURCE_FILES = {
    SOURCE_ROOT+"fortune_batch01_part1_vi.csv",
    SOURCE_ROOT+"fortune_batch01_part2_vi.csv",
    SOURCE_ROOT+"fortune_batch01_part3_vi.csv",
}

def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def build(clean: bytes, base: bytes, project: Path, static_check_043: bool = False):
    if len(clean) != 0x200000 or sha(clean) != CLEAN_SHA:
        raise ValueError("exact clean Japanese headerless 2MiB ROM required")
    expected_base = BASE_043_SHA if static_check_043 else BASE_047_SHA
    if len(base) != len(clean) or sha(base) != expected_base:
        raise ValueError(f"incorrect baseline ROM SHA; expected {expected_base}")

    manifest=json.loads((project/"translation/runtime/fortune_content_first_103_048.json")
                        .read_text(encoding="utf-8"))
    records=manifest["records"]
    if (manifest["schema"]!="chibi.fortune.content_first.048.v1"
        or manifest["new_Fortune_fields"]!=103
        or len(records)!=103
        or len({r["file_offset"].upper() for r in records})!=103
        or manifest["verified_existing_043_rom_sha256"]!=BASE_043_SHA
        or manifest["published_prior_047_rom_sha256"]!=BASE_047_SHA
        or manifest["verified_103_text_only_overlay_sha256"]!=TEXT_OVERLAY_SHA):
        raise AssertionError("048 source manifest drift")

    canonical={}
    for fn in SOURCE_FILES:
        for row in read_csv(project/fn):
            k=row["file_offset"].upper()
            if k in canonical: raise AssertionError("duplicate canonical Fortune address "+k)
            canonical[k]=(fn,row)
    glyph={r["unicode"]:r["code_hex"]
           for r in read_csv(project/"translation/codepage/vi_codepage_v4_fe4_native.csv")}
    ptr=int.from_bytes(base[0x2975E:0x29760],"little")
    if glyph.get(" ")!="8440" or ptr!=0x9A74:
        raise AssertionError("already-existing V2 0x84 font table changed")

    updated=bytearray(base)
    allowed=set()
    old_markers=[]
    for row in records:
        key=row["file_offset"].upper()
        original=canonical.get(key)
        if original is None: raise AssertionError("unknown original Fortune source "+key)
        fname,rec=original
        if (row["source_file"]!=fn
            or row["source_jp"]!=rec["source_jp"]
            or row["vi_full_reference"]!=rec["vi_full"]
            or row["status"]!="approved_static_048_experimental_not_emulator_reviewed"):
            raise AssertionError("unreviewed Japanese/complete Vietnamese source at "+key)

        at=int(key,16)
        jp=row["source_jp"]
        vi=row["vi_runtime"]
        raw=jp.encode("cp932")
        capacity=int(row["max_source_two_byte_units"])
        if (len(raw)!=2*capacity or len(vi)>capacity
            or unicodedata.normalize("NFC",vi)!=vi):
            raise AssertionError(f"two-byte original/translation capacity mismatch {key}")
        if clean[at:at+len(raw)]!=raw or base[at:at+len(raw)]!=raw:
            raise AssertionError("preexisting ROM contents collide with Fortune source "+key)
        if clean[at+len(raw):at+len(raw)+2]!=b"\x81\x6F":
            raise AssertionError("original Japanese Fortune line boundary missing "+key)
        if base[at+len(raw):at+len(raw)+2]!=b"\x81\x6F":
            raise AssertionError("published baseline 047 altered native Fortune control "+key)
        span=set(range(at,at+len(raw)))
        if allowed&span: raise AssertionError("overlapping 048 source fields "+key)
        allowed|=span
        dst=bytearray()
        for c in vi+" "*(capacity-len(vi)):
            digits=glyph.get(c)
            if digits is None or len(digits)!=4 or not digits.startswith("84"):
                raise AssertionError(f"missing previously existing glyph {c!r} at {key}")
            index=int(digits[-2:],16)
            offset=0x28000+(ptr&0x7FFF)+2*(index-0x40)
            if index<0x40 or int.from_bytes(base[offset:offset+2],"little")==0:
                raise AssertionError(f"unassigned existing V2 glyph {c!r} at {key}")
            dst.extend(bytes.fromhex(digits))
        if len(dst)!=len(raw): raise AssertionError("unexpected mapped field bytes "+key)
        updated[at:at+len(raw)]=dst

    if len(allowed)!=2002: raise AssertionError("048 original glyph byte span drift")
    modified={i for i,(old,new) in enumerate(zip(base,updated)) if old!=new}
    if len(modified)!=1997 or modified-allowed:
        raise AssertionError("048 touched original data outside approved Fortune source")
    text_only=bytes(updated)
    text_overlay,overlay_records=make_ips(base,text_only)
    if (sha(text_overlay)!=TEXT_OVERLAY_SHA or len(text_overlay)!=2545
        or overlay_records!=108 or apply_ips(base,text_overlay)!=text_only):
        raise AssertionError("text-only IPS differs from physical 043 prototype")

    report={
        "status":"048_FORTUNE_103_STATIC_PASS_"+("043_COMPATIBILITY_PROBE_NOT_FULL_MERGE"
                                         if static_check_043 else "COMBINED_047_MERGE_UNTESTED_EMULATOR"),
        "source_ROM_sha256":CLEAN_SHA,
        "source_baseline_sha256":expected_base,
        "additional_real_fortune_fields":103,
        "existing_prior_fortune_fields_047":48,
        "original_CP932_and_816F_markers_checked":103,
        "writable_legacy_two_byte_source_bytes":len(allowed),
        "actual_text_byte_differences":len(modified),
        "text_overlay_IPS_sha256":TEXT_OVERLAY_SHA,
        "text_overlay_IPS_bytes":len(text_overlay),
        "text_overlay_IPS_records":overlay_records,
        "prior_font_modified":False,
        "source_full_vi_full_modified":False,
        "emulator_runtime":"NOT_TESTED",
        "complete_game_translation":False,
    }
    if static_check_043:
        if sha(text_only)!=PREVIEW_043_PLUS_TEXT_SHA:
            raise AssertionError("043+103 non-checksum source ROM SHA unexpected")
        report["verification_target_sha256"]=PREVIEW_043_PLUS_TEXT_SHA
        report["full_047_plus_048_integrated"]=False
        return text_only,text_overlay,report

    # The checksum belongs to the merged 047+048 ROM, not the glyph overlay.
    updated[0x7FDC:0x7FE0]=bytes(4)
    checksum=(sum(updated)+0x1FE)&0xffff
    updated[0x7FDC:0x7FDE]=(checksum^0xFFFF).to_bytes(2,"little")
    updated[0x7FDE:0x7FE0]=checksum.to_bytes(2,"little")
    full=bytes(updated)
    diff={i for i,(a,b) in enumerate(zip(base,full)) if a!=b}
    if diff-(allowed|set(range(0x7FDC,0x7FE0))):
        raise AssertionError("048 final combined ROM changed bytes outside 103 Fortune fields/checksum")
    ips,records_count=make_ips(clean,full)
    if apply_ips(clean,ips)!=full:
        raise AssertionError("final clean-ROM 048 patch replay failed")
    report.update({
        "full_047_plus_048_integrated":True,
        "new_combined_ROM_sha256":sha(full),
        "new_combined_clean_ROM_IPS_sha256":sha(ips),
        "new_combined_IPS_bytes":len(ips),
        "new_combined_IPS_records":records_count,
        "SNES_checksum":f"0x{checksum:04X}",
        "SNES_complement":f"0x{checksum^0xFFFF:04X}",
        "all_modified_bytes_within_approved_fields_and_checksum":True,
        "SNES_emulator_acceptance":"NOT_TESTED",
    })
    return full,ips,report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("exact_clean_ROM",type=Path)
    p.add_argument("exact_047_or_043_ROM",type=Path)
    p.add_argument("--project-root",type=Path,default=PROJECT)
    p.add_argument("--ips",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--output-rom",type=Path)
    p.add_argument("--static-check-043",action="store_true")
    p.add_argument("--allow-untested",action="store_true")
    a=p.parse_args()
    if not a.allow_untested:
        p.error("game runtime NOT TESTED; pass --allow-untested explicitly")
    paths=[a.exact_clean_ROM,a.exact_047_or_043_ROM,a.ips,a.report]
    if a.output_rom:paths.append(a.output_rom)
    if len({f.resolve() for f in paths})!=len(paths):
        p.error("all inputs and output paths must be distinct")
    rom,patch,report=build(
        a.exact_clean_ROM.read_bytes(),a.exact_047_or_043_ROM.read_bytes(),
        a.project_root,a.static_check_043)
    for filename,data in ((a.ips,patch),
                          (a.report,(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
                           .encode("utf-8"))):
        filename.parent.mkdir(parents=True,exist_ok=True)
        filename.write_bytes(data)
    if a.output_rom:
        a.output_rom.parent.mkdir(parents=True,exist_ok=True)
        a.output_rom.write_bytes(rom)
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
