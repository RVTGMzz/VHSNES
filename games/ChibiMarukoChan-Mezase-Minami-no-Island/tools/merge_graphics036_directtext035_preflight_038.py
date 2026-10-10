#!/usr/bin/env python3
"""Fail-closed merger for actual Chibi direct-text Build035 + GRAPHICS036.

Input A is the exact historical *DIRECT-TEXT* Build035, NOT the separate
GRAPHICS checkpoint035. Input B is GRAPHICS checkpoint036 derived from the
clean Japanese ROM (G0 startup title + Votri Valley credit, G1 Start/Password
and Chọn gì đây?). The clean ROM is the 3-way common ancestor.

Require hash identities, reject every existing direct-text edit inside the
ENTIRE graphics asset allocations (including G0 relocated bank86 staging),
preserve every byte of Build035 outside the graphics regions, check loader
calls and SNES header, and create a Build035-relative IPS if explicitly asked.

This tool CANNOT claim runtime acceptance or include any post-Build035
editorial vi_full changes: those require separate integration.
No copyrighted ROM contents are bundled in the repository.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

CLEAN_SHA = "e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
TEXT035_SHA = "f8fb662a9e1b8fc5a5ff689f690ceaf332055ed86983e52b476a78852e4fd58d"
GRAPHICS036_SHA = "2c8beee73e985c9a2690cc36ace335f05115c1a3e81b369e09d0cfb132117090"
SIZE = 0x200000
HEADER = (0x7FDC, 0x7FE0)
# Reserve *complete allocations*, not just differing bytes.
REGIONS = (
    ("g0_package_pointer", 0x12095, 0x12098),
    ("g0_bank86_relocated", 0x36907, 0x36907 + 3420),
    ("g0_4bpp_title", 0xF6456, 0xF6456 + 5570),
    ("g0_title_map", 0xF1F00, 0xF1F00 + 545),
    ("g1_story_choices", 0xBF95E, 0xBF95E + 436),
    ("g1_mode_question", 0xC706F, 0xC706F + 3485),
)
# Exact original loader and resource references outside the reserved spans.
ANCHORS = (
    (0x20047, "A2 13 A2 22 55 E2 80"), # main mode package $82:A213
    (0x12233, "00 70 6F F0 98"),       # $98:F06F at VRAM word $7000
    (0x12F4D, "00 78 5E F9 97"),       # $97:F95E at VRAM word $7800
)

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def validate_inputs(clean: bytes, text: bytes, graphics: bytes) -> None:
    for label, blob, expected in (
        ("exact_clean", clean, CLEAN_SHA),
        ("direct_text_035", text, TEXT035_SHA),
        ("graphics_036", graphics, GRAPHICS036_SHA),
    ):
        if len(blob) != SIZE or sha(blob) != expected:
            raise ValueError(f"{label}: exact 2MiB ROM and SHA-256 required")

def preflight(clean: bytes, base: bytes, graphics: bytes) -> dict:
    if not(len(clean) == len(base) == len(graphics) == SIZE):
        raise ValueError("all inputs must be exactly 2MiB unheadered")
    original_edit = {i for i,(a,b) in enumerate(zip(clean, base)) if a != b}
    graphics_edit = {i for i,(a,b) in enumerate(zip(clean, graphics)) if a != b}
    graphics_allowed = set(range(*HEADER))
    for _name, lo, hi in REGIONS:
        graphics_allowed.update(range(lo,hi))
    outliers = sorted(graphics_edit - graphics_allowed)
    asset_conflicts=[]
    for name, lo, hi in REGIONS:
        positions=[i for i in range(lo,hi) if clean[i] != base[i]]
        if positions:
            asset_conflicts.append({
                "asset":name, "preexisting_text_build_bytes":len(positions),
                "sample_offsets":[f"0x{p:X}" for p in positions[:8]],
            })
    anchor_conflicts=[]
    for off, hex_bytes in ANCHORS:
        signature=bytes.fromhex(hex_bytes)
        if clean[off:off+len(signature)] != signature:
            raise AssertionError(f"clean ROM loader signature drift: 0x{off:X}")
        if (base[off:off+len(signature)] != signature
            or graphics[off:off+len(signature)] != signature):
            anchor_conflicts.append(f"0x{off:X}")
    shared = (original_edit & graphics_edit) - set(range(*HEADER))
    return {
        "status": "SAFE_TO_MERGE" if not(asset_conflicts or anchor_conflicts or outliers)
                                  else "BLOCKED_NO_ROM_WRITE",
        "direct_text_base_sha256":sha(base),
        "graphics_base_sha256":sha(graphics),
        "prior_text_build_changed_bytes":len(original_edit),
        "graphics_build_changed_bytes":len(graphics_edit),
        "changed_byte_overlap_excluding_header":len(shared),
        "graphics_out_of_whitelist":[f"0x{p:X}" for p in outliers[:20]],
        "reserved_asset_region_conflicts":asset_conflicts,
        "retail_loader_anchor_conflicts":anchor_conflicts,
        "g0_relocation_region_file":"0x36907..0x37662",
        "source_vi_full_post_035_editorial_integrated":False,
        "font_65816_changes_performed":False,
        "emulator_runtime":"NOT_TESTED",
    }

def checksum(rebuilt: bytearray) -> tuple[int,int]:
    rebuilt[HEADER[0]:HEADER[1]] = bytes(4)
    value=(sum(rebuilt)+0x1FE)&0xFFFF
    comp=value^0xFFFF
    rebuilt[HEADER[0]:HEADER[0]+2]=comp.to_bytes(2,"little")
    rebuilt[HEADER[0]+2:HEADER[1]]=value.to_bytes(2,"little")
    return value,comp

def merge(clean: bytes, text: bytes, graphics: bytes) -> tuple[bytes,dict]:
    state=preflight(clean,text,graphics)
    if state["status"] != "SAFE_TO_MERGE":
        raise ValueError("CONFLICT: "+json.dumps(state,ensure_ascii=False))
    merged=bytearray(text)
    diff=0
    for _name,lo,hi in REGIONS:
        for off in range(lo,hi):
            if clean[off] != graphics[off]:
                merged[off]=graphics[off]
                diff+=1
    c,k=checksum(merged)
    if (merged[0x12095:0x12098] != bytes.fromhex("07 E9 86")
        or merged[0x12233:0x12238] != bytes.fromhex("00 70 6F F0 98")
        or merged[0x12F4D:0x12F52] != bytes.fromhex("00 78 5E F9 97")):
        raise AssertionError("merged asset loaders/pointers changed unexpectedly")
    for i in range(SIZE):
        if i in range(*HEADER):
            continue
        if not any(lo <= i < hi for _name,lo,hi in REGIONS) and merged[i]!=text[i]:
            raise AssertionError(f"direct-text source mutated outside graphics: {i:06X}")
    result=bytes(merged)
    state.update({"status":"MERGED_STATIC_ONLY",
                  "output_sha256":sha(result),
                  "graphics_bytes_written":diff,
                  "snes_checksum":f"0x{c:04X}",
                  "snes_complement":f"0x{k:04X}",
                  "release_ready":False})
    return result,state

def ips_patch(original: bytes, updated: bytes) -> bytes:
    out=bytearray(b"PATCH")
    pos=0
    while pos<len(original):
        if original[pos]==updated[pos]:
            pos+=1
            continue
        start=pos
        data=bytearray()
        while (pos<len(original) and len(data)<65535
               and original[pos]!=updated[pos]):
            data.append(updated[pos]);pos+=1
        out += start.to_bytes(3,"big")+len(data).to_bytes(2,"big")+data
    return bytes(out+b"EOF")

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("exact_clean_rom",type=Path)
    ap.add_argument("exact_direct_text_Build035_rom",type=Path)
    ap.add_argument("exact_graphics_checkpoint036_rom",type=Path)
    ap.add_argument("--report",type=Path)
    ap.add_argument("--output-rom",type=Path)
    ap.add_argument("--ips",type=Path)
    ap.add_argument("--explicit-untested-merge",action="store_true")
    a=ap.parse_args()
    paths=[a.exact_clean_rom,a.exact_direct_text_Build035_rom,
           a.exact_graphics_checkpoint036_rom]
    extra=[x for x in (a.report,a.output_rom,a.ips) if x is not None]
    if len({p.resolve() for p in paths+extra}) != len(paths+extra):
        ap.error("all input and output paths must be different")
    if bool(a.ips) != bool(a.output_rom):
        ap.error("--ips and --output-rom must be specified together")
    if a.output_rom and not a.explicit_untested_merge:
        ap.error("binary output is experimental; pass --explicit-untested-merge")
    clean,text,graphics=[p.read_bytes() for p in paths]
    validate_inputs(clean,text,graphics)
    status=preflight(clean,text,graphics)
    if status["status"]=="SAFE_TO_MERGE" and a.output_rom:
        candidate,merged=merge(clean,text,graphics)
        patch=ips_patch(text,candidate)
        status=merged
        a.output_rom.parent.mkdir(parents=True,exist_ok=True)
        a.output_rom.write_bytes(candidate)
        a.ips.parent.mkdir(parents=True,exist_ok=True)
        a.ips.write_bytes(patch)
        status["IPS_against_exact_direct_text_Build035_bytes"]=len(patch)
    elif status["status"]=="SAFE_TO_MERGE":
        status["status"]="DRY_RUN_SAFE_NOT_WRITTEN"
    status["release_ready"]=False
    result=json.dumps(status,ensure_ascii=False,indent=2)+"\n"
    if a.report:
        a.report.parent.mkdir(parents=True,exist_ok=True)
        a.report.write_text(result,encoding="utf-8")
    print(result)
    return 2 if status["status"]=="BLOCKED_NO_ROM_WRITE" else 0

if __name__=="__main__":
    raise SystemExit(main())
