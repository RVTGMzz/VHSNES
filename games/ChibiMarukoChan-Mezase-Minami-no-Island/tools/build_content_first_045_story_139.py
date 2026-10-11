#!/usr/bin/env python3
"""Chibi SNES checkpoint045 — rebuild +139 real Story B02/B03 fields.

Inputs: exact clean Japanese 2MiB ROM and EXACT checkpoint044 CLEAN-ROM IPS.
Source-of-truth: 140 reviewed VN runtime entries in translation/runtime/
story_batch02_03_content_first_045.json, canonical Story Batch02 and Batch03
full Vietnamese source files, and existing V2 0x84 glyph table.

No change to font/graphics/script bytes outside these exact original glyph
fields. Strict SHA pins and fail-closed per-physical-segment checks.
Static only; game/emulator NOT TESTED. Do not commit commercial ROM.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import unicodedata
from collections import Counter
from pathlib import Path

from build_content_first_040_fortune import apply_ips, make_ips
from build_content_first_042_story_safe_segments import physical_segments

ROOT=Path(__file__).resolve().parent.parent
CLEAN_SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
BASE_IPS_SHA="823009a95534b851b238efc439fa39c5b8af6af75a97075d1925e98f879c144d"
BASE_ROM_SHA="2312b9ba52c0cf6ac491e71117d5c537ad7dc61828dc9e87d838826e5165f322"
OUTPUT_SHA="7ddf449c2266838c3d55415f14aeee34fc21334c1ed0a490590647eb75e047b5"
OUTPUT_IPS_SHA="685d7e9f0146950ca030fd8469f57313a0b368be98e0a9c95999bda48cb65379"
SOURCE_FILES=(
    "story_batch02_part1_vi.csv","story_batch02_part2_vi.csv",
    "story_batch02_part3_vi.csv","story_batch03_part1_vi.csv",
    "story_batch03_part2a_vi.csv","story_batch03_part2b_vi.csv",
)

def sha(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()

def read_csv(path:Path):
    with path.open("r",newline="",encoding="utf-8-sig") as source:
        return list(csv.DictReader(source))

def marker_positions(data:bytes):
    return tuple(i for i in range(0x18000,0x1E000)
                 if data[i:i+2] in (b"\x81\x6f",b"\x81\xa5"))

def build(clean:bytes,patch044:bytes,project:Path):
    if len(clean)!=0x200000 or sha(clean)!=CLEAN_SHA:
        raise ValueError("requires exact clean Japanese ROM without copier header")
    if len(patch044)!=33893 or sha(patch044)!=BASE_IPS_SHA:
        raise ValueError("requires exact checkpoint044 clean-ROM IPS")
    previous=apply_ips(clean,patch044)
    if len(previous)!=0x200000 or sha(previous)!=BASE_ROM_SHA:
        raise AssertionError("044 ROM reconstruction hash did not match")
    path=project/"translation/runtime/story_batch02_03_content_first_045.json"
    manifest=json.loads(path.read_text(encoding="utf-8"))
    records=manifest["records"]
    if (manifest["schema"]!="chibi.story.content_first.045.v1"
        or manifest["clean_rom_sha256"]!=CLEAN_SHA
        or manifest["baseline_044_rom_sha256"]!=BASE_ROM_SHA
        or manifest["rom_sha256"]!=OUTPUT_SHA
        or manifest["ips_sha256"]!=OUTPUT_IPS_SHA
        or len(records)!=139 or manifest["total_new"]!=139
        or len({r["file_offset"].upper() for r in records})!=139):
        raise AssertionError("045 reviewed source manifest changed")
    source={}
    for fname in SOURCE_FILES:
        for row in read_csv(project/"translation/source"/fname):
            key=row["file_offset"].upper()
            if key in source:
                raise AssertionError(f"duplicate canonical Story address: {key}")
            source[key]=(fname,row)
    mapping={row["unicode"]:row["code_hex"] for row in
             read_csv(project/"translation/codepage/vi_codepage_v4_fe4_native.csv")}
    if (mapping.get(" ")!="8440"
        or int.from_bytes(previous[0x2975E:0x29760],"little")!=0x9A74):
        raise AssertionError("existing V2 codepage did not match")
    output=bytearray(previous)
    allowed=set()
    counts=Counter()
    original_breaks=0
    physical_spans=0
    for item in records:
        key=item["file_offset"].upper()
        off=int(key,16)
        original=source.get(key)
        if original is None:
            raise AssertionError(f"missing canonical Story source for {key}")
        name,canonical=original
        if (item["source_file"]!="translation/source/"+name
            or item["vi_full_reference"]!=canonical["vi_full"]
            or item["status"]!="static_exact_slot_translation_not_runtime_accepted"):
            raise AssertionError(f"canonical meaning/source mismatch {key}")
        batch="batch02" if name.startswith("story_batch02") else "batch03"
        if item["story_batch"]!=batch:
            raise AssertionError(f"wrong Story grouping at {key}")
        # 88F3/92F3/FAF3 are internal scanner/metadata prefixes, not proven
        # ordinary player-facing glyphs. Never overwrite them in fixed slots.
        if clean[off:off+2] in (bytes.fromhex("88F3"),bytes.fromhex("92F3"),bytes.fromhex("FAF3")):
            raise AssertionError(f"unverified source prefix at {key}")
        end,segments,breaks=physical_segments(clean,off)
        if previous[off:end]!=clean[off:end]:
            raise AssertionError(f"previous 044 patch already changed source at {key}")
        lines=item["vi_runtime_lines"]
        if len(lines)!=len(segments):
            raise AssertionError(f"original Story physical frame count drift {key}")
        for (a,b),caption in zip(segments,lines):
            if ((b-a)%2 or len(caption)>(b-a)//2
                or unicodedata.normalize("NFC",caption)!=caption):
                raise AssertionError(f"unapproved size or Unicode normalization {key}")
            encoded=bytearray()
            for c in caption+" "*((b-a)//2-len(caption)):
                digits=mapping.get(c)
                if not digits or len(digits)!=4 or not digits.startswith("84"):
                    raise AssertionError(f"missing existing V2 glyph {c!r} at {key}")
                idx=int(digits[-2:],16)
                slot=0x28000+0x1A74+2*(idx-0x40)
                if (idx<0x40 or slot+2>len(previous)
                    or int.from_bytes(previous[slot:slot+2],"little")==0):
                    raise AssertionError(f"invalid glyph ID at {key}: {c!r}")
                encoded.extend(bytes.fromhex(digits))
            positions=set(range(a,b))
            if allowed & positions:
                raise AssertionError(f"overlapping source target {key}")
            allowed.update(positions)
            output[a:b]=encoded
        for pointer in breaks:
            if output[pointer:pointer+2]!=clean[pointer:pointer+2]:
                raise AssertionError(f"corrupt Story line/page marker at {key}")
        if output[end]!=clean[end]:
            raise AssertionError(f"corrupt Story engine script opcode at {key}")
        counts[batch]+=1
        original_breaks+=len(breaks)
        physical_spans+=len(segments)
    if (counts!={"batch02":58,"batch03":81}
        or physical_spans!=368 or original_breaks!=367
        or len(allowed)!=7918):
        raise AssertionError("actual verified 045 Story source scope changed")
    output[0x7FDC:0x7FE0]=bytes(4)
    checksum=(sum(output)+0x1FE)&0xffff
    output[0x7FDC:0x7FDE]=(checksum^0xffff).to_bytes(2,"little")
    output[0x7FDE:0x7FE0]=checksum.to_bytes(2,"little")
    binary=bytes(output)
    diff={i for i,(a,b) in enumerate(zip(previous,binary)) if a!=b}
    if sha(binary)!=OUTPUT_SHA or len(diff)!=7915:
        raise AssertionError("045 experimental binary does not match reviewed exact SHA")
    if diff-(allowed|set(range(0x7FDC,0x7FE0))):
        raise AssertionError("045 changed bytes outside reviewed script glyph fields")
    if marker_positions(previous)!=marker_positions(binary):
        raise AssertionError("original Story line/page marker offsets moved")
    patch,num=make_ips(clean,binary)
    if (sha(patch)!=OUTPUT_IPS_SHA or len(patch)!=43679
        or num!=1568 or apply_ips(clean,patch)!=binary):
        raise AssertionError("independent original-ROM IPS replay failed")
    report={
        "status":"045_STORY_139_STATIC_PASS_NOT_EMULATOR",
        "added_Story_fields":dict(counts),
        "new_Story_records":139,
        "original_physical_glyph_segments":physical_spans,
        "original_line_page_delimiters_kept":original_breaks,
        "Story_bank_line_page_positions_unchanged":True,
        "unchanged_044_outside_approved_spans":True,
        "new_replacement_glyph_bytes":len(allowed),
        "changed_byte_positions_in_ROM":len(diff),
        "ROM_SHA256":OUTPUT_SHA,
        "IPS_SHA256":OUTPUT_IPS_SHA,
        "IPS_bytes":len(patch),
        "IPS_records":num,
        "SNES_checksum":f"0x{checksum:04X}",
        "SNES_complement":f"0x{checksum^0xffff:04X}",
        "legacy_font_glyphs_modified":False,
        "SNES_emulator":"NOT_TESTED",
        "whole_game_translation_finished":False,
    }
    return binary,patch,report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("exact_clean_rom",type=Path)
    p.add_argument("exact_checkpoint044_clean_ips",type=Path)
    p.add_argument("--project-root",type=Path,default=ROOT)
    p.add_argument("--ips",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--output-rom",type=Path)
    p.add_argument("--allow-untested",action="store_true")
    a=p.parse_args()
    if not a.allow_untested:
        p.error("045 ROM is experimental and emulator-untested; pass --allow-untested")
    paths=[a.exact_clean_rom,a.exact_checkpoint044_clean_ips,a.ips,a.report]+([a.output_rom] if a.output_rom else [])
    if len({x.resolve() for x in paths})!=len(paths):
        p.error("input and output paths must be distinct")
    binary,ips,report=build(a.exact_clean_rom.read_bytes(),
                            a.exact_checkpoint044_clean_ips.read_bytes(),
                            a.project_root)
    for target,data in ((a.ips,ips),(a.report,
          (json.dumps(report,indent=2,ensure_ascii=False)+"\n").encode("utf-8"))):
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
    if a.output_rom:
        a.output_rom.parent.mkdir(parents=True,exist_ok=True)
        a.output_rom.write_bytes(binary)
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
