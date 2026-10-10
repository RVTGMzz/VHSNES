#!/usr/bin/env python3
"""Opt-in Probe008 029: copy Japanese G2 quotes into VI 9px-only font cells.

Input is exact, UNTESTED 028 combined V3 medium+glyph-geometry diagnostic.
This is deliberately NOT a release. Replaces exactly six G2 quotation
code-pairs (same two-byte width), not line separators/control bytes, to keep
native 8175/8176 glyphs at their original 13px throughout Japanese screens.

Requires 0x85 codepage lead, 0x0A54/0x0A55 font slots; both require runtime
validation. No commercial ROM data is added to GitHub.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from build_g2_probe008_glyph_geometry9_diagnostic import A, word_hook, shift_hook
from build_g2_probe008_v3_medium_geometry9_experiment import (
    code_to_gid, read_glyph, write_glyph,
)

BASE_SHA = "59f4c45b14a24e6cf67de1c9c7cbe1d9b862eaa2eb4c6518bbc4bcbd6dd006fb"
OUTPUT_SHA = "a23304cedff0eac959a6455d90b866c49543ca381425b089771b65da264e928e"
G2_STARTS = (0x181CE, 0x18247, 0x182C0)
REMAP = (("8175", "8574", 0x0159, 0x0A54),
         ("8176", "8575", 0x015A, 0x0A55))


def compact_word_hook():
    a = A(0x85FB80)
    a.emit(0x08, 0xE2, 0x20, 0xA3, 0x01, 0x29, 0x10)
    a.branch(0xF0, "x16")
    a.emit(0xC2, 0x20, 0xA3, 0x0A)
    a.branch(0x80, "compare")
    a.label("x16")
    a.emit(0xC2, 0x20, 0xA3, 0x0C)
    a.label("compare")
    for lo, hi in ((0x083A, 0x0864), (0x090A, 0x0964), (0x0A00, 0x0A56)):
        a.cmp16(lo)
        a.branch(0x90, "native")
        a.cmp16(hi)
        a.branch(0x90, "vi")
    a.label("native")
    a.emit(0x28)
    a.load_long_x(0x859670)
    a.emit(0x6B)
    a.label("vi")
    a.emit(0x28)
    a.load_long_x(0x85FC80)
    a.emit(0x6B)
    result = a.finish()
    if len(result) != 61:
        raise AssertionError("new word hook length is not reviewed")
    return result


def compact_shift_hook():
    a = A(0x85FD00)
    a.emit(0x08, 0xC2, 0x20, 0xA5, 0x18)
    for value, tag in ((0xC000, "page8"), (0xC800, "page9"),
                       (0xD000, "page10")):
        a.cmp16(value)
        a.branch(0xF0, tag)
    a.jump("native")
    a.label("page8")
    a.emit(0xA5, 0x0A)
    a.cmp16(72)
    a.branch(0xB0, "vi")
    a.cmp16(60)
    a.branch(0xD0, "native")
    a.emit(0xA5, 0x08)
    a.cmp16(96)
    a.branch(0xB0, "vi")
    a.jump("native")
    a.label("page9")
    a.emit(0xA5, 0x0A)
    a.cmp16(12)
    a.branch(0xB0, "vi")
    a.jump("native")
    a.label("page10")
    a.emit(0xA5, 0x0A)
    a.cmp16(96)
    a.branch(0x90, "vi")
    a.branch(0xD0, "native")
    a.emit(0xA5, 0x08)
    a.cmp16(72)  # columns 0..5 in the final atlas row; cells 80..85
    a.branch(0x90, "vi")
    a.jump("native")
    a.label("native")
    a.emit(0x28)
    a.load_long_x(0x859696)
    a.emit(0x6B)
    a.label("vi")
    a.emit(0x28)
    a.load_long_x(0x85FCC0)
    a.emit(0x6B)
    result = a.finish()
    if len(result) != 86:
        raise AssertionError("new shift hook length is not reviewed")
    return result


def select_9px(gid):
    return (0x083A <= gid < 0x0864 or 0x090A <= gid < 0x0964 or
            0x0A00 <= gid < 0x0A56)


def build(source):
    if len(source) != 0x200000 or hashlib.sha256(source).hexdigest() != BASE_SHA:
        raise ValueError("requires exact V3 medium + geometry9 checkpoint 028 ROM")
    # Historical hook signatures MUST match checkpoint 028.
    if source[0x2FB80:0x2FB80+71] != word_hook():
        raise AssertionError("unexpected 028 word hook")
    if source[0x2FD00:0x2FD00+120] != shift_hook():
        raise AssertionError("unexpected 028 shift hook")
    out = bytearray(source)
    w, s = compact_word_hook(), compact_shift_hook()
    out[0x2FB80:0x2FC00] = bytes([0xFF])*0x80
    out[0x2FD00:0x2FE00] = bytes([0xFF])*0x100
    out[0x2FB80:0x2FB80+len(w)] = w
    out[0x2FD00:0x2FD00+len(s)] = s

    for old_code, new_code, old_id, new_id in REMAP:
        if code_to_gid(source, old_code) != old_id:
            raise AssertionError("original Japanese quote maps unexpectedly")
        if code_to_gid(source, new_code) != 0:
            raise AssertionError("new code already allocated")
        blank = read_glyph(source, new_id)
        if any(blank):
            raise AssertionError("target font cell is not blank")
        write_glyph(out, new_id, read_glyph(source, old_id))
        map_offset = 0x2FA00 + 2*(int(new_code[-2:], 16)-0x40)
        if out[map_offset:map_offset+2] != bytes(2):
            raise AssertionError("target codepage row is occupied")
        out[map_offset:map_offset+2] = new_id.to_bytes(2,"little")
        if read_glyph(out, new_id) != read_glyph(source, old_id):
            raise AssertionError("duplicate glyph bitmap not identical")
        if read_glyph(out, old_id) != read_glyph(source, old_id):
            raise AssertionError("native quote font was damaged")
        if code_to_gid(out, new_code) != new_id:
            raise AssertionError("new G2 codepage not connected")

    for first in G2_STARTS:
        old = source[first:first+106]
        total = 0
        for i in range(53):
            pos = first+2*i
            pair = source[pos:pos+2]
            for old_code, new_code, _, _ in REMAP:
                if pair == bytes.fromhex(old_code):
                    out[pos:pos+2] = bytes.fromhex(new_code)
                    total += 1
        if total != 2:
            raise AssertionError("expected one opening and closing quote per field")
        for index in (32, 68, 104):
            if (out[first+index:first+index+2] != bytes.fromhex("816F")
                    or old[index:index+2] != bytes.fromhex("816F")):
                raise AssertionError("scene separators changed")
        for i in range(53):
            pair = bytes(out[first+2*i:first+2*i+2])
            if i in (16,34,52):
                continue
            gid = code_to_gid(out, pair.hex())
            if not select_9px(gid):
                raise AssertionError(f"G2 glyph outside compact range: {pair.hex()}")

    for old_code, _, old_id, _ in REMAP:
        if code_to_gid(out, old_code) != old_id or select_9px(old_id):
            raise AssertionError("native Japanese quotes no longer use 13px")
    out[0x7FDC:0x7FE0] = bytes(4)
    ck = (sum(out)+0x1FE) & 0xFFFF
    out[0x7FDC:0x7FDE] = (ck^0xFFFF).to_bytes(2,"little")
    out[0x7FDE:0x7FE0] = ck.to_bytes(2,"little")
    allowed=set(range(0x7FDC,0x7FE0))
    for first in G2_STARTS:
        allowed.update(range(first,first+106))
    for first,last in ((0x2FB80,0x2FC00),(0x2FD00,0x2FE00),
                       (0x2FA68,0x2FA6C),(0x125000,0x125800)):
        allowed.update(range(first,last))
    changed={i for i,(a,b) in enumerate(zip(source,out)) if a!=b}
    if changed-allowed:
        raise AssertionError(f"out of whitelist: {sorted(changed-allowed)[:10]}")
    for first,last in ((0x28E0C,0x28E10),(0x290EE,0x290F2),
                       (0x29670,0x296A9),(0x28EA8,0x28EB2)):
        if source[first:last] != out[first:last]:
            raise AssertionError("renderer original data altered")
    result=bytes(out)
    digest=hashlib.sha256(result).hexdigest()
    if digest!=OUTPUT_SHA or len(changed)!=180 or ck!=0x9309:
        raise AssertionError("generated ROM diverges from independently reviewed local build")
    return result,{
        "status":"STATIC_QUOTE_ISOLATION_PASS_NOT_RUNTIME",
        "sha256":digest,"source028_sha256":BASE_SHA,
        "changed_bytes":len(changed),"checksum":f"0x{ck:04X}",
        "complement":f"0x{ck^0xFFFF:04X}",
        "word_stub_len":len(w),"byte_stub_len":len(s),
        "G2_quote_code_pairs_changed":6,
        "native_japanese_quote_codes_preserved":["8175","8176"],
        "G2_only_quote_codes":["8574","8575"],
        "G2_only_quote_font_ids":["0A54","0A55"],
        "separators_816F_preserved":True,
        "G2_3x106_bytes_same_length":True,
        "G2_original_quote_bytes_same":False,
        "outside_G2_japanese_quote_9px_changed":False,
        "original_13px_tables_preserved":True,
        "runtime":"NOT_TESTED","release_ready":False,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("exact_combined_028_rom",type=Path)
    p.add_argument("output_029_diagnostic_rom",type=Path)
    p.add_argument("output_report",type=Path)
    p.add_argument("--allow-untested-diagnostic", action="store_true")
    a=p.parse_args()
    if not a.allow_untested_diagnostic:
        p.error("EXPERIMENT ONLY: use --allow-untested-diagnostic to opt in")
    paths=(a.exact_combined_028_rom,a.output_029_diagnostic_rom,a.output_report)
    if len({p.resolve() for p in paths}) != 3:
        p.error("source ROM and output paths must be different")
    binary,report=build(a.exact_combined_028_rom.read_bytes())
    a.output_029_diagnostic_rom.parent.mkdir(parents=True,exist_ok=True)
    a.output_029_diagnostic_rom.write_bytes(binary)
    a.output_report.parent.mkdir(parents=True,exist_ok=True)
    a.output_report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",
                               encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
