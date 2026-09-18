#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

ROM_SIZE = 0x200000

DMA_REG_NAMES = {}
for ch in range(8):
    b = 0x4300 + ch * 0x10
    DMA_REG_NAMES.update({
        b + 0x0: (ch, "DMAP"),
        b + 0x1: (ch, "BBAD"),
        b + 0x2: (ch, "A1TL"),
        b + 0x3: (ch, "A1TH"),
        b + 0x4: (ch, "A1B"),
        b + 0x5: (ch, "DASL"),
        b + 0x6: (ch, "DASH"),
    })

LOAD_IMM_A = 0xA9
REP = 0xC2
SEP = 0xE2


@dataclass(frozen=True)
class Write:
    off: int
    reg: int
    channel: int
    name: str
    value: int | None
    width: int | None
    confidence: str


@dataclass(frozen=True)
class Transfer:
    channel: int
    trigger_off: int
    source_cpu: int | None
    source_file: int | None
    size: int | None
    bbad: int | None
    dmap: int | None
    confidence: str
    evidence: tuple[str, ...]


def cpu_to_file(cpu: int) -> int | None:
    bank = (cpu >> 16) & 0xFF
    addr = cpu & 0xFFFF
    if addr < 0x8000:
        return None
    off = (bank & 0x7F) * 0x8000 + (addr - 0x8000)
    return off if 0 <= off < ROM_SIZE else None


def file_to_cpu(off: int) -> int:
    bank_index, within = divmod(off, 0x8000)
    return ((0x80 | bank_index) << 16) | (0x8000 + within)


def infer_m_state(data: bytes | bytearray, start: int, end: int) -> dict[int, int | None]:
    """Best-effort accumulator-width map. Unknown until local REP/SEP proves it."""
    m: int | None = None
    out: dict[int, int | None] = {}
    i = max(0, start)
    end = min(len(data), end)
    while i < end:
        out[i] = m
        op = data[i]
        if op in (REP, SEP) and i + 1 < end:
            mask = data[i + 1]
            if mask & 0x20:
                m = 16 if op == REP else 8
            i += 2
            continue
        if op == LOAD_IMM_A:
            if m == 8:
                i += 2
            elif m == 16:
                i += 3
            else:
                i += 2
            continue
        if op == 0x8D:
            i += 3
            continue
        i += 1
    return out


def nearest_lda_immediate(
    data: bytes | bytearray,
    sta_off: int,
    m_map: dict[int, int | None],
    back: int = 12,
) -> list[tuple[int, int, int, str]]:
    """Return nearby LDA #imm candidates before one STA.

    This is deliberately heuristic and does not claim full 65816 dataflow.
    """
    lo = max(0, sta_off - back)
    candidates: list[tuple[int, int, int, str]] = []
    for p in range(lo, sta_off):
        if data[p] != LOAD_IMM_A:
            continue
        m = m_map.get(p)
        if m == 8 and p + 1 < sta_off:
            candidates.append((p, data[p + 1], 8, "width_proven"))
        elif m == 16 and p + 2 < sta_off:
            value = data[p + 1] | (data[p + 2] << 8)
            candidates.append((p, value, 16, "width_proven"))
        elif m is None:
            if p + 1 < sta_off:
                candidates.append((p, data[p + 1], 8, "width_unknown"))
            if p + 2 < sta_off:
                value = data[p + 1] | (data[p + 2] << 8)
                candidates.append((p, value, 16, "width_unknown"))
    return candidates[-4:]


def collect_dma_writes(data: bytes | bytearray, start: int, end: int) -> list[Write]:
    start = max(0, start)
    end = min(len(data), end)
    m_map = infer_m_state(data, start, end)
    out: list[Write] = []

    for off in range(start, end - 2):
        if data[off] != 0x8D:  # STA abs
            continue
        reg = data[off + 1] | (data[off + 2] << 8)
        if reg not in DMA_REG_NAMES:
            continue

        channel, name = DMA_REG_NAMES[reg]
        cands = nearest_lda_immediate(data, off, m_map)
        chosen = None

        # A1T/DAS commonly receive a 16-bit write starting at low register.
        want = 16 if name in ("A1TL", "DASL") else 8

        for cand in reversed(cands):
            if cand[2] == want and cand[3] == "width_proven":
                chosen = cand
                break
        if chosen is None:
            for cand in reversed(cands):
                if cand[2] == want:
                    chosen = cand
                    break
        if chosen is None and cands:
            chosen = cands[-1]

        if chosen:
            _, value, width, confidence = chosen
            out.append(Write(off, reg, channel, name, value, width, confidence))
        else:
            out.append(Write(off, reg, channel, name, None, None, "no_immediate"))

    return out


def reconstruct_before_trigger(
    data: bytes | bytearray,
    trigger_off: int,
    lookback: int = 0x80,
) -> list[Transfer]:
    writes = collect_dma_writes(data, trigger_off - lookback, trigger_off)
    last: dict[tuple[int, str], Write] = {}
    for w in writes:
        last[(w.channel, w.name)] = w

    # Best-effort MDMAEN mask reconstruction from nearby LDA #imm8.
    m_map = infer_m_state(data, max(0, trigger_off - 16), trigger_off + 3)
    mdma_value = None
    for cand in reversed(nearest_lda_immediate(data, trigger_off, m_map, back=12)):
        if cand[2] == 8:
            mdma_value = cand[1]
            break

    channels = (
        range(8)
        if mdma_value is None
        else [ch for ch in range(8) if mdma_value & (1 << ch)]
    )

    out: list[Transfer] = []
    for ch in channels:
        evidence: list[str] = []

        def get(name: str) -> Write | None:
            return last.get((ch, name))

        a1t = get("A1TL")
        a1b = get("A1B")
        das = get("DASL")
        bbad = get("BBAD")
        dmap = get("DMAP")

        low16 = None
        if a1t and a1t.value is not None:
            if a1t.width == 16:
                low16 = a1t.value & 0xFFFF
                evidence.append(f"A1T=0x{low16:04X}@0x{a1t.off:X}")
            elif a1t.width == 8:
                hi = get("A1TH")
                if hi and hi.value is not None:
                    low16 = (a1t.value & 0xFF) | ((hi.value & 0xFF) << 8)
                    evidence.append(
                        f"A1T=0x{low16:04X}@0x{a1t.off:X}/0x{hi.off:X}"
                    )

        bank = (
            a1b.value & 0xFF
            if a1b and a1b.value is not None
            else None
        )
        source_cpu = ((bank << 16) | low16) if bank is not None and low16 is not None else None
        source_file = cpu_to_file(source_cpu) if source_cpu is not None else None

        size = None
        if das and das.value is not None:
            if das.width == 16:
                size = das.value & 0xFFFF
                evidence.append(f"DAS=0x{size:04X}@0x{das.off:X}")
            elif das.width == 8:
                hi = get("DASH")
                if hi and hi.value is not None:
                    size = (das.value & 0xFF) | ((hi.value & 0xFF) << 8)
                    evidence.append(
                        f"DAS=0x{size:04X}@0x{das.off:X}/0x{hi.off:X}"
                    )

        bbad_v = bbad.value & 0xFF if bbad and bbad.value is not None else None
        dmap_v = dmap.value & 0xFF if dmap and dmap.value is not None else None
        if bbad_v is not None:
            evidence.append(f"BBAD=0x{bbad_v:02X}")
        if dmap_v is not None:
            evidence.append(f"DMAP=0x{dmap_v:02X}")

        confidence = (
            "high"
            if source_file is not None and size is not None and bbad_v is not None
            else "medium"
            if source_file is not None
            else "low"
        )

        out.append(
            Transfer(
                ch,
                trigger_off,
                source_cpu,
                source_file,
                size,
                bbad_v,
                dmap_v,
                confidence,
                tuple(evidence),
            )
        )

    return out


def find_mdma_sites(
    data: bytes | bytearray,
    start: int = 0,
    end: int | None = None,
) -> list[int]:
    if end is None:
        end = len(data)
    out = []
    for off in range(max(0, start), min(len(data), end) - 2):
        if data[off] == 0x8D and data[off + 1] == 0x0B and data[off + 2] == 0x42:
            out.append(off)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description="READ-ONLY conservative DMA source reconstruction for Chibi SNES"
    )
    ap.add_argument("rom", type=Path)
    ap.add_argument("--start", type=lambda s: int(s, 0), default=0)
    ap.add_argument("--end", type=lambda s: int(s, 0), default=ROM_SIZE)
    ap.add_argument("--lookback", type=lambda s: int(s, 0), default=0x80)
    ap.add_argument("--report", type=Path)
    ap.add_argument("--csv", type=Path)
    args = ap.parse_args()

    from rom_common import require_clean_rom

    data = require_clean_rom(args.rom)
    sites = find_mdma_sites(data, args.start, args.end)

    lines: list[str] = []
    rows: list[dict[str, str | int]] = []

    def emit(s: str = "") -> None:
        print(s)
        lines.append(s)

    emit("CHIBI MARUKO DMA SOURCE RECONSTRUCTION")
    emit("mode=READ_ONLY")
    emit("clean_rom_contract=PASS")
    emit("runtime_claim=NO")
    emit(
        f"mdma_sites={len(sites)} range=0x{args.start:X}..0x{args.end:X} "
        f"lookback=0x{args.lookback:X}"
    )
    emit(
        "heuristic_note=immediate-width inference requires local REP/SEP; "
        "unknown-width cases are downgraded"
    )
    emit()

    total = 0
    for off in sites:
        for transfer in reconstruct_before_trigger(data, off, args.lookback):
            total += 1
            source_file = (
                f"0x{transfer.source_file:06X}"
                if transfer.source_file is not None
                else "-"
            )
            source_cpu = (
                f"${transfer.source_cpu:06X}"
                if transfer.source_cpu is not None
                else "-"
            )
            size = f"0x{transfer.size:04X}" if transfer.size is not None else "-"
            bbad = f"0x{transfer.bbad:02X}" if transfer.bbad is not None else "-"
            dmap = f"0x{transfer.dmap:02X}" if transfer.dmap is not None else "-"

            emit(
                f"trigger=0x{off:06X} ch={transfer.channel} "
                f"conf={transfer.confidence} source={source_cpu} "
                f"file={source_file} size={size} BBAD={bbad} DMAP={dmap}"
            )
            if transfer.evidence:
                emit("  evidence=" + "; ".join(transfer.evidence))

            rows.append({
                "trigger_file": f"0x{off:06X}",
                "trigger_cpu": f"0x{file_to_cpu(off):06X}",
                "channel": transfer.channel,
                "confidence": transfer.confidence,
                "source_cpu": source_cpu,
                "source_file": source_file,
                "size": size,
                "bbad": bbad,
                "dmap": dmap,
                "evidence": " | ".join(transfer.evidence),
            })

    emit()
    emit(f"transfers={total}")
    emit(
        "proof_rule=source reconstruction is candidate evidence; "
        "screen/title reachability and visual decode are still required"
    )
    emit("runtime_claim=NO")

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        fields = [
            "trigger_file",
            "trigger_cpu",
            "channel",
            "confidence",
            "source_cpu",
            "source_file",
            "size",
            "bbad",
            "dmap",
            "evidence",
        ]
        with args.csv.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
