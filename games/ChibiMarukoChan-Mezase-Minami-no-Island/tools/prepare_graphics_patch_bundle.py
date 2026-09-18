#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def run_capture(cmd: list[str]) -> str:
    result = subprocess.run(
        cmd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def require_exact_fit(
    source: Path,
    span_length: int,
    output: Path,
    *,
    allow_padding: bool,
) -> str:
    data = source.read_bytes()
    if len(data) > span_length:
        raise RuntimeError(
            f"{source.name}: replacement 0x{len(data):X} "
            f"exceeds span 0x{span_length:X}"
        )

    if len(data) == span_length:
        output.write_bytes(data)
        return "EXACT_FIT"

    if not allow_padding:
        raise RuntimeError(
            f"{source.name}: replacement 0x{len(data):X} "
            f"is smaller than span 0x{span_length:X}; "
            "padding was not authorized"
        )

    output.write_bytes(
        data + bytes(span_length - len(data))
    )
    return "FITS_WITH_ZERO_PADDING"


def patch_entry(
    build035: Path,
    replacement: Path,
    patch_id: str,
    offset: int,
    evidence: str,
    tool_dir: Path,
) -> dict:
    text = run_capture(
        [
            sys.executable,
            str(tool_dir / "make_graphics_patch_entry.py"),
            str(build035),
            str(replacement),
            "--id",
            patch_id,
            "--offset",
            hex(offset),
            "--evidence",
            evidence,
        ]
    )
    return json.loads(text)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Prepare one guarded G1-G3 Vietnamese graphics "
            "candidate bundle from a proven asset geometry/span"
        )
    )
    ap.add_argument("build035", type=Path)
    ap.add_argument("output_dir", type=Path)
    ap.add_argument("--codepage", type=Path, required=True)
    ap.add_argument("--id", required=True)
    ap.add_argument("--text", required=True)
    ap.add_argument("--evidence", required=True)
    ap.add_argument("--bpp", type=int, choices=(2, 4), required=True)
    ap.add_argument("--gfx-offset", type=lambda s: int(s, 0), required=True)
    ap.add_argument("--gfx-span-length", type=lambda s: int(s, 0), required=True)
    ap.add_argument("--width-tiles", type=int, required=True)
    ap.add_argument("--height-tiles", type=int, required=True)
    ap.add_argument("--x", type=int, default=0)
    ap.add_argument("--y", type=int, default=0)
    ap.add_argument("--advance", type=int, default=12)
    ap.add_argument("--line-height", type=int, default=12)
    ap.add_argument("--ink-index", type=int, default=1)
    ap.add_argument("--tile-base", type=int, default=0)
    ap.add_argument("--palette", type=int, default=0)
    ap.add_argument("--priority", action="store_true")
    ap.add_argument(
        "--allow-gfx-zero-padding",
        action="store_true",
        help="allow generated tile data to be padded with 00 to exact proven graphics span length",
    )
    ap.add_argument("--tilemap-offset", type=lambda s: int(s, 0))
    ap.add_argument("--tilemap-span-length", type=lambda s: int(s, 0))
    args = ap.parse_args()

    if (args.tilemap_offset is None) != (
        args.tilemap_span_length is None
    ):
        raise SystemExit(
            "tilemap-offset and tilemap-span-length must be supplied together"
        )

    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    tool_dir = Path(__file__).resolve().parent

    raw_prefix = out / f"{args.id}_raw"
    raster_cmd = [
        sys.executable,
        str(tool_dir / "rasterize_vi_text_to_snes_tiles.py"),
        str(args.build035),
        str(raw_prefix),
        "--codepage",
        str(args.codepage),
        "--text",
        args.text,
        "--bpp",
        str(args.bpp),
        "--ink-index",
        str(args.ink_index),
        "--width-tiles",
        str(args.width_tiles),
        "--height-tiles",
        str(args.height_tiles),
        "--x",
        str(args.x),
        "--y",
        str(args.y),
        "--advance",
        str(args.advance),
        "--line-height",
        str(args.line_height),
        "--tile-base",
        str(args.tile_base),
        "--palette",
        str(args.palette),
    ]
    if args.priority:
        raster_cmd.append("--priority")
    raster_stdout = run_capture(raster_cmd)

    raw_tiles = Path(str(raw_prefix) + ".tiles.bin")
    raw_map = Path(str(raw_prefix) + ".tilemap.bin")
    preview = Path(str(raw_prefix) + ".png")
    metadata = Path(str(raw_prefix) + ".json")

    gfx_replacement = out / f"{args.id}.gfx.bin"
    gfx_fit = require_exact_fit(
        raw_tiles,
        args.gfx_span_length,
        gfx_replacement,
        allow_padding=args.allow_gfx_zero_padding,
    )

    entries = [
        patch_entry(
            args.build035,
            gfx_replacement,
            f"{args.id}_gfx",
            args.gfx_offset,
            args.evidence + " | generated Vietnamese tile graphics",
            tool_dir,
        )
    ]

    tilemap_fit = None
    tilemap_replacement = None
    if args.tilemap_offset is not None:
        tilemap_replacement = out / f"{args.id}.tilemap.bin"
        tilemap_fit = require_exact_fit(
            raw_map,
            args.tilemap_span_length,
            tilemap_replacement,
            allow_padding=False,
        )
        entries.append(
            patch_entry(
                args.build035,
                tilemap_replacement,
                f"{args.id}_tilemap",
                args.tilemap_offset,
                args.evidence + " | generated Vietnamese tilemap",
                tool_dir,
            )
        )

    fragment = {
        "schema": "chibi.graphics.patch.fragment.v1",
        "id": args.id,
        "text": args.text,
        "evidence": args.evidence,
        "geometry": {
            "bpp": args.bpp,
            "width_tiles": args.width_tiles,
            "height_tiles": args.height_tiles,
            "x": args.x,
            "y": args.y,
            "advance": args.advance,
            "line_height": args.line_height,
            "tile_base": args.tile_base,
            "palette": args.palette,
            "priority": args.priority,
        },
        "fit": {
            "graphics": gfx_fit,
            "tilemap": tilemap_fit,
        },
        "patches": entries,
        "artifacts": {
            "raw_tiles": str(raw_tiles),
            "raw_tilemap": str(raw_map),
            "preview": str(preview),
            "raster_metadata": str(metadata),
            "graphics_replacement": str(gfx_replacement),
            "tilemap_replacement": (
                str(tilemap_replacement)
                if tilemap_replacement
                else None
            ),
        },
        "rasterizer_output": raster_stdout.splitlines(),
        "runtime_status": "UNTESTED",
        "runtime_claim": False,
    }

    fragment_path = out / f"{args.id}.patch_fragment.json"
    fragment_path.write_text(
        json.dumps(
            fragment,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print("build035_contract=PASS")
    print(f"id={args.id}")
    print(f"text={args.text}")
    print(f"graphics_fit={gfx_fit}")
    if tilemap_fit:
        print(f"tilemap_fit={tilemap_fit}")
    print(f"patch_entries={len(entries)}")
    print(f"preview={preview}")
    print(f"fragment={fragment_path}")
    print("runtime_status=UNTESTED")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
