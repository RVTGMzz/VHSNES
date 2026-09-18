#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

from rom_common import require_clean_rom

ROM_SIZE = 0x200000
BANK85_START = 0x28000
BANK85_END = 0x30000

ANCHORS = {
    "parser": 0x283D8,
    "descriptor_start_password": 0x286B4,
    "descriptor_demo_start": 0x286EA,
    "descriptor_vs": 0x28714,
    "descriptor_win": 0x28732,
    "descriptor_lose": 0x2875E,
    "descriptor_continue": 0x2878A,
    "descriptor_quit_story": 0x287AC,
    "descriptor_final_win": 0x287E0,
    "descriptor_ending": 0x287FC,
    "main_menu_text_first": 0x28818,
    "renderer": 0x28E7B,
    "font_page_ptr_table": 0x295EE,
    "lead_ptr_table": 0x29756,
}

TARGET_CP932 = {
    "heading": "どれにする？",
    "start": "はじめから",
    "password": "パスワード",
}

# High-value PPU / DMA registers for an asset upload trace.
PPU_DMA_REGS = {
    0x2115: "VMAIN",
    0x2116: "VMADDL/H",
    0x2118: "VMDATAL",
    0x2119: "VMDATAH",
    0x420B: "MDMAEN",
}
for channel in range(8):
    base = 0x4300 + channel * 0x10
    for delta, name in (
        (0x0, "DMAP"),
        (0x1, "BBAD"),
        (0x2, "A1TL"),
        (0x3, "A1TH"),
        (0x4, "A1B"),
        (0x5, "DASL"),
        (0x6, "DASH"),
    ):
        PPU_DMA_REGS[base + delta] = f"DMA{channel}_{name}"


@dataclass(frozen=True)
class RefHit:
    kind: str
    source_off: int
    target_off: int
    target_cpu: int


def file_to_lorom_cpu(off: int) -> int:
    if not (0 <= off < ROM_SIZE):
        raise ValueError(f"file offset outside ROM: 0x{off:X}")
    bank_index, within = divmod(off, 0x8000)
    return ((0x80 | bank_index) << 16) | (0x8000 + within)


def lorom_cpu_to_file(cpu: int) -> int | None:
    bank = (cpu >> 16) & 0xFF
    addr = cpu & 0xFFFF
    if addr < 0x8000:
        return None
    bank_index = bank & 0x7F
    off = bank_index * 0x8000 + (addr - 0x8000)
    if 0 <= off < ROM_SIZE:
        return off
    return None


def iter_hits(data: bytes | bytearray, needle: bytes, start: int = 0, end: int | None = None):
    if end is None:
        end = len(data)
    pos = start
    while True:
        pos = data.find(needle, pos, end)
        if pos < 0:
            return
        yield pos
        pos += 1


def hex_window(data: bytes | bytearray, center: int, radius: int = 32) -> str:
    start = max(0, center - radius)
    end = min(len(data), center + radius)
    return f"0x{start:06X}..0x{end:06X}: " + bytes(data[start:end]).hex(" ").upper()


def xrefs_to_offset(data: bytes | bytearray, target_off: int) -> list[RefHit]:
    cpu = file_to_lorom_cpu(target_off)
    bank = (cpu >> 16) & 0xFF
    addr = cpu & 0xFFFF
    out: list[RefHit] = []

    p24 = bytes((addr & 0xFF, addr >> 8, bank))
    for off in iter_hits(data, p24):
        out.append(RefHit("ptr24", off, target_off, cpu))

    # Same-bank 16-bit pointers are common in local tables. Restrict to the
    # target bank's 32 KiB file window so random whole-ROM matches do not swamp
    # the report.
    bank_index = bank & 0x7F
    b0 = bank_index * 0x8000
    b1 = b0 + 0x8000
    p16 = addr.to_bytes(2, "little")
    for off in iter_hits(data, p16, b0, min(b1, len(data))):
        if off == target_off:
            continue
        out.append(RefHit("ptr16_same_bank", off, target_off, cpu))
    return out


def classify_local_u16(value: int, bank: int = 0x85) -> int | None:
    if value < 0x8000:
        return None
    return lorom_cpu_to_file((bank << 16) | value)


def pointer_runs_u16_bank85(data: bytes | bytearray, min_items: int = 4) -> list[tuple[int, list[int]]]:
    runs: list[tuple[int, list[int]]] = []
    off = BANK85_START
    while off + 2 <= BANK85_END:
        vals: list[int] = []
        cur = off
        while cur + 2 <= BANK85_END:
            value = int.from_bytes(data[cur:cur + 2], "little")
            target = classify_local_u16(value, 0x85)
            if target is None or not (BANK85_START <= target < BANK85_END):
                break
            vals.append(target)
            cur += 2
        if len(vals) >= min_items and len(set(vals)) >= min_items - 1:
            runs.append((off, vals))
            off = cur
        else:
            off += 2
    return runs


def pointer_runs_24(data: bytes | bytearray, min_items: int = 3) -> list[tuple[int, list[int]]]:
    runs: list[tuple[int, list[int]]] = []
    off = BANK85_START
    while off + 3 <= BANK85_END:
        vals: list[int] = []
        cur = off
        while cur + 3 <= BANK85_END:
            cpu = data[cur] | (data[cur + 1] << 8) | (data[cur + 2] << 16)
            target = lorom_cpu_to_file(cpu)
            if target is None:
                break
            vals.append(target)
            cur += 3
        if len(vals) >= min_items and len(set(vals)) >= min_items:
            runs.append((off, vals))
            off = cur
        else:
            off += 1
    return runs


def jsl_calls_to(data: bytes | bytearray, target_cpu: int) -> list[int]:
    pattern = bytes((0x22, target_cpu & 0xFF, (target_cpu >> 8) & 0xFF, (target_cpu >> 16) & 0xFF))
    return list(iter_hits(data, pattern))


def dma_register_sites(data: bytes | bytearray) -> list[tuple[int, str, int]]:
    # Absolute store opcodes that are useful even without knowing M/X width.
    # STA/STX/STY/STZ abs.
    stores = {
        0x8D: "STA",
        0x8E: "STX",
        0x8C: "STY",
        0x9C: "STZ",
    }
    out: list[tuple[int, str, int]] = []
    for off in range(BANK85_START, BANK85_END - 2):
        op = data[off]
        if op not in stores:
            continue
        addr = data[off + 1] | (data[off + 2] << 8)
        if addr in PPU_DMA_REGS:
            out.append((off, stores[op], addr))
    return out


def local_control_flow_targets(data: bytes | bytearray, start: int, end: int) -> list[tuple[int, str, int, int | None]]:
    out: list[tuple[int, str, int, int | None]] = []
    # Pattern scan, not a full disassembler. Only opcodes with fixed operand sizes
    # are used so this remains safe under unknown processor width flags.
    for off in range(max(0, start), min(len(data), end)):
        op = data[off]
        if op in (0x22, 0x5C) and off + 3 < len(data):  # JSL/JML long
            cpu = data[off + 1] | (data[off + 2] << 8) | (data[off + 3] << 16)
            out.append((off, "JSL" if op == 0x22 else "JML", cpu, lorom_cpu_to_file(cpu)))
        elif op in (0x20, 0x4C) and off + 2 < len(data):  # JSR/JMP absolute, same bank
            addr = data[off + 1] | (data[off + 2] << 8)
            caller_bank = (file_to_lorom_cpu(off) >> 16) & 0xFF
            cpu = (caller_bank << 16) | addr
            out.append((off, "JSR" if op == 0x20 else "JMP", cpu, lorom_cpu_to_file(cpu)))
    return out


def exact_cp932_hits(data: bytes | bytearray) -> dict[str, list[int]]:
    return {name: list(iter_hits(data, text.encode("cp932"))) for name, text in TARGET_CP932.items()}


def write_csv(path: Path, rows: list[dict[str, str | int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="READ-ONLY G1 render-path trace for Chibi Maruko-chan SNES (no guessed asset offsets)"
    )
    ap.add_argument("rom", type=Path, help="exact canonical clean ROM")
    ap.add_argument("--report", type=Path, help="optional UTF-8 text report")
    ap.add_argument("--csv", type=Path, help="optional CSV with xrefs/DMA sites")
    args = ap.parse_args()

    data = require_clean_rom(args.rom)
    lines: list[str] = []
    csv_rows: list[dict[str, str | int]] = []

    def emit(s: str = "") -> None:
        print(s)
        lines.append(s)

    emit("CHIBI MARUKO G1 RENDER-PATH TRACE")
    emit("mode=READ_ONLY")
    emit("clean_rom_contract=PASS")
    emit("runtime_claim=NO")
    emit()

    emit("[ANCHORS]")
    for name, off in ANCHORS.items():
        cpu = file_to_lorom_cpu(off)
        refs = xrefs_to_offset(data, off)
        emit(f"{name:28s} file=0x{off:06X} cpu=${cpu:06X} refs={len(refs)}")
        for hit in refs[:24]:
            emit(f"  {hit.kind:16s} @0x{hit.source_off:06X} ({file_to_lorom_cpu(hit.source_off):06X})")
            csv_rows.append({
                "type": "xref",
                "name": name,
                "source_file": f"0x{hit.source_off:06X}",
                "source_cpu": f"0x{file_to_lorom_cpu(hit.source_off):06X}",
                "target_file": f"0x{off:06X}",
                "target_cpu": f"0x{cpu:06X}",
                "detail": hit.kind,
            })
    emit()

    emit("[EXACT CP932 TARGET HITS]")
    for name, hits in exact_cp932_hits(data).items():
        emit(f"{name:10s} text={TARGET_CP932[name]} hits={len(hits)} offsets={[f'0x{x:06X}' for x in hits[:32]]}")
    emit("note=hits inside descriptor prose are evidence only for descriptor text, not visible retail asset storage")
    emit()

    renderer_cpu = file_to_lorom_cpu(ANCHORS["renderer"])
    parser_cpu = file_to_lorom_cpu(ANCHORS["parser"])
    emit("[DIRECT CALLS TO PROVEN TEXT PATH]")
    for label, cpu in (("renderer", renderer_cpu), ("parser", parser_cpu)):
        calls = jsl_calls_to(data, cpu)
        emit(f"{label}_jsl_calls={len(calls)}")
        for off in calls:
            emit(f"  call @ file=0x{off:06X} cpu=${file_to_lorom_cpu(off):06X}")
            emit("    " + hex_window(data, off, 24))
            csv_rows.append({
                "type": "call",
                "name": label,
                "source_file": f"0x{off:06X}",
                "source_cpu": f"0x{file_to_lorom_cpu(off):06X}",
                "target_file": f"0x{lorom_cpu_to_file(cpu):06X}" if lorom_cpu_to_file(cpu) is not None else "",
                "target_cpu": f"0x{cpu:06X}",
                "detail": "JSL",
            })
    emit()

    dma_sites = dma_register_sites(data)
    emit("[BANK $85 VRAM / DMA REGISTER STORES]")
    emit(f"sites={len(dma_sites)}")
    for off, op, addr in dma_sites:
        cpu = file_to_lorom_cpu(off)
        emit(f"file=0x{off:06X} cpu=${cpu:06X} {op} ${addr:04X} {PPU_DMA_REGS[addr]}")
        emit("  " + hex_window(data, off, 28))
        flows = local_control_flow_targets(data, off - 40, off + 44)
        if flows:
            for foff, opname, target_cpu, target_file in flows[:16]:
                tf = f"0x{target_file:06X}" if target_file is not None else "unmapped"
                emit(f"    nearby {opname} @0x{foff:06X} -> ${target_cpu:06X} ({tf})")
        csv_rows.append({
            "type": "ppu_dma_store",
            "name": PPU_DMA_REGS[addr],
            "source_file": f"0x{off:06X}",
            "source_cpu": f"0x{cpu:06X}",
            "target_file": "",
            "target_cpu": f"0x{addr:04X}",
            "detail": op,
        })
    emit()

    emit("[BANK $85 16-BIT LOCAL POINTER RUNS]")
    runs16 = pointer_runs_u16_bank85(data)
    emit(f"runs={len(runs16)}")
    for start, targets in runs16[:80]:
        sample = ",".join(f"0x{x:06X}" for x in targets[:12])
        emit(f"table@0x{start:06X} count={len(targets)} targets={sample}")
    emit()

    emit("[BANK $85 24-BIT ROM POINTER RUNS]")
    runs24 = pointer_runs_24(data)
    emit(f"runs={len(runs24)}")
    for start, targets in runs24[:80]:
        sample = ",".join(f"0x{x:06X}" for x in targets[:12])
        emit(f"table@0x{start:06X} count={len(targets)} targets={sample}")
    emit()

    emit("[G1 TRIAGE]")
    desc_refs = xrefs_to_offset(data, ANCHORS["descriptor_start_password"])
    menu_refs = xrefs_to_offset(data, ANCHORS["main_menu_text_first"])
    render_calls = jsl_calls_to(data, renderer_cpu)
    emit(f"descriptor_start_password_refs={len(desc_refs)}")
    emit(f"main_menu_text_refs={len(menu_refs)}")
    emit(f"renderer_calls={len(render_calls)}")
    emit(f"bank85_dma_sites={len(dma_sites)}")
    emit("next=correlate descriptor/menu setup xrefs with nearest VRAM/DMA site; then prove source pointer before any asset write")
    emit("do_not_patch=0x286B4..0x287FC descriptor/debug prose")
    emit("runtime_claim=NO")

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"report={args.report}")
    if args.csv:
        write_csv(args.csv, csv_rows)
        print(f"csv={args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
