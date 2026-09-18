#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

from rom_common import LOROM_HEADER, read_u16le, require_clean_rom

ROM_SIZE = 0x200000
RESET_VECTOR_OFF = LOROM_HEADER + 0x3C

PPU_DMA_REGS = {
    0x2105: "BGMODE",
    0x2107: "BG1SC",
    0x2108: "BG2SC",
    0x2109: "BG3SC",
    0x210A: "BG4SC",
    0x210B: "BG12NBA",
    0x210C: "BG34NBA",
    0x2115: "VMAIN",
    0x2116: "VMADDL/H",
    0x2118: "VMDATAL",
    0x2119: "VMDATAH",
    0x212C: "TM",
    0x212D: "TS",
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

STORE_OPS = {0x8D: "STA", 0x8E: "STX", 0x8C: "STY", 0x9C: "STZ"}
CONTROL_OPS = {0x22: ("JSL", 3), 0x5C: ("JML", 3), 0x20: ("JSR", 2), 0x4C: ("JMP", 2)}


@dataclass(frozen=True)
class Window:
    center: int
    depth: int
    parent: int | None
    via: str


@dataclass(frozen=True)
class RegSite:
    off: int
    op: str
    reg: int
    depth: int
    window_center: int


def cpu_to_file(cpu: int) -> int | None:
    bank = (cpu >> 16) & 0xFF
    addr = cpu & 0xFFFF
    if addr < 0x8000:
        return None
    off = (bank & 0x7F) * 0x8000 + (addr - 0x8000)
    return off if 0 <= off < ROM_SIZE else None


def file_to_cpu(off: int) -> int:
    if not 0 <= off < ROM_SIZE:
        raise ValueError(off)
    bank_index, within = divmod(off, 0x8000)
    return ((0x80 | bank_index) << 16) | (0x8000 + within)


def scan_fixed_control(data: bytes | bytearray, start: int, end: int) -> list[tuple[int, str, int, int | None]]:
    out = []
    start = max(0, start)
    end = min(len(data), end)
    for off in range(start, end):
        op = data[off]
        if op not in CONTROL_OPS:
            continue
        name, operand_len = CONTROL_OPS[op]
        if off + operand_len >= end:
            continue
        if operand_len == 3:
            cpu = data[off + 1] | (data[off + 2] << 8) | (data[off + 3] << 16)
        else:
            addr = data[off + 1] | (data[off + 2] << 8)
            bank = (file_to_cpu(off) >> 16) & 0xFF
            cpu = (bank << 16) | addr
        out.append((off, name, cpu, cpu_to_file(cpu)))
    return out


def build_boot_windows(
    data: bytes | bytearray,
    reset_off: int,
    *,
    radius: int,
    max_depth: int,
    max_windows: int,
) -> list[Window]:
    windows = [Window(reset_off, 0, None, "RESET")]
    seen = {reset_off}
    idx = 0
    while idx < len(windows) and len(windows) < max_windows:
        w = windows[idx]
        idx += 1
        if w.depth >= max_depth:
            continue
        calls = scan_fixed_control(data, w.center - radius // 4, w.center + radius)
        for source_off, opname, _cpu, target_off in calls:
            if target_off is None or target_off in seen:
                continue
            seen.add(target_off)
            windows.append(Window(target_off, w.depth + 1, source_off, opname))
            if len(windows) >= max_windows:
                break
    return windows


def register_sites(data: bytes | bytearray, windows: list[Window], radius: int) -> list[RegSite]:
    best: dict[tuple[int, int], RegSite] = {}
    for w in windows:
        start = max(0, w.center - radius // 4)
        end = min(len(data), w.center + radius)
        for off in range(start, end - 2):
            op = data[off]
            if op not in STORE_OPS:
                continue
            reg = data[off + 1] | (data[off + 2] << 8)
            if reg not in PPU_DMA_REGS:
                continue
            site = RegSite(off, STORE_OPS[op], reg, w.depth, w.center)
            key = (off, reg)
            old = best.get(key)
            if old is None or site.depth < old.depth:
                best[key] = site
    return sorted(best.values(), key=lambda s: (s.depth, s.off, s.reg))


def score_window(w: Window, sites: list[RegSite], radius: int) -> tuple[int, dict[str, int]]:
    start = w.center - radius // 4
    end = w.center + radius
    local = [s for s in sites if start <= s.off < end]
    counts = {
        "dma": sum(1 for s in local if s.reg == 0x420B or 0x4300 <= s.reg <= 0x4376),
        "vram": sum(1 for s in local if s.reg in (0x2115, 0x2116, 0x2118, 0x2119)),
        "bg": sum(
            1
            for s in local
            if s.reg in (0x2105, 0x2107, 0x2108, 0x2109, 0x210A, 0x210B, 0x210C, 0x212C, 0x212D)
        ),
    }
    score = counts["dma"] * 6 + counts["vram"] * 5 + counts["bg"] * 3 - w.depth * 2
    return score, counts


def nearby_source_literals(
    data: bytes | bytearray,
    site_off: int,
    radius: int = 36,
) -> list[tuple[int, int, int | None]]:
    """Heuristic only: collect 24-bit ROM-looking literals near DMA setup."""
    out = []
    start = max(0, site_off - radius)
    end = min(len(data) - 2, site_off + radius)
    seen = set()
    for off in range(start, end):
        cpu = data[off] | (data[off + 1] << 8) | (data[off + 2] << 16)
        target = cpu_to_file(cpu)
        if target is None:
            continue
        key = (cpu, target)
        if key in seen:
            continue
        seen.add(key)
        out.append((off, cpu, target))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="READ-ONLY G0 boot/title render-path tracer")
    ap.add_argument("rom", type=Path, help="exact canonical clean ROM")
    ap.add_argument("--radius", type=lambda s: int(s, 0), default=0x180)
    ap.add_argument("--depth", type=int, default=3)
    ap.add_argument("--max-windows", type=int, default=192)
    ap.add_argument("--report", type=Path)
    ap.add_argument("--csv", type=Path)
    args = ap.parse_args()

    data = require_clean_rom(args.rom)
    reset_addr = read_u16le(data, RESET_VECTOR_OFF)
    reset_cpu = reset_addr
    reset_off = cpu_to_file(reset_cpu)
    if reset_off is None:
        raise SystemExit(f"reset vector does not map to ROM: ${reset_cpu:06X}")

    windows = build_boot_windows(
        data,
        reset_off,
        radius=args.radius,
        max_depth=args.depth,
        max_windows=args.max_windows,
    )
    sites = register_sites(data, windows, args.radius)
    ranked = []
    for w in windows:
        score, counts = score_window(w, sites, args.radius)
        ranked.append((score, counts, w))
    ranked.sort(key=lambda x: (-x[0], x[2].depth, x[2].center))

    lines: list[str] = []
    csv_rows: list[dict[str, str | int]] = []

    def emit(s: str = "") -> None:
        print(s)
        lines.append(s)

    emit("CHIBI MARUKO G0 BOOT/TITLE TRACE")
    emit("mode=READ_ONLY")
    emit("clean_rom_contract=PASS")
    emit("runtime_claim=NO")
    emit(f"reset_vector=${reset_addr:04X} reset_cpu=$00:{reset_addr:04X} reset_file=0x{reset_off:06X}")
    emit("pattern_scan_warning=control-flow scan is fixed-opcode heuristic, not width-aware 65816 disassembly")
    emit()

    emit("[BOOT WINDOW RANKING]")
    emit(f"windows={len(windows)} depth={args.depth} radius=0x{args.radius:X}")
    for rank, (score, counts, w) in enumerate(ranked[:80], 1):
        parent = f"0x{w.parent:06X}" if w.parent is not None else "-"
        emit(
            f"#{rank:02d} score={score:4d} center=0x{w.center:06X} cpu=${file_to_cpu(w.center):06X} "
            f"depth={w.depth} via={w.via} parent={parent} "
            f"dma={counts['dma']} vram={counts['vram']} bg={counts['bg']}"
        )
        csv_rows.append(
            {
                "type": "window",
                "rank": rank,
                "score": score,
                "file": f"0x{w.center:06X}",
                "cpu": f"0x{file_to_cpu(w.center):06X}",
                "depth": w.depth,
                "via": w.via,
                "detail": f"dma={counts['dma']} vram={counts['vram']} bg={counts['bg']}",
            }
        )
    emit()

    emit("[PPU / DMA SITES IN BOOT-EXPANDED WINDOWS]")
    emit(f"sites={len(sites)}")
    for s in sites[:320]:
        emit(
            f"file=0x{s.off:06X} cpu=${file_to_cpu(s.off):06X} depth={s.depth} "
            f"{s.op} ${s.reg:04X} {PPU_DMA_REGS[s.reg]} window=0x{s.window_center:06X}"
        )
        csv_rows.append(
            {
                "type": "reg_site",
                "rank": "",
                "score": "",
                "file": f"0x{s.off:06X}",
                "cpu": f"0x{file_to_cpu(s.off):06X}",
                "depth": s.depth,
                "via": s.op,
                "detail": f"${s.reg:04X} {PPU_DMA_REGS[s.reg]}",
            }
        )
        if s.reg == 0x420B:
            lits = nearby_source_literals(data, s.off)
            for loff, cpu, target in lits[:20]:
                emit(
                    f"  source_literal_candidate @0x{loff:06X} "
                    f"cpu=${cpu:06X} -> file=0x{target:06X}"
                )
    emit()

    emit("[G0 PROOF GATE]")
    emit("candidate_priority=boot-near routine with coherent BG base/tilemap setup + VRAM/DMA upload")
    emit("next=for top-ranked routine, prove DMA A1 source pointer and decode source tiles/tilemap before editing")
    emit("title_target=Chibi Maruko-chan / Tiến tới đảo phương Nam!!")
    emit("localization_credit=Việt hóa bởi VôtriValley")
    emit("preserve=original publisher/copyright attribution")
    emit("asset_offset_claim=NO")
    emit("runtime_claim=NO")

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"report={args.report}")
    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        fields = ["type", "rank", "score", "file", "cpu", "depth", "via", "detail"]
        with args.csv.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(csv_rows)
        print(f"csv={args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
