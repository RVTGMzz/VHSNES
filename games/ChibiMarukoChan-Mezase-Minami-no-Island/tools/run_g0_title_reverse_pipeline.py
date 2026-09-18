#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

from rom_common import require_clean_rom


def run(cmd: list[str], *, stdout_path: Path | None = None) -> None:
    if stdout_path:
        stdout_path.parent.mkdir(parents=True, exist_ok=True)
        with stdout_path.open("w", encoding="utf-8") as f:
            subprocess.run(cmd, check=True, stdout=f, stderr=subprocess.STDOUT)
    else:
        subprocess.run(cmd, check=True)


def parse_int(text: str) -> int | None:
    text = text.strip().replace("$", "")
    if not text or text == "-":
        return None
    return int(text, 16)


def read_boot_windows(path: Path) -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("type") != "window":
                continue
            rows.append(
                {
                    "rank": int(row["rank"]),
                    "score": int(row["score"]),
                    "file": int(row["file"], 16),
                    "depth": int(row["depth"]),
                }
            )
    return rows


def read_transfers(path: Path) -> list[dict[str, int | str | None]]:
    rows: list[dict[str, int | str | None]] = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            source_cpu = parse_int(row["source_cpu"])
            rows.append(
                {
                    "trigger": int(row["trigger_file"], 16),
                    "channel": int(row["channel"]),
                    "confidence": row["confidence"],
                    "source_cpu": source_cpu,
                    "source_file": parse_int(row["source_file"]),
                    "size": parse_int(row["size"]),
                    "bbad": parse_int(row["bbad"]),
                    "dmap": parse_int(row["dmap"]),
                }
            )
    return rows


def nearest_window(trigger: int, windows: list[dict[str, int]], radius: int):
    best = None
    best_dist = 1 << 30
    for w in windows:
        d = abs(trigger - w["file"])
        if d < best_dist:
            best = w
            best_dist = d
    if best_dist > radius:
        return None, best_dist
    return best, best_dist


def hypotheses(size: int | None) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    if not size:
        return out
    if size % 16 == 0:
        out.append((2, size // 16))
    if size % 32 == 0:
        out.append((4, size // 32))
    return [(bpp, count) for bpp, count in out if count > 0]


def candidate_score(
    transfer: dict[str, int | str | None],
    window: dict[str, int] | None,
    dist: int,
) -> int:
    score = 0
    if window:
        score += window["score"] * 100 - min(dist, 0xFFFF)
    score += {"high": 5000, "medium": 2000, "low": 0}.get(
        str(transfer["confidence"]), 0
    )
    if transfer["bbad"] == 0x18:
        score += 4000
    elif transfer["bbad"] == 0x19:
        score += 2500
    if transfer["source_file"] is not None:
        score += 1500
    if hypotheses(transfer["size"] if isinstance(transfer["size"], int) else None):
        score += 1000
    size = transfer["size"]
    if isinstance(size, int) and 0x20 <= size <= 0x8000:
        score += 500
    return score


def main() -> int:
    ap = argparse.ArgumentParser(
        description="One-command G0 title reverse pipeline for canonical Chibi ROM"
    )
    ap.add_argument("rom", type=Path)
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("reports/generated/g0_pipeline"),
    )
    ap.add_argument("--radius", type=lambda s: int(s, 0), default=0x180)
    ap.add_argument("--correlation-radius", type=lambda s: int(s, 0), default=0x300)
    ap.add_argument("--depth", type=int, default=3)
    ap.add_argument("--max-windows", type=int, default=192)
    ap.add_argument("--lookback", type=lambda s: int(s, 0), default=0x80)
    ap.add_argument("--render-top", type=int, default=8)
    ap.add_argument("--render-scale", type=int, default=3)
    ap.add_argument("--no-render", action="store_true")
    args = ap.parse_args()

    # Fail immediately before producing misleading partial reports.
    require_clean_rom(args.rom)

    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    tool_dir = Path(__file__).resolve().parent
    py = sys.executable

    boot_txt = out / "g0_title_boot_trace.txt"
    boot_csv = out / "g0_title_boot_trace.csv"
    dma_txt = out / "g0_dma_sources.txt"
    dma_csv = out / "g0_dma_sources.csv"
    corr_txt = out / "g0_boot_dma_correlation.txt"
    wram_txt = out / "g0_wram_staging_trace.txt"
    render_dir = out / "renders"
    render_dir.mkdir(parents=True, exist_ok=True)

    run(
        [
            py,
            str(tool_dir / "trace_g0_title_boot.py"),
            str(args.rom),
            "--radius",
            hex(args.radius),
            "--depth",
            str(args.depth),
            "--max-windows",
            str(args.max_windows),
            "--report",
            str(boot_txt),
            "--csv",
            str(boot_csv),
        ]
    )

    run(
        [
            py,
            str(tool_dir / "reconstruct_dma_sources.py"),
            str(args.rom),
            "--lookback",
            hex(args.lookback),
            "--sites-csv",
            str(boot_csv),
            "--report",
            str(dma_txt),
            "--csv",
            str(dma_csv),
        ]
    )

    run(
        [
            py,
            str(tool_dir / "correlate_g0_dma_sources.py"),
            str(boot_csv),
            str(dma_csv),
            "--radius",
            hex(args.correlation_radius),
            "--top",
            "80",
            "--rom-name",
            str(args.rom),
        ],
        stdout_path=corr_txt,
    )

    run(
        [
            py,
            str(tool_dir / "trace_wram_staging_candidates.py"),
            str(args.rom),
            str(dma_csv),
        ],
        stdout_path=wram_txt,
    )

    windows = read_boot_windows(boot_csv)
    transfers = read_transfers(dma_csv)

    ranked = []
    for transfer in transfers:
        window, dist = nearest_window(
            int(transfer["trigger"]),
            windows,
            args.correlation_radius,
        )
        score = candidate_score(transfer, window, dist)
        ranked.append((score, transfer, window, dist))
    ranked.sort(
        key=lambda item: (
            -item[0],
            int(item[1]["trigger"]),
            int(item[1]["channel"]),
        )
    )

    rendered: list[dict[str, object]] = []
    seen_render_keys: set[tuple[int, int, int]] = set()

    if not args.no_render:
        direct_rank = 0
        for score, transfer, window, dist in ranked:
            source = transfer["source_file"]
            size = transfer["size"]
            bbad = transfer["bbad"]
            if not isinstance(source, int) or not isinstance(size, int):
                continue
            if bbad not in (0x18, 0x19):
                continue

            hyps = hypotheses(size)
            if not hyps:
                continue

            direct_rank += 1
            if direct_rank > args.render_top:
                break

            for bpp, count in hyps:
                key = (source, size, bpp)
                if key in seen_render_keys:
                    continue
                seen_render_keys.add(key)

                output = render_dir / (
                    f"candidate_{direct_rank:02d}_"
                    f"src_{source:06X}_{bpp}bpp.png"
                )
                run(
                    [
                        py,
                        str(tool_dir / "render_snes_graphics_probe.py"),
                        str(args.rom),
                        str(output),
                        "--bpp",
                        str(bpp),
                        "--gfx-offset",
                        hex(source),
                        "--scale",
                        str(args.render_scale),
                        "--mask",
                        "tiles",
                        "--count",
                        str(count),
                        "--cols",
                        "16",
                    ]
                )
                rendered.append(
                    {
                        "rank": direct_rank,
                        "score": score,
                        "source_file": f"0x{source:06X}",
                        "size": f"0x{size:X}",
                        "bpp": bpp,
                        "tile_count": count,
                        "bbad": f"0x{int(bbad):02X}",
                        "trigger_file": f"0x{int(transfer['trigger']):06X}",
                        "boot_window": (
                            f"0x{window['file']:06X}" if window else None
                        ),
                        "distance": dist,
                        "png": str(output),
                    }
                )

    wram_sources = []
    for transfer in transfers:
        cpu = transfer["source_cpu"]
        if not isinstance(cpu, int):
            continue
        bank = (cpu >> 16) & 0xFF
        if bank not in (0x7E, 0x7F):
            continue
        wram_sources.append(
            {
                "trigger_file": f"0x{int(transfer['trigger']):06X}",
                "channel": transfer["channel"],
                "source_cpu": f"0x{cpu:06X}",
                "size": (
                    f"0x{int(transfer['size']):X}"
                    if isinstance(transfer["size"], int)
                    else None
                ),
                "confidence": transfer["confidence"],
            }
        )

    summary = {
        "mode": "READ_ONLY",
        "runtime_claim": False,
        "asset_identity_claim": False,
        "title_target": [
            "Chibi Maruko-chan",
            "Tiến tới đảo phương Nam!!",
            "Việt hóa bởi VôtriValley",
        ],
        "boot_windows": len(windows),
        "dma_transfers": len(transfers),
        "direct_rom_rendered": rendered,
        "wram_dma_sources": wram_sources,
        "reports": {
            "boot_text": str(boot_txt),
            "boot_csv": str(boot_csv),
            "dma_text": str(dma_txt),
            "dma_csv": str(dma_csv),
            "correlation": str(corr_txt),
            "wram_staging": str(wram_txt),
        },
        "next_gate": (
            "inspect rendered candidates; if one reproduces title artwork, "
            "prove exact tile/tilemap span and screen reachability before patch; "
            "otherwise follow WRAM staging/decompressor evidence"
        ),
    }
    summary_path = out / "g0_pipeline_summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print("G0 TITLE REVERSE PIPELINE")
    print("clean_rom_contract=PASS")
    print("mode=READ_ONLY")
    print(f"boot_windows={len(windows)}")
    print(f"dma_transfers={len(transfers)}")
    print(f"direct_rom_pngs={len(rendered)}")
    print(f"wram_dma_sources={len(wram_sources)}")
    print(f"summary={summary_path}")
    print("asset_identity_claim=NO")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
