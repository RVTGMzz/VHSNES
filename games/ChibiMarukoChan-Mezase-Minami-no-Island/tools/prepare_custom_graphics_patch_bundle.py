#!/usr/bin/env python3
from __future__ import annotations

import argparse
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


def fit_file(
    source: Path,
    span_length: int,
    output: Path,
    *,
    allow_zero_padding: bool,
) -> str:
    data = source.read_bytes()
    if len(data) > span_length:
        raise RuntimeError(
            f"{source.name}: 0x{len(data):X} exceeds "
            f"proven span 0x{span_length:X}"
        )

    if len(data) == span_length:
        output.write_bytes(data)
        return "EXACT_FIT"

    if not allow_zero_padding:
        raise RuntimeError(
            f"{source.name}: 0x{len(data):X} is smaller than "
            f"span 0x{span_length:X}; padding not authorized"
        )

    output.write_bytes(
        data + bytes(span_length - len(data))
    )
    return "FITS_WITH_ZERO_PADDING"


def make_entry(
    build035: Path,
    replacement: Path,
    patch_id: str,
    offset: int,
    evidence: str,
    tool_dir: Path,
) -> dict:
    stdout = run_capture(
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
    entry = json.loads(stdout)
    entry["replacement_file"] = replacement.name
    return entry


def main() -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Prepare a guarded G0/custom graphics patch fragment "
            "from indexed P1/P2 pixel art"
        )
    )
    ap.add_argument("build035", type=Path)
    ap.add_argument("input_pnm", type=Path)
    ap.add_argument("output_dir", type=Path)
    ap.add_argument("--id", required=True)
    ap.add_argument("--evidence", required=True)
    ap.add_argument("--bpp", type=int, choices=(2, 4), required=True)
    ap.add_argument("--gfx-offset", type=lambda s: int(s, 0), required=True)
    ap.add_argument("--gfx-span-length", type=lambda s: int(s, 0), required=True)
    ap.add_argument("--tile-base", type=int, default=0)
    ap.add_argument("--palette", type=int, default=0)
    ap.add_argument("--priority", action="store_true")
    ap.add_argument("--pad-to-tiles", action="store_true")
    ap.add_argument("--allow-gfx-zero-padding", action="store_true")
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
    cmd = [
        sys.executable,
        str(tool_dir / "encode_indexed_pnm_to_snes_tiles.py"),
        str(args.input_pnm),
        str(raw_prefix),
        "--bpp",
        str(args.bpp),
        "--tile-base",
        str(args.tile_base),
        "--palette",
        str(args.palette),
    ]
    if args.priority:
        cmd.append("--priority")
    if args.pad_to_tiles:
        cmd.append("--pad-to-tiles")

    encoder_stdout = run_capture(cmd)

    raw_tiles = Path(str(raw_prefix) + ".tiles.bin")
    raw_map = Path(str(raw_prefix) + ".tilemap.bin")
    preview = Path(str(raw_prefix) + ".png")
    metadata = Path(str(raw_prefix) + ".json")

    gfx_replacement = out / f"{args.id}.gfx.bin"
    gfx_fit = fit_file(
        raw_tiles,
        args.gfx_span_length,
        gfx_replacement,
        allow_zero_padding=args.allow_gfx_zero_padding,
    )

    entries = [
        make_entry(
            args.build035,
            gfx_replacement,
            f"{args.id}_gfx",
            args.gfx_offset,
            args.evidence + " | custom indexed G0 graphics",
            tool_dir,
        )
    ]

    tilemap_fit = None
    tilemap_replacement = None
    if args.tilemap_offset is not None:
        tilemap_replacement = out / f"{args.id}.tilemap.bin"
        tilemap_fit = fit_file(
            raw_map,
            args.tilemap_span_length,
            tilemap_replacement,
            allow_zero_padding=False,
        )
        entries.append(
            make_entry(
                args.build035,
                tilemap_replacement,
                f"{args.id}_tilemap",
                args.tilemap_offset,
                args.evidence + " | custom indexed G0 tilemap",
                tool_dir,
            )
        )

    fragment = {
        "schema": "chibi.graphics.patch.fragment.v1",
        "id": args.id,
        "kind": "custom_indexed_graphics",
        "source_art": str(args.input_pnm),
        "evidence": args.evidence,
        "geometry": {
            "bpp": args.bpp,
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
            "encoder_metadata": str(metadata),
            "graphics_replacement": str(gfx_replacement),
            "tilemap_replacement": (
                str(tilemap_replacement)
                if tilemap_replacement
                else None
            ),
        },
        "encoder_output": encoder_stdout.splitlines(),
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

    print("custom_graphics_encode=PASS")
    print(f"id={args.id}")
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
