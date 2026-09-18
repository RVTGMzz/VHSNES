#!/usr/bin/env python3
from __future__ import annotations

import tempfile
from pathlib import Path

from rasterize_vi_text_to_snes_tiles import (
    encode_canvas,
    encode_tile,
    encode_tilemap,
    required_canvas,
    write_preview_png,
)


def check(name: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(name)
    print(f"{name}=PASS")


def main() -> int:
    print("CHIBI VI TEXT -> SNES GRAPHICS SELFTEST")

    check(
        "required_canvas_single_line",
        required_canvas("ABC", 0, 0, 12, 12) == (36, 12),
    )
    check(
        "required_canvas_multiline",
        required_canvas("AB\nC", 2, 3, 12, 14) == (26, 29),
    )

    tile = [[0] * 8 for _ in range(8)]
    tile[0][0] = 1

    b2 = encode_tile(tile, 2, 3)
    check(
        "encode_2bpp_planes",
        len(b2) == 16
        and (b2[0] & 0x80) != 0
        and (b2[1] & 0x80) != 0,
    )

    b4 = encode_tile(tile, 4, 5)
    check(
        "encode_4bpp_planes",
        len(b4) == 32
        and (b4[0] & 0x80) != 0
        and (b4[16] & 0x80) != 0
        and (b4[1] & 0x80) == 0,
    )

    canvas = [[0] * 16 for _ in range(8)]
    canvas[0][0] = 1
    canvas[0][8] = 1
    encoded = encode_canvas(canvas, 4, 1)
    check("canvas_tile_count", len(encoded) == 64)

    tilemap = encode_tilemap(
        2,
        2,
        tile_base=4,
        palette=3,
        priority=True,
    )
    first = int.from_bytes(tilemap[0:2], "little")
    last = int.from_bytes(tilemap[-2:], "little")
    check(
        "tilemap_first_entry",
        first == 4 | (3 << 10) | 0x2000,
    )
    check(
        "tilemap_sequential_entries",
        (last & 0x03FF) == 7,
    )

    with tempfile.TemporaryDirectory() as td:
        png = Path(td) / "preview.png"
        write_preview_png(
            png,
            [[1, 0], [0, 1]],
            3,
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
