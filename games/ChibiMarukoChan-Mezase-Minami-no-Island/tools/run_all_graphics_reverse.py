#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from rom_common import require_clean_rom


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Run all Chibi graphics reverse pipelines G0 through G3"
    )
    ap.add_argument("rom", type=Path)
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("reports/generated/graphics_master"),
    )
    ap.add_argument("--no-render", action="store_true")
    args = ap.parse_args()

    require_clean_rom(args.rom)

    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    tool_dir = Path(__file__).resolve().parent
    py = sys.executable

    g0_out = out / "g0"
    g1_out = out / "g1"
    g23_out = out / "g2_g3"

    g0_cmd = [
        py,
        str(tool_dir / "run_g0_title_reverse_pipeline.py"),
        str(args.rom),
        "--out",
        str(g0_out),
    ]
    if args.no_render:
        g0_cmd.append("--no-render")
    run(g0_cmd)

    run(
        [
            py,
            str(tool_dir / "run_g1_graphics_reverse_pipeline.py"),
            str(args.rom),
            "--out",
            str(g1_out),
        ]
    )

    run(
        [
            py,
            str(tool_dir / "run_g2_g3_graphics_reverse_pipeline.py"),
            str(args.rom),
            "--out",
            str(g23_out),
        ]
    )

    g0 = load_json(g0_out / "g0_pipeline_summary.json")
    g1 = load_json(g1_out / "g1_pipeline_summary.json")
    g23 = load_json(g23_out / "g2_g3_pipeline_summary.json")
    g2 = load_json(g23_out / "g2_pipeline_summary.json")
    g3 = load_json(g23_out / "g3_pipeline_summary.json")

    summary = {
        "mode": "READ_ONLY",
        "runtime_claim": False,
        "asset_identity_claim": False,
        "batches": {
            "g0": {
                "title": "Chibi Maruko-chan / Tiến tới đảo phương Nam!!",
                "localization_credit": "Việt hóa bởi VôtriValley",
                "boot_windows": g0.get("boot_windows"),
                "dma_transfers": g0.get("dma_transfers"),
                "direct_rom_pngs": len(g0.get("direct_rom_rendered", [])),
                "wram_dma_sources": len(g0.get("wram_dma_sources", [])),
                "summary": str(g0_out / "g0_pipeline_summary.json"),
            },
            "g1": {
                "targets": g1.get("targets"),
                "shape_clusters": g1.get("shape_clusters_ranked"),
                "strong_candidates_in_top": g1.get(
                    "strong_candidates_in_top"
                ),
                "summary": str(g1_out / "g1_pipeline_summary.json"),
            },
            "g2": {
                "targets": g2.get("targets"),
                "shape_clusters": g2.get("shape_clusters_ranked"),
                "strong_candidates_in_top": g2.get(
                    "strong_candidates_in_top"
                ),
                "summary": str(g23_out / "g2_pipeline_summary.json"),
            },
            "g3": {
                "targets": g3.get("targets"),
                "shape_clusters": g3.get("shape_clusters_ranked"),
                "strong_candidates_in_top": g3.get(
                    "strong_candidates_in_top"
                ),
                "summary": str(g23_out / "g3_pipeline_summary.json"),
            },
        },
        "do_not_patch": "0x286B4..0x287FC descriptor/debug prose",
        "proof_gate": (
            "screen setup -> pointer/DMA/staging path -> decoded asset identity "
            "-> bounded patch span -> guarded ROM write -> runtime screenshot"
        ),
        "next": (
            "inspect strongest G0-G3 candidates; promote only candidates with "
            "both execution-path evidence and recognizable decoded retail asset"
        ),
    }

    summary_path = out / "graphics_master_summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print("CHIBI GRAPHICS MASTER REVERSE G0-G3")
    print("clean_rom_contract=PASS")
    print("mode=READ_ONLY")
    print(
        f"g0_direct_pngs={summary['batches']['g0']['direct_rom_pngs']} "
        f"g0_wram_sources={summary['batches']['g0']['wram_dma_sources']}"
    )
    for batch in ("g1", "g2", "g3"):
        info = summary["batches"][batch]
        print(
            f"{batch}_clusters={info['shape_clusters']} "
            f"{batch}_strong_top={info['strong_candidates_in_top']}"
        )
    print(f"summary={summary_path}")
    print("asset_identity_claim=NO")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
