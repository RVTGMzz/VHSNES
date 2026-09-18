#!/usr/bin/env python3
from __future__ import annotations

import tempfile
from pathlib import Path

from correlate_g0_dma_sources import tile_hypotheses
from reconstruct_dma_sources import reconstruct_before_trigger
from render_snes_graphics_probe import decode_tile, write_gray_png
from run_g0_title_reverse_pipeline import candidate_score, hypotheses
from trace_g0_title_boot import (
    Window,
    build_boot_windows,
    cpu_to_file,
    file_to_cpu,
    register_sites,
)
from trace_wram_staging_candidates import WramSource, hits_for_source


def check(name: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(name)
    print(f"{name}=PASS")


def test_lorom_mapping() -> None:
    check("reset_mapping", cpu_to_file(0x00FF90) == 0x7F90)
    check("reset_mirror_mapping", cpu_to_file(0x80FF90) == 0x7F90)
    check("file_cpu_roundtrip", cpu_to_file(file_to_cpu(0x29000)) == 0x29000)


def test_boot_expansion_and_ppu() -> None:
    data = bytearray(0x30000)
    reset = 0x7F90
    target = 0x29000
    target_cpu = file_to_cpu(target)

    data[reset:reset + 4] = bytes(
        (
            0x22,
            target_cpu & 0xFF,
            (target_cpu >> 8) & 0xFF,
            (target_cpu >> 16) & 0xFF,
        )
    )
    data[target:target + 3] = bytes((0x8D, 0x16, 0x21))  # STA $2116

    windows = build_boot_windows(
        data,
        reset,
        radius=0x40,
        max_depth=2,
        max_windows=16,
    )
    check("boot_call_expansion", any(w.center == target for w in windows))

    sites = register_sites(data, [Window(target, 1, reset, "JSL")], 0x40)
    check(
        "ppu_vram_detection",
        any(s.off == target and s.reg == 0x2116 for s in sites),
    )


def test_dma_reconstruction() -> None:
    data = bytearray(0x30000)
    p = 0x29200

    # M=16, A1T=$9000 -> $4302/$4303
    seq = [
        0xC2, 0x20,
        0xA9, 0x00, 0x90,
        0x8D, 0x02, 0x43,
        # M=8, A1B=$85
        0xE2, 0x20,
        0xA9, 0x85,
        0x8D, 0x04, 0x43,
        # M=16, DAS=$0200
        0xC2, 0x20,
        0xA9, 0x00, 0x02,
        0x8D, 0x05, 0x43,
        # M=8, BBAD=$18
        0xE2, 0x20,
        0xA9, 0x18,
        0x8D, 0x01, 0x43,
        # DMAP=$01
        0xA9, 0x01,
        0x8D, 0x00, 0x43,
        # MDMAEN channel 0
        0xA9, 0x01,
        0x8D, 0x0B, 0x42,
    ]
    data[p:p + len(seq)] = bytes(seq)
    trigger = p + len(seq) - 3

    transfers = reconstruct_before_trigger(data, trigger, lookback=0x80)
    t0 = next(t for t in transfers if t.channel == 0)
    check("dma_source_cpu", t0.source_cpu == 0x859000)
    check("dma_source_file", t0.source_file == 0x29000)
    check("dma_size", t0.size == 0x0200)
    check("dma_bbad", t0.bbad == 0x18)


def test_tile_hypotheses_and_scoring() -> None:
    check(
        "correlator_tile_hypotheses",
        tile_hypotheses(0x200) == [("2bpp", 32), ("4bpp", 16)],
    )
    check(
        "pipeline_tile_hypotheses",
        hypotheses(0x200) == [(2, 32), (4, 16)],
    )

    transfer = {
        "confidence": "high",
        "bbad": 0x18,
        "source_file": 0x29000,
        "size": 0x200,
    }
    window = {"score": 30, "file": 0x29100}
    good = candidate_score(transfer, window, 0x20)
    weak = candidate_score(
        {
            "confidence": "low",
            "bbad": None,
            "source_file": None,
            "size": None,
        },
        None,
        0x1000,
    )
    check("pipeline_candidate_ranking", good > weak)


def test_graphics_decode_and_png() -> None:
    two = bytearray(16)
    two[0] = 0x80
    t2 = decode_tile(two, 0, 2)
    check("decode_2bpp", t2[0][0] == 1 and t2[0][1] == 0)

    four = bytearray(32)
    four[16] = 0x80
    t4 = decode_tile(four, 0, 4)
    check("decode_4bpp", t4[0][0] == 4 and t4[0][1] == 0)

    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "probe.png"
        canvas = [bytearray([255, 0]), bytearray([0, 255])]
        write_gray_png(path, canvas)
        check("png_writer", path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))


def test_wram_staging() -> None:
    data = bytearray(0x200)
    source = WramSource(
        trigger_file=0x100,
        channel=0,
        cpu=0x7E9000,
        size=0x20,
        confidence="low",
    )
    data[0x20:0x23] = bytes((0x00, 0x90, 0x7E))
    data[0x40:0x44] = bytes((0x8F, 0x00, 0x90, 0x7E))
    data[0x60:0x63] = bytes((0x54, 0x80, 0x7E))

    hits = hits_for_source(data, source)
    kinds = {h.kind for h in hits}
    check("wram_literal_hit", "literal24" in kinds)
    check("wram_long_store_hit", "long_store" in kinds)
    check("wram_block_move_hit", "block_move" in kinds)


def main() -> int:
    print("CHIBI G0 REVERSE TOOLS STATIC SELFTEST")
    test_lorom_mapping()
    test_boot_expansion_and_ppu()
    test_dma_reconstruction()
    test_tile_hypotheses_and_scoring()
    test_graphics_decode_and_png()
    test_wram_staging()
    print("selftest=PASS")
    print("commercial_rom_required=NO")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
