#!/usr/bin/env python3
"""Chibi content-first checkpoint044: 87 NEW Story Batch01+02 fixed-slot records.

Reconstruct from exact original Japanese 2MiB ROM + exact 043 CLEAN-ROM IPS.
No new glyph/font work, never overwrite an older edited script field.
Canonical full Vietnamese text stays in source; short display candidates are
separately reviewed in runtime JSON. SNES emulator NOT tested.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, unicodedata
from pathlib import Path
from build_content_first_040_fortune import apply_ips, make_ips
from build_content_first_042_story_safe_segments import physical_segments

ROOT=Path(__file__).resolve().parent.parent
SOURCE_SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
BASE_IPS_SHA="d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50"
BASE_ROM_SHA="45ffca7db5db83bc2734e885ee90c77f33746e2c4a54d1c99f1502f3e992a6ae"
NEW_ROM_SHA="2312b9ba52c0cf6ac491e71117d5c537ad7dc61828dc9e87d838826e5165f322"
NEW_IPS_SHA="823009a95534b851b238efc439fa39c5b8af6af75a97075d1925e98f879c144d"
CHECKSUM=(0x7FDC,0x7FE0)

def sha(blob):return hashlib.sha256(blob).hexdigest()
def load_csv(path):
    with path.open(encoding="utf-8-sig",newline="") as fp:return list(csv.DictReader(fp))
def marker_positions(blob):
    return tuple(i for i in range(0x18000,0x1E000)
                 if blob[i:i+2] in (b"\x81\x6F",b"\x81\xA5"))

def build(clean,ips043,project):
    if len(clean)!=0x200000 or sha(clean)!=SOURCE_SHA:
        raise ValueError("need exact original headerless Japanese ROM")
    if len(ips043)!=28135 or sha(ips043)!=BASE_IPS_SHA:
        raise ValueError("need exact 043 CLEAN-ROM IPS")
    previous=apply_ips(clean,ips043)
    if sha(previous)!=BASE_ROM_SHA:
        raise AssertionError("043 baseline reconstruction failed")

    plan=json.loads((project/"translation/runtime/story_batch01_02_content_first_044.json").read_text(encoding="utf-8"))
    records=plan["records"]
    if (plan["schema"]!="chibi.story.content_first.044.v1"
        or plan["expected_records"]!=87 or len(records)!=87
        or len({x["file_offset"].upper() for x in records})!=87
        or plan["output_044_sha256"]!=NEW_ROM_SHA
        or plan["output_044_ips_sha256"]!=NEW_IPS_SHA):
        raise AssertionError("reviewed 044 plan changed")
    allcanonical={}
    for name in ("story_batch01_vi.csv","story_batch02_part1_vi.csv",
                 "story_batch02_part2_vi.csv"):
        for item in load_csv(project/"translation/source"/name):
            key=item["file_offset"].upper()
            if key in allcanonical:
                raise AssertionError("duplicate source row "+key)
            allcanonical[key]=(name,item)
    codepage={r["unicode"]:r["code_hex"] for r in
              load_csv(project/"translation/codepage/vi_codepage_v4_fe4_native.csv")}
    if codepage.get(" ")!="8440" or int.from_bytes(previous[0x2975E:0x29760],"little")!=0x9A74:
        raise AssertionError("existing font V2/codepage identity changed")
    previous_plan=json.loads((project/"translation/runtime/story_batch01_safe_segments_043.json").read_text(encoding="utf-8"))
    prev_offsets={r["file_offset"].upper() for r in previous_plan["records"]}
    translated=bytearray(previous)
    allowed=set()
    controls=0
    physical_spans=0
    categories={"batch01":0,"batch02":0}
    for entry in records:
        key=entry["file_offset"].upper()
        if key in prev_offsets or int(key,16) in (0x181CC,0x18245,0x182BE):
            raise AssertionError("cannot rewrite previously localized source "+key)
        original=allcanonical.get(key)
        if original is None:raise AssertionError("unknown canonical source "+key)
        filename,source=original
        if (entry["vi_full_reference"]!=source["vi_full"]
            or entry["source_file"]!="translation/source/"+filename
            or entry["status"]!="candidate_static_not_emulator_reviewed"):
            raise AssertionError("canonical full Vietnamese meaning changed at "+key)
        if entry["story_batch"] not in categories:raise AssertionError("unknown Story batch")
        if entry["story_batch"]=="batch01" and filename!="story_batch01_vi.csv":
            raise AssertionError("wrong batch01 source")
        if entry["story_batch"]=="batch02" and not filename.startswith("story_batch02"):
            raise AssertionError("wrong batch02 source")
        offset=int(key,16)
        end,spans,breaks=physical_segments(clean,offset)
        text=entry["vi_runtime_lines"]
        if len(text)!=len(spans) or not spans:
            raise AssertionError("original physical Story frame count changed "+key)
        if previous[offset:end]!=clean[offset:end]:
            raise AssertionError("earlier patch already occupies Story record "+key)
        for (begin,stop),caption in zip(spans,text):
            if ((stop-begin)%2 or caption!=unicodedata.normalize("NFC",caption)
                or len(caption)>(stop-begin)//2):
                raise AssertionError("odd source field / overflow / non-NFC "+key)
            encoded=bytearray()
            for char in caption+" "*((stop-begin)//2-len(caption)):
                digits=codepage.get(char)
                if digits is None or len(digits)!=4 or not digits.startswith("84"):
                    raise AssertionError(f"undefined source codepoint at {key}: {char!r}")
                idx=int(digits[-2:],16)
                ptr=0x28000+0x1A74+2*(idx-0x40)
                if idx<0x40 or ptr+2>len(previous) or int.from_bytes(previous[ptr:ptr+2],"little")==0:
                    raise AssertionError(f"unmapped legacy glyph in {key}: {char!r}")
                encoded.extend(bytes.fromhex(digits))
            positions=set(range(begin,stop))
            if allowed&positions:raise AssertionError("overlapping Story fields "+key)
            allowed.update(positions)
            translated[begin:stop]=encoded
        for at in breaks:
            if translated[at:at+2]!=clean[at:at+2]:
                raise AssertionError("original line/page opcode changed")
        if translated[end]!=clean[end]:
            raise AssertionError("original Story next script opcode changed")
        physical_spans+=len(spans)
        controls+=len(breaks)
        categories[entry["story_batch"]]+=1
    if (categories!={"batch01":33,"batch02":54} or controls!=214
        or physical_spans!=214 or len(allowed)!=4680):
        raise AssertionError("reviewed 044 physical source contract changed")
    translated[CHECKSUM[0]:CHECKSUM[1]]=bytes(4)
    checksum=(sum(translated)+0x1FE)&0xFFFF
    translated[0x7FDC:0x7FDE]=(checksum^0xFFFF).to_bytes(2,"little")
    translated[0x7FDE:0x7FE0]=checksum.to_bytes(2,"little")
    output=bytes(translated)
    if sha(output)!=NEW_ROM_SHA:
        raise AssertionError("result differs from exact independently verified 044")
    changed={i for i,(a,b) in enumerate(zip(previous,output)) if a!=b}
    if len(changed)!=4682 or changed-(allowed|set(range(*CHECKSUM))):
        raise AssertionError("044 changed non-Story bytes or source size")
    if marker_positions(previous)!=marker_positions(output):
        raise AssertionError("an original Story 816F/81A5 delimiter moved")
    patch,record_count=make_ips(clean,output)
    if (sha(patch)!=NEW_IPS_SHA or len(patch)!=33893
        or record_count!=1193 or apply_ips(clean,patch)!=output):
        raise AssertionError("044 IPS clean-ROM replay mismatch")
    report={
        "status":"044_STATIC_STORY_87_PASS_NOT_EMULATOR",
        "new_stories":categories,"new_story_records":87,
        "physical_story_segments":physical_spans,"original_breaks_kept":controls,
        "all_story_bank_breaks_unchanged":True,
        "bytes_changed_from_043":len(changed),"prior_043_SHA":BASE_ROM_SHA,
        "new_ROM_SHA":NEW_ROM_SHA,"clean_ROM_IPS_SHA":NEW_IPS_SHA,
        "ips_bytes":len(patch),"ips_records":record_count,
        "checksum":f"0x{checksum:04X}",
        "complement":f"0x{checksum^0xFFFF:04X}",
        "font_or_glyph_edits":False,"SNES_emulator":"NOT_TESTED",
        "full_game_localized":False,
    }
    return output,patch,report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("clean_rom",type=Path)
    p.add_argument("checkpoint043_clean_rom_ips",type=Path)
    p.add_argument("--project-root",type=Path,default=ROOT)
    p.add_argument("--ips",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--output-rom",type=Path)
    p.add_argument("--allow-untested",action="store_true")
    a=p.parse_args()
    if not a.allow_untested:p.error("Static-only ROM; pass --allow-untested")
    paths=[a.clean_rom,a.checkpoint043_clean_rom_ips,a.ips,a.report]+([a.output_rom] if a.output_rom else [])
    if len({x.resolve() for x in paths})!=len(paths):
        p.error("all input and output paths must differ")
    rom,ips,report=build(a.clean_rom.read_bytes(),a.checkpoint043_clean_rom_ips.read_bytes(),a.project_root)
    for dest,data in ((a.ips,ips),(a.report,(json.dumps(report,ensure_ascii=False,indent=2)+"\n").encode())):
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    if a.output_rom:
        a.output_rom.parent.mkdir(parents=True,exist_ok=True)
        a.output_rom.write_bytes(rom)
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
