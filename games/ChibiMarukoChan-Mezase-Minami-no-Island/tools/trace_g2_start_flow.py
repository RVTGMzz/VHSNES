#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from decompress_chibi_resource import cpu_to_file
from rom_common import require_clean_rom

ANCHORS = {
    "sequence_A1_handler": 0x80E131,
    "sequence_A1_stage": 0x80E169,
    "g2_entry": 0x888139,
    "school_front_dispatch": 0x88CB4E,
}

RESOURCE_INTERPRETER = 0x80E255
WORKER_INIT = 0x81D10D
DESCRIPTOR_DEMO_START_FILE = 0x286EA
REJECTED_GFX_CANDIDATE = 0x9ACB34


def file_to_cpu(off: int) -> int:
    if not 0 <= off < 0x200000:
        raise ValueError(f"file offset outside ROM: 0x{off:X}")
    bank, within = divmod(off, 0x8000)
    return ((0x80 | bank) << 16) | (0x8000 + within)


def iter_hits(data: bytes | bytearray, needle: bytes, start: int, end: int):
    pos = max(0, start)
    end = min(len(data), end)
    while True:
        pos = data.find(needle, pos, end)
        if pos < 0:
            return
        yield pos
        pos += 1


def control_flow(data: bytes | bytearray, start: int, end: int) -> list[dict]:
    rows: list[dict] = []
    start = max(0, start)
    end = min(len(data), end)
    for off in range(start, end):
        op = data[off]
        if op in (0x22, 0x5C) and off + 3 < end:
            cpu = data[off + 1] | (data[off + 2] << 8) | (data[off + 3] << 16)
            try:
                target_file = cpu_to_file(cpu)
            except ValueError:
                target_file = None
            rows.append({
                "source_file": off,
                "source_cpu": file_to_cpu(off),
                "op": "JSL" if op == 0x22 else "JML",
                "target_cpu": cpu,
                "target_file": target_file,
            })
        elif op in (0x20, 0x4C) and off + 2 < end:
            addr = data[off + 1] | (data[off + 2] << 8)
            source_bank = (file_to_cpu(off) >> 16) & 0xFF
            cpu = (source_bank << 16) | addr
            try:
                target_file = cpu_to_file(cpu)
            except ValueError:
                target_file = None
            rows.append({
                "source_file": off,
                "source_cpu": file_to_cpu(off),
                "op": "JSR" if op == 0x20 else "JMP",
                "target_cpu": cpu,
                "target_file": target_file,
            })
    return rows


def resource_calls(data: bytes | bytearray, start: int, end: int) -> list[dict]:
    """Find the proven LDX #script ; JSL $80:E255 call shape."""
    rows: list[dict] = []
    pat_tail = bytes((0x22, 0x55, 0xE2, 0x80))
    for off in range(max(0, start), min(len(data) - 7, end)):
        if data[off] != 0xA2:
            continue
        if bytes(data[off + 3:off + 7]) != pat_tail:
            continue
        ptr = data[off + 1] | (data[off + 2] << 8)
        script_cpu = 0x820000 | ptr
        try:
            script_file = cpu_to_file(script_cpu)
        except ValueError:
            script_file = None
        rows.append({
            "source_file": off,
            "source_cpu": file_to_cpu(off),
            "script_cpu": script_cpu,
            "script_file": script_file,
        })
    return rows


def exact_long_calls(data: bytes | bytearray, target_cpu: int, start: int, end: int) -> list[dict]:
    needle = bytes((0x22, target_cpu & 0xFF, (target_cpu >> 8) & 0xFF, (target_cpu >> 16) & 0xFF))
    return [
        {"source_file": off, "source_cpu": file_to_cpu(off), "target_cpu": target_cpu}
        for off in iter_hits(data, needle, start, end)
    ]


def hex_window(data: bytes | bytearray, center: int, radius: int) -> str:
    a = max(0, center - radius)
    b = min(len(data), center + radius)
    return bytes(data[a:b]).hex(" ").upper()


def analyze_anchor(data: bytes | bytearray, name: str, cpu: int, radius: int) -> dict:
    off = cpu_to_file(cpu)
    start = max(0, off - radius)
    end = min(len(data), off + radius)
    flows = control_flow(data, start, end)
    resources = resource_calls(data, start, end)
    worker_calls = exact_long_calls(data, WORKER_INIT, start, end)
    interp_calls = exact_long_calls(data, RESOURCE_INTERPRETER, start, end)
    return {
        "name": name,
        "cpu": f"0x{cpu:06X}",
        "file": f"0x{off:06X}",
        "window_start": f"0x{start:06X}",
        "window_end": f"0x{end:06X}",
        "hex": hex_window(data, off, min(radius, 96)),
        "control_flow": [
            {
                "source_file": f"0x{r['source_file']:06X}",
                "source_cpu": f"0x{r['source_cpu']:06X}",
                "op": r["op"],
                "target_cpu": f"0x{r['target_cpu']:06X}",
                "target_file": None if r["target_file"] is None else f"0x{r['target_file']:06X}",
            }
            for r in flows
        ],
        "resource_calls": [
            {
                "source_file": f"0x{r['source_file']:06X}",
                "source_cpu": f"0x{r['source_cpu']:06X}",
                "script_cpu": f"0x{r['script_cpu']:06X}",
                "script_file": None if r["script_file"] is None else f"0x{r['script_file']:06X}",
            }
            for r in resources
        ],
        "worker_calls": [
            {
                "source_file": f"0x{r['source_file']:06X}",
                "source_cpu": f"0x{r['source_cpu']:06X}",
            }
            for r in worker_calls
        ],
        "resource_interpreter_calls": [
            {
                "source_file": f"0x{r['source_file']:06X}",
                "source_cpu": f"0x{r['source_cpu']:06X}",
            }
            for r in interp_calls
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Targeted READ-ONLY G2 trace from Story Start A1 to school-front overlay"
    )
    ap.add_argument("rom", type=Path)
    ap.add_argument("--json", type=Path)
    ap.add_argument("--radius", type=lambda s: int(s, 0), default=0x180)
    args = ap.parse_args()

    data = require_clean_rom(args.rom)

    report = {
        "mode": "READ_ONLY_G2_TARGETED_TRACE",
        "runtime_claim": False,
        "asset_identity_claim": False,
        "target": {
            "jp": "今からやるよ",
            "vi": "Bắt đầu thôi!",
        },
        "known_chain": [
            "Start",
            "A1",
            "$80:E131",
            "$80:E169",
            "$88:8139",
            "$88:CB4E",
            "group 4",
            "school-front scene",
        ],
        "descriptor_only": f"0x{DESCRIPTOR_DEMO_START_FILE:06X}",
        "rejected_candidate": f"0x{REJECTED_GFX_CANDIDATE:06X}",
        "anchors": [
            analyze_anchor(data, name, cpu, args.radius)
            for name, cpu in ANCHORS.items()
        ],
        "next_gate": (
            "identify an executed resource/callback from the school-front window, "
            "decode its source, and visually tie it to 今からやるよ before any ROM write"
        ),
    }

    print("G2 TARGETED TRACE")
    print("clean_rom_contract=PASS")
    print("mode=READ_ONLY")
    print("known_chain=Start>A1>$80:E131>$80:E169>$88:8139>$88:CB4E>group4>school-front")
    for anchor in report["anchors"]:
        print(
            f"{anchor['name']}: cpu={anchor['cpu']} file={anchor['file']} "
            f"flow={len(anchor['control_flow'])} "
            f"resource_calls={len(anchor['resource_calls'])} "
            f"worker_calls={len(anchor['worker_calls'])}"
        )
        for r in anchor["resource_calls"]:
            print(
                f"  resource_call source={r['source_cpu']} "
                f"script={r['script_cpu']} file={r['script_file']}"
            )
    print("descriptor_0x286EA=EVIDENCE_ONLY")
    print("candidate_0x9ACB34=REJECTED")
    print("asset_identity_claim=NO")
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
