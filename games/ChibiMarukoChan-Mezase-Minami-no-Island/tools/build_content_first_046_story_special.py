#!/usr/bin/env python3
"""Chibi SNES 046: resolve exceptional Story fields without corrupting CP932.

15 truly distinct original ROM text records are patched on top of exact 045.
8 false scanner offsets are mapped to the earlier/full real CP932 record;
they are NOT treated as independent sources. Leading xxF3 glyphs are retained
unchanged, not presumed editable text nor incorrectly deleted. Field widths,
original line/page markers and script stop opcodes are guarded byte-for-byte.

This is a *static experimental* IPS. It has NOT been run in an SNES emulator.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import unicodedata
from pathlib import Path

from build_content_first_040_fortune import apply_ips, make_ips
from build_content_first_042_story_safe_segments import physical_segments

ROOT=Path(__file__).resolve().parent.parent
CLEAN_SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
BASE_IPS_SHA="685d7e9f0146950ca030fd8469f57313a0b368be98e0a9c95999bda48cb65379"
BASE_ROM_SHA="7ddf449c2266838c3d55415f14aeee34fc21334c1ed0a490590647eb75e047b5"
OUTPUT_ROM_SHA="c10c0f444a97d6bea7f8f669d67bb6c0c5b6889b654d99d6e6dfa25e3d061624"
OUTPUT_IPS_SHA="11abac1b8e0f48e6580822bcdcd3b1b3568ae08676020b86c819ae641f53367d"

CANONICAL_FILES=(
    "story_batch01_vi.csv",
    "story_batch02_part1_vi.csv",
    "story_batch02_part2_vi.csv",
    "story_batch02_part3_vi.csv",
    "story_batch03_part1_vi.csv",
    "story_batch03_part2a_vi.csv",
    "story_batch03_part2b_vi.csv",
)

def sha(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()

def read_csv(path:Path)->list[dict[str,str]]:
    with path.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def markers(data:bytes):
    return tuple(i for i in range(0x18000,0x1e000)
        if data[i:i+2] in (b"\x81\x6f",b"\x81\xa5"))

def build(clean:bytes,ips045:bytes,project:Path):
    if len(clean)!=0x200000 or sha(clean)!=CLEAN_SHA:
        raise ValueError("Exact clean Japanese 2 MiB cartridge ROM required")
    if len(ips045)!=43679 or sha(ips045)!=BASE_IPS_SHA:
        raise ValueError("Exact checkpoint045 clean-ROM IPS required")
    before=apply_ips(clean,ips045)
    if sha(before)!=BASE_ROM_SHA:
        raise AssertionError("045 ROM reconstruction wrong")
    plan=json.loads(
        (project/"translation/runtime/story_special_cp932_alignment_046.json")
        .read_text(encoding="utf-8")
    )
    rows=plan["records"]
    if (plan["schema"]!="chibi.story.046.corrected_cp932_split"
        or plan["source_clean_sha256"]!=CLEAN_SHA
        or plan["input_045_rom_sha256"]!=BASE_ROM_SHA
        or plan["output_046_rom_sha256"]!=OUTPUT_ROM_SHA
        or plan["output_046_ips_sha256"]!=OUTPUT_IPS_SHA
        or len(rows)!=15 or plan["record_count"]!=15
        or len(plan["scanner_aliases"])!=8
        or len({r["physical_record_start"].upper() for r in rows})!=15):
        raise AssertionError("046 reviewed special-source manifest changed")
    source={}
    for filename in CANONICAL_FILES:
        for item in read_csv(project/"translation/source"/filename):
            k=item["file_offset"].upper()
            if k in source: raise AssertionError("duplicate source: "+k)
            source[k]=(filename,item)
    mapping={r["unicode"]:r["code_hex"] for r in
        read_csv(project/"translation/codepage/vi_codepage_v4_fe4_native.csv")}
    if (mapping.get(" ")!="8440"
        or int.from_bytes(before[0x2975e:0x29760],"little")!=0x9a74):
        raise AssertionError("Legacy font V2 unchanged mapping required")

    # All scanner "Q/R/P/O" digits are CP932 trailing bytes 0x51/0x52/
    # 0x50/0x4F of Japanese ２/３/１/０, NOT standalone variables.
    for alias in plan["scanner_aliases"]:
        off=int(alias["scanner_wrong_offset"],16)
        if clean[off-1]!=0x82 or clean[off] not in (0x4f,0x50,0x51,0x52):
            raise AssertionError(f"unverified CP932 second-byte alias {off:X}")
        parent=alias["parent_real_record"].upper()
        if not any(row["physical_record_start"].upper()==parent for row in rows):
            # A previous 043 or 044 full-field has already translated it.
            if before[off:off+1]==clean[off:off+1]:
                raise AssertionError("historically resolved split alias lacks real patch")

    output=bytearray(before)
    editable=set()
    source_breaks=0
    segment_count=0
    checked=[]
    for row in rows:
        key=row["canonical_scanner_offset"].upper()
        physical=int(row["physical_record_start"],16)
        prefix=bytes.fromhex(row["preserve_leading_cp932_hex"])
        fname,item=source.get(key,(None,None))
        if (item is None or row["source_file"]!="translation/source/"+fname
            or row["vi_full_reference"]!=item["vi_full"]
            or row["status"]!="static_edited_special_source_not_runtime_qa"):
            raise AssertionError("canonical Story identity drift: "+key)
        if prefix:
            if (len(prefix)!=2 or prefix[1]!=0xf3
                or clean[physical:physical+2]!=prefix
                or before[physical:physical+2]!=prefix):
                raise AssertionError("protected original xxF3 glyph changed "+key)
        if int(key,16)!=physical and int(key,16) not in (0x1a64f,0x1ba79):
            raise AssertionError("new corrected-start offset not approved "+key)
        if int(key,16)!=physical:
            scanner=int(key,16)
            if clean[scanner-1:scanner+1]!=b"\x82\x51":
                raise AssertionError("expected full CP932 ２ number "+key)
        end,spans,breaks=physical_segments(clean,physical)
        if before[physical:end]!=clean[physical:end]:
            raise AssertionError("preexisting translation collision "+key)
        caps=[(b-a)//2 for a,b in spans]
        if caps!=row["original_glyph_capacities"]:
            raise AssertionError("physical original Story budget changed "+key)
        texts=row["vi_runtime_lines"]
        if len(spans)!=len(texts):
            raise AssertionError("physical source segment count changed "+key)
        for i,((a,b),text) in enumerate(zip(spans,texts)):
            lead=len(prefix) if i==0 else 0
            if ((b-a)%2 or len(text)>(b-a-lead)//2
                or unicodedata.normalize("NFC",text)!=text):
                raise AssertionError("Story glyph overflow/normalization "+key)
            encoded=bytearray()
            for c in text+" "*((b-a-lead)//2-len(text)):
                digits=mapping.get(c)
                if digits is None or len(digits)!=4 or not digits.startswith("84"):
                    raise AssertionError(f"Unsupported existing font codepoint {c!r} {key}")
                idx=int(digits[-2:],16)
                ptr=0x28000+0x1a74+2*(idx-0x40)
                if idx<0x40 or int.from_bytes(before[ptr:ptr+2],"little")==0:
                    raise AssertionError(f"Unassigned codepoint {c!r} {key}")
                encoded.extend(bytes.fromhex(digits))
            positions=set(range(a+lead,b))
            if editable&positions:raise AssertionError("Overlapping 046 script spans")
            editable.update(positions)
            output[a+lead:b]=encoded
        if any(output[x:x+2]!=clean[x:x+2] for x in breaks):
            raise AssertionError("Original page/line marker changed "+key)
        if output[end]!=clean[end]:
            raise AssertionError("Original script control opcode changed "+key)
        source_breaks+=len(breaks)
        segment_count+=len(spans)
        checked.append(key)
    if len(editable)!=616 or source_breaks!=30 or segment_count!=31:
        raise AssertionError("Reviewed 046 original slot span changed")

    if markers(before)!=markers(output):
        raise AssertionError("Story line/page layout moved")
    output[0x7fdc:0x7fe0]=bytes(4)
    checksum=(sum(output)+0x1fe)&0xffff
    output[0x7fdc:0x7fde]=(checksum^0xffff).to_bytes(2,"little")
    output[0x7fde:0x7fe0]=checksum.to_bytes(2,"little")
    candidate=bytes(output)
    diff={i for i,(a,b) in enumerate(zip(before,candidate)) if a!=b}
    if sha(candidate)!=OUTPUT_ROM_SHA or len(diff)!=620:
        raise AssertionError("Result does not match reviewed 046 binary")
    if diff-(editable|set(range(0x7fdc,0x7fe0))):
        raise AssertionError("Unexpected non-dialogue ROM edits")
    ips,count=make_ips(clean,candidate)
    if (sha(ips)!=OUTPUT_IPS_SHA or len(ips)!=44450 or count!=1599
        or apply_ips(clean,ips)!=candidate):
        raise AssertionError("Original-ROM IPS replay failed")
    report={
        "status":"STATIC_STORY_SPECIAL_046_PASS_EMULATOR_UNTESTED",
        "actual_new_physical_Story_entries":len(checked),
        "aliased_false_CP932_scanner_offsets":8,
        "unchanged_original_line_page_breaks":source_breaks,
        "original_physical_segments":segment_count,
        "editable_original_glyph_bytes":len(editable),
        "changed_byte_positions_vs_045":len(diff),
        "preserved_leading_xxF3_prefixes":sum(
            bool(r["preserve_leading_cp932_hex"]) for r in rows),
        "all_original_Story_line_page_positions_unchanged":True,
        "new_ROM_SHA256":OUTPUT_ROM_SHA,
        "new_clean_ROM_IPS_SHA256":OUTPUT_IPS_SHA,
        "IPS_length":len(ips),
        "IPS_records":count,
        "checksum":f"{checksum:04X}",
        "checksum_complement":f"{checksum^0xffff:04X}",
        "full_game_translation_done":False,
        "real_SNES_emulator_QA":"NOT_TESTED",
    }
    return candidate,ips,report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("exact_clean_japanese_rom",type=Path)
    p.add_argument("exact_045_clean_rom_ips",type=Path)
    p.add_argument("--project-root",type=Path,default=ROOT)
    p.add_argument("--ips",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--output-rom",type=Path)
    p.add_argument("--allow-untested",action="store_true")
    a=p.parse_args()
    if not a.allow_untested:p.error("046 is STATIC ONLY; pass --allow-untested")
    files=[a.exact_clean_japanese_rom,a.exact_045_clean_rom_ips,
           a.ips,a.report]+([a.output_rom] if a.output_rom else [])
    if len({x.resolve() for x in files})!=len(files):
        p.error("Inputs and outputs must have different paths")
    blob,patch,report=build(
        a.exact_clean_japanese_rom.read_bytes(),
        a.exact_045_clean_rom_ips.read_bytes(),a.project_root)
    for dest,data in ((a.ips,patch),(a.report,
        (json.dumps(report,ensure_ascii=False,indent=2)+"\n").encode("utf-8"))):
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(data)
    if a.output_rom:
        a.output_rom.parent.mkdir(parents=True,exist_ok=True)
        a.output_rom.write_bytes(blob)
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
