#!/usr/bin/env python3
"""Apply checkpoint053 reviewed Quiz slots to exact integrated 048 ROM.

All source bytes, literal CP932 text, original 816F endings, existing V2
glyph assignments and untouched 048 baseline are guarded. On success write
only clean-ROM-based IPS + QA report, never copyrighted ROM.
Emulator testing remains separate and mandatory before release.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,unicodedata
from pathlib import Path
from build_content_first_040_fortune import make_ips,apply_ips

ROOT=Path(__file__).resolve().parent.parent
CLEAN_SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"

def sha(b):return hashlib.sha256(b).hexdigest()
def load_csv(p):
    with p.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))

def build(clean,base,root):
    raise RuntimeError("DEPRECATED: 15/16 entries here were already translated in 041. Use guarded rebuild_content_first_054_full_chain.py instead.")
    if len(clean)!=0x200000 or sha(clean)!=CLEAN_SHA or len(base)!=len(clean):
        raise ValueError("Need exact clean 2MiB Japanese ROM and same-size full 048")
    manifest=json.loads((root/"translation/runtime/quiz_content_first_16_053.json").read_text(encoding="utf-8"))
    entries=manifest["records"]
    if (manifest["schema"]!="chibi.quiz.content_first.053.v1" or len(entries)!=16
        or manifest.get("record_count")!=16):
        raise AssertionError("053 source manifest drift")
    # Baseline identity is checked by main() using --expected-048-sha.
    # Do not silently accept any other candidate base.
    mapping={r["unicode"]:r["code_hex"] for r in load_csv(root/"translation/codepage/vi_codepage_v4_fe4_native.csv")}
    if mapping.get(" ")!="8440" or int.from_bytes(base[0x2975e:0x29760],"little")!=0x9a74:
        raise AssertionError("V2 codepage/table pointer mismatch")
    old_047=json.loads((root/"translation/runtime/quiz_fortune_exactfit_047.json").read_text(encoding="utf-8"))
    used={r["file_offset"].upper() for r in old_047["records"]}
    source={}
    for r in entries:
        file=r["source_file"]
        if not file.startswith("translation/source/") or not file.endswith(".csv"):
            raise AssertionError("Unknown canonical source path")
        if file not in source:
            source[file]={row["file_offset"].upper():row for row in load_csv(root/file)}
    output=bytearray(base);allowed=set()
    for r in entries:
        key=r["file_offset"].upper();off=int(key,16)
        row=source[r["source_file"]].get(key)
        if key in used or not row or row["source_jp_scanner"]!=r["source_jp"] or row["vi_full"]!=r["vi_full_reference"]:
            raise AssertionError("Source drift / earlier Quiz collision "+key)
        original=r["source_jp"].encode("cp932")
        text=r["vi_runtime"]
        units=r["max_source_two_byte_units"]
        lead=r.get("leading_source_padding_bytes",0)
        tail=r.get("trailing_source_padding_bytes",0)
        if (not isinstance(lead,int) or not isinstance(tail,int) or
            (lead,tail) not in ((0,0),(6,8)) or
            ((lead,tail)==(6,8) and key!="0X340C0")):
            raise AssertionError("Unapproved Quiz alignment change "+key)
        if ("｛" in r["source_jp"] or len(original)!=2*units or len(text)>units or
            unicodedata.normalize("NFC",text)!=text):
            raise AssertionError("Unsafe scanner field or unsupported length "+key)
        field=off+lead
        end=field+len(original)
        marker=end+tail
        if clean[off:field]!=b" "*lead or base[off:field]!=b" "*lead:
            raise AssertionError("Original leading layout padding missing "+key)
        if clean[end:marker]!=b" "*tail or base[end:marker]!=b" "*tail:
            raise AssertionError("Original trailing layout padding missing "+key)
        if clean[field:end]!=original or base[field:end]!=original:
            raise AssertionError("Unverified CP932 source/changed baseline "+key)
        if clean[marker:marker+2]!=b"\x81\x6f" or base[marker:marker+2]!=b"\x81\x6f":
            raise AssertionError("Original 816F delimiter missing "+key)
        span=set(range(field,end))
        if span&allowed:raise AssertionError("Overlapping Quiz slots "+key)
        allowed.update(span)
        dst=bytearray()
        for c in text+" "*(units-len(text)):
            glyph=mapping.get(c)
            if not glyph or len(glyph)!=4 or not glyph.startswith("84"):
                raise AssertionError("Missing codepage glyph "+repr(c)+" "+key)
            idx=int(glyph[-2:],16)
            ptr=0x28000+0x1a74+2*(idx-0x40)
            if idx<0x40 or int.from_bytes(base[ptr:ptr+2],"little")==0:
                raise AssertionError("Unassigned V2 glyph "+repr(c)+" "+key)
            dst.extend(bytes.fromhex(glyph))
        output[field:end]=dst
    output[0x7fdc:0x7fe0]=bytes(4)
    ck=(sum(output)+0x1fe)&0xffff
    output[0x7fdc:0x7fde]=(ck^0xffff).to_bytes(2,"little")
    output[0x7fde:0x7fe0]=ck.to_bytes(2,"little")
    final=bytes(output)
    changes={i for i,(x,y) in enumerate(zip(base,final)) if x!=y}
    if changes-(allowed|set(range(0x7fdc,0x7fe0))):
        raise AssertionError("Non-Quiz bytes touched")
    ips,count=make_ips(clean,final)
    if apply_ips(clean,ips)!=final:
        raise AssertionError("Independent clean-ROM IPS replay failed")
    return ips,{"status":"053_STATIC_INTEGRATION_PASS_NOT_EMULATOR","records":16,
                "ROM_sha256":sha(final),"IPS_sha256":sha(ips),"IPS_records":count,
                "base_048_sha256":sha(base),"checksum":f"{ck:04X}",
                "changed_bytes":len(changes),"emulator_tested":False}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("clean_rom",type=Path)
    p.add_argument("integrated_048_rom",type=Path)
    p.add_argument("--expected-048-sha",required=True)
    p.add_argument("--project-root",type=Path,default=ROOT)
    p.add_argument("--ips",required=True,type=Path)
    p.add_argument("--report",required=True,type=Path)
    p.add_argument("--allow-untested",action="store_true")
    a=p.parse_args()
    if not a.allow_untested:p.error("Emulator QA not performed; pass --allow-untested")
    if len(a.expected_048_sha)!=64 or any(c not in "0123456789abcdef" for c in a.expected_048_sha):
        p.error("--expected-048-sha must be lowercase SHA256")
    base=a.integrated_048_rom.read_bytes()
    if sha(base)!=a.expected_048_sha:
        p.error("048 baseline SHA mismatch")
    ips,report=build(a.clean_rom.read_bytes(),base,a.project_root)
    if len({q.resolve() for q in [a.clean_rom,a.integrated_048_rom,a.ips,a.report]})!=4:
        p.error("Inputs and outputs must differ")
    for path,data in ((a.ips,ips),(a.report,(json.dumps(report,ensure_ascii=False,indent=2)+"\n").encode())):
        path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
