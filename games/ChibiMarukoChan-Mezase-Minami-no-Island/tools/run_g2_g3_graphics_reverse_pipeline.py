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
from scan_graphics_shape_targets import BATCHES


def run(cmd: list[str], *, stdout_path: Path | None = None) -> None:
    if stdout_path:
        stdout_path.parent.mkdir(parents=True, exist_ok=True)
        with stdout_path.open("w", encoding="utf-8") as f:
            subprocess.run(cmd, check=True, stdout=f, stderr=subprocess.STDOUT)
    else:
        subprocess.run(cmd, check=True)


def rank_batch(shape_report: Path, trace_report: Path, near: int):
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


def batch_summary(
    batch: str,
    ranked,
    pointers,
    dma,
    anchor_refs,
    top: int,
) -> dict:
    rows = []
    for rank, item in enumerate(ranked[:top], 1):
        score, cluster, direct, near_ptrs, nearest = item
        rows.append(
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

    return {
        "batch": batch,
        "targets": BATCHES[batch],
        "shape_clusters_ranked": len(ranked),
        "pointer_targets": len(pointers),
        "dma_sites": len(dma),
        "anchor_refs": len(anchor_refs),
        "strong_candidates_in_top": sum(
            1 for row in rows if row["strong_reverse_priority"]
        ),
        "top_candidates": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="One-command G2/G3 graphics reverse pipeline for canonical Chibi ROM"
    )
    ap.add_argument("rom", type=Path)
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("reports/generated/g2_g3_pipeline"),
    )
    ap.add_argument("--max-diff", type=int, default=14)
    ap.add_argument("--cluster-span", type=lambda s: int(s, 0), default=0x800)
    ap.add_argument("--near", type=lambda s: int(s, 0), default=0x400)
    ap.add_argument("--top", type=int, default=60)
    args = ap.parse_args()

    require_clean_rom(args.rom)

    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    tool_dir = Path(__file__).resolve().parent
    py = sys.executable

    trace_txt = out / "graphics_render_path_trace.txt"
    trace_csv = out / "graphics_render_path_trace.csv"

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

    combined = {
        "mode": "READ_ONLY",
        "runtime_claim": False,
        "asset_identity_claim": False,
        "do_not_patch": "0x286B4..0x287FC descriptor/debug prose",
        "trace_report": str(trace_txt),
        "trace_csv": str(trace_csv),
        "batches": {},
    }

    for batch in ("g2", "g3"):
        shape_txt = out / f"{batch}_shape_probe.txt"
        corr_txt = out / f"{batch}_evidence_correlation.txt"
        summary_json = out / f"{batch}_pipeline_summary.json"

        run(
            [
                py,
                str(tool_dir / "scan_graphics_shape_targets.py"),
                str(args.rom),
                "--batch",
                batch,
                "--max-diff",
                str(args.max_diff),
                "--cluster-span",
                hex(args.cluster_span),
                "--top",
                "500",
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

        ranked, pointers, dma, anchor_refs = rank_batch(
            shape_txt,
            trace_txt,
            args.near,
        )
        summary = batch_summary(
            batch,
            ranked,
            pointers,
            dma,
            anchor_refs,
            args.top,
        )
        summary["reports"] = {
            "shape_probe": str(shape_txt),
            "correlation": str(corr_txt),
        }
        summary["next_gate"] = (
            "for any strong candidate, prove the matching screen transition "
            "reaches its pointer/DMA path and decoded source reproduces the "
            "visible label before a ROM write"
        )
        summary_json.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        combined["batches"][batch] = {
            "summary": str(summary_json),
            "strong_candidates_in_top": summary[
                "strong_candidates_in_top"
            ],
            "shape_clusters_ranked": summary[
                "shape_clusters_ranked"
            ],
        }

    combined_json = out / "g2_g3_pipeline_summary.json"
    combined_json.write_text(
        json.dumps(combined, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print("G2/G3 GRAPHICS REVERSE PIPELINE")
    print("clean_rom_contract=PASS")
    print("mode=READ_ONLY")
    for batch in ("g2", "g3"):
        b = combined["batches"][batch]
        print(
            f"{batch}_clusters={b['shape_clusters_ranked']} "
            f"{batch}_strong_top={b['strong_candidates_in_top']}"
        )
    print(f"summary={combined_json}")
    print("do_not_patch=0x286B4..0x287FC")
    print("asset_identity_claim=NO")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
