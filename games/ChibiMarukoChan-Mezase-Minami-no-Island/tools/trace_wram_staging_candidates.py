#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

WRAM_BANKS = {0x7E, 0x7F}
LONG_STORE_OPS = {
    0x8F: "STA_LONG",
    0x9F: "STA_LONG_X",
}
BLOCK_MOVE_OPS = {
    0x44: "MVP",
    0x54: "MVN",
}


@dataclass(frozen=True)
class WramSource:
    trigger_file: int
    channel: int
    cpu: int
    size: int | None
    confidence: str


@dataclass(frozen=True)
class Hit:
    kind: str
    off: int
    detail: str


def parse_cpu(s: str) -> int | None:
    s = s.strip().replace("$", "")
    if not s or s == "-":
        return None
    return int(s, 16)


def parse_hex(s: str) -> int | None:
    s = s.strip()
    if not s or s == "-":
        return None
    return int(s, 16)


def read_wram_sources(path: Path) -> list[WramSource]:
    out: list[WramSource] = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            cpu = parse_cpu(row["source_cpu"])
            if cpu is None or ((cpu >> 16) & 0xFF) not in WRAM_BANKS:
                continue
            out.append(
                WramSource(
                    int(row["trigger_file"], 16),
                    int(row["channel"]),
                    cpu,
                    parse_hex(row["size"]),
                    row["confidence"],
                )
            )
    return out


def iter_find(data: bytes | bytearray, needle: bytes):
    pos = 0
    while True:
        pos = data.find(needle, pos)
        if pos < 0:
            return
        yield pos
        pos += 1


def hits_for_source(
    data: bytes | bytearray,
    source: WramSource,
) -> list[Hit]:
    out: list[Hit] = []
    bank = (source.cpu >> 16) & 0xFF
    addr = source.cpu & 0xFFFF

    raw = bytes((addr & 0xFF, (addr >> 8) & 0xFF, bank))
    for off in iter_find(data, raw):
        out.append(Hit("literal24", off, f"${source.cpu:06X}"))

    for off in range(0, len(data) - 3):
        op = data[off]

        if op in LONG_STORE_OPS:
            cpu = (
                data[off + 1]
                | (data[off + 2] << 8)
                | (data[off + 3] << 16)
            )
            if ((cpu >> 16) & 0xFF) in WRAM_BANKS:
                inside = False
                if source.size:
                    start = source.cpu
                    end = (source.cpu + source.size) & 0xFFFFFF
                    inside = (
                        start <= cpu < end
                        if end >= start
                        else cpu >= start or cpu < end
                    )

                if cpu == source.cpu or inside:
                    out.append(
                        Hit(
                            "long_store",
                            off,
                            f"{LONG_STORE_OPS[op]} -> ${cpu:06X}",
                        )
                    )

        if op in BLOCK_MOVE_OPS:
            bank_a = data[off + 1]
            bank_b = data[off + 2]
            if bank in (bank_a, bank_b):
                out.append(
                    Hit(
                        "block_move",
                        off,
                        f"{BLOCK_MOVE_OPS[op]} banks=${bank_a:02X},${bank_b:02X}",
                    )
                )

    unique = {
        (hit.kind, hit.off, hit.detail): hit
        for hit in out
    }
    return sorted(
        unique.values(),
        key=lambda hit: (hit.off, hit.kind, hit.detail),
    )


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Trace candidates that may populate WRAM used as a DMA source"
    )
    ap.add_argument("rom", type=Path)
    ap.add_argument("dma_csv", type=Path)
    ap.add_argument("--top", type=int, default=160)
    args = ap.parse_args()

    from rom_common import require_clean_rom

    data = require_clean_rom(args.rom)
    sources = read_wram_sources(args.dma_csv)

    print("CHIBI MARUKO WRAM STAGING TRACE")
    print("mode=READ_ONLY")
    print("clean_rom_contract=PASS")
    print("runtime_claim=NO")
    print(f"wram_dma_sources={len(sources)}")

    for index, source in enumerate(sources, 1):
        size = f"0x{source.size:X}" if source.size is not None else "-"
        print(
            f"[{index}] trigger=0x{source.trigger_file:06X} "
            f"ch={source.channel} source=${source.cpu:06X} "
            f"size={size} conf={source.confidence}"
        )

        hits = hits_for_source(data, source)
        print(f"  staging_hits={len(hits)}")
        for hit in hits[: args.top]:
            print(
                f"  {hit.kind:12s} @0x{hit.off:06X} "
                f"{hit.detail}"
            )

    print(
        "interpretation=literal/store/block-move hits are "
        "staging/decompressor candidates only"
    )
    print(
        "next=inspect candidate routine reachability and prove that it fills "
        "the WRAM span before title DMA"
    )
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
