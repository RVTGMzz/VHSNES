#!/usr/bin/env python3
"""Chibi 043: integrate 58 additional scene-aware Story dialogues over exact 042 IPS.

No destructive truncation of canonical full Vietnamese, guessed pointers, or
overwritten dialogue control codes. Runtime lines are separately edited
short forms with exact original physical segment capacities; full meaning
stays in canonical story_batch01_vi.csv. Static ROM only; NOT emulator QA.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,unicodedata
from pathlib import Path

from build_content_first_040_fortune import apply_ips, make_ips, sha

ROOT=Path(__file__).resolve().parent.parent
CLEAN_SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
BASE_IPS_SHA="3e3c3de245a9a0a6648b2e62eff44a72093ef1e2e9cfcb1cf013ff6c4cbb5035"
BASE_SHA="901744ff2edb6bbf667e225e68478009f426a4d1358c1c35ccb34cdc29254691"
OUTPUT_SHA="45ffca7db5db83bc2734e885ee90c77f33746e2c4a54d1c99f1502f3e992a6ae"
OUTPUT_IPS_SHA="d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50"
LOW_CONTROL_MAX=0x20
BREAKS=(b"\x81\x6f",b"\x81\xa5")


def read_csv(file:Path)->list[dict[str,str]]:
    with file.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))


def physical_segments(clean:bytes,off:int)->tuple[int,list[tuple[int,int]],list[int]]:
    """Consume only original raw Japanese text until first low-byte script op.

    0x816F line delimiters and 0x81A5 page breaks are immutable; pair lead
    bytes and single raw ASCII spaces form editable physical glyph regions.
    Other literal ASCII or invalid CP932 pairs cause a fail-closed abort.
    """
    if off<0x18000 or off>=0x1e000:
        raise AssertionError(f"outside validated Story bank: {off:X}")
    i=lo=off
    spans=[]
    controls=[]
    while i<off+400:
        b=clean[i]
        if b<LOW_CONTROL_MAX:
            break
        if clean[i:i+2] in BREAKS:
            if i>lo:spans.append((lo,i))
            controls.append(i)
            i+=2
            lo=i
            continue
        if b==0x20:
            i+=1
            continue
        if 0x81<=b<=0x9f or 0xe0<=b<=0xfc:
            if i+1>=len(clean) or clean[i+1]<0x40:
                raise AssertionError(f"invalid double-byte Japanese source at {i:X}")
            i+=2
            continue
        raise AssertionError(f"unexpected ASCII or script byte at {i:X}: {b:02X}")
    else:
        raise AssertionError("Story physical record exceeded 400B safety limit")
    if i>lo:spans.append((lo,i))
    if not spans:
        raise AssertionError(f"empty source text at {off:X}")
    return i,spans,controls


def build(clean:bytes,ips042:bytes,project:Path):
    if len(clean)!=0x200000 or sha(clean)!=CLEAN_SHA:
        raise ValueError("exact original headerless 2MiB Japanese ROM required")
    if len(ips042)!=23105 or sha(ips042)!=BASE_IPS_SHA:
        raise ValueError("exact original 042 clean-ROM IPS required")
    prior=apply_ips(clean,ips042)
    if sha(prior)!=BASE_SHA:
        raise AssertionError("042 source reconstruction hash failed")
    plan=json.loads((project/"translation/runtime/story_batch01_safe_segments_043.json").read_text(encoding="utf-8"))
    rows=plan["records"]
    if (plan.get("schema")!="chibi.story.runtime043.v1"
        or len(rows)!=58 or plan["expected_records"]!=58
        or len({x["file_offset"] for x in rows})!=58
        or plan["output_043_rom_sha256"]!=OUTPUT_SHA or plan["output_043_ips_sha256"]!=OUTPUT_IPS_SHA):
        raise AssertionError("043 translation manifest changed")
    canonical={row["file_offset"].upper():row for row in
               read_csv(project/"translation/source/story_batch01_vi.csv")}
    mapping={r["unicode"]:r["code_hex"] for r in
             read_csv(project/"translation/codepage/vi_codepage_v4_fe4_native.csv")}
    if mapping.get(" ")!="8440" or int.from_bytes(prior[0x2975e:0x29760],"little")!=0x9a74:
        raise AssertionError("previously verified V2 character table changed")

    previous_plan=json.loads((project/"translation/runtime/story_batch01_safe_segments_042.json").read_text(encoding="utf-8"))
    previous_offsets={r["file_offset"].upper() for r in previous_plan["records"]}
    if any(r["file_offset"].upper() in previous_offsets for r in rows):
        raise AssertionError("043 cannot write a Story field already modified by 042")
    output=bytearray(prior)
    changed_allowed=set()
    result=[]
    original_controls=0
    for record in rows:
        key=record["file_offset"].upper()
        off=int(key,16)
        source=canonical.get(key)
        if (source is None or source["vi_full"]!=record["vi_full_reference"]
                or record["status"]!="editorial_compact_static_candidate"):
            raise AssertionError(f"Story full-meaning source drift at {key}")
        end,segments,controls=physical_segments(clean,off)
        captions=record["vi_runtime_lines"]
        sizes=[(stop-start)//2 for start,stop in segments]
        if sizes!=record["expected_segment_capacities"] or len(captions)!=len(segments):
            raise AssertionError(f"Story line/segment capacity changed at {key}")
        if prior[off:end]!=clean[off:end]:
            raise AssertionError(f"043 would overwrite preexisting translation at {key}")
        for (start,stop),caption in zip(segments,captions):
            if (stop-start)%2:
                raise AssertionError(f"odd-byte Story source requires manual handling {key}")
            if (caption!=unicodedata.normalize("NFC",caption)
                    or len(caption)>(stop-start)//2):
                raise AssertionError(f"bad Vietnamese punctuation/width at {key}")
            encoded=bytearray()
            for char in caption+" "*((stop-start)//2-len(caption)):
                hexdigits=mapping.get(char)
                if not hexdigits or len(hexdigits)!=4 or not hexdigits.startswith("84"):
                    raise AssertionError(f"missing V2 glyph {char!r} in {key}")
                code=int(hexdigits,16)
                glyph_ptr=0x28000+0x1a74+2*((code&0xff)-0x40)
                if int.from_bytes(prior[glyph_ptr:glyph_ptr+2],"little")==0 and char!="0":
                    raise AssertionError(f"V2 glyph unassigned: {char!r} {key}")
                encoded+=bytes.fromhex(hexdigits)
            target=set(range(start,start+len(encoded)))
            if changed_allowed&target:
                raise AssertionError(f"overlapping Story fields at {key}")
            changed_allowed.update(target)
            output[start:start+len(encoded)]=encoded
            if (stop-start)%2 and output[stop-1]!=clean[stop-1]:
                raise AssertionError(f"lone original 1B-space modified: {key}")
        for control in controls:
            if output[control:control+2]!=clean[control:control+2]:
                raise AssertionError(f"original dialogue page/line control changed: {key}")
        if output[end]!=clean[end]:
            raise AssertionError(f"original dialogue script op changed: {key}")
        original_controls+=len(controls)
        result.append({"file_offset":key,"line_units":sizes,"vi_runtime":captions})

    output[0x7fdc:0x7fe0]=bytes(4)
    ck=(sum(output)+0x1fe)&0xffff
    output[0x7fdc:0x7fde]=(ck^0xffff).to_bytes(2,"little")
    output[0x7fde:0x7fe0]=ck.to_bytes(2,"little")
    binary=bytes(output)
    if sha(binary)!=OUTPUT_SHA:
        raise AssertionError(f"physical 043 output differs: {sha(binary)}")
    diff={i for i,(a,b) in enumerate(zip(prior,binary)) if a!=b}
    if diff-(changed_allowed|set(range(0x7fdc,0x7fe0))):
        raise AssertionError("Story patch changed bytes outside whitelisted text glyphs")
    def marker_positions(rom):
        return [(i,rom[i:i+2]) for i in range(0x18000,0x1DFFF)
                if rom[i:i+2] in BREAKS]
    if marker_positions(prior)!=marker_positions(binary):
        raise AssertionError("043 moved or corrupted an existing Story bank marker")
    if len(result)!=58 or original_controls!=167 or len(changed_allowed)!=4148 or len(diff)!=4144:
        raise AssertionError("043 reviewed physical Story scope changed")
    patch,records=make_ips(clean,binary)
    if (sha(patch)!=OUTPUT_IPS_SHA or len(patch)!=28135
            or records!=977 or apply_ips(clean,patch)!=binary):
        raise AssertionError("original-ROM IPS mismatch or failed replay")
    report={
        "status":"043_58_STORY_RUNTIME_SAFE_STATIC_PASS_NOT_EMULATOR",
        "source_rom_sha256":CLEAN_SHA,"previous_042_rom_sha256":BASE_SHA,
        "patched_043_rom_sha256":OUTPUT_SHA,"patched_043_ips_sha256":OUTPUT_IPS_SHA,
        "new_Story_dialogue_records":len(result),"previous_total_direct_text_fields_preserved":118,
        "cumulative_direct_text_fields":176,
        "original_story_line_page_controls_preserved":original_controls,
        "physical_story_segments":170,
        "entire_story_bank_break_markers_unchanged":True,
        "rom_changed_bytes_vs_042":len(diff),
        "checksum":f"{ck:04X}","complement":f"{ck^0xffff:04X}",
        "ips_bytes":len(patch),"ips_records":records,
        "existing_font_V2_modified":False,
        "full_canonical_vi_full_modified":False,
        "remaining_long_Story_dialogues":"REQUIRE_LAYOUT_EXPANSION",
        "SNES_emulator":"NOT_TESTED","release_ready":False,
        "entries":result,
    }
    return binary,patch,report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("exact_clean_rom",type=Path)
    p.add_argument("exact_042_ips",type=Path)
    p.add_argument("--project-root",type=Path,default=ROOT)
    p.add_argument("--ips",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--output-rom",type=Path)
    p.add_argument("--allow-untested",action="store_true")
    a=p.parse_args()
    if not a.allow_untested:
        p.error("no emulator QA; pass --allow-untested")
    files=[a.exact_clean_rom,a.exact_042_ips,a.ips,a.report]+([a.output_rom] if a.output_rom else [])
    if len({x.resolve() for x in files})!=len(files):
        p.error("input and output files must be distinct")
    binary,ips,report=build(a.exact_clean_rom.read_bytes(),a.exact_042_ips.read_bytes(),a.project_root)
    outputs=[
        (a.ips,ips),
        (a.report,(json.dumps(report,indent=2,ensure_ascii=False)+"\n").encode("utf-8")),
    ]
    for target,data in outputs:
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
    if a.output_rom:
        a.output_rom.parent.mkdir(parents=True,exist_ok=True)
        a.output_rom.write_bytes(binary)
    print(json.dumps({k:v for k,v in report.items() if k!="entries"},ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
