#!/usr/bin/env python3
"""Static 65816 LoROM parser -> mapping -> page pointer -> glyph bitmap audit.

Proof of byte-level lookup only. Neither SNES execution nor native 0x85 safety
is established, so the V2 font cannot be declared release-ready.
"""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / "translation/codepage/g2_probe008_complete_candidate_v2.json"
CLEAN_SHA256 = "e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
PROBE003_SHA256 = "5208bec10147f478cc17955c4f262a5cde08e5b85708caa2717370f6835fbacd"
PROBE008_SHA256 = "2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd"


def cpu_to_file(bank, address):
    if address < 0x8000:
        raise ValueError("not a LoROM ROM address")
    return (bank & 0x7F)*0x8000 + (address & 0x7FFF)


def read_glyph(rom, code):
    hi,lo = bytes.fromhex(code)
    if not (0x80 <= hi <= 0x9F and 0x40 <= lo <= 0xFC):
        raise ValueError(f"unsupported two-byte code {code}")
    lead_entry=0x29756 + 2*(hi-0x80)
    map_cpu=int.from_bytes(rom[lead_entry:lead_entry+2],"little")
    map_off=cpu_to_file(0x85,map_cpu)+2*(lo-0x40)
    gid=int.from_bytes(rom[map_off:map_off+2],"little")
    page=gid>>8
    cell=gid&0xFF
    if not (0<=page<=10 and 0<=cell<100):
        raise ValueError(f"out of bounds glyph ID {gid:04X}")
    # Both code operands $85:8EA8 and $85:8EAE address the same
    # 3-byte overlapping page-pointer array at 0x2F800.
    page_off=0x2F800 + 3*page
    low=rom[page_off]
    high=rom[page_off+1]
    bank=rom[page_off+2]
    addr=low|(high<<8)
    file_base=cpu_to_file(bank,addr)
    cx,cy=(cell%10)*12,(cell//10)*12
    value=0
    for y in range(12):
        for x in range(12):
            px=cx+x
            py=cy+y
            off=file_base + py*16 + px//8
            value=(value<<1)|int(bool(rom[off] & (0x80>>(px%8))))
    return gid,value.to_bytes(18,"big"),f"{bank:02X}:{addr:04X}"


def verify(clean,probe003,probe008):
    expected=((clean,CLEAN_SHA256),(probe003,PROBE003_SHA256),
              (probe008,PROBE008_SHA256))
    for rom,h in expected:
        if len(rom)!=0x200000 or hashlib.sha256(rom).hexdigest()!=h:
            raise ValueError(f"exact ROM size/hash contract failed: {h}")
    if probe008[0x28EA8:0x28EAC]!=bytes.fromhex("BF00F885"):
        raise AssertionError("low word page pointer still uses original table")
    if probe008[0x28EAE:0x28EB2]!=bytes.fromhex("BF01F885"):
        raise AssertionError("bank byte page pointer still uses original table")
    font=json.loads(FONT.read_text(encoding="utf-8"))
    if len(font)!=212:
        raise AssertionError("candidate font must have exactly 212 entries")
    groups=Counter()
    gids=set()
    for char,row in font.items():
        gid,bmp,pointer=read_glyph(probe008,row["code_hex"])
        if bmp != bytes.fromhex(row["bitmap_hex"]):
            raise AssertionError(f"bitmap lookup not identical: {char!r}")
        groups[pointer]+=1
        gids.add(gid)
    if groups["A4:D000"]!=84 or len(gids)!=210:
        raise AssertionError("11th font page capacity/physical glyph count mismatch")
    if (read_glyph(probe008,"8175")[0]!=0x0159 or
        read_glyph(probe008,"8176")[0]!=0x015A):
        raise AssertionError("native quote glyph identities changed")
    # Data-scan inventory is purposefully NOT a proof of code 0x85 usage.
    ambiguous=[i for i in range(0x18000,0x283D7)
               if clean[i]==0x85 and 0x40<=clean[i+1]<=0x73]
    # Original final line uses up to 16 Vietnamese chars followed by
    # untouched native closing quote. Its per-glyph 13px x-position differs
    # from a fully compact 9px line by 4*16=64 logical pixels.
    quote_index=len("Rèn gu mỹ thuật!")
    native_quote_x=4+13*quote_index
    compact_quote_x=4+9*quote_index
    return {
        "status":"STATIC_POINTER_CHAIN_PASS",
        "mapped_codepoints":212,
        "unique_physical_glyphs":len(gids),
        "page_pointers":dict(sorted(groups.items())),
        "new_page_A4_D000_characters":groups["A4:D000"],
        "native_85_candidate_byte_pairs_in_0x18000_0x283D8":len(ambiguous),
        "native_85_first_candidate_offsets":[f"0x{i:06X}" for i in ambiguous[:12]],
        "native_85_proprietary_use":"NOT PROVEN SAFE",
        "original_close_quote_code":"8176",
        "original_close_quote_glyph_id":"015A",
        "mixed_line_closing_quote_x_native":native_quote_x,
        "mixed_line_closing_quote_x_expected_compact":compact_quote_x,
        "selective_9px_quote_displacement_px":native_quote_x-compact_quote_x,
        "selective_9px_release_blocker":"PER-GLYPH MODE IS NOT LINE-AWARE",
        "runtime":"UNTESTED",
        "release_ready":False
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("clean_rom",type=Path)
    p.add_argument("probe003_rom",type=Path)
    p.add_argument("probe008_v2_font_rom",type=Path)
    p.add_argument("report_json",type=Path)
    a=p.parse_args()
    paths=(a.clean_rom,a.probe003_rom,a.probe008_v2_font_rom,a.report_json)
    if len({x.resolve() for x in paths})!=4:
        raise ValueError("input and output paths must differ")
    report=verify(a.clean_rom.read_bytes(),a.probe003_rom.read_bytes(),
                  a.probe008_v2_font_rom.read_bytes())
    a.report_json.parent.mkdir(parents=True,exist_ok=True)
    a.report_json.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",
                             encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
