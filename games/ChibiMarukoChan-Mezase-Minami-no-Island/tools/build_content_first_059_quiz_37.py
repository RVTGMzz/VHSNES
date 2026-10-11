#!/usr/bin/env python3
"""Apply 37 original-ROM-verified Quiz fields to full 058 ROM. Strict byte QA, not emulator acceptance."""
from __future__ import annotations
import argparse,csv,hashlib,json,unicodedata
from pathlib import Path
from build_content_first_040_fortune import make_ips,apply_ips
ROOT=Path(__file__).resolve().parent.parent
CLEAN_SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
PREVIEW_IPS_SHA="d383a705336236b3ff2c992ab3ce28c4605d1a5afd809bb8f8eb630035802a81"
PREVIEW_ROM_SHA="7a6c5cb411738706b019ea4b320e20d4bb131888ba2acdf3bd3aae3fdd3be0c2"
def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def csv_rows(p:Path):
    with p.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def native_frames(clean:bytes,off:int):
    if not 0x31d00<=off<0x3288e:raise AssertionError("Unapproved Quiz source bank")
    i=lo=off;frames=[];breaks=[]
    while i<off+280:
        b=clean[i]
        if b<0x20:break
        if clean[i:i+2]==b"\x81\x6f":
            frames.append((lo,i));breaks.append(i);i+=2;lo=i;continue
        if b==0x20:i+=1;continue
        if (0x81<=b<=0x9f or 0xe0<=b<=0xfc) and clean[i+1]>=0x40:
            i+=2;continue
        raise AssertionError(f"Unexpected native script opcode at {i:X}: {b:02X}")
    else:raise AssertionError("Unbounded Quiz source text")
    if i>lo:frames.append((lo,i))
    if not frames or not breaks or clean[i]>=0x20:
        raise AssertionError("Quiz source has no native line marker/stop")
    return frames,breaks,i

def build(clean:bytes,base058:bytes,root:Path):
    if len(clean)!=0x200000 or sha(clean)!=CLEAN_SHA:
        raise ValueError("Exact original Japanese 2MiB game ROM required")
    if len(base058)!=len(clean):raise ValueError("Full 058 ROM size mismatch")
    if int.from_bytes(base058[0x2975e:0x29760],"little")!=0x9a74:
        raise AssertionError("Vietnamese V2 glyph lookup pointer absent")
    plan=json.loads((root/"translation/runtime/quiz_content_first_37_059.json").read_text(encoding="utf-8"))
    rows=plan["records"]
    if (plan["schema"]!="chibi.quiz.content_first.059.v1" or
        plan["source_clean_rom_sha256"]!=CLEAN_SHA or len(rows)!=34 or
        plan["candidate_count"]!=34 or plan["native_physical_segments"]!=73 or
        len({r["file_offset"].upper() for r in rows})!=34 or
        plan["clean_source_only_IPS_sha256"]!=PREVIEW_IPS_SHA or
        plan["clean_source_only_ROM_sha256"]!=PREVIEW_ROM_SHA):
        raise AssertionError("059 reviewed Quiz source manifest drift")
    # The three birthday choices at 0x31F75/0x31F84/0x31F95 were already
    # integrated by stage047. Fail closed if they are re-added to stage059.
    prior={"0X31F75","0X31F84","0X31F95"}
    if {r["file_offset"].upper() for r in rows}&prior:
        raise AssertionError("Duplicate 047 birthday answer in 059")
    canonical={}
    for filename in ("quiz_batch03_part1_vi.csv",):
        for rec in csv_rows(root/"translation/source"/filename):
            key=rec["file_offset"].upper()
            if key in canonical:raise AssertionError("Duplicate original Quiz source "+key)
            canonical[key]=rec
    mapping={r["unicode"]:r["code_hex"] for r in
             csv_rows(root/"translation/codepage/vi_codepage_v4_fe4_native.csv")}
    if mapping.get(" ")!="8440":raise AssertionError("Existing V2 space glyph changed")
    output=bytearray(base058);preview=bytearray(clean)
    allowed=set();markers=set();nsegments=0
    for item in rows:
        key=item["file_offset"].upper();at=int(key,16)
        original_source=canonical.get(key)
        if (original_source is None or not original_source["vi_full"] or
            not original_source["source_jp_scanner"] or
            item.get("source_jp_scanner")!=original_source["source_jp_scanner"] or
            item.get("vi_full_reference")!=original_source["vi_full"] or
            item.get("source_file")!="translation/source/quiz_batch03_part1_vi.csv" or
            item["status"]!="verified_clean_original_byte_overlay_pending_full_058_merged_ROM_and_emulator"):
            raise AssertionError("Missing complete canonical Vietnamese/Japanese for "+key)
        frames,breaks,end=native_frames(clean,at)
        if base058[at:end]!=clean[at:end]:
            raise AssertionError("058 already modified Quiz source (collision) "+key)
        captions=item["vi_runtime_lines"]
        if len(frames)!=len(captions) or len(captions)!=len(item["expected_capacities"]):
            raise AssertionError("059 approved physical line/width inventory changed "+key)
        capacities=[]
        if len(frames)!=len(captions):
            raise AssertionError("Changed Quiz physical line count "+key)
        for (a,b),caption in zip(frames,captions):
            raw=clean[a:b]
            lead=len(raw)-len(raw.lstrip(b" "))
            tail=len(raw)-len(raw.rstrip(b" ")) if lead<len(raw) else 0
            start=a+lead;stop=b-tail;field=clean[start:stop]
            if len(field)%2:raise AssertionError("Odd original Quiz glyph bytes "+key)
            cells=len(field)//2
            capacities.append(cells)
            if (caption!=unicodedata.normalize("NFC",caption) or len(caption)>cells):
                raise AssertionError("Vietnamese overflow/non-NFC Quiz field "+key)
            if not field and caption:raise AssertionError("Text inserted into blank line "+key)
            dst=bytearray()
            for letter in caption+" "*(cells-len(caption)):
                code=mapping.get(letter)
                if not code or len(code)!=4 or not code.startswith("84"):
                    raise AssertionError(f"No 0x84 Vietnamese glyph {letter!r} at {key}")
                index=int(code[-2:],16);ptr=0x28000+0x1a74+2*(index-0x40)
                if index<0x40 or int.from_bytes(base058[ptr:ptr+2],"little")==0:
                    raise AssertionError(f"Existing V2 lookup missing glyph {letter!r} at {key}")
                dst.extend(bytes.fromhex(code))
            if field:
                span=set(range(start,stop))
                if span&allowed:raise AssertionError("Overlap between 058 Quiz fields "+key)
                allowed|=span
                output[start:stop]=dst
                preview[start:stop]=dst
        if capacities!=item["expected_capacities"]:
            raise AssertionError("059 source slots differ from original ROM audit "+key)
        markers.update(breaks);nsegments+=len(frames)
    if (len(allowed)!=1544 or nsegments!=73 or len(markers)!=73):
        raise AssertionError("059 physical text / native line inventory changed")
    if any(output[m:m+2]!=b"\x81\x6f" for m in markers):
        raise AssertionError("059 altered original 816F script line controls")
    probe=bytes(preview);probe_ips,probe_count=make_ips(clean,probe)
    if (sha(probe)!=PREVIEW_ROM_SHA or sha(probe_ips)!=PREVIEW_IPS_SHA or
        len(probe_ips)!=1914 or probe_count!=73 or apply_ips(clean,probe_ips)!=probe):
        raise AssertionError("057 actual clean Japanese ROM overlay fingerprint mismatch")
    changed={i for i,(a,b) in enumerate(zip(base058,output)) if a!=b}
    if len(changed)!=1541 or changed-allowed:
        raise AssertionError("057 modified unapproved source/script/font data")
    output[0x7fdc:0x7fe0]=bytes(4)
    checksum=(sum(output)+0x1fe)&0xffff
    output[0x7fdc:0x7fde]=(checksum^0xffff).to_bytes(2,"little")
    output[0x7fde:0x7fe0]=checksum.to_bytes(2,"little")
    merged=bytes(output)
    all_changes={i for i,(a,b) in enumerate(zip(base058,merged)) if a!=b}
    if all_changes-(allowed|set(range(0x7fdc,0x7fe0))):
        raise AssertionError("059 final ROM changed bytes outside Quiz and checksum")
    ips,records=make_ips(clean,merged)
    if apply_ips(clean,ips)!=merged:
        raise AssertionError("059 final clean-ROM IPS replay failed")
    return ips,{"status":"059_QUIZ37_STATIC_PASS_EMULATOR_NOT_TESTED",
        "new_Quiz_records":34,"original_native_line_frames":nsegments,
        "native_816F_controls_preserved":len(markers),
        "source_glyph_bytes_written":len(allowed),
        "actual_text_byte_differences":len(changed),
        "clean_ROM_overlay_IPS_sha256":PREVIEW_IPS_SHA,
        "source_058_rom_sha256":sha(base058),"final_ROM_sha256":sha(merged),
        "final_clean_IPS_sha256":sha(ips),"final_IPS_bytes":len(ips),
        "final_IPS_records":records,
        "SNES_checksum":f"0x{checksum:04X}",
        "SNES_complement":f"0x{checksum^0xffff:04X}",
        "emulator_tested":False,"whole_game_fully_translated":False}
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("clean_original_rom",type=Path)
    p.add_argument("full_058_rom",type=Path)
    p.add_argument("--expected-058-sha",required=True)
    p.add_argument("--project-root",type=Path,default=ROOT)
    p.add_argument("--ips",required=True,type=Path)
    p.add_argument("--report",required=True,type=Path)
    p.add_argument("--allow-untested",action="store_true")
    a=p.parse_args()
    if not a.allow_untested:
        p.error("This ROM build has no emulator gameplay QA; pass --allow-untested")
    if (len(a.expected_058_sha)!=64 or
        any(ch not in "0123456789abcdef" for ch in a.expected_058_sha)):
        p.error("Expected 058 SHA must be 64 lowercase hex characters")
    paths=[a.clean_original_rom,a.full_058_rom,a.ips,a.report]
    if len({x.resolve() for x in paths})!=4:p.error("Input and output paths must differ")
    base=a.full_058_rom.read_bytes()
    if sha(base)!=a.expected_058_sha:p.error("058 input ROM hash not as expected")
    ips,report=build(a.clean_original_rom.read_bytes(),base,a.project_root)
    for dst,blob in ((a.ips,ips),
                     (a.report,(json.dumps(report,ensure_ascii=False,indent=2)+"\n").encode())):
        dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(blob)
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
