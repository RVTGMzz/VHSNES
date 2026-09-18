#!/usr/bin/env python3
from __future__ import annotations

import tempfile
from pathlib import Path

from correlate_g1_evidence import (
    coverage_score,
    distance_to_span,
    parse_shape_report,
    parse_trace_report,
)
from run_g1_graphics_reverse_pipeline import rank_evidence


def check(name: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(name)
    print(f"{name}=PASS")


def main() -> int:
    print("CHIBI G1 REVERSE TOOLS STATIC SELFTEST")

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        shape = td / "shape.txt"
        trace = td / "trace.txt"

        shape.write_text(
            "\n".join(
                [
                    "cluster 0x001000..0x001080 unique_chars=3 chars=どれに "
                    "hits=7 best=0.9722 coverage=heading:3/6,start:0/5,password:0/5 "
                    "modes=snes4bpp_2x2_seq",
                    "cluster 0x002000..0x002040 unique_chars=1 chars=は "
                    "hits=2 best=0.9300 coverage=heading:0/6,start:1/5,password:0/5 "
                    "modes=1bpp12_msb",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        trace.write_text(
            "\n".join(
                [
                    "[ANCHORS]",
                    "renderer file=0x028E7B cpu=$858E7B refs=1",
                    "  ptr16_same_bank @0x002900 (858900)",
                    "",
                    "[BANK $85 16-BIT LOCAL POINTER RUNS]",
                    "table@0x002A00 count=4 targets=0x001020,0x001200,0x001400,0x001600",
                    "",
                    "[BANK $85 24-BIT ROM POINTER RUNS]",
                    "table@0x002B00 count=3 targets=0x001050,0x003000,0x004000",
                    "",
                    "[BANK $85 VRAM / DMA REGISTER STORES]",
                    "file=0x002850 cpu=$858850 STA $420B MDMAEN",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        clusters = parse_shape_report(shape)
        check("shape_parse_count", len(clusters) == 2)
        check("shape_first_span", clusters[0].start == 0x1000 and clusters[0].end == 0x1080)
        check("coverage_score", coverage_score("heading:3/6,start:0/5,password:0/5") == 50)
        check("distance_inside", distance_to_span(0x1020, 0x1000, 0x1080) == 0)
        check("distance_outside", distance_to_span(0x1100, 0x1000, 0x1080) == 0x80)

        pointers, dma, anchor_refs = parse_trace_report(trace)
        check("pointer_parse", any(p.target_off == 0x1020 for p in pointers))
        check("dma_parse", len(dma) == 1 and dma[0].reg == 0x420B)
        check("anchor_ref_parse", len(anchor_refs) == 1)

        ranked, pointers2, dma2, refs2 = rank_evidence(shape, trace, 0x400)
        check("pipeline_parse_counts", len(pointers2) == len(pointers) and len(dma2) == len(dma) and len(refs2) == len(anchor_refs))
        score, cluster, direct, near, nearest = ranked[0]
        check("strong_candidate_ranked_first", cluster.start == 0x1000 and len(direct) >= 1 and cluster.unique_chars >= 2)
        check("strong_candidate_nearest_zero", nearest == 0)
        check("strong_candidate_score_positive", score > 0)

    print("selftest=PASS")
    print("commercial_rom_required=NO")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
