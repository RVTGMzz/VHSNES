#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Window:
    rank: int
    score: int
    file: int
    depth: int


@dataclass(frozen=True)
class Transfer:
    trigger: int
    channel: int
    confidence: str
    source_file: int | None
    size: int | None
    bbad: int | None
    dmap: int | None


def parse_hex(s: str) -> int | None:
    s = s.strip()
    if not s or s == "-":
        return None
    return int(s, 16)


def read_boot(path: Path) -> list[Window]:
    out: list[Window] = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("type") != "window":
                continue
            out.append(
                Window(
                    int(row["rank"]),
                    int(row["score"]),
                    int(row["file"], 16),
                    int(row["depth"]),
                )
            )
    if not out:
        raise RuntimeError("no boot windows parsed")
    return out


def read_dma(path: Path) -> list[Transfer]:
    out: list[Transfer] = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            out.append(
                Transfer(
                    int(row["trigger_file"], 16),
                    int(row["channel"]),
                    row["confidence"],
                    parse_hex(row["source_file"]),
                    parse_hex(row["size"]),
                    parse_hex(row["bbad"]),
                    parse_hex(row["dmap"]),
                )
            )
    if not out:
        raise RuntimeError("no DMA transfers parsed")
    return out


def nearest_window(
    trigger: int,
    windows: list[Window],
    radius: int,
) -> tuple[Window | None, int]:
    best = None
    dist = 1 << 30
    for w in windows:
        d = abs(trigger - w.file)
        if d < dist:
            best = w
            dist = d
    if dist > radius:
        return None, dist
    return best, dist


def tile_hypotheses(size: int | None) -> list[tuple[str, int]]:
    out: list[tuple[str, int]] = []
    if not size:
        return out
    if size % 16 == 0 and size // 16 > 0:
        out.append(("2bpp", size // 16))
    if size % 32 == 0 and size // 32 > 0:
        out.append(("4bpp", size // 32))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Correlate G0 boot windows with reconstructed DMA source candidates"
    )
    ap.add_argument("boot_csv", type=Path)
    ap.add_argument("dma_csv", type=Path)
    ap.add_argument("--radius", type=lambda s: int(s, 0), default=0x300)
    ap.add_argument("--top", type=int, default=40)
    ap.add_argument("--rom-name", default="clean.sfc")
    args = ap.parse_args()

    windows = read_boot(args.boot_csv)
    transfers = read_dma(args.dma_csv)

    ranked = []
    for transfer in transfers:
        window, dist = nearest_window(transfer.trigger, windows, args.radius)
        score = 0

        if window:
            score += window.score * 100 - min(dist, 0xFFFF)

        score += {
            "high": 5000,
            "medium": 2000,
            "low": 0,
        }.get(transfer.confidence, 0)

        if transfer.bbad == 0x18:
            score += 4000
        elif transfer.bbad == 0x19:
            score += 2500

        if transfer.source_file is not None:
            score += 1500

        hypotheses = tile_hypotheses(transfer.size)
        if hypotheses:
            score += 1000

        if transfer.size and 0x20 <= transfer.size <= 0x8000:
            score += 500

        ranked.append((score, transfer, window, dist, hypotheses))

    ranked.sort(key=lambda x: (-x[0], x[1].trigger, x[1].channel))

    print("CHIBI MARUKO G0 BOOT/DMA CORRELATION")
    print("mode=READ_ONLY_REPORT_CORRELATION")
    print("runtime_claim=NO")
    print(
        f"boot_windows={len(windows)} dma_transfers={len(transfers)} "
        f"radius=0x{args.radius:X}"
    )

    for rank, (score, transfer, window, dist, hypotheses) in enumerate(
        ranked[: args.top],
        1,
    ):
        window_file = f"0x{window.file:06X}" if window else "-"
        window_rank = window.rank if window else "-"
        window_score = window.score if window else "-"
        source_file = (
            f"0x{transfer.source_file:06X}"
            if transfer.source_file is not None
            else "-"
        )
        size = f"0x{transfer.size:X}" if transfer.size is not None else "-"
        bbad = f"0x{transfer.bbad:02X}" if transfer.bbad is not None else "-"
        dmap = f"0x{transfer.dmap:02X}" if transfer.dmap is not None else "-"

        print(
            f"#{rank:02d} score={score} "
            f"trigger=0x{transfer.trigger:06X} ch={transfer.channel} "
            f"conf={transfer.confidence} source={source_file} size={size} "
            f"BBAD={bbad} DMAP={dmap} "
            f"boot_rank={window_rank} boot_score={window_score} "
            f"boot={window_file} dist=0x{dist:X}"
        )

        for mode, count in hypotheses:
            bpp = 2 if mode == "2bpp" else 4
            print(f"    hypothesis={mode} tiles={count}")
            if transfer.source_file is not None:
                print(
                    "    render: "
                    f'python tools/render_snes_graphics_probe.py "{args.rom_name}" '
                    f"g0_{rank:02d}_{mode}.png "
                    f"--bpp {bpp} "
                    f"--gfx-offset 0x{transfer.source_file:X} "
                    f"--scale 3 --mask "
                    f"tiles --count {count} --cols 16"
                )

    print(
        "priority_rule=boot-near + VRAM BBAD 0x18/0x19 + "
        "reconstructed ROM source + tile-aligned transfer size"
    )
    print(
        "proof_rule=ranking is triage only; decoded artwork must reproduce "
        "title and be reached by title-screen setup"
    )
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
