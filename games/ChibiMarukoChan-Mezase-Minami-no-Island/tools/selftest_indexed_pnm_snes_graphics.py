#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


def check(name: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(name)
    print(f"{name}=PASS")


def main() -> int:
    print("CHIBI INDEXED PNM -> SNES GRAPHICS SELFTEST")
    tool = Path(__file__).with_name(
        "encode_indexed_pnm_to_snes_tiles.py"
    )

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        pnm = td / "logo.pgm"
        prefix = td / "logo"

        values = [5] + [0] * 63
        pnm.write_text(
            "P2\n"
            "8 8\n"
            "15\n"
            + " ".join(
                str(v)
                for v in values
            )
            + "\n",
            encoding="ascii",
        )

        result = subprocess.run(
            [
                sys.executable,
                str(tool),
                str(pnm),
                str(prefix),
                "--bpp",
                "4",
                "--tile-base",
                "7",
                "--palette",
                "2",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        check(
            "encoder_reports_pass",
            "pnm_parse=PASS"
            in result.stdout,
        )

        tiles = Path(
            str(prefix) + ".tiles.bin"
        ).read_bytes()
        check(
            "one_4bpp_tile",
            len(tiles) == 32,
        )
        check(
            "pixel_index_5_planes",
            (tiles[0] & 0x80) != 0
            and (tiles[16] & 0x80) != 0
            and (tiles[1] & 0x80) == 0,
        )

        tilemap = Path(
            str(prefix) + ".tilemap.bin"
        ).read_bytes()
        entry = int.from_bytes(
            tilemap[:2],
            "little",
        )
        check(
            "tilemap_base_palette",
            (entry & 0x03FF) == 7
            and ((entry >> 10) & 0x7) == 2,
        )

        png = Path(
            str(prefix) + ".png"
        )
        check(
            "preview_png",
            png.read_bytes().startswith(
                b"\x89PNG\r\n\x1a\n"
            ),
        )

    print("selftest=PASS")
    print("commercial_rom_required=NO")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
