#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from collections import deque
from pathlib import Path

from decompress_chibi_resource import cpu_to_file
from render_chibi_resource_package import (
    decode_tile,
    parse_type0_package,
    write_gray_png,
)
from rom_common import require_clean_rom
from trace_g2_start_flow import (
    ANCHORS,
    RESOURCE_INTERPRETER,
    WORKER_INIT,
    control_flow,
    file_to_cpu,
    resource_calls,
)

DEFAULT_CODE_BANKS = {0x80, 0x81, 0x85, 0x88}


def render_tile_sheet(
    vram: bytes | bytearray,
    *,
    start_word: int,
    byte_length: int,
    bpp: int,
    cols: int = 16,
    scale: int = 2,
) -> list[bytearray]:
    tile_bytes = 16 if bpp == 2 else 32
    if byte_length <= 0 or byte_length % tile_bytes:
        raise ValueError("tile sheet length is not aligned")
    count = byte_length // tile_bytes
    rows = max(1, math.ceil(count / cols))
    width = cols * 8 * scale
    height = rows * 8 * scale
    canvas = [bytearray([255] * width) for _ in range(height)]
    maxv = (1 << bpp) - 1
    base = start_word * 2

    for i in range(count):
        off = base + i * tile_bytes
        if off + tile_bytes > len(vram):
            break
        tile = decode_tile(vram, off, bpp)
        tx = i % cols
        ty = i // cols
        for y in range(8):
            for x in range(8):
                gray = 255 - round((tile[y][x] / maxv) * 255)
                px = (tx * 8 + x) * scale
                py = (ty * 8 + y) * scale
                for yy in range(scale):
                    row = canvas[py + yy]
                    for xx in range(scale):
                        row[px + xx] = gray
    return canvas


def crop_nonwhite(canvas: list[bytearray], margin: int = 4) -> list[bytearray]:
    xs: list[int] = []
    ys: list[int] = []
    for y, row in enumerate(canvas):
        for x, value in enumerate(row):
            if value < 250:
                xs.append(x)
                ys.append(y)
    if not xs:
        return canvas
    h = len(canvas)
    w = len(canvas[0])
    x0 = max(0, min(xs) - margin)
    x1 = min(w, max(xs) + margin + 1)
    y0 = max(0, min(ys) - margin)
    y1 = min(h, max(ys) + margin + 1)
    return [bytearray(row[x0:x1]) for row in canvas[y0:y1]]


def parse_single_ff_script(data: bytes | bytearray, script_cpu: int) -> dict:
    off = cpu_to_file(script_cpu)
    if off + 7 > len(data):
        raise ValueError("truncated FF resource script")
    if data[off] != 0xFF or data[off + 6] != 0x80:
        raise ValueError("not the proven standalone FF script shape")
    source_cpu = data[off + 1] | (data[off + 2] << 8) | (data[off + 3] << 16)
    param = data[off + 4] | (data[off + 5] << 8)
    return {
        "kind": "type_ff",
        "script_cpu": f"0x{script_cpu:06X}",
        "script_file": f"0x{off:06X}",
        "source_cpu": f"0x{source_cpu:06X}",
        "source_file": f"0x{cpu_to_file(source_cpu):06X}",
        "parameter": f"0x{param:04X}",
        "terminator": "0x80",
    }


def describe_resource(
    data: bytes | bytearray,
    script_cpu: int,
    *,
    out_dir: Path | None = None,
) -> dict:
    script_off = cpu_to_file(script_cpu)
    kind = data[script_off]

    if kind == 0x00:
        _typ, flags, records, vram = parse_type0_package(data, script_cpu)
        out = {
            "kind": "type_00",
            "script_cpu": f"0x{script_cpu:06X}",
            "script_file": f"0x{script_off:06X}",
            "flags": f"0x{flags:02X}",
            "records": [],
        }
        for rec in records:
            row = {
                "index": rec.index,
                "vram_word": f"0x{rec.vram_word:04X}",
                "source_cpu": f"0x{rec.source_cpu:06X}",
                "source_file": f"0x{rec.source_file:06X}",
                "compressed_span": f"0x{rec.compressed_span:X}",
                "postprocess": rec.postprocess,
                "output_size": f"0x{rec.output_size:X}",
                "previews": [],
            }

            if out_dir and 0 < rec.output_size <= 0x6000:
                stem = f"res_{script_cpu:06X}_r{rec.index:02d}_v{rec.vram_word:04X}"
                for bpp in (4, 2):
                    tile_bytes = 32 if bpp == 4 else 16
                    if rec.output_size % tile_bytes:
                        continue
                    png = out_dir / f"{stem}_{bpp}bpp.png"
                    canvas = render_tile_sheet(
                        vram,
                        start_word=rec.vram_word,
                        byte_length=rec.output_size,
                        bpp=bpp,
                        cols=16,
                        scale=2,
                    )
                    write_gray_png(png, crop_nonwhite(canvas, 4))
                    row["previews"].append({
                        "bpp": bpp,
                        "png": str(png),
                    })
            out["records"].append(row)
        return out

    if kind == 0xFF:
        return parse_single_ff_script(data, script_cpu)

    return {
        "kind": "unknown",
        "script_cpu": f"0x{script_cpu:06X}",
        "script_file": f"0x{script_off:06X}",
        "first_byte": f"0x{kind:02X}",
    }


def walk_code_candidates(
    data: bytes | bytearray,
    *,
    roots: list[int],
    radius: int,
    max_depth: int,
    code_banks: set[int] | None = None,
) -> dict:
    allowed = DEFAULT_CODE_BANKS if code_banks is None else code_banks
    queue = deque((cpu, 0, None) for cpu in roots)
    seen: set[int] = set()
    routines: list[dict] = []
    resources: list[dict] = []

    while queue:
        cpu, depth, parent = queue.popleft()
        if cpu in seen:
            continue
        seen.add(cpu)

        bank = (cpu >> 16) & 0xFF
        if bank not in allowed:
            continue
        try:
            off = cpu_to_file(cpu)
        except ValueError:
            continue

        start = max(0, off - radius)
        end = min(len(data), off + radius)
        flows = control_flow(data, start, end)
        rcalls = resource_calls(data, start, end)

        routines.append({
            "cpu": cpu,
            "file": off,
            "depth": depth,
            "parent": parent,
            "window_start": start,
            "window_end": end,
            "flow_count": len(flows),
            "resource_call_count": len(rcalls),
        })

        for r in rcalls:
            resources.append({
                "routine_cpu": cpu,
                "routine_depth": depth,
                "call_source_cpu": r["source_cpu"],
                "call_source_file": r["source_file"],
                "script_cpu": r["script_cpu"],
                "script_file": r["script_file"],
            })

        if depth >= max_depth:
            continue

        for flow in flows:
            target = flow["target_cpu"]
            tbank = (target >> 16) & 0xFF
            if target in (RESOURCE_INTERPRETER, WORKER_INIT):
                continue
            if tbank not in allowed:
                continue
            queue.append((target, depth + 1, cpu))

    # Deduplicate exact resource call sites while preserving first-seen order.
    dedup: list[dict] = []
    keys: set[tuple[int, int]] = set()
    for row in resources:
        key = (row["call_source_cpu"], row["script_cpu"])
        if key not in keys:
            keys.add(key)
            dedup.append(row)

    return {
        "routines": routines,
        "resource_calls": dedup,
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description=(
            "READ-ONLY execution-aware G2 school-front resource collector. "
            "It follows bounded local code candidates and exports resource previews; "
            "it does not claim asset identity by itself."
        )
    )
    ap.add_argument("rom", type=Path)
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("reports/generated/g2_school_front_resources"),
    )
    ap.add_argument("--radius", type=lambda s: int(s, 0), default=0x100)
    ap.add_argument("--depth", type=int, default=2)
    args = ap.parse_args()

    data = require_clean_rom(args.rom)
    out = args.out
    previews = out / "previews"
    previews.mkdir(parents=True, exist_ok=True)

    roots = [
        ANCHORS["g2_entry"],
        ANCHORS["school_front_dispatch"],
    ]
    walked = walk_code_candidates(
        data,
        roots=roots,
        radius=args.radius,
        max_depth=args.depth,
    )

    scripts: dict[int, dict] = {}
    for call in walked["resource_calls"]:
        script_cpu = call["script_cpu"]
        if script_cpu in scripts:
            continue
        try:
            scripts[script_cpu] = describe_resource(
                data,
                script_cpu,
                out_dir=previews,
            )
        except Exception as exc:
            scripts[script_cpu] = {
                "kind": "parse_error",
                "script_cpu": f"0x{script_cpu:06X}",
                "error": str(exc),
            }

    report = {
        "mode": "READ_ONLY_EXECUTION_AWARE_RESOURCE_COLLECTION",
        "runtime_claim": False,
        "asset_identity_claim": False,
        "target": {
            "jp": "今からやるよ",
            "vi": "Bắt đầu thôi!",
        },
        "roots": [f"0x{x:06X}" for x in roots],
        "radius": f"0x{args.radius:X}",
        "max_depth": args.depth,
        "routines": [
            {
                **row,
                "cpu": f"0x{row['cpu']:06X}",
                "file": f"0x{row['file']:06X}",
                "parent": (
                    None if row["parent"] is None
                    else f"0x{row['parent']:06X}"
                ),
                "window_start": f"0x{row['window_start']:06X}",
                "window_end": f"0x{row['window_end']:06X}",
            }
            for row in walked["routines"]
        ],
        "resource_calls": [
            {
                **row,
                "routine_cpu": f"0x{row['routine_cpu']:06X}",
                "call_source_cpu": f"0x{row['call_source_cpu']:06X}",
                "call_source_file": f"0x{row['call_source_file']:06X}",
                "script_cpu": f"0x{row['script_cpu']:06X}",
                "script_file": (
                    None if row["script_file"] is None
                    else f"0x{row['script_file']:06X}"
                ),
            }
            for row in walked["resource_calls"]
        ],
        "resources": [
            scripts[k] for k in sorted(scripts)
        ],
        "guardrails": [
            "0x286EA remains descriptor-only evidence",
            "0x9ACB34 remains rejected",
            "preview resemblance alone is not asset proof",
            "promote only after matching executed resource -> decoded source -> visible overlay",
        ],
        "next_gate": (
            "inspect exported previews from resources reached by the school-front "
            "execution neighborhood, then prove the exact record/source that renders "
            "今からやるよ before any write"
        ),
    }

    out.mkdir(parents=True, exist_ok=True)
    report_path = out / "g2_school_front_resources.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print("G2 SCHOOL-FRONT RESOURCE COLLECTOR")
    print("clean_rom_contract=PASS")
    print("mode=READ_ONLY")
    print(f"routines={len(report['routines'])}")
    print(f"resource_calls={len(report['resource_calls'])}")
    print(f"unique_scripts={len(report['resources'])}")
    for row in report["resource_calls"]:
        print(
            f"depth={row['routine_depth']} "
            f"routine={row['routine_cpu']} "
            f"call={row['call_source_cpu']} "
            f"script={row['script_cpu']}"
        )
    print(f"report={report_path}")
    print(f"previews={previews}")
    print("asset_identity_claim=NO")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
