#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from rom_common import require_clean_rom
from decompress_chibi_resource import cpu_to_file
from render_chibi_resource_package import parse_type0_package

MENU_TEXT_PTR = 0x858814
MENU_INIT = 0x848038
MENU_ROUTE_TABLE = 0x80D60B
STORY_SEQUENCE = 0x00A0
SEQUENCE_DISPATCH = 0x80D184
STORY_HANDLER = 0x80D328
STORY_MODULE = 0x88F5F1
G1_MODULE_INIT = 0x85E959
G1_STATE_TABLE = 0x85E975
G1_INPUT = 0x85EAB8
G1_RESULT = 0x85EB84

G1_TYPE0_PACKAGES = (0x82AF23, 0x82AA30, 0x82AA50)
G1_FF_SCRIPT = 0x82B364
G1_NEIGHBOR_FF_SCRIPTS = (
    0x82B36B,
    0x82B372,
    0x82B379,
    0x82B380,
    0x82B387,
    0x82B38E,
)
G1_NEIGHBOR_TYPE0 = 0x82B395


def read_u16(rom: bytes | bytearray, cpu: int) -> int:
    o = cpu_to_file(cpu)
    return rom[o] | (rom[o + 1] << 8)


def require_bytes(
    rom: bytes | bytearray,
    cpu: int,
    expected: bytes,
    label: str,
) -> None:
    o = cpu_to_file(cpu)
    actual = bytes(rom[o:o + len(expected)])
    if actual != expected:
        raise RuntimeError(
            f"{label} signature mismatch at ${cpu:06X}: "
            f"{actual.hex()} != {expected.hex()}"
        )


def parse_single_ff_script(rom: bytes | bytearray, cpu: int) -> dict:
    """Parse one standalone type-FF script.

    Proven retail shape:
        FF + source24 + parameter16 + 80

    The trailing 0x80 terminates this script. Neighboring bytes at B36B,
    B372, ... are separate script entries and must not be concatenated.
    """
    p = cpu_to_file(cpu)
    if p + 7 > len(rom):
        raise RuntimeError("truncated type-FF script")
    if rom[p] != 0xFF or rom[p + 6] != 0x80:
        raise RuntimeError(
            f"type-FF signature mismatch at ${cpu:06X}"
        )
    src = rom[p + 1] | (rom[p + 2] << 8) | (rom[p + 3] << 16)
    param = rom[p + 4] | (rom[p + 5] << 8)
    return {
        "script_cpu": f"0x{cpu:06X}",
        "source_cpu": f"0x{src:06X}",
        "source_file": f"0x{cpu_to_file(src):06X}",
        "parameter": f"0x{param:04X}",
        "terminator": "0x80",
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Verify the retail Story -> G1 Start/Password execution path"
    )
    ap.add_argument("rom", type=Path)
    ap.add_argument("--json", type=Path)
    args = ap.parse_args()

    rom = require_clean_rom(args.rom)

    # Main menu init: LDY #$8814 ; JSL $85:805C.
    require_bytes(
        rom,
        0x84803E,
        bytes.fromhex("A0 14 88 22 5C 80 85"),
        "main-menu text init",
    )

    # Story is menu selection index 0, so entry 0 of the route table is A0.
    story_route = read_u16(rom, MENU_ROUTE_TABLE)
    if story_route != STORY_SEQUENCE:
        raise RuntimeError(
            f"Story route mismatch: 0x{story_route:04X} != 0x{STORY_SEQUENCE:04X}"
        )

    # $80:D717 starts with STA $70. Story route therefore becomes $70=A0.
    require_bytes(
        rom,
        0x80D717,
        bytes.fromhex("85 70"),
        "sequence setter",
    )

    story_handler = read_u16(
        rom,
        SEQUENCE_DISPATCH + STORY_SEQUENCE * 2,
    )
    if story_handler != (STORY_HANDLER & 0xFFFF):
        raise RuntimeError(
            f"Story sequence handler mismatch: 0x{story_handler:04X}"
        )

    # Handler A0 calls the G1 module.
    require_bytes(
        rom,
        STORY_HANDLER,
        bytes.fromhex("22 F1 F5 88"),
        "Story G1 module call",
    )

    # G1 state table.
    state_ptrs = [
        read_u16(rom, G1_STATE_TABLE + i * 2)
        for i in range(5)
    ]
    expected_states = [0xE97F, 0xEA09, 0xEAB8, 0xEB84, 0xEB8C]
    if state_ptrs != expected_states:
        raise RuntimeError(
            f"G1 state table mismatch: {state_ptrs!r}"
        )

    # Input state toggles $1404 with EOR #1.
    require_bytes(
        rom,
        0x85EAE9,
        bytes.fromhex("AD 04 14 49 01 00 8D 04 14"),
        "G1 selection toggle",
    )

    # Selection Y positions.
    y0 = read_u16(rom, 0x85EB02)
    y1 = read_u16(rom, 0x85EB04)
    if (y0, y1) != (0x00A8, 0x00B8):
        raise RuntimeError(
            f"G1 selection positions mismatch: {(hex(y0), hex(y1))}"
        )

    # Result state returns selection + 1 in $1406.
    require_bytes(
        rom,
        G1_RESULT,
        bytes.fromhex("AD 04 14 1A 8D 06 14 6B"),
        "G1 selection result",
    )
    require_bytes(
        rom,
        0x85EB8C,
        bytes.fromhex("A9 03 00 8D 06 14 6B"),
        "G1 alternate result",
    )

    # Initializer directly loads AF23 / AA30 / AA50 / B364.
    init_off = cpu_to_file(0x85E97F)
    init_blob = bytes(rom[init_off:init_off + 0x24])
    for ptr in (0xAF23, 0xAA30, 0xAA50, 0xB364):
        needle = bytes((0xA2, ptr & 0xFF, (ptr >> 8) & 0xFF, 0x22, 0x55, 0xE2, 0x80))
        if needle not in init_blob:
            raise RuntimeError(f"G1 initializer missing script ${ptr:04X}")

    packages = {}
    for cpu in G1_TYPE0_PACKAGES:
        _typ, flags, records, _vram = parse_type0_package(rom, cpu)
        packages[f"0x{cpu:06X}"] = {
            "flags": f"0x{flags:02X}",
            "records": [
                {
                    "vram_word": f"0x{r.vram_word:04X}",
                    "source_cpu": f"0x{r.source_cpu:06X}",
                    "source_file": f"0x{r.source_file:06X}",
                    "compressed_span": f"0x{r.compressed_span:X}",
                    "postprocess": r.postprocess,
                    "output_size": f"0x{r.output_size:X}",
                }
                for r in records
            ],
        }

    ff_script = parse_single_ff_script(rom, G1_FF_SCRIPT)
    neighbor_ff_scripts = [
        parse_single_ff_script(rom, cpu)
        for cpu in G1_NEIGHBOR_FF_SCRIPTS
    ]

    # B395 is a separate neighboring type-0 script. It is recorded only as
    # local script-bank context; this tool does NOT claim G1 executes it.
    _typ, neighbor_flags, neighbor_records, _vram = parse_type0_package(
        rom,
        G1_NEIGHBOR_TYPE0,
    )

    report = {
        "mode": "READ_ONLY_EXECUTION_PROOF",
        "main_menu": {
            "text_script_cpu": f"0x{MENU_TEXT_PTR:06X}",
            "story_selection_index": 0,
            "story_route_value": f"0x{story_route:04X}",
        },
        "story_sequence": {
            "sequence_id": f"0x{STORY_SEQUENCE:04X}",
            "handler_cpu": f"0x{STORY_HANDLER:06X}",
            "module_cpu": f"0x{STORY_MODULE:06X}",
        },
        "g1_module": {
            "initializer_cpu": f"0x{G1_MODULE_INIT:06X}",
            "state_table_cpu": f"0x{G1_STATE_TABLE:06X}",
            "states": [f"0x85{x:04X}" for x in state_ptrs],
            "selection_variable": "$1404",
            "selection_positions": [f"0x{y0:04X}", f"0x{y1:04X}"],
            "result_variable": "$1406",
            "result_mapping": {
                "0": 1,
                "1": 2,
                "alternate": 3,
            },
        },
        "type0_packages": packages,
        "g1_ff_script": ff_script,
        "neighbor_script_context": {
            "note": (
                "B36B..B38E and B395 are separate neighboring scripts; "
                "no G1 execution claim is made for them here."
            ),
            "ff_scripts": neighbor_ff_scripts,
            "type0_cpu": f"0x{G1_NEIGHBOR_TYPE0:06X}",
            "type0_flags": f"0x{neighbor_flags:02X}",
            "type0_records": [
                {
                    "vram_word": f"0x{r.vram_word:04X}",
                    "source_cpu": f"0x{r.source_cpu:06X}",
                    "output_size": f"0x{r.output_size:X}",
                }
                for r in neighbor_records
            ],
        },
        "claims": {
            "g1_screen_execution_path": "STATIC_PASS",
            "g1_stage_background_identity": "STATIC_PASS",
            "g1_selection_logic": "STATIC_PASS",
            "g1_visible_label_source": "UNPROVEN",
            "runtime_pass": False,
        },
    }

    print("clean_rom_contract=PASS")
    print("main_menu_story_route=PASS")
    print("story_sequence_A0=PASS")
    print("g1_module_call=PASS")
    print("g1_state_table=PASS")
    print("g1_selection_logic=PASS")
    print(f"type0_packages={len(packages)}")
    print("g1_type_ff_script=PASS")
    print(f"neighbor_ff_scripts={len(neighbor_ff_scripts)}")
    print(f"neighbor_type0=0x{G1_NEIGHBOR_TYPE0:06X}")
    print("g1_visible_label_source=UNPROVEN")
    print("runtime_claim=NO")

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"json={args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
