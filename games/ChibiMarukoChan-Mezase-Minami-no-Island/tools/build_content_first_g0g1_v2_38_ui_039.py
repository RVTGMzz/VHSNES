#!/usr/bin/env python3
"""Chibi 039: combine real G0/G1 graphics036, existing V2 font/codepage
and 38 rigorously exact-fit direct Vietnamese menu/VS/Quiz labels.

This is an EXPERIMENTAL static ROM candidate, not an emulator pass or
a recreation of the lost direct-text Build035. Uses existing font V2
WITHOUT changing its glyphs. Do not upload ROMs or font files to GitHub.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHA = {
    "clean": "e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956",
    "v2": "2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd",
    "graphics": "2c8beee73e985c9a2690cc36ace335f05115c1a3e81b369e09d0cfb132117090",
    "output": "a1f4459942e3a757cc314d12c959168046b4a6dd66018d55b014c70d052e98ce",
}
HEADER = set(range(0x7FDC,0x7FE0))

def hash256(blob:bytes)->str:
    return hashlib.sha256(blob).hexdigest()

def read_rows(file:Path)->list[dict[str,str]]:
    with file.open("r",encoding="utf-8-sig",newline="") as fp:
        return list(csv.DictReader(fp))

def to_ips(clean:bytes,built:bytes)->tuple[bytes,int]:
    result=bytearray(b"PATCH")
    p=records=0
    while p<len(clean):
        if clean[p]==built[p]:
            p+=1
            continue
        start=p
        block=bytearray()
        while p<len(clean) and clean[p]!=built[p] and len(block)<65535:
            block.append(built[p])
            p+=1
        result+=start.to_bytes(3,"big")+len(block).to_bytes(2,"big")+block
        records+=1
    return bytes(result+b"EOF"),records

def build(clean:bytes,v2:bytes,graphics:bytes,
          menu_csv:Path,ui_csv:Path,codepage_csv:Path):
    for name,raw in (("clean",clean),("v2",v2),("graphics",graphics)):
        if len(raw)!=0x200000 or hash256(raw)!=SHA[name]:
            raise ValueError(f"wrong unheadered 2MiB {name} ROM SHA256")
    menu=read_rows(menu_csv)
    ui=read_rows(ui_csv)
    if len(menu)!=10 or len(ui)!=33:
        raise AssertionError("runtime source row inventory changed")
    approved=menu+[r for r in ui if r["status"]=="runtime_candidate_exact_fit"]
    if len(approved)!=38 or any(r["status"]!="runtime_candidate_exact_fit"
                                for r in approved):
        raise AssertionError("expected 10 menu +28 exact-fit UI labels")
    mapping={r["unicode"]:r["code_hex"] for r in read_rows(codepage_csv)}
    if mapping.get(" ")!="8440":
        raise AssertionError("legacy V2 space code changed")

    v2_changed={i for i,(x,y) in enumerate(zip(clean,v2)) if x!=y}
    gfx_changed={i for i,(x,y) in enumerate(zip(clean,graphics)) if x!=y}
    if (v2_changed&gfx_changed)-HEADER:
        raise AssertionError("existing V2 font and 036 graphics would collide")
    output=bytearray(graphics)
    for pos in v2_changed-HEADER:
        output[pos]=v2[pos]

    # This is the actual font V2 0x84 codepage root as decoded from ROM.
    page_ptr=int.from_bytes(v2[0x2975E:0x29760],"little")
    if page_ptr!=0x9A74:
        raise AssertionError("original V2 0x84 glyph lookup table moved")

    translated=[]
    written=set()
    for r in approved:
        off=int(r["file_offset"],0)
        jp=r["source_jp"]
        vi=r["vi_runtime_v1"]
        width=int(r["max_units"])
        if not vi or len(jp)!=width or len(vi)>width:
            raise AssertionError(f"bad original/final unit count at 0x{off:X}")
        expected=jp.encode("cp932")
        if len(expected)!=2*width:
            raise AssertionError(f"not all original chars CP932 double-byte at 0x{off:X}")
        if (clean[off:off+2*width]!=expected
            or v2[off:off+2*width]!=expected
            or graphics[off:off+2*width]!=expected):
            raise AssertionError(f"source mismatch at 0x{off:X}")

        # Preserve the original 0x816F record terminator and any intervening
        # raw ASCII / CP932 full-width spaces. Some Japanese UI records use
        # extra layout padding that must not be interpreted as another label.
        tail=clean[off+2*width:off+2*width+14]
        guards=[]
        for pad in range(9):
            prefix=tail[:pad]
            if (tail[pad:pad+2]==b"\x81\x6f"
                    and prefix.replace(b" ",b"").replace(b"\x81\x40",b"")==b""):
                guards.append(tail[:pad+2])
        if not guards:
            raise AssertionError(f"delimiter/padding contract failed at 0x{off:X}")

        glyphbytes=bytearray()
        for char in vi+" "*(width-len(vi)):
            code=mapping.get(char)
            if not code or len(code)!=4 or not code.startswith("84"):
                raise AssertionError(f"unsupported 2-byte font glyph {char!r}")
            idx=int(code,16)&0xff
            target=0x28000+(page_ptr&0x7fff)+2*(idx-0x40)
            gid=int.from_bytes(v2[target:target+2],"little")
            if gid==0 and char!="0":
                raise AssertionError(f"unmapped V2 glyph {char!r}")
            glyphbytes.extend(bytes.fromhex(code))
        if len(glyphbytes)!=2*width:
            raise AssertionError("encoded bytes do not fit exact field")
        destination=set(range(off,off+2*width))
        if destination&written:
            raise AssertionError(f"overlapping translation fields at 0x{off:X}")
        written|=destination
        output[off:off+2*width]=glyphbytes
        if output[off+2*width:off+2*width+len(guards[0])]!=guards[0]:
            raise AssertionError(f"record controls overwritten 0x{off:X}")
        translated.append({"file_offset":r["file_offset"],"source_jp":jp,
                           "vi_runtime":vi,"unit_limit":width})

    output[0x7FDC:0x7FE0]=bytes(4)
    checksum=(sum(output)+0x1FE)&0xffff
    output[0x7FDC:0x7FDE]=(checksum^0xffff).to_bytes(2,"little")
    output[0x7FDE:0x7FE0]=checksum.to_bytes(2,"little")
    built=bytes(output)
    if hash256(built)!=SHA["output"]:
        raise AssertionError("final ROM differs from locally verified 039 prototype: "+
                             hash256(built))
    actual={i for i,(a,b) in enumerate(zip(clean,built)) if a!=b}
    if actual-(v2_changed|gfx_changed|written|HEADER):
        raise AssertionError("binary changes outside three guarded source layers")
    ips,records=to_ips(clean,built)
    if len(ips)!=21130 or records!=674:
        raise AssertionError("IPS no longer matches independently verified 039 prototype")
    report={
        "status":"STATIC_G0_G1_V2_PLUS_38_DIRECT_UI_SOURCE_PASS_NOT_RUNTIME",
        "clean_sha256":SHA["clean"],"v2_sha256":SHA["v2"],
        "graphics036_sha256":SHA["graphics"],"output_sha256":SHA["output"],
        "existing_font_v2_reused_without_modification":True,
        "existing_graphics036_reused_without_modification":True,
        "main_menu_labels_patched":len(menu),
        "minigame_and_quiz_labels_patched":len(approved)-len(menu),
        "needs_expansion_labels_preserved_Japanese":len(ui)-(len(approved)-len(menu)),
        "all_source_CP932_and_delimiters_verified":True,
        "changed_bytes_from_clean":len(actual),
        "no_cross_layer_collisions":True,
        "checksum":f"0x{checksum:04X}",
        "complement":f"0x{checksum^0xffff:04X}",
        "ips_bytes":len(ips),"ips_records":records,
        "reviewed_rows":translated,
        "full_Story_Quiz_Fortune_translation_integrated":False,
        "historical_directtext_Build035_integrated":False,
        "SNES_runtime":"NOT_TESTED",
        "font_025_previous_user_visual_fail":"NOT_CLEARED",
        "release_ready":False}
    return built,ips,report

def main()->None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("clean_rom",type=Path)
    ap.add_argument("v2_font_only_rom",type=Path)
    ap.add_argument("graphics036_rom",type=Path)
    ap.add_argument("output_rom",type=Path)
    ap.add_argument("--menu-csv",type=Path,default=ROOT/"translation/runtime/main_menu_compact_v1.csv")
    ap.add_argument("--ui-csv",type=Path,default=ROOT/"translation/runtime/ui_choices_compact_v1.csv")
    ap.add_argument("--codepage-csv",type=Path,default=ROOT/"translation/codepage/vi_codepage_v4_fe4_native.csv")
    ap.add_argument("--ips",type=Path,required=True)
    ap.add_argument("--report",type=Path,required=True)
    ap.add_argument("--allow-untested",action="store_true")
    args=ap.parse_args()
    if not args.allow_untested:
        ap.error("experimental 039 not accepted in SNES emulator; pass --allow-untested")
    paths=[args.clean_rom,args.v2_font_only_rom,args.graphics036_rom,
           args.output_rom,args.ips,args.report]
    if len({p.resolve() for p in paths})!=len(paths):
        ap.error("input ROMs and output paths must be distinct")
    raw,ips,report=build(args.clean_rom.read_bytes(),
                         args.v2_font_only_rom.read_bytes(),
                         args.graphics036_rom.read_bytes(),
                         args.menu_csv,args.ui_csv,args.codepage_csv)
    for file,data in ((args.output_rom,raw),(args.ips,ips)):
        file.parent.mkdir(parents=True,exist_ok=True)
        file.write_bytes(data)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",
                           encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="reviewed_rows"},
                     indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
