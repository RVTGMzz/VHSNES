#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

EXPECTED_SHA256 = "5586abea7c33cdc15510a4ac2cf75dbf814c1973e23ddb004b6962b6ff8e57e8"
EXPECTED = {"!","D","L","N","R","T","c","g","h","i","k","m","n","p","r","t","u","x","y","è","é","ó","ơ","ạ","ả","ậ","ẳ","ệ","ọ","ỏ","ớ","ỹ"}


def main() -> int:
    path = Path(__file__).resolve().parent.parent / "translation" / "codepage" / "g2_probe005_dialogue_glyphs.json"
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256
    data = json.loads(raw.decode("utf-8"))
    assert set(data) == EXPECTED
    seen = set()
    for ch, meta in data.items():
        gid = int(meta["glyph_id"], 16)
        assert 0 <= (gid >> 8) < 10
        assert 0 <= (gid & 0xFF) < 100
        assert len(bytes.fromhex(meta["bitmap_hex"])) == 18
        assert meta["bitmap_hex"] != "00" * 18
        if ch in {"!","L","y","R","T"}:
            assert gid not in seen
        seen.add(gid)
    assert data["é"]["bitmap_hex"] != data["è"]["bitmap_hex"]
    assert data["ả"]["bitmap_hex"] != data["ẳ"]["bitmap_hex"]
    assert data["ỹ"]["bitmap_hex"] != data["y"]["bitmap_hex"]
    assert data["ệ"]["bitmap_hex"] != data["é"]["bitmap_hex"]
    print("g2_probe005_dialogue_font_selftest=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
