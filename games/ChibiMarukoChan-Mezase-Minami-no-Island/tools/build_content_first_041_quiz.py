#!/usr/bin/env python3
"""Content-first Chibi SNES 041: 21 exact-fit Quiz choices over clean+040 IPS.

All Japanese CP932 fields and existing canonical full Vietnamese are
validated. Only 21 original fixed-size glyph fields and header checksum
may change. Existing font V2 and G0/G1 graphics are untouched. Output
is static experimental IPS, NOT a gameplay-tested full localization.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import unicodedata
from pathlib import Path

from build_content_first_040_fortune import apply_ips, make_ips, read_csv, sha

ROOT=Path(__file__).resolve().parent.parent
CLEAN_SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
BASE_IPS_SHA="2bfdcc64973bc31ce268fa7e68a6118808c633b10d1437b7f811ac290616e580"
BASE_SHA="d892c51576c103f5881f1481c65fd2746635d222b1d387f9666cd7f44b1da3ac"
OUTPUT_SHA="56c36cbc8e477d262216d3aa0f06909e09b9929ba0f6f544dccbaa3671bf48fb"
OUTPUT_IPS_SHA="2117bc6e165f2c86263e74a637b6961a13f79257fccd9f02152a769fe1deb962"
CANONICAL=(
    "quiz_batch01_part1_vi.csv",
    "quiz_batch01_part2_vi.csv",
    "quiz_batch02_part1_vi.csv",
    "quiz_batch02_part2_vi.csv",
    "quiz_batch02_part3_vi.csv",
)


def build(clean:bytes,ips040:bytes,project:Path):
    if len(clean)!=0x200000 or sha(clean)!=CLEAN_SHA:
        raise ValueError("requires exact original 2MiB Japanese ROM")
    if len(ips040)!=21727 or sha(ips040)!=BASE_IPS_SHA:
        raise ValueError("requires exact checkpoint040 clean-ROM IPS")
    prior=apply_ips(clean,ips040)
    if sha(prior)!=BASE_SHA:
        raise ValueError("040 baseline failed SHA256 verification")

    rows=read_csv(project/"translation/runtime/quiz_answers_exact_fit_041.csv")
    if len(rows)!=21 or len({r["file_offset"] for r in rows})!=21:
        raise AssertionError("041 requires exactly 21 unique reviewed Quiz fields")
    source={}
    for filename in CANONICAL:
        for row in read_csv(project/"translation/source"/filename):
            key=row["file_offset"].upper()
            if key in source:
                raise AssertionError(f"duplicate canonical source ROM offset {key}")
            source[key]=row
    codepage={r["unicode"]:r["code_hex"] for r in
              read_csv(project/"translation/codepage/vi_codepage_v4_fe4_native.csv")}
    if codepage.get(" ")!="8440":
        raise AssertionError("expected V2 0x84xx space codepoint")
    ptr=int.from_bytes(prior[0x2975E:0x29760],"little")
    if ptr!=0x9A74:
        raise AssertionError("existing V2 0x84 codepoint table pointer moved")
    out=bytearray(prior)
    allowed=set()
    resolved=[]
    for r in rows:
        ident=r["file_offset"].upper()
        pos=int(r["file_offset"],16)
        japanese=r["source_jp"]
        full=r["vi_full_reference"]
        compact=r["vi_runtime"]
        units=int(r["max_units"])
        original=source.get(ident)
        if original is None:
            raise AssertionError(f"missing canonical Quiz source row {ident}")
        original_japanese=original.get("source_jp",original.get("source_jp_scanner",""))
        if original_japanese!=japanese or original["vi_full"]!=full:
            raise AssertionError(f"Japanese or full Vietnamese canonical mismatch {ident}")
        if r["status"]!="runtime_candidate_exact_fit":
            raise AssertionError(f"unapproved Quiz short-form at {ident}")
        if compact!=unicodedata.normalize("NFC",compact):
            raise AssertionError(f"non-NFC runtime Quiz text at {ident}")
        raw=japanese.encode("cp932")
        if len(japanese)!=units or len(raw)!=2*units or len(compact)>units:
            raise AssertionError(f"original 2-byte glyph budget mismatch at {ident}")
        if (clean[pos:pos+len(raw)]!=raw or prior[pos:pos+len(raw)]!=raw
            or clean[pos+len(raw):pos+len(raw)+2]!=b"\x81\x6F"
            or prior[pos+len(raw):pos+len(raw)+2]!=b"\x81\x6F"):
            raise AssertionError(f"wrong original Japanese bytes or terminator at {ident}")
        positions=set(range(pos,pos+len(raw)))
        if positions&allowed:
            raise AssertionError(f"overlapping source fields at {ident}")
        allowed.update(positions)
        encoded=bytearray()
        for character in compact+" "*(units-len(compact)):
            code=codepage.get(character)
            if not code or len(code)!=4 or not code.startswith("84"):
                raise AssertionError(f"missing V2 codepoint for {character!r} at {ident}")
            index=int(code[-2:],16)
            pointer=0x28000+(ptr&0x7FFF)+2*(index-0x40)
            if int.from_bytes(prior[pointer:pointer+2],"little")==0:
                raise AssertionError(f"undefined existing V2 glyph {character!r}")
            encoded.extend(bytes.fromhex(code))
        if len(encoded)!=len(raw):
            raise AssertionError("encoded field length drift")
        out[pos:pos+len(raw)]=encoded
        if out[pos+len(raw):pos+len(raw)+2]!=b"\x81\x6F":
            raise AssertionError("original record control byte overwritten")
        resolved.append({"source_offset":r["file_offset"],"source_jp":japanese,
                         "full_vi":full,"compact_vi":compact,"capacity":units,
                         "category":r["category"]})

    out[0x7FDC:0x7FE0]=bytes(4)
    ck=(sum(out)+0x1FE)&0xFFFF
    out[0x7FDC:0x7FDE]=(ck^0xFFFF).to_bytes(2,"little")
    out[0x7FDE:0x7FE0]=ck.to_bytes(2,"little")
    binary=bytes(out)
    if sha(binary)!=OUTPUT_SHA:
        raise AssertionError(f"unexpected final 041 ROM SHA256 {sha(binary)}")
    modified={i for i,(before,after) in enumerate(zip(prior,binary))
              if before!=after}
    if modified-(allowed|set(range(0x7FDC,0x7FE0))):
        raise AssertionError("modified byte outside approved 21 Quiz fields")
    ips,records=make_ips(clean,binary)
    if (sha(ips)!=OUTPUT_IPS_SHA or len(ips)!=22100 or records!=756
        or apply_ips(clean,ips)!=binary):
        raise AssertionError("IPS output or clean-ROM replay failed")
    counts={r["category"]:sum(x["category"]==r["category"] for x in resolved)
            for r in resolved}
    report={
        "status":"041_QUIZ21_EXACTFIT_STATIC_PASS_NOT_RUNTIME",
        "source_clean_sha256":CLEAN_SHA,
        "source_040_ips_sha256":BASE_IPS_SHA,
        "source_040_rom_sha256":BASE_SHA,
        "new_041_rom_sha256":OUTPUT_SHA,
        "new_041_ips_sha256":OUTPUT_IPS_SHA,
        "additional_quiz_rows":len(resolved),
        "categories":counts,
        "direct_text_fields_cumulative":92,
        "existing_previous_ROM_bytes_preserved_outside_fields":True,
        "source_Japanese_and_canonical_meanings_verified":len(resolved),
        "V2_font_modified":False,
        "byte_changes_vs_040":len(modified),
        "snes_checksum":f"0x{ck:04X}",
        "snes_complement":f"0x{ck^0xFFFF:04X}",
        "ips_bytes":len(ips),"ips_records":records,
        "gameplay_emulator":"NOT_TESTED",
        "whole_game_Story_Quiz_Fortune_translated":False,
        "release_ready":False,
        "translations":resolved,
    }
    return binary,ips,report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("clean_rom",type=Path)
    parser.add_argument("exact_040_ips",type=Path)
    parser.add_argument("--project-root",type=Path,default=ROOT)
    parser.add_argument("--ips",type=Path,required=True)
    parser.add_argument("--report",type=Path,required=True)
    parser.add_argument("--output-rom",type=Path)
    parser.add_argument("--allow-untested",action="store_true")
    args=parser.parse_args()
    if not args.allow_untested:
        parser.error("Static experiment, pass --allow-untested")
    unique=[args.clean_rom,args.exact_040_ips,args.ips,args.report]
    if args.output_rom: unique.append(args.output_rom)
    if len({p.resolve() for p in unique})!=len(unique):
        parser.error("input/output paths must be different")
    binary,ips,report=build(args.clean_rom.read_bytes(),
                            args.exact_040_ips.read_bytes(),args.project_root)
    for p,data in ((args.ips,ips),
                   (args.report,(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
                    .encode("utf-8"))):
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(data)
    if args.output_rom:
        args.output_rom.parent.mkdir(parents=True,exist_ok=True)
        args.output_rom.write_bytes(binary)
    print(json.dumps({k:v for k,v in report.items() if k!="translations"},
                     ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
