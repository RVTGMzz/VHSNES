#!/usr/bin/env python3
"""Chibi SNES 047: add 30 exact-slot Quiz/Fortune labels to 046 ROM.

15 Quiz numeric age/date/price/class choices and 15 Fortune numeric/messaging
items. Preserve complete canonical vi_full and unchanged original two-byte
CP932 controls. Existing V2 84xx codepage reused without glyph modification.
Static only; no emulator or completed-game status claimed.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,unicodedata
from pathlib import Path
from build_content_first_040_fortune import apply_ips,make_ips

ROOT=Path(__file__).resolve().parent.parent
CLEAN_SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
BASE_ROM_SHA="c10c0f444a97d6bea7f8f669d67bb6c0c5b6889b654d99d6e6dfa25e3d061624"
BASE_IPS_SHA="11abac1b8e0f48e6580822bcdcd3b1b3568ae08676020b86c819ae641f53367d"
NEW_ROM_SHA="1f6430064b70671a4f3ba94f0fd256764db54690950519c22d9e03ec74230dd9"
NEW_IPS_SHA="725ca433dfeb919bd19bde6903a1e2e7d95cde1889980677863724007090cd6c"

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def read_csv(path:Path):
    with path.open(encoding="utf-8-sig",newline="") as fp:
        return list(csv.DictReader(fp))

def build(clean:bytes,ips046:bytes,project:Path):
    if len(clean)!=0x200000 or sha(clean)!=CLEAN_SHA:
        raise ValueError("Exact headerless clean original Japanese ROM required")
    if len(ips046)!=44450 or sha(ips046)!=BASE_IPS_SHA:
        raise ValueError("Exact 046 original-clean ROM IPS required")
    base=apply_ips(clean,ips046)
    if sha(base)!=BASE_ROM_SHA:raise AssertionError("reconstructed 046 base SHA drift")
    manifest=json.loads((project/"translation/runtime/quiz_fortune_exactfit_047.json").read_text(encoding="utf-8"))
    records=manifest["records"]
    if (manifest["schema"]!="chibi.quiz_fortune.047.v1"
        or manifest["base_046_rom_sha256"]!=BASE_ROM_SHA
        or manifest["output_047_rom_sha256"]!=NEW_ROM_SHA
        or manifest["output_047_clean_ips_sha256"]!=NEW_IPS_SHA
        or len(records)!=30 or len({r["file_offset"].upper() for r in records})!=30):
        raise AssertionError("047 reviewed source inventory changed")
    canonical={}
    for r in records:
        filename=r["source_file"]
        if not filename.startswith("translation/source/") or not filename.endswith(".csv"):
            raise AssertionError("unexpected canonical file")
        if filename not in canonical:
            canonical[filename]={s["file_offset"].upper():s for s in read_csv(project/filename)}
    mapping={r["unicode"]:r["code_hex"] for r in
             read_csv(project/"translation/codepage/vi_codepage_v4_fe4_native.csv")}
    if mapping.get(" ")!="8440" or int.from_bytes(base[0x2975e:0x29760],"little")!=0x9a74:
        raise AssertionError("existing legacy V2 codepage changed")
    patched=bytearray(base)
    approved=set()
    categories={"quiz":0,"fortune":0}
    for row in records:
        key=row["file_offset"].upper()
        original=canonical[row["source_file"]].get(key)
        if (original is None or row["full_vi_reference"]!=original["vi_full"]
            or row["source_jp"]!=(original.get("source_jp") or original.get("source_jp_scanner"))
            or row["status"]!="natural_compact_exact_slot_static"):
            raise AssertionError("Japanese/full Vietnamese source changed "+key)
        category=row["category"]
        if category not in categories:raise AssertionError("unknown Quiz/Fortune category")
        off=int(key,16)
        japanese=row["source_jp"]
        text=row["vi_runtime"]
        units=int(row["max_units"])
        raw=japanese.encode("cp932")
        if (len(japanese)!=units or len(raw)!=2*units or len(text)>units
            or text!=unicodedata.normalize("NFC",text)):
            raise AssertionError("invalid source glyph-width budget at "+key)
        if clean[off:off+len(raw)]!=raw or base[off:off+len(raw)]!=raw:
            raise AssertionError("original CP932 not at exact source offset "+key)
        if (clean[off+len(raw):off+len(raw)+2]!=b"\x81\x6f"
            or base[off+len(raw):off+len(raw)+2]!=b"\x81\x6f"):
            raise AssertionError("original 816F line terminator changed "+key)
        b=bytearray()
        for char in text+" "*(units-len(text)):
            digits=mapping.get(char)
            if digits is None or len(digits)!=4 or not digits.startswith("84"):
                raise AssertionError(f"unmapped existing V2 character at {key}: {char!r}")
            idx=int(digits[-2:],16)
            pos=0x28000+0x1a74+2*(idx-0x40)
            if idx<0x40 or int.from_bytes(base[pos:pos+2],"little")==0:
                raise AssertionError(f"undefined existing glyph at {key}: {char!r}")
            b.extend(bytes.fromhex(digits))
        region=set(range(off,off+len(raw)))
        if region&approved:raise AssertionError("duplicate Quiz/Fortune ROM offset")
        approved.update(region)
        patched[off:off+len(raw)]=b
        if patched[off+len(raw):off+len(raw)+2]!=b"\x81\x6f":
            raise AssertionError("marker overwritten")
        categories[category]+=1
    if categories!={"quiz":15,"fortune":15} or len(approved)!=222:
        raise AssertionError("source slots/category inventory changed")
    patched[0x7fdc:0x7fe0]=bytes(4)
    ck=(sum(patched)+0x1fe)&0xffff
    patched[0x7fdc:0x7fde]=(ck^0xffff).to_bytes(2,"little")
    patched[0x7fde:0x7fe0]=ck.to_bytes(2,"little")
    new=bytes(patched)
    diff={i for i,(a,b) in enumerate(zip(base,new)) if a!=b}
    if sha(new)!=NEW_ROM_SHA or len(diff)!=174:
        raise AssertionError("result does not match reviewed 047 ROM")
    if diff-(approved|set(range(0x7fdc,0x7fe0))):
        raise AssertionError("unexpected code/font/graphics or non-047 changes")
    ips,records_count=make_ips(clean,new)
    if (sha(ips)!=NEW_IPS_SHA or len(ips)!=44980
        or records_count!=1671 or apply_ips(clean,ips)!=new):
        raise AssertionError("047 IPS exact clean-ROM replay mismatch")
    return new,ips,{
        "status":"STATIC_047_QUIZ_FORTUNE_30_PASS_EMULATOR_UNTESTED",
        "new_categories":categories,"new_fields":30,
        "original_CP932_source_and_816F_verified":30,
        "allowed_two_byte_glyph_bytes":len(approved),
        "modified_ROM_byte_positions_vs_046":len(diff),
        "output_ROM_SHA256":NEW_ROM_SHA,"output_clean_ROM_IPS_SHA256":NEW_IPS_SHA,
        "IPS_bytes":len(ips),"IPS_records":records_count,
        "checksum":f"{ck:04X}","complement":f"{ck^0xffff:04X}",
        "existing_font_modified":False,
        "emulator_runtime":"NOT_TESTED","full_game_finished":False,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("clean_rom",type=Path)
    p.add_argument("exact_046_clean_ips",type=Path)
    p.add_argument("--project-root",type=Path,default=ROOT)
    p.add_argument("--ips",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--output-rom",type=Path)
    p.add_argument("--allow-untested",action="store_true")
    a=p.parse_args()
    if not a.allow_untested:p.error("No SNES runtime acceptance; pass --allow-untested")
    paths=[a.clean_rom,a.exact_046_clean_ips,a.ips,a.report]+([a.output_rom] if a.output_rom else [])
    if len({f.resolve() for f in paths})!=len(paths):
        p.error("input and output paths must not overlap")
    output,ips,report=build(a.clean_rom.read_bytes(),a.exact_046_clean_ips.read_bytes(),a.project_root)
    for dest,data in ((a.ips,ips),(a.report,(json.dumps(report,ensure_ascii=False,indent=2)+"\n").encode("utf-8"))):
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    if a.output_rom:
        a.output_rom.parent.mkdir(parents=True,exist_ok=True)
        a.output_rom.write_bytes(output)
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
