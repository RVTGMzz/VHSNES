#!/usr/bin/env python3
"""Read-only independent 036 G0+G1 mode heading graphics/IPS verifier.

Verifies real resource $98:F06F (main menu $82:A213), untouched first
192 4bpp tiles (menu words/icons), G0 title and G1 Story Start/Password
binary preservation, valid IPS replay and cartridge header. Static only.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from decompress_chibi_resource import decompress_resource
from rom_common import require_clean_rom

CLEAN_SHA = "e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
BEFORE_SHA = "77a207589857d2886059057151eaf3d47530032b726744fe739e991ff81a5b80"
AFTER_SHA = "2c8beee73e985c9a2690cc36ace335f05115c1a3e81b369e09d0cfb132117090"
SRC=0xC706F
SPAN=3485
REFERENCE_PACKAGES=(0x121F2,0x12213,0x12239,0x12294,0x122C0,
                    0x122E6,0x1230C,0x12332,0x12358,0x1237E,
                    0x123A4,0x123F7,0x12EE9)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def decode_ips(original: bytes, ips: bytes):
    if not ips.startswith(b"PATCH") or not ips.endswith(b"EOF"):
        raise ValueError("bad IPS framing")
    result=bytearray(original)
    cursor=5
    end=len(ips)-3
    records=0
    while cursor<end:
        if cursor+5>end:
            raise ValueError("truncated IPS")
        off=int.from_bytes(ips[cursor:cursor+3],"big")
        size=int.from_bytes(ips[cursor+3:cursor+5],"big")
        cursor+=5
        if size:
            if cursor+size>end:raise ValueError("truncated IPS data")
            payload=ips[cursor:cursor+size]
            cursor+=size
        else:
            if cursor+3>end:raise ValueError("truncated IPS RLE")
            n=int.from_bytes(ips[cursor:cursor+2],"big")
            payload=bytes((ips[cursor+2],))*n
            cursor+=3
        if off+len(payload)>len(result):
            raise ValueError("IPS exceeds clean ROM")
        result[off:off+len(payload)]=payload
        records+=1
    if cursor!=end:
        raise ValueError("trailing IPS data")
    return bytes(result),records


def scan_reference_packages(rom: bytes):
    confirmations=[]
    for script in REFERENCE_PACKAGES:
        if rom[script]!=0:
            raise AssertionError(f"non-type0 package 0x{script:X}")
        cursor=script+2
        references=0
        for _ in range(22):
            if rom[cursor]==0xFF:break
            dest=int.from_bytes(rom[cursor:cursor+2],"little")
            cpu=int.from_bytes(rom[cursor+2:cursor+5],"little")
            if (dest,cpu)==(0x7000,0x98F06F):
                references+=1
            cursor+=5
        if references!=1:
            raise AssertionError(f"shared 4bpp resource pointer no longer unique in 0x{script:X}")
        confirmations.append(f"0x{script:X}")
    return confirmations


def verify(clean,old,new,ips):
    if (len(clean)!=0x200000 or sha(clean)!=CLEAN_SHA
        or len(old)!=0x200000 or sha(old)!=BEFORE_SHA
        or len(new)!=0x200000 or sha(new)!=AFTER_SHA):
        raise ValueError("exact 035/036 ROM SHA identities required")
    if new[0x20047:0x2004E]!=bytes.fromhex("A2 13 A2 22 55 E2 80"):
        raise AssertionError("real main-menu resource call changed")
    if new[0x12233:0x12238]!=bytes.fromhex("00 70 6F F0 98"):
        raise AssertionError("real main-menu heading source reference changed")
    shared=scan_reference_packages(new)
    a,oh,_=decompress_resource(old,SRC)
    b,nh,_=decompress_resource(new,SRC)
    if (oh.span,nh.span,len(a),len(b),oh.postprocess,nh.postprocess)!=(3485,2428,8192,8192,False,False):
        raise AssertionError("decompressed game 4bpp heading resource invalid")
    if a[:6144]!=b[:6144]:
        raise AssertionError("original first 192 tiles (menu/icon sprites) not identical")
    if a[6144:]==b[6144:]:
        raise AssertionError("heading glyph tiles not replaced")
    histogram=Counter()
    for tile_idx in range(192,256):
        tile=b[tile_idx*32:(tile_idx+1)*32]
        for y in range(8):
            for x in range(8):
                sh=7-x
                value=((tile[2*y]>>sh)&1)|(((tile[2*y+1]>>sh)&1)<<1)
                value|=(((tile[16+2*y]>>sh)&1)<<2)|(((tile[17+2*y]>>sh)&1)<<3)
                histogram[value]+=1
    if set(histogram)!={0,2} or histogram[2]<300:
        raise AssertionError("Vietnamese 2-line label was not rasterized as reviewed")
    for start,size in ((0x12095,3),(0x36907,3420),
                       (0xF6456,5570),(0xF1F00,545),
                       (0xBF95E,436)):
        if new[start:start+size]!=old[start:start+size]:
            raise AssertionError(f"prior G0/G1 asset changed outside heading scope 0x{start:X}")
    changed={i for i,(x,y) in enumerate(zip(old,new)) if x!=y}
    allowed=set(range(SRC,SRC+SPAN))|set(range(0x7FDC,0x7FE0))
    if changed-allowed:
        raise AssertionError(f"036 modified outside title/heading resource: {sorted(changed-allowed)[:5]}")
    complement=int.from_bytes(new[0x7FDC:0x7FDE],"little")
    checksum=int.from_bytes(new[0x7FDE:0x7FE0],"little")
    recalculated=(sum(new[:0x7FDC])+sum(new[0x7FE0:])+0x1FE)&0xFFFF
    if (checksum,complement)!=(0x3A35,0xC5CA) or recalculated!=checksum or complement^checksum!=0xFFFF:
        raise AssertionError("SNES ROM header checksum invalid")
    replay,records=decode_ips(clean,ips)
    if replay!=new or len(ips)!=14452 or records!=263:
        raise AssertionError("independent IPS replay does not reproduce exact 036 ROM")
    return {
        "status":"INDEPENDENT_G0_G1_HEADING_036_STATIC_PASS",
        "output_sha256":AFTER_SHA,
        "asset_source":"$98:F06F / file 0xC706F",
        "main_menu_initializer_file":"0x20047",
        "resource_original_bytes":3485,
        "resource_new_bytes":2428,
        "preserved_sprite_tiles":"0..191 exact",
        "modified_heading_tiles":"192..255",
        "raster_index_histogram":dict(histogram),
        "shared_scripts_checked":shared,
        "previous_G0_title_G1_Start_Password_assets_unchanged":True,
        "IPS_exact_replay":True,"IPS_bytes":len(ips),"IPS_records":records,
        "SNES_checksum":f"0x{checksum:04X}",
        "live_gameplay_test":"NOT_PERFORMED",
        "complete_Vietnamese_game":False,"release_ready":False,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("exact_clean_rom",type=Path)
    p.add_argument("exact_graphics_035_rom",type=Path)
    p.add_argument("graphics_036_rom",type=Path)
    p.add_argument("graphics_036_ips",type=Path)
    p.add_argument("--report",type=Path)
    a=p.parse_args()
    obj=verify(bytes(require_clean_rom(a.exact_clean_rom)),
               a.exact_graphics_035_rom.read_bytes(),
               a.graphics_036_rom.read_bytes(),
               a.graphics_036_ips.read_bytes())
    output=json.dumps(obj,ensure_ascii=False,indent=2)+"\n"
    print(output)
    if a.report:
        a.report.parent.mkdir(parents=True,exist_ok=True)
        a.report.write_text(output,encoding="utf-8")


if __name__=="__main__":
    main()
