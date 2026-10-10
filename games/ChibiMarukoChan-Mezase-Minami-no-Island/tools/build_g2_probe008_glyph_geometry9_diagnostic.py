#!/usr/bin/env python3
"""Build a DO-NOT-RELEASE glyph-geometry 9px renderer diagnostic (SNES/65816).

This corrects older checks that wrongly treated $001FB2 as glyph ID, or
assumed live DBR remained $83. No new WRAM state is used: first hook reads
original glyph PHA on CPU stack; second reads original font-page / 12x12 atlas
scratch geometry at DP $18/$08/$0A. All original Japanese quotes in three G2
records are included. This has NOT been executed in a real SNES emulator.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

BASE_SHA = "2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd"
DIAG_SHA = "a3d2e75da5f9dac36750ef77e249fae7613ffd35f8185c50cd6f6197ca8a8688"
WORD_HOOK, BYTE_HOOK = 0x28E0C, 0x290EE
WORD_CODE, BYTE_CODE = 0x2FB80, 0x2FD00
NINE_WORD, NINE_SHIFT = 0x2FC80, 0x2FCC0
HEADER = 0x7FDC


class A:
    def __init__(self, origin):
        self.origin, self.b, self.labels, self.todo = origin, bytearray(), {}, []

    def emit(self, *v):
        self.b.extend(v)

    def label(self, name):
        if name in self.labels:
            raise AssertionError("duplicate label")
        self.labels[name] = len(self.b)

    def branch(self, op, name):
        self.emit(op, 0)
        self.todo.append((len(self.b)-1, "rel", name))

    def jump(self, name):
        self.emit(0x4C, 0, 0)
        self.todo.append((len(self.b)-2, "abs", name))

    def cmp16(self, value):
        self.emit(0xC9, value & 255, value >> 8)

    def load_long_x(self, address):
        self.emit(0xBF, address & 255, (address >> 8) & 255, address >> 16)

    def finish(self):
        for off, kind, name in self.todo:
            dest = self.labels[name]
            if kind == "rel":
                delta = dest-off-1
                if not -128 <= delta <= 127:
                    raise ValueError(f"out-of-range branch {name}")
                self.b[off] = delta & 255
            else:
                address = (self.origin+dest) & 0xFFFF
                self.b[off:off+2] = address.to_bytes(2, "little")
        return bytes(self.b)


def word_hook() -> bytes:
    a = A(0x85FB80)
    # CPU: original renderer PHA glyph; JSL helper; PHX; PHY; JSL hook;
    # PHP. Therefore glyph is at $0A,S if X8 or $0C,S if X16.
    a.emit(0x08,0xE2,0x20,0xA3,0x01,0x29,0x10)
    a.branch(0xF0,"x16")
    a.emit(0xC2,0x20,0xA3,0x0A)
    a.branch(0x80,"compare")
    a.label("x16")
    a.emit(0xC2,0x20,0xA3,0x0C)
    a.label("compare")
    # Quotes MUST be checked before an early BCC to the native path.
    for gid in (0x0159, 0x015A):
        a.cmp16(gid)
        a.branch(0xF0,"vietnamese")
    for lower, upper in ((0x083A,0x0864),(0x090A,0x0964),(0x0A00,0x0A54)):
        a.cmp16(lower)
        a.branch(0x90,"native")
        a.cmp16(upper)
        a.branch(0x90,"vietnamese")
    a.label("native")
    a.emit(0x28)
    a.load_long_x(0x859670)
    a.emit(0x6B)
    a.label("vietnamese")
    a.emit(0x28)
    a.load_long_x(0x85FC80)
    a.emit(0x6B)
    result = a.finish()
    if len(result) != 71:
        raise AssertionError("word stub byte identity changed")
    return result


def shift_hook() -> bytes:
    a = A(0x85FD00)
    a.emit(0x08,0xC2,0x20,0xA5,0x18)  # PHP, REP M16, LDA DP $18
    a.cmp16(0xC000);a.branch(0xF0,"p8")
    a.cmp16(0xC800);a.branch(0xF0,"p9")
    a.cmp16(0xD000);a.branch(0xF0,"p10")
    a.cmp16(0x8800);a.branch(0xF0,"quotes")
    a.jump("native")
    # V2 font page 08, cells decimal 58..99.
    a.label("p8")
    a.emit(0xA5,0x0A);a.cmp16(72);a.branch(0xB0,"vietnamese")
    a.cmp16(60);a.branch(0xD0,"native")
    a.emit(0xA5,0x08);a.cmp16(96);a.branch(0xB0,"vietnamese")
    a.jump("native")
    # V2 font page 09, cells decimal 10..99.
    a.label("p9")
    a.emit(0xA5,0x0A);a.cmp16(12);a.branch(0xB0,"vietnamese")
    a.jump("native")
    # New page 0A cells decimal 0..83; cells 84..99 remain unused.
    a.label("p10")
    a.emit(0xA5,0x0A);a.cmp16(96)
    a.branch(0x90,"vietnamese");a.branch(0xD0,"native")
    a.emit(0xA5,0x08);a.cmp16(48);a.branch(0x90,"vietnamese")
    a.jump("native")
    # Original Japanese quote IDs 0159 (cell89) / 015A (cell90).
    a.label("quotes")
    a.emit(0xA5,0x0A);a.cmp16(96);a.branch(0xD0,"quote_end")
    a.emit(0xA5,0x08);a.cmp16(108);a.branch(0xF0,"vietnamese")
    a.jump("native")
    a.label("quote_end")
    a.cmp16(108);a.branch(0xD0,"native")
    a.emit(0xA5,0x08);a.cmp16(0);a.branch(0xF0,"vietnamese")
    a.label("native")
    a.emit(0x28)
    a.load_long_x(0x859696)
    a.emit(0x6B)
    a.label("vietnamese")
    a.emit(0x28)
    a.load_long_x(0x85FCC0)
    a.emit(0x6B)
    result = a.finish()
    if len(result) != 120:
        raise AssertionError("shift stub byte identity changed")
    return result


def build(raw: bytes):
    if len(raw) != 0x200000 or hashlib.sha256(raw).hexdigest() != BASE_SHA:
        raise ValueError("exact Probe008 V2 font-only baseline required")
    signatures = (
        (0x28E0C, "BF 70 96 85"), (0x290EE, "BF 96 96 85"),
        (0x28E7B, "8B DA 5A 48 AF B2 1F 00 22 05 8E 85"),
        (0x28E87, "68 85 02 29 FF 00 AA BF 0C 96 85 29 FF 00"),
        (0x28E95, "F4 00 7F AB AB"),
        (0x28EA8, "BF 00 F8 85"), (0x28EAE, "BF 01 F8 85"),
        (0x290EC, "A6 10 BF 96 96 85"),
    )
    for off, hx in signatures:
        b = bytes.fromhex(hx)
        if raw[off:off+len(b)] != b:
            raise AssertionError(f"renderer signature changed at {off:06X}")

    regions = ((WORD_CODE,WORD_CODE+0x80),(BYTE_CODE,BYTE_CODE+0x100),
               (NINE_WORD,NINE_WORD+38),(NINE_SHIFT,NINE_SHIFT+19))
    for lo,hi in regions:
        if raw[lo:hi] != bytes([255])*(hi-lo):
            raise AssertionError(f"ROM staging region already occupied: {lo:06X}")

    code1, code2 = word_hook(), shift_hook()
    data = bytearray(raw)
    data[WORD_CODE:WORD_CODE+len(code1)] = code1
    data[BYTE_CODE:BYTE_CODE+len(code2)] = code2
    for i in range(19):
        pos = 4 + 9*i
        data[NINE_WORD+2*i:NINE_WORD+2*i+2] = (16*(pos//8)).to_bytes(2, "little")
        data[NINE_SHIFT+i] = pos%8
    data[WORD_HOOK:WORD_HOOK+4] = bytes.fromhex("22 80 FB 85")
    data[BYTE_HOOK:BYTE_HOOK+4] = bytes.fromhex("22 00 FD 85")

    data[HEADER:HEADER+4] = bytes(4)
    checksum = (sum(data)+0x1FE)&0xFFFF
    data[HEADER:HEADER+2] = (checksum^0xFFFF).to_bytes(2,"little")
    data[HEADER+2:HEADER+4] = checksum.to_bytes(2,"little")
    allowed=set(range(HEADER,HEADER+4))
    for lo,hi in regions:
        allowed.update(range(lo,hi))
    allowed.update(range(WORD_HOOK,WORD_HOOK+4))
    allowed.update(range(BYTE_HOOK,BYTE_HOOK+4))
    changed={i for i,(a,b) in enumerate(zip(raw,data)) if a!=b}
    if changed-allowed:
        raise AssertionError("changed bytes outside whitelist")

    for off in (0x181CE,0x18247,0x182C0):
        if data[off:off+106] != raw[off:off+106]:
            raise AssertionError("G2 two-byte scene payload changed")
    if data[0x29670:0x296A9] != raw[0x29670:0x296A9]:
        raise AssertionError("original Japanese 13px tables changed")
    result = bytes(data)
    if hashlib.sha256(result).hexdigest() != DIAG_SHA:
        raise AssertionError("ROM differs from independently staged prototype")
    return result,{
        "status":"EXPERIMENTAL_OFFLINE_BUILD_ONLY",
        "sha256":DIAG_SHA,"base_sha256":BASE_SHA,
        "changed_bytes":len(changed),
        "checksum":f"0x{checksum:04X}",
        "complement":f"0x{checksum^0xFFFF:04X}",
        "word_hook_bytes":len(code1),"shift_hook_bytes":len(code2),
        "original_13px_tables_preserved":True,
        "G2_strict_two_byte_records_preserved":True,
        "emulator_test":"NOT_PERFORMED","release_ready":False,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("exact_v2_font_only_rom",type=Path)
    p.add_argument("out_diagnostic_rom",type=Path)
    p.add_argument("out_report",type=Path)
    p.add_argument("--allow-untested-diagnostic",action="store_true",
                   help="mandatory opt-in; never distribute as a release")
    a=p.parse_args()
    if not a.allow_untested_diagnostic:
        p.error("EXPERIMENTAL ONLY; requires --allow-untested-diagnostic")
    if len({x.resolve() for x in (a.exact_v2_font_only_rom,
                                 a.out_diagnostic_rom,a.out_report)}) != 3:
        p.error("source ROM and output paths must differ")
    result, report=build(a.exact_v2_font_only_rom.read_bytes())
    a.out_diagnostic_rom.parent.mkdir(parents=True,exist_ok=True)
    a.out_diagnostic_rom.write_bytes(result)
    a.out_report.parent.mkdir(parents=True,exist_ok=True)
    a.out_report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",
                            encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
