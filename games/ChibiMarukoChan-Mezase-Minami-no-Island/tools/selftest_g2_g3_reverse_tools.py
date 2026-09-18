#!/usr/bin/env python3
from __future__ import annotations

import tempfile
from pathlib import Path

from correlate_g1_evidence import parse_shape_report, parse_trace_report
from run_g2_g3_graphics_reverse_pipeline import batch_summary, rank_batch
from scan_graphics_shape_targets import BATCHES, coverage, unique_chars


def check(name: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(name)
    print(f"{name}=PASS")


def main() -> int:
    print("CHIBI G2/G3 REVERSE TOOLS STATIC SELFTEST")

    check("g2_targets_present", {"start_banner", "rules_heading", "first_to_two", "until_win"} <= set(BATCHES["g2"]))
    check("g3_targets_present", {"win", "lose", "continue", "quit", "final_win", "ending"} <= set(BATCHES["g3"]))

    chars = unique_chars({"a": "勝ち", "b": "勝利"})
    check("unique_chars_dedup", chars.count("勝") == 1)

    cov = coverage({"勝", "ち"}, {"win": "勝ち", "final": "最終勝利"})
    check("coverage_exact", "win:2/2" in cov)

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        shape = td / "g3_shape.txt"
        trace = td / "trace.txt"

        shape.write_text(
            "\n".join(
                [
                    "cluster 0x004000..0x004080 unique_chars=2 chars=勝ち "
                    "hits=4 best=0.9800 coverage=win:2/2,lose:0/3,continue:0/7,quit:0/3,final_win:1/4,ending:0/6 "
                    "modes=snes4bpp_2x2_seq",
                    "cluster 0x006000..0x006040 unique_chars=1 chars=エ "
                    "hits=2 best=0.9200 coverage=win:0/2,lose:0/3,continue:0/7,quit:0/3,final_win:0/4,ending:1/6 "
                    "modes=1bpp12_msb",
                ]
            ) + "\n",
            encoding="utf-8",
        )

        trace.write_text(
            "\n".join(
                [
                    "[ANCHORS]",
                    "descriptor_win file=0x028732 cpu=$858732 refs=1",
                    "  ptr16_same_bank @0x002900 (858900)",
                    "",
                    "[BANK $85 16-BIT LOCAL POINTER RUNS]",
                    "table@0x002A00 count=4 targets=0x004020,0x004200,0x004400,0x004600",
                    "",
                    "[BANK $85 24-BIT ROM POINTER RUNS]",
                    "table@0x002B00 count=3 targets=0x004050,0x007000,0x008000",
                    "",
                    "[BANK $85 VRAM / DMA REGISTER STORES]",
                    "file=0x002850 cpu=$858850 STA $420B MDMAEN",
                ]
            ) + "\n",
            encoding="utf-8",
        )

        clusters = parse_shape_report(shape)
        pointers, dma, refs = parse_trace_report(trace)
        check("generic_cluster_parse", len(clusters) == 2)
        check("generic_pointer_parse", any(p.target_off == 0x4020 for p in pointers))
        check("generic_dma_parse", len(dma) == 1)
        check("generic_anchor_parse", len(refs) == 1)

        ranked, pointers2, dma2, refs2 = rank_batch(shape, trace, 0x400)
        check("g3_rank_count", len(ranked) == 2)
        score, cluster, direct, near, nearest = ranked[0]
        check("g3_strong_ranked_first", cluster.start == 0x4000 and len(direct) >= 1 and cluster.unique_chars >= 2)
        check("g3_nearest_zero", nearest == 0)

        summary = batch_summary("g3", ranked, pointers2, dma2, refs2, 10)
        check("g3_summary_strong", summary["strong_candidates_in_top"] >= 1)
        check("g3_summary_targets", summary["targets"]["win"] == "勝ち")

    print("selftest=PASS")
    print("commercial_rom_required=NO")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
