#!/usr/bin/env python3
"""Guarded 65816 selective 9px spacing DIAGNOSTIC from exact Probe008 V2.

The 13px Japanese position tables stay untouched. Hook locations and a new
9px table apply only to IDs in dedicated Vietnamese font-cell ranges.
This is NOT an emulator test and is NOT release ready: mixed native quotation
marks can still have unwanted space. Do not add commercial ROMs to GitHub.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONT_JSON = ROOT / "translation/codepage/g2_probe008_complete_candidate_v2.json"
EXPECTED_SHA256 = "2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd"
HOOK_WORD = 0x28E0C
HOOK_BYTE = 0x290EE
STUB_WORD = 0x2FB80     # $85:FB80
STUB_BYTE = 0x2FC00     # $85:FC00
NINE_WORD = 0x2FC80     # $85:FC80
NINE_BYTE = 0x2FCC0     # $85:FCC0
VI_RANGES = ((0x083A,0x0864),(0x090A,0x0964),(0x0A00,0x0A54))
CHECKSUM = 0x7FDC


class Asm:
    def __init__(self):
        self.data = bytearray()
        self.labels = {}
        self.relative = []

    def mark(self, name):
        self.labels[name] = len(self.data)

    def put(self, *values):
        self.data.extend(values)

    def cmp16(self, value):
        self.put(0xC9, value & 0xFF, value >> 8)

    def bcc(self, label):
        self.relative.append((len(self.data) + 1, label))
        self.put(0x90, 0)

    def lda_long_x(self, address):
        self.put(0xBF, address & 255, (address >> 8) & 255, address >> 16)

    def finish(self):
        for operand, label in self.relative:
            relative = self.labels[label] - (operand + 1)
            if not -128 <= relative <= 127:
                raise ValueError("branch outside relative range")
            self.data[operand] = relative & 0xFF
        return bytes(self.data)


def make_hook(word):
    a = Asm()
    if word:
        a.put(0x98)  # TYA: still contains glyph ID from $85:8E05 TAY
    else:
        # Word glyph ID is at $001FB2. Restore initial 8-bit accumulator
        # before loading the original or Vietnamese bit-shift table.
        a.put(0x08, 0xC2, 0x20, 0xAF, 0xB2, 0x1F, 0x00)
    for lo, hi in VI_RANGES:
        a.cmp16(lo)
        a.bcc("native")
        a.cmp16(hi)
        a.bcc("vi")
    a.mark("native")
    if not word:
        a.put(0x28)   # PLP
    a.lda_long_x(0x859670 if word else 0x859696)
    a.put(0x6B)       # RTL
    a.mark("vi")
    if not word:
        a.put(0x28)
    a.lda_long_x(0x85FC80 if word else 0x85FCC0)
    a.put(0x6B)
    result = a.finish()
    if len(result) > 0x80:
        raise AssertionError("stub exceeds guarded 0x80-byte stage")
    return result


def file_offset(address):
    if (address & 0xFFFF) < 0x8000:
        raise ValueError("invalid LoROM address")
    return ((address >> 16) & 0x7F)*0x8000 + (address & 0x7FFF)


def execute_stub(stub, data, glyph_id, slot, word):
    """Tiny STRICT subset 65816 instruction interpreter for regression only."""
    pc = 0
    a = glyph_id if word else 0
    x = slot*2 if word else slot
    y = glyph_id
    m = 16 if word else 8
    original_m = m
    carry = 0
    stack = []
    for step in range(40):
        opcode = stub[pc]
        pc += 1
        if opcode == 0x98:
            a = y
        elif opcode == 0x08:
            stack.append(m)
        elif opcode == 0xC2:
            if stub[pc] != 0x20:
                raise ValueError("unexpected REP mask")
            pc += 1
            m = 16
        elif opcode == 0xAF:
            addr = int.from_bytes(stub[pc:pc+3], "little")
            pc += 3
            if addr != 0x001FB2:
                raise ValueError("unexpected glyph fetch")
            a = glyph_id
        elif opcode == 0xC9:
            number = int.from_bytes(stub[pc:pc+2], "little")
            pc += 2
            carry = (a >= number)
        elif opcode == 0x90:
            delta = stub[pc]
            pc += 1
            if not carry:
                pc += delta if delta < 128 else delta - 256
        elif opcode == 0x28:
            m = stack.pop()
        elif opcode == 0xBF:
            address = int.from_bytes(stub[pc:pc+3], "little")
            pc += 3
            off = file_offset(address) + x
            a = data[off] if m == 8 else int.from_bytes(data[off:off+2], "little")
        elif opcode == 0x6B:
            if stack or m != original_m:
                raise AssertionError("unbalanced flags / accumulator size")
            return a
        else:
            raise ValueError(f"unknown instruction 0x{opcode:02X}")
    raise AssertionError("stub did not return")


def build(raw):
    if len(raw) != 0x200000 or hashlib.sha256(raw).hexdigest() != EXPECTED_SHA256:
        raise ValueError("exact Probe008 V2 13px font-only ROM required")
    if raw[HOOK_WORD:HOOK_WORD+4] != bytes.fromhex("BF709685"):
        raise ValueError("unexpected 16-bit tile offset lookup")
    if raw[HOOK_BYTE:HOOK_BYTE+4] != bytes.fromhex("BF969685"):
        raise ValueError("unexpected 8-bit shift lookup")
    stages = ((STUB_WORD,STUB_WORD+0x80),
              (STUB_BYTE,STUB_BYTE+0x80),
              (NINE_WORD,NINE_WORD+38),
              (NINE_BYTE,NINE_BYTE+19))
    for a,b in stages:
        if any(v != 0xFF for v in raw[a:b]):
            raise ValueError(f"overwrites occupied ROM data at 0x{a:06X}")
    data = bytearray(raw)
    word = make_hook(True)
    byte = make_hook(False)
    data[STUB_WORD:STUB_WORD+len(word)] = word
    data[STUB_BYTE:STUB_BYTE+len(byte)] = byte
    for i in range(19):
        position = 4 + 9*i
        data[NINE_WORD+2*i:NINE_WORD+2*i+2] = (16*(position//8)).to_bytes(2, "little")
        data[NINE_BYTE+i] = position % 8
    data[HOOK_WORD:HOOK_WORD+4] = bytes.fromhex("2280FB85")
    data[HOOK_BYTE:HOOK_BYTE+4] = bytes.fromhex("2200FC85")
    data[CHECKSUM:CHECKSUM+4] = bytes(4)
    ck = (sum(data)+0x1FE) & 0xFFFF
    data[CHECKSUM:CHECKSUM+2] = (ck ^ 0xFFFF).to_bytes(2, "little")
    data[CHECKSUM+2:CHECKSUM+4] = ck.to_bytes(2, "little")
    allowed = set(range(CHECKSUM,CHECKSUM+4))
    for a,b in stages:
        allowed.update(range(a,b))
    allowed.update(range(HOOK_WORD,HOOK_WORD+4))
    allowed.update(range(HOOK_BYTE,HOOK_BYTE+4))
    changed = {i for i,(a,b) in enumerate(zip(raw,data)) if a != b}
    if changed - allowed:
        raise AssertionError(f"unexpected ROM writes: {sorted(changed-allowed)[:15]}")
    if raw[0x29670:0x296A9] != data[0x29670:0x296A9]:
        raise AssertionError("original 13px position tables changed")
    for pos in (0x181CE,0x18247,0x182C0):
        if raw[pos:pos+106] != data[pos:pos+106]:
            raise AssertionError("Probe003 dialogue changed")
    font = json.loads(FONT_JSON.read_text(encoding="utf-8"))
    if len(font) != 212:
        raise AssertionError("font entry count changed")
    ids = []
    for row in font.values():
        code = bytes.fromhex(row["code_hex"])
        p = 0x29756 + 2*(code[0]-0x80)
        map_address = int.from_bytes(data[p:p+2], "little")
        off = file_offset(0x850000 + map_address) + 2*(code[1]-0x40)
        gid = int.from_bytes(data[off:off+2], "little")
        if not any(lo <= gid < hi for lo,hi in VI_RANGES):
            raise AssertionError(f"Vietnamese glyph not covered: {row['code_hex']} {gid:04X}")
        ids.append(gid)
    for gid in ids:
        for i in range(19):
            x = 4 + 9*i
            if (execute_stub(word,data,gid,i,True) != 16*(x//8) or
                execute_stub(byte,data,gid,i,False) != x % 8):
                raise AssertionError(f"9px stub failure gid={gid:04X}, i={i}")
    # Non-Vietnamese glyph controls stay 13px. This is a micro-instruction
    # test, NOT full native Japanese gameplay coverage.
    native_controls = (0x0000,0x0120,0x0150,0x0200,0x022D,
                       0x0340,0x0517,0x074D,0x0820,0x0900)
    for gid in native_controls:
        for i in range(19):
            x = 4 + 13*i
            if (execute_stub(word,data,gid,i,True) != 16*(x//8) or
                execute_stub(byte,data,gid,i,False) != x % 8):
                raise AssertionError(f"native regression gid={gid:04X}, i={i}")
    report = {
        "status":"OFFLINE_STATIC_MICROHOOK_PASS",
        "runtime":"UNTESTED", "release_ready":False,
        "base_sha256":EXPECTED_SHA256,
        "diagnostic_sha256":hashlib.sha256(data).hexdigest(),
        "changed_bytes":len(changed), "word_stub_size":len(word),
        "byte_stub_size":len(byte), "checksum":f"0x{ck:04X}",
        "complement":f"0x{ck^0xFFFF:04X}",
        "vi_test_cases":len(ids)*19, "native_control_cases":len(native_controls)*19,
        "old_13px_tables_unchanged":True,
        "mixed_japanese_quotation_marks":"POTENTIAL_SPACING_ISSUE",
        "limitations":"No SNES emulator/WRAM behavior demonstrated; no Japanese full-game PASS",
    }
    return bytes(data), report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("probe008_v2_13px",type=Path)
    ap.add_argument("out_diagnostic_rom",type=Path)
    ap.add_argument("report_json",type=Path)
    args=ap.parse_args()
    paths={v.resolve() for v in (args.probe008_v2_13px,args.out_diagnostic_rom,args.report_json)}
    if len(paths)!=3:
        raise ValueError("never overwrite source ROM or results with report")
    result,report=build(args.probe008_v2_13px.read_bytes())
    args.out_diagnostic_rom.parent.mkdir(parents=True,exist_ok=True)
    args.out_diagnostic_rom.write_bytes(result)
    args.report_json.parent.mkdir(parents=True,exist_ok=True)
    args.report_json.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",
                                encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
