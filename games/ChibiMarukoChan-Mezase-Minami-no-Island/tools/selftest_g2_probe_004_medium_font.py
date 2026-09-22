#!/usr/bin/env python3
from __future__ import annotations

from build_g2_probe_004_medium_font import thicken_right


def main() -> int:
    grid = [[0] * 12 for _ in range(12)]
    grid[5][3] = 1
    grid[5][5] = 1
    out = thicken_right(grid)
    assert out[5][3] == 1
    assert out[5][4] == 1
    assert out[5][5] == 1
    assert out[5][6] == 1
    assert sum(sum(row) for row in out) == 4
    print("g2_probe004_medium_font_selftest=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
