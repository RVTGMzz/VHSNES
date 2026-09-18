#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

CLUSTER_RE = re.compile(
    r"^cluster\s+0x([0-9A-Fa-f]+)\.\.0x([0-9A-Fa-f]+)\s+"
    r"unique_chars=(\d+)\s+chars=(.*?)\s+hits=(\d+)\s+best=([0-9.]+)\s+"
    r"coverage=(.*?)\s+modes=(.*)$"
)
PTR_RUN_RE = re.compile(r"^table@0x([0-9A-Fa-f]+)\s+count=(\d+)\s+targets=(.*)$")
HEX_RE = re.compile(r"0x([0-9A-Fa-f]+)")
DMA_RE = re.compile(r"^file=0x([0-9A-Fa-f]+)\s+cpu=\$[0-9A-Fa-f]+\s+\w+\s+\$([0-9A-Fa-f]{4})\s+(\S+)")
ANCHOR_REF_RE = re.compile(r"^\s+(ptr24|ptr16_same_bank)\s+@0x([0-9A-Fa-f]+)")
ANCHOR_LINE_RE = re.compile(r"^(\w+)\s+file=0x([0-9A-Fa-f]+)\s+cpu=\$[0-9A-Fa-f]+\s+refs=(\d+)")


@dataclass(frozen=True)
class ShapeCluster:
    start: int
    end: int
    unique_chars: int
    chars: str
    hits: int
    best: float
    coverage: str
    modes: str


@dataclass(frozen=True)
class PointerTarget:
    table_off: int
    target_off: int
    width: int


@dataclass(frozen=True)
class DmaSite:
    off: int
    reg: int
    name: str


@dataclass(frozen=True)
class AnchorRef:
    anchor: str
    kind: str
    source_off: int


def parse_shape_report(path: Path) -> list[ShapeCluster]:
    out: list[ShapeCluster] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = CLUSTER_RE.match(line.strip())
        if not m:
            continue
        out.append(
            ShapeCluster(
                start=int(m.group(1), 16),
                end=int(m.group(2), 16),
                unique_chars=int(m.group(3)),
                chars=m.group(4),
                hits=int(m.group(5)),
                best=float(m.group(6)),
                coverage=m.group(7),
                modes=m.group(8),
            )
        )
    if not out:
        raise RuntimeError(f"no shape clusters parsed from {path}")
    return out


def parse_trace_report(path: Path) -> tuple[list[PointerTarget], list[DmaSite], list[AnchorRef]]:
    pointers: list[PointerTarget] = []
    dma: list[DmaSite] = []
    anchor_refs: list[AnchorRef] = []
    current_anchor: str | None = None
    current_ptr_width = 0

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        stripped = line.strip()

        if stripped == "[BANK $85 16-BIT LOCAL POINTER RUNS]":
            current_ptr_width = 16
            current_anchor = None
            continue
        if stripped == "[BANK $85 24-BIT ROM POINTER RUNS]":
            current_ptr_width = 24
            current_anchor = None
            continue
        if stripped.startswith("["):
            current_ptr_width = 0

        am = ANCHOR_LINE_RE.match(stripped)
        if am:
            current_anchor = am.group(1)
            continue
        arm = ANCHOR_REF_RE.match(line)
        if arm and current_anchor:
            anchor_refs.append(AnchorRef(current_anchor, arm.group(1), int(arm.group(2), 16)))
            continue

        dm = DMA_RE.match(stripped)
        if dm:
            dma.append(DmaSite(int(dm.group(1), 16), int(dm.group(2), 16), dm.group(3)))
            continue

        pm = PTR_RUN_RE.match(stripped)
        if pm and current_ptr_width:
            table = int(pm.group(1), 16)
            for hx in HEX_RE.findall(pm.group(3)):
                pointers.append(PointerTarget(table, int(hx, 16), current_ptr_width))

    if not pointers:
        raise RuntimeError(f"no pointer targets parsed from {path}")
    return pointers, dma, anchor_refs


def distance_to_span(value: int, start: int, end: int) -> int:
    if start <= value <= end:
        return 0
    if value < start:
        return start - value
    return value - end


def coverage_score(text: str) -> int:
    score = 0
    for part in text.split(","):
        try:
            _name, frac = part.split(":", 1)
            got, total = frac.split("/", 1)
            g, t = int(got), int(total)
        except ValueError:
            continue
        if t:
            score += round(100 * g / t)
    return score


def main() -> int:
    ap = argparse.ArgumentParser(description="Correlate G1 bitmap-shape candidates with render-path pointer evidence")
    ap.add_argument("shape_report", type=Path)
    ap.add_argument("trace_report", type=Path)
    ap.add_argument("--near", type=lambda s: int(s, 0), default=0x400)
    ap.add_argument("--top", type=int, default=50)
    args = ap.parse_args()

    clusters = parse_shape_report(args.shape_report)
    pointers, dma, anchor_refs = parse_trace_report(args.trace_report)

    ranked = []
    for c in clusters:
        direct = [p for p in pointers if c.start <= p.target_off <= c.end]
        nearest = min((distance_to_span(p.target_off, c.start, c.end) for p in pointers), default=1 << 30)
        near = [p for p in pointers if distance_to_span(p.target_off, c.start, c.end) <= args.near]
        tables = sorted({p.table_off for p in direct})
        widths = sorted({p.width for p in direct})
        score = (
            len(direct) * 100000
            + len(near) * 1000
            + c.unique_chars * 100
            + coverage_score(c.coverage)
            + round(c.best * 10)
            - min(nearest, 0xFFFF)
        )
        ranked.append((score, c, direct, near, nearest, tables, widths))

    ranked.sort(key=lambda x: (-x[0], x[1].start))

    print("CHIBI MARUKO G1 EVIDENCE CORRELATION")
    print("mode=READ_ONLY_REPORT_CORRELATION")
    print("runtime_claim=NO")
    print(f"shape_clusters={len(clusters)}")
    print(f"pointer_targets={len(pointers)}")
    print(f"dma_sites={len(dma)}")
    print(f"anchor_refs={len(anchor_refs)}")
    print(f"near_threshold=0x{args.near:X}")
    print()

    for rank, item in enumerate(ranked[:args.top], 1):
        score, c, direct, near, nearest, tables, widths = item
        table_s = ",".join(f"0x{x:06X}" for x in tables) if tables else "-"
        width_s = ",".join(map(str, widths)) if widths else "-"
        print(
            f"#{rank:02d} score={score} span=0x{c.start:06X}..0x{c.end:06X} "
            f"chars={c.chars} unique={c.unique_chars} best={c.best:.4f} coverage={c.coverage}"
        )
        print(
            f"    direct_ptrs={len(direct)} near_ptrs={len(near)} nearest=0x{nearest:X} "
            f"direct_tables={table_s} widths={width_s} modes={c.modes}"
        )

    strong = [x for x in ranked if x[2] and x[1].unique_chars >= 2]
    print()
    print(f"strong_candidates={len(strong)}")
    print("strong_gate=at least one pointer target lands inside cluster AND cluster has >=2 distinct G1 glyph shapes")
    print("note=strong here means reverse priority, not proven retail asset")
    print("final_proof_gate=screen setup must reach the pointer/DMA path and decoded source must reproduce visible G1 text")
    print("do_not_patch=0x286B4..0x287FC descriptor/debug prose")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
