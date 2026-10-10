#!/usr/bin/env python3
"""Independent read-only G0+G1 035 check on actual patched SNES ROM bytes.

Do not claim emulator runtime PASS. Detect accidental writes to any other
G1 sprite/icon or any G0 title resource, and verify IPS clean-ROM replay.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from decompress_chibi_resource import decompress_resource
from rom_common import require_clean_rom, validate_internal_header

BASE_SHA = "e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
G0_SHA = "012cdfb87eae1b7c5a9feada4e1c322541e3c91ba45ba0b857e08a2465f47ce0"
JOINT_SHA = "77a207589857d2886059057151eaf3d47530032b726744fe739e991ff81a5b80"
G1_START = 0xBF95E
G1_LEN = 436
G1_PTR = 0x12F4D


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def ips_replay(clean: bytes, ips: bytes) -> tuple[bytes, int]:
    if not ips.startswith(b"PATCH") or ips[-3:] != b"EOF":
        raise AssertionError("invalid IPS framing")
    output = bytearray(clean)
    p = 5
    records = 0
    while p < len(ips)-3:
        if p+5 > len(ips)-3:
            raise AssertionError("truncated IPS record")
        at = int.from_bytes(ips[p:p+3], "big")
        size = int.from_bytes(ips[p+3:p+5], "big")
        p += 5
        if not size:
            if p+3 > len(ips)-3:
                raise AssertionError("truncated IPS RLE")
            run = int.from_bytes(ips[p:p+2], "big")
            frag = bytes((ips[p+2],))*run
            p += 3
        else:
            if p+size > len(ips)-3:
                raise AssertionError("truncated IPS data")
            frag = ips[p:p+size]
            p += size
        if at + len(frag) > len(output):
            raise AssertionError("IPS overwrote original 2MiB")
        output[at:at+len(frag)] = frag
        records += 1
    if p != len(ips)-3:
        raise AssertionError("trailing garbage before IPS EOF")
    return bytes(output), records


def audit(clean: bytes, g0: bytes, combined: bytes, ips: bytes) -> dict:
    if (sha(clean)!=BASE_SHA or sha(g0)!=G0_SHA or sha(combined)!=JOINT_SHA):
        raise ValueError("requires exact original ROM, G0-only and 035 combined")
    if (clean[G1_PTR:G1_PTR+5] != bytes.fromhex("00 78 5E F9 97")
            or combined[G1_PTR:G1_PTR+5] != clean[G1_PTR:G1_PTR+5]):
        raise AssertionError("G1 script $82:AF23 reference changed")
    old,hdr0,_=decompress_resource(clean,G1_START)
    edited,hdr1,_=decompress_resource(combined,G1_START)
    if hdr0.span!=436 or hdr1.span!=331 or len(old)!=992 or len(edited)!=992:
        raise AssertionError("unexpected G1 decoded resource shape")
    if old[15*32:16*32]!=edited[15*32:16*32] or old[29*32:]!=edited[29*32:]:
        raise AssertionError("G1 untouched spacer/icon tiles modified")
    modified_tiles=[i for i in range(31)
                    if old[i*32:(i+1)*32]!=edited[i*32:(i+1)*32]]
    if any(i not in (*range(15),*range(16,29)) for i in modified_tiles):
        raise AssertionError("unexpected G1 sprite tile modified")
    g0_change={i for i,(a,b) in enumerate(zip(clean,g0)) if a!=b}
    g1_change={i for i,(a,b) in enumerate(zip(g0,combined)) if a!=b}
    if (g0_change & g1_change)-set(range(0x7FDC,0x7FE0)):
        raise AssertionError("G0 and G1 overlap unexpectedly")
    allowed=set(range(G1_START,G1_START+G1_LEN))|set(range(0x7FDC,0x7FE0))
    if g1_change-allowed:
        raise AssertionError("G1 modification escaped sprite+checksum regions")
    if combined[0x12095:0x12098]!=g0[0x12095:0x12098]:
        raise AssertionError("G0 title graphics relocation pointer changed")
    if combined[0x36907:0x36907+3420]!=g0[0x36907:0x36907+3420]:
        raise AssertionError("G0 title relocated graphics changed")
    # G0 modified original resources should be byte-identical.
    for start,size in ((0xF6456,5570),(0xF1F00,545)):
        if combined[start:start+size]!=g0[start:start+size]:
            raise AssertionError(f"G0 graphics resource changed: {start:X}")
    replay,count=ips_replay(clean,ips)
    if count!=225 or len(ips)!=10880 or replay!=combined:
        raise AssertionError("IPS roundtrip or length differs from staged build")
    hdr=validate_internal_header(combined)
    if not hdr["checksum_matches"] or not hdr["checksum_pair_valid"]:
        raise AssertionError("SNES checksum invalid")
    return {
        "status":"G0_G1_035_INDEPENDENT_STATIC_PASS_NOT_RUNTIME",
        "clean_sha256":BASE_SHA,"g0_sha256":G0_SHA,
        "combined_sha256":JOINT_SHA,
        "g1_decoded_snes_4bpp_bytes":992,
        "g1_compressed_old_span":hdr0.span,
        "g1_compressed_new_span":hdr1.span,
        "g1_exact_sprite_tiles_changed":modified_tiles,
        "g1_spacer_tile15_unchanged":True,
        "g1_icon_tile29_30_unchanged":True,
        "g0_relocation_and_original_title_sources_unchanged":True,
        "ips_size":len(ips),"ips_records":count,
        "IPS_replay_exact":True,
        "SNES_checksum":f"0x{hdr['checksum']:04X}",
        "SNES_emulator_test":"NOT_PERFORMED",
        "whole_game_vietnamese":False,"release_ready":False
    }


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("clean_rom",type=Path)
    p.add_argument("g0_title_only_rom",type=Path)
    p.add_argument("combined_g0_g1_rom",type=Path)
    p.add_argument("combined_ips",type=Path)
    p.add_argument("--report",type=Path)
    args=p.parse_args()
    report=audit(bytes(require_clean_rom(args.clean_rom)),
                 args.g0_title_only_rom.read_bytes(),
                 args.combined_g0_g1_rom.read_bytes(),
                 args.combined_ips.read_bytes())
    data=json.dumps(report,ensure_ascii=False,indent=2)+"\n"
    print(data)
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(data,encoding="utf-8")


if __name__=="__main__":
    main()
