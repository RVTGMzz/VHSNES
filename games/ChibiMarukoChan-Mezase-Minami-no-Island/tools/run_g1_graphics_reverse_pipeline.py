#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from correlate_g1_evidence import (
    coverage_score,
    distance_to_span,
    parse_shape_report,
    parse_trace_report,
)
from rom_common import require_clean_rom


TARGETS = {
    "heading": "Chọn gì đây?",
    "start": "Bắt đầu",
    "password": "Mật khẩu",
}


def run(cmd: list[str], *, stdout_path: Path | None = None) -> None:
    if stdout_path:
        stdout_path.parent.mkdir(parents=True, exist_ok=True)
        with stdout_path.open("w", encoding="utf-8") as f:
            subprocess.run(cmd, check=True, stdout=f, stderr=subprocess.STDOUT)
    else:
        subprocess.run(cmd, check=True)


def rank_evidence(shape_report: Path, trace_report: Path, near: int):
    clusters = parse_shape_report(shape_report)
    pointers, dma, anchor_refs = parse_trace_report(trace_report)
    ranked = []

    for cluster in clusters:
        direct = [
            p
            for p in pointers
            if cluster.start <= p.target_off <= cluster.end
        ]
        nearest = min(
            (
                distance_to_span(
                    p.target_off,
                    cluster.start,
                    cluster.end,
                )
                for p in pointers
            ),
            default=1 << 30,
        )
        near_ptrs = [
            p
            for p in pointers
            if distance_to_span(
                p.target_off,
                cluster.start,
                cluster.end,
            )
            <= near
        ]
        score = (
            len(direct) * 100000
            + len(near_ptrs) * 1000
            + cluster.unique_chars * 100
            + coverage_score(cluster.coverage)
            + round(cluster.best * 10)
            - min(nearest, 0xFFFF)
        )
        ranked.append(
            (
                score,
                cluster,
                direct,
                near_ptrs,
                nearest,
            )
        )

    ranked.sort(key=lambda x: (-x[0], x[1].start))
    return ranked, pointers, dma, anchor_refs


def main() -> int:
    ap = argparse.ArgumentParser(
        description="One-command G1 graphics reverse pipeline for canonical Chibi ROM"
    )
    ap.add_argument("rom", type=Path)
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("reports/generated/g1_pipeline"),
    )
    ap.add_argument("--max-diff", type=int, default=14)
    ap.add_argument("--cluster-span", type=lambda s: int(s, 0), default=0x800)
    ap.add_argument("--near", type=lambda s: int(s, 0), default=0x400)
    ap.add_argument("--top", type=int, default=50)
    args = ap.parse_args()

    require_clean_rom(args.rom)

    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    tool_dir = Path(__file__).resolve().parent
    py = sys.executable

    trace_txt = out / "g1_render_path_trace.txt"
    trace_csv = out / "g1_render_path_trace.csv"
    shape_txt = out / "g1_shape_probe.txt"
    corr_txt = out / "g1_evidence_correlation.txt"
    summary_json = out / "g1_pipeline_summary.json"

    run(
        [
            py,
            str(tool_dir / "trace_g1_render_path.py"),
            str(args.rom),
            "--report",
            str(trace_txt),
            "--csv",
            str(trace_csv),
        ]
    )

    run(
        [
            py,
            str(tool_dir / "scan_g1_shape_fingerprints.py"),
            str(args.rom),
            "--max-diff",
            str(args.max_diff),
            "--cluster-span",
            hex(args.cluster_span),
            "--top",
            "400",
        ],
        stdout_path=shape_txt,
    )

    run(
        [
            py,
            str(tool_dir / "correlate_g1_evidence.py"),
            str(shape_txt),
            str(trace_txt),
            "--near",
            hex(args.near),
            "--top",
            str(args.top),
        ],
        stdout_path=corr_txt,
    )

    ranked, pointers, dma, anchor_refs = rank_evidence(
        shape_txt,
        trace_txt,
        args.near,
    )

    top_rows = []
    for rank, item in enumerate(ranked[: args.top], 1):
        score, cluster, direct, near_ptrs, nearest = item
        top_rows.append(
            {
                "rank": rank,
                "score": score,
                "span_start": f"0x{cluster.start:06X}",
                "span_end": f"0x{cluster.end:06X}",
                "chars": cluster.chars,
                "unique_chars": cluster.unique_chars,
                "best_similarity": cluster.best,
                "coverage": cluster.coverage,
                "modes": cluster.modes,
                "direct_pointer_hits": len(direct),
                "near_pointer_hits": len(near_ptrs),
                "nearest_pointer_distance": f"0x{nearest:X}",
                "strong_reverse_priority": bool(
                    direct and cluster.unique_chars >= 2
                ),
            }
        )

    strong = [
        row
        for row in top_rows
        if row["strong_reverse_priority"]
    ]

    summary = {
        "mode": "READ_ONLY",
        "runtime_claim": False,
        "asset_identity_claim": False,
        "targets": TARGETS,
        "shape_clusters_ranked": len(ranked),
        "pointer_targets": len(pointers),
        "dma_sites": len(dma),
        "anchor_refs": len(anchor_refs),
        "strong_candidates_in_top": len(strong),
        "top_candidates": top_rows,
        "do_not_patch": "0x286B4..0x287FC descriptor/debug prose",
        "reports": {
            "render_path": str(trace_txt),
            "render_path_csv": str(trace_csv),
            "shape_probe": str(shape_txt),
            "correlation": str(corr_txt),
        },
        "next_gate": (
            "for any strong candidate, prove screen setup -> pointer/DMA path "
            "-> decoded source asset -> visible G1 label before writing ROM"
        ),
    }

    summary_json.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print("G1 GRAPHICS REVERSE PIPELINE")
    print("clean_rom_contract=PASS")
    print("mode=READ_ONLY")
    print(f"shape_clusters={len(ranked)}")
    print(f"pointer_targets={len(pointers)}")
    print(f"dma_sites={len(dma)}")
    print(f"strong_candidates_in_top={len(strong)}")
    print(f"summary={summary_json}")
    print("do_not_patch=0x286B4..0x287FC")
    print("asset_identity_claim=NO")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
