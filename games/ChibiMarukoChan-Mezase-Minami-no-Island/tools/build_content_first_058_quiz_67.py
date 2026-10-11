#!/usr/bin/env python3
"""Apply 67 original-ROM-verified Quiz fields to full 057 ROM. Strict byte QA, not emulator acceptance."""
from __future__ import annotations
import argparse,csv,hashlib,json,unicodedata
from pathlib import Path
from build_content_first_040_fortune import make_ips,apply_ips
ROOT=Path(__file__).resolve().parent.parent
CLEAN_SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
PREVIEW_IPS_SHA="6403b2937ac1f82e33809954c6693b196bd425a830dfb79be4f18741a15da7d7"
PREVIEW_ROM_SHA="510f1f64a765f16f00235fa2218b9919fab1e5fb977f7ed8afc633fbf4565ff8"
def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def csv_rows(p:Path):
    with p.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def native_frames(clean:bytes,off:int):
    if not 0x32800<=off<0x34000:raise AssertionError("Unapproved Quiz source bank")
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

def build(clean:bytes,base057:bytes,root:Path):
    if len(clean)!=0x200000 or sha(clean)!=CLEAN_SHA:
        raise ValueError("Exact original Japanese 2MiB game ROM required")
    if len(base057)!=len(clean):raise ValueError("Full 057 ROM size mismatch")
    if int.from_bytes(base057[0x2975e:0x29760],"little")!=0x9a74:
        raise AssertionError("Vietnamese V2 glyph lookup pointer absent")
    plan=json.loads((root/"translation/runtime/quiz_content_first_67_058.json").read_text(encoding="utf-8"))
    rows=plan["records"]
    if (plan["schema"]!="chibi.quiz.content_first.058.v1" or
        plan["source_clean_rom_sha256"]!=CLEAN_SHA or len(rows)!=67 or
        plan["candidate_count"]!=67 or plan["physical_line_segments"]!=149 or
        len({r["file_offset"].upper() for r in rows})!=67 or
        plan["clean_source_only_IPS_sha256"]!=PREVIEW_IPS_SHA or
        plan["clean_source_only_ROM_sha256"]!=PREVIEW_ROM_SHA):
        raise AssertionError("058 reviewed Quiz source manifest drift")
    canonical={}
    for filename in ("quiz_batch03_part2_vi.csv","quiz_batch03_part3_vi.csv"):
        for rec in csv_rows(root/"translation/source"/filename):
            key=rec["file_offset"].upper()
            if key in canonical:raise AssertionError("Duplicate original Quiz source "+key)
            canonical[key]=rec
    mapping={r["unicode"]:r["code_hex"] for r in
             csv_rows(root/"translation/codepage/vi_codepage_v4_fe4_native.csv")}
    if mapping.get(" ")!="8440":raise AssertionError("Existing V2 space glyph changed")
    output=bytearray(base057);preview=bytearray(clean)
    allowed=set();markers=set();nsegments=0
    for item in rows:
        key=item["file_offset"].upper();at=int(key,16)
        original_source=canonical.get(key)
        if (original_source is None or not original_source["vi_full"] or
            not original_source["source_jp_scanner"] or
            item.get("source_jp_scanner")!=original_source["source_jp_scanner"] or
            item.get("vi_full_reference")!=original_source["vi_full"] or
            item.get("source_file") not in
               ("translation/source/quiz_batch03_part2_vi.csv",
                "translation/source/quiz_batch03_part3_vi.csv") or
            item["status"]!="clean_source_058_verified_await_057_merge_and_emulator"):
            raise AssertionError("Missing complete canonical Vietnamese/Japanese for "+key)
        expected_file="quiz_batch03_part2_vi.csv" if at<0x33460 else "quiz_batch03_part3_vi.csv"
        if item["source_file"]!="translation/source/"+expected_file:
            raise AssertionError("Canonical source filename/offset mismatch "+key)
        frames,breaks,end=native_frames(clean,at)
        if base057[at:end]!=clean[at:end]:
            raise AssertionError("057 already modified Quiz source (collision) "+key)
        captions=item["vi_runtime_lines"]
        if len(frames)!=len(captions):
            raise AssertionError("Changed Quiz physical line count "+key)
        for (a,b),caption in zip(frames,captions):
            raw=clean[a:b]
            lead=len(raw)-len(raw.lstrip(b" "))
            tail=len(raw)-len(raw.rstrip(b" ")) if lead<len(raw) else 0
            start=a+lead;stop=b-tail;field=clean[start:stop]
            if len(field)%2:raise AssertionError("Odd original Quiz glyph bytes "+key)
            cells=len(field)//2
            if (caption!=unicodedata.normalize("NFC",caption) or len(caption)>cells):
                raise AssertionError("Vietnamese overflow/non-NFC Quiz field "+key)
            if not field and caption:raise AssertionError("Text inserted into blank line "+key)
            dst=bytearray()
            for letter in caption+" "*(cells-len(caption)):
                code=mapping.get(letter)
                if not code or len(code)!=4 or not code.startswith("84"):
                    raise AssertionError(f"No 0x84 Vietnamese glyph {letter!r} at {key}")
                index=int(code[-2:],16);ptr=0x28000+0x1a74+2*(index-0x40)
                if index<0x40 or int.from_bytes(base057[ptr:ptr+2],"little")==0:
                    raise AssertionError(f"Existing V2 lookup missing glyph {letter!r} at {key}")
                dst.extend(bytes.fromhex(code))
            if field:
                span=set(range(start,stop))
                if span&allowed:raise AssertionError("Overlap between 058 Quiz fields "+key)
                allowed|=span
                output[start:stop]=dst
                preview[start:stop]=dst
        markers.update(breaks);nsegments+=len(frames)
    if (len(allowed)!=3180 or nsegments!=149 or len(markers)!=149):
        raise AssertionError("058 physical text / native line inventory changed")
    if any(output[m:m+2]!=b"\x81\x6f" for m in markers):
        raise AssertionError("058 altered original 816F script line controls")
    probe=bytes(preview);probe_ips,probe_count=make_ips(clean,probe)
    if (sha(probe)!=PREVIEW_ROM_SHA or sha(probe_ips)!=PREVIEW_IPS_SHA or
        len(probe_ips)!=3937 or probe_count!=151 or apply_ips(clean,probe_ips)!=probe):
        raise AssertionError("057 actual clean Japanese ROM overlay fingerprint mismatch")
    changed={i for i,(a,b) in enumerate(zip(base057,output)) if a!=b}
    if len(changed)!=3174 or changed-allowed:
        raise AssertionError("057 modified unapproved source/script/font data")
    output[0x7fdc:0x7fe0]=bytes(4)
    checksum=(sum(output)+0x1fe)&0xffff
    output[0x7fdc:0x7fde]=(checksum^0xffff).to_bytes(2,"little")
    output[0x7fde:0x7fe0]=checksum.to_bytes(2,"little")
    merged=bytes(output)
    all_changes={i for i,(a,b) in enumerate(zip(base057,merged)) if a!=b}
    if all_changes-(allowed|set(range(0x7fdc,0x7fe0))):
        raise AssertionError("058 final ROM changed bytes outside Quiz and checksum")
    ips,records=make_ips(clean,merged)
    if apply_ips(clean,ips)!=merged:
        raise AssertionError("058 final clean-ROM IPS replay failed")
    return ips,{"status":"058_QUIZ67_STATIC_PASS_EMULATOR_NOT_TESTED",
        "new_Quiz_records":67,"original_native_line_frames":nsegments,
        "native_816F_controls_preserved":len(markers),
        "source_glyph_bytes_written":len(allowed),
        "actual_text_byte_differences":len(changed),
        "clean_ROM_overlay_IPS_sha256":PREVIEW_IPS_SHA,
        "source_057_rom_sha256":sha(base057),"final_ROM_sha256":sha(merged),
        "final_clean_IPS_sha256":sha(ips),"final_IPS_bytes":len(ips),
        "final_IPS_records":records,
        "SNES_checksum":f"0x{checksum:04X}",
        "SNES_complement":f"0x{checksum^0xffff:04X}",
        "emulator_tested":False,"whole_game_fully_translated":False}
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("clean_original_rom",type=Path)
    p.add_argument("full_057_rom",type=Path)
    p.add_argument("--expected-057-sha",required=True)
    p.add_argument("--project-root",type=Path,default=ROOT)
    p.add_argument("--ips",required=True,type=Path)
    p.add_argument("--report",required=True,type=Path)
    p.add_argument("--allow-untested",action="store_true")
    a=p.parse_args()
    if not a.allow_untested:
        p.error("This ROM build has no emulator gameplay QA; pass --allow-untested")
    if (len(a.expected_057_sha)!=64 or
        any(ch not in "0123456789abcdef" for ch in a.expected_057_sha)):
        p.error("Expected 057 SHA must be 64 lowercase hex characters")
    paths=[a.clean_original_rom,a.full_057_rom,a.ips,a.report]
    if len({x.resolve() for x in paths})!=4:p.error("Input and output paths must differ")
    base=a.full_057_rom.read_bytes()
    if sha(base)!=a.expected_057_sha:p.error("057 input ROM hash not as expected")
    ips,report=build(a.clean_original_rom.read_bytes(),base,a.project_root)
    for dst,blob in ((a.ips,ips),
                     (a.report,(json.dumps(report,ensure_ascii=False,indent=2)+"\n").encode())):
        dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(blob)
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
