#!/usr/bin/env python3
"""G2 source-range 9px spacing DIAGNOSTIC. Stateless, no ROMs in GitHub.

Only the exact three 106-byte G2 direct-text ROM fields use 9px, including
native Japanese quotes. All other source banks/ranges retain original 13px.
This assumes renderer DBR still identifies the source bank ($83), and thus
needs real emulator confirmation before ANY release claim.
"""
import argparse
import hashlib
import json
from pathlib import Path

INPUT_SHA256 = "2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd"
G2_RANGES = ((0x81CE, 0x8238), (0x8247, 0x82B1), (0x82C0, 0x832A))
WORD_HOOK = 0x28E0C
BYTE_HOOK = 0x290EE
WORD_STUB = 0x2FB80   # $85:FB80
BYTE_STUB = 0x2FC00   # $85:FC00
NINE_WORD = 0x2FC80   # $85:FC80
NINE_BYTE = 0x2FCC0   # $85:FCC0
CHECKSUM = 0x7FDC


class Assembly:
    def __init__(self):
        self.code = bytearray()
        self.labels = {}
        self.fixups = []

    def emit(self, *bytes_):
        self.code.extend(bytes_)

    def label(self, name):
        self.labels[name] = len(self.code)

    def branch(self, opcode, label):
        self.emit(opcode, 0)
        self.fixups.append((len(self.code)-1, label))

    def cmp16(self, value):
        self.emit(0xC9, value & 255, value >> 8)

    def load_long_x(self, addr):
        self.emit(0xBF, addr & 255, (addr >> 8) & 255, addr >> 16)

    def assemble(self):
        for offset, label in self.fixups:
            distance = self.labels[label] - (offset + 1)
            if not -128 <= distance <= 127:
                raise ValueError("branch out of range: " + label)
            self.code[offset] = distance & 255
        return bytes(self.code)


def make_stub(is_word):
    a = Assembly()
    # The original word/shift consumers have M=16 and M=8 respectively.
    # PHP/PLP restore M and C; PHB/PLA read DBR without altering it.
    a.emit(0x08, 0xE2, 0x20)  # PHP; SEP M=8
    if is_word:
        a.emit(0x8B, 0x68)  # PHB; PLA: live source DBR before bank switch
    else:
        # The saved DBR lies at 7,S if X=8 (1-byte PHX/PHY), or at 9,S
        # if X=16 (2-byte PHX/PHY). Read X flag from PHP-saved status.
        a.emit(0xA3, 0x01, 0x29, 0x10)  # LDA $01,S; AND #$10
        a.branch(0xF0, "x16")  # BEQ if X flag is clear
        a.emit(0xA3, 0x07)  # LDA $07,S for X8
        a.branch(0x80, "got_bank")
        a.label("x16")
        a.emit(0xA3, 0x09)  # LDA $09,S for X16
        a.label("got_bank")
    a.emit(0xC9, 0x83)  # CMP #$83
    a.branch(0xD0, "native")  # if DBR != 0x83, preserve native 13px
    a.emit(0xC2, 0x20, 0xAF, 0x94, 0x1F, 0x00)  # REP M=16; LDA.l $001F94
    for first, end in G2_RANGES:
        a.cmp16(first)
        a.branch(0x90, "native")
        a.cmp16(end)
        a.branch(0x90, "g2")
    a.label("native")
    a.emit(0x28)
    a.load_long_x(0x859670 if is_word else 0x859696)
    a.emit(0x6B)
    a.label("g2")
    a.emit(0x28)
    a.load_long_x(0x85FC80 if is_word else 0x85FCC0)
    a.emit(0x6B)
    output = a.assemble()
    if len(output) > 0x80:
        raise ValueError("stub exceeds guarded staging span")
    return output


def cpu_to_file(addr):
    if addr & 0xFFFF < 0x8000:
        raise ValueError("invalid LoROM pointer")
    return (addr >> 16 & 0x7F)*0x8000 + (addr & 0x7FFF)


def interpret(stub, rom, source_pointer, source_dbr, index, is_word, x8=False):
    """Only the emitted 65816 subset; static test, NOT SNES emulation."""
    ip = 0
    stack = []
    m = original_m = 16 if is_word else 8
    accumulator = 0xBEEF if is_word else 0xEE
    x = index * (2 if is_word else 1)
    carry = zero = False
    # At the word hook DBR is the source bank. Before the shift hook the
    # renderer executes PEA $7F00; PLB; PLB, so LIVE DBR becomes $7F.
    live_dbr = source_dbr if is_word else 0x7F
    for _ in range(90):
        op = stub[ip]
        ip += 1
        if op == 0x08:  # PHP
            stack.append(m)
        elif op in (0xE2, 0xC2):  # SEP / REP
            if stub[ip] != 0x20:
                raise ValueError("unexpected processor-width flag")
            ip += 1
            m = 8 if op == 0xE2 else 16
        elif op == 0x8B:  # PHB
            stack.append(live_dbr)
        elif op == 0x68:  # PLA (M=8)
            accumulator = stack.pop()
        elif op == 0xA3:  # LDA stack relative (saved P or saved original DBR)
            displacement = stub[ip]
            ip += 1
            if is_word or len(stack) != 1 or live_dbr != 0x7F:
                raise AssertionError("invalid stack-frame access")
            if displacement == 0x01:
                accumulator = 0x10 if x8 else 0  # PHP-saved X-width status
            elif displacement == (0x07 if x8 else 0x09):
                accumulator = source_dbr
            else:
                raise AssertionError("wrong saved-DBR stack offset")
        elif op == 0x29:  # AND immediate, 8-bit A
            if m != 8:
                raise AssertionError("X-width test was not 8-bit")
            accumulator &= stub[ip]
            ip += 1
            zero = accumulator == 0
        elif op == 0xC9:  # CMP immediate
            width = 2 if m == 16 else 1
            operand = int.from_bytes(stub[ip:ip+width], "little")
            ip += width
            carry, zero = accumulator >= operand, accumulator == operand
        elif op in (0xD0, 0x90, 0xF0, 0x80):  # BNE / BCC / BEQ / BRA
            rel = stub[ip]
            ip += 1
            if (op == 0xD0 and not zero) or (op == 0x90 and not carry) or (op == 0xF0 and zero) or op == 0x80:
                ip += rel if rel < 128 else rel - 256
        elif op == 0xAF:  # LDA long current ROM-source pointer
            addr = int.from_bytes(stub[ip:ip+3], "little")
            ip += 3
            if addr != 0x001F94:
                raise ValueError("unexpected source-pointer read")
            accumulator = source_pointer
        elif op == 0x28:  # PLP
            m = stack.pop()
        elif op == 0xBF:  # LDA long,X 13px or 9px table
            addr = int.from_bytes(stub[ip:ip+3], "little")
            ip += 3
            offset = cpu_to_file(addr) + x
            accumulator = (int.from_bytes(rom[offset:offset+2], "little")
                           if m == 16 else rom[offset])
        elif op == 0x6B:  # RTL
            if m != original_m or stack:
                raise AssertionError("processor flags or stack not preserved")
            return accumulator
        else:
            raise ValueError(f"unsupported opcode 0x{op:02X}")
    raise AssertionError("stub did not return")


def build(original):
    if len(original) != 0x200000 or hashlib.sha256(original).hexdigest() != INPUT_SHA256:
        raise ValueError("exact Probe008 V2 font-only source ROM required")
    if original[WORD_HOOK:WORD_HOOK+4] != bytes.fromhex("BF709685"):
        raise ValueError("unexpected original tile-lookup instruction")
    if original[BYTE_HOOK:BYTE_HOOK+4] != bytes.fromhex("BF969685"):
        raise ValueError("unexpected original shift-lookup instruction")
    if original[0x28EA8:0x28EAC] != bytes.fromhex("BF00F885"):
        raise ValueError("font low-pointer relocation is missing")
    if original[0x28EAE:0x28EB2] != bytes.fromhex("BF01F885"):
        raise ValueError("font bank-pointer relocation is missing")
    # The renderer saves the source DBR, changes it to $7F before BYTE lookup.
    if original[0x28E7B:0x28E7F] != bytes.fromhex("8BDA5A48"):
        raise ValueError("renderer PHB/PHX/PHY/PHA stack frame changed")
    if original[0x28E87] != 0x68 or original[0x28E95:0x28E9A] != bytes.fromhex("F4007FABAB"):
        raise ValueError("renderer bank switch or original PHA/PLA changed")
    spans = ((WORD_STUB, WORD_STUB+0x80), (BYTE_STUB, BYTE_STUB+0x80),
             (NINE_WORD, NINE_WORD+38), (NINE_BYTE, NINE_BYTE+19))
    for lo, hi in spans:
        if original[lo:hi] != bytes([0xFF])*(hi-lo):
            raise ValueError(f"occupied ROM stage 0x{lo:06X}")
    for lo, hi in G2_RANGES:
        if hi-lo != 106:
            raise AssertionError("G2 record width changed")
    data = bytearray(original)
    word, byte = make_stub(True), make_stub(False)
    data[WORD_STUB:WORD_STUB+len(word)] = word
    data[BYTE_STUB:BYTE_STUB+len(byte)] = byte
    for i in range(19):
        x = 4 + 9*i
        data[NINE_WORD+2*i:NINE_WORD+2*i+2] = (16*(x//8)).to_bytes(2,"little")
        data[NINE_BYTE+i] = x % 8
    data[WORD_HOOK:WORD_HOOK+4] = bytes.fromhex("2280FB85")
    data[BYTE_HOOK:BYTE_HOOK+4] = bytes.fromhex("2200FC85")
    data[CHECKSUM:CHECKSUM+4] = bytes(4)
    ck = (sum(data) + 0x1FE) & 0xFFFF
    data[CHECKSUM:CHECKSUM+2] = (ck^0xFFFF).to_bytes(2,"little")
    data[CHECKSUM+2:CHECKSUM+4] = ck.to_bytes(2,"little")
    allowed = set(range(CHECKSUM,CHECKSUM+4))
    for lo,hi in spans:
        allowed.update(range(lo,hi))
    allowed.update(range(WORD_HOOK,WORD_HOOK+4))
    allowed.update(range(BYTE_HOOK,BYTE_HOOK+4))
    diff = {i for i,(a,b) in enumerate(zip(data,original)) if a!=b}
    if diff-allowed:
        raise AssertionError("unexpected ROM byte changes")
    if data[0x29670:0x296A9] != original[0x29670:0x296A9]:
        raise AssertionError("native 13px tables changed")
    for o in (0x181CE,0x18247,0x182C0):
        if data[o:o+106] != original[o:o+106]:
            raise AssertionError("strict G2 text bytes changed")
    checks = 0
    for i in range(19):
        for first,end in G2_RANGES:
            for pointer in range(first,end):
                for is_word,stub in ((True,word),(False,byte)):
                    for x8 in ((False,) if is_word else (False,True)):
                        value = interpret(stub,data,pointer,0x83,i,is_word,x8=x8)
                        x = 4+9*i
                        expected = 16*(x//8) if is_word else x%8
                        if value != expected:
                            raise AssertionError("9px field-address microhook failed")
                        checks += 1
        for ptr,dbr in ((0x81CE,0x80),(0x82C0,0x7E),(0x8238,0x83),
                        (0x8246,0x83),(0x82B1,0x83),(0x82BF,0x83),
                        (0x832A,0x83),(0x81CD,0x83),(0,0x83),(0xFFFF,0x83)):
            for is_word,stub in ((True,word),(False,byte)):
                for x8 in ((False,) if is_word else (False,True)):
                    value = interpret(stub,data,ptr,dbr,i,is_word,x8=x8)
                    x = 4+13*i
                    expected = 16*(x//8) if is_word else x%8
                    if value != expected:
                        raise AssertionError("13px native-field microhook failed")
                    checks += 1
    return bytes(data), {
        "status":"STATIC_65816_SUBSET_PASS_ONLY", "release_ready":False,
        "runtime":"UNTESTED", "base_sha256":INPUT_SHA256,
        "sha256":hashlib.sha256(data).hexdigest(),"changed_bytes":len(diff),
        "checksum":f"0x{ck:04X}","complement":f"0x{ck^0xFFFF:04X}",
        "word_stub_bytes":len(word),"byte_stub_bytes":len(byte),
        "subset_interpreter_cases":checks,
        "G2_source_ranges":[[hex(x),hex(y)] for x,y in G2_RANGES],
        "G2_native_quotes_use_9px":True,
        "out_of_range_source_keeps_13px":True,
        "runtime_blocker":"DBR bank, source pointer, and saved-stack provenance require emulator confirmation"
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("probe008_v2_font_only",type=Path)
    p.add_argument("output_diagnostic_rom",type=Path)
    p.add_argument("output_json_report",type=Path)
    a=p.parse_args()
    paths=(a.probe008_v2_font_only,a.output_diagnostic_rom,a.output_json_report)
    if len({p.resolve() for p in paths})!=3:
        raise ValueError("do not overwrite source ROM or report")
    result, report=build(a.probe008_v2_font_only.read_bytes())
    a.output_diagnostic_rom.parent.mkdir(parents=True,exist_ok=True)
    a.output_diagnostic_rom.write_bytes(result)
    a.output_json_report.parent.mkdir(parents=True,exist_ok=True)
    a.output_json_report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",
                                    encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
