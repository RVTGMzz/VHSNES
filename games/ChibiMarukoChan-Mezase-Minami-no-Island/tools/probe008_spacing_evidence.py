#!/usr/bin/env python3
"""Probe 008 renderer-pitch evidence and OFFLINE preview.

Never commits ROMs. Optional --diagnostic-9px builds an explicitly UNTESTED
global-spacing experiment from exact Probe003, not a release-ready patch.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLEAN_SHA256 = "e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
PROBE003_SHA256 = "5208bec10147f478cc17955c4f262a5cde08e5b85708caa2717370f6835fbacd"
PROBE008_V2_FONT_SHA256 = "2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd"
TABLE_TILES = 0x29670
TABLE_SHIFTS = 0x29696
COUNT = 19
SAMPLES = (
    "Nói thẳng nhé!", "Du học chớ ngại!", "Rèn gu mỹ thuật!",
    "M W mư ơ ớ ả ẳ ỹ", "ƯỚI?",
)
FONT_JSON = ROOT / "translation/codepage/g2_probe008_custom_round_glyphs.json"


def table_bytes(pitch: int) -> tuple[bytes, bytes]:
    if not 8 <= pitch <= 16:
        raise ValueError("unsupported diagnostic pitch")
    x = [4 + pitch * i for i in range(COUNT)]
    return (
        b"".join((16 * (pos // 8)).to_bytes(2, "little") for pos in x),
        bytes(pos % 8 for pos in x),
    )


def proof(rom: bytes) -> dict:
    h = hashlib.sha256(rom).hexdigest()
    if len(rom) != 0x200000 or h not in (CLEAN_SHA256, PROBE003_SHA256, PROBE008_V2_FONT_SHA256):
        raise ValueError("exact clean or Probe003 2 MiB ROM required")
    expected_tiles, expected_shifts = table_bytes(13)
    if rom[TABLE_TILES:TABLE_TILES + 38] != expected_tiles:
        raise ValueError("renderer tile-offset table differs from verified 13px positions")
    if rom[TABLE_SHIFTS:TABLE_SHIFTS + 19] != expected_shifts:
        raise ValueError("renderer pixel-shift table differs from verified 13px positions")
    if rom.count(bytes.fromhex("BF 70 96 85")) < 1 or rom.count(bytes.fromhex("BF 96 96 85")) < 1:
        raise ValueError("renderer table-use opcodes missing")
    return {
        "rom_sha256": h, "checked_positions": COUNT, "actual_advance_px": 13,
        "x_formula": "4 + 13 * character_index",
        "tile_table_offset": "0x29670", "bitshift_table_offset": "0x29696",
        "suggested_advance_px": 9, "status": "STATIC PASS; emulator UNTESTED",
        "warning": "9px globally modifies native Japanese text too; diagnostic only.",
    }


def glyph_pixels(value: str) -> set[tuple[int, int]]:
    raw = bytes.fromhex(value)
    if len(raw) != 18:
        raise ValueError("glyph must be 12x12 raw 1bpp")
    return {(i % 12, i // 12) for i in range(144)
            if (raw[i // 8] >> (7 - i % 8)) & 1}


def layout(sentence: str, pitch: int, fonts: dict) -> tuple[set[tuple[int, int]], int]:
    seen: set[tuple[int, int]] = set()
    collisions = 0
    for i, ch in enumerate(sentence):
        for x, y in glyph_pixels(fonts[ch]["bitmap_hex"]):
            p = (4 + i * pitch + x, y)
            if p in seen:
                collisions += 1
            seen.add(p)
    return seen, collisions


def make_preview(destination: Path, fonts: dict) -> list[dict]:
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new("RGB", (2240, 1010), "#e7edf2")
    d = ImageDraw.Draw(im)
    normal = ImageFont.truetype("DejaVuSans.ttf", 22)
    small = ImageFont.truetype("DejaVuSans.ttf", 17)
    d.text((25, 18), "CHIBI MARUKO | VERIFIED FONT ADVANCE", font=normal, fill="#172538")
    d.text((25, 51), "13px = actual renderer | 12px = previous preview | 9px = experiment", font=small, fill="#263b51")
    results = []
    for ci, pitch in enumerate((13, 12, 9)):
        bx = 25 + ci * 730
        d.text((bx, 90), f"{pitch} px", font=normal, fill="#213246")
        for ri, s in enumerate(SAMPLES):
            by = 140 + ri * 165
            pixels, collisions = layout(s, pitch, fonts)
            results.append({"sample": s, "pitch_px": pitch, "collisions": collisions})
            d.text((bx, by), s, font=small, fill="#33485a")
            for x, y in pixels:
                d.rectangle((bx + x * 3, by + 32 + y * 3,
                             bx + x * 3 + 2, by + 32 + y * 3 + 2), fill="#1c313d")
            d.text((bx, by + 86), f"ink collisions: {collisions}", font=small,
                   fill="#903f31" if collisions else "#2b6148")
    d.text((25, 968), "OFFLINE bitmap simulation, NOT an emulator screenshot.", font=small, fill="#405465")
    destination.parent.mkdir(parents=True, exist_ok=True)
    im.save(destination)
    return results


def patch_diagnostic_9px(rom: bytes, dest: Path) -> dict:
    if hashlib.sha256(rom).hexdigest() not in (PROBE003_SHA256, PROBE008_V2_FONT_SHA256):
        raise ValueError("diagnostic patch needs exact Probe003 or verified Probe008 V2 13px font-only build")
    original = bytes(rom)
    data = bytearray(rom)
    tiles, shifts = table_bytes(9)
    data[TABLE_TILES:TABLE_TILES + len(tiles)] = tiles
    data[TABLE_SHIFTS:TABLE_SHIFTS + len(shifts)] = shifts
    data[0x7FDC:0x7FE0] = b"\x00" * 4
    checksum = (sum(data) + 0x1FE) & 0xFFFF
    data[0x7FDC:0x7FDE] = (checksum ^ 0xFFFF).to_bytes(2, "little")
    data[0x7FDE:0x7FE0] = checksum.to_bytes(2, "little")
    allowed = set(range(TABLE_TILES, TABLE_TILES + 38)) | set(
        range(TABLE_SHIFTS, TABLE_SHIFTS + 19)) | set(range(0x7FDC, 0x7FE0))
    diff = {i for i, (a, b) in enumerate(zip(original, data)) if a != b}
    if not diff <= allowed or any(data[o:o+106] != original[o:o+106]
                                 for o in (0x181CE, 0x18247, 0x182C0)):
        raise AssertionError("diagnostic changed dialogue or non-whitelisted bytes")
    if ((int.from_bytes(data[0x7FDC:0x7FDE], "little") ^
         int.from_bytes(data[0x7FDE:0x7FE0], "little")) != 0xFFFF):
        raise AssertionError("SNES complement mismatch")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return {"sha256": hashlib.sha256(data).hexdigest(),
            "checksum": f"0x{checksum:04X}", "changed_bytes": len(diff),
            "runtime": "UNTESTED", "release_ready": False,
            "global_native_text_spacing_may_regress": True,
            "source_is_font_v2": hashlib.sha256(original).hexdigest() == PROBE008_V2_FONT_SHA256}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("rom", type=Path)
    ap.add_argument("--report", type=Path)
    ap.add_argument("--preview", type=Path)
    ap.add_argument("--diagnostic-9px", type=Path,
                    help="UNTESTED global renderer experiment on exact Probe003 or Probe008 V2 font-only")
    args = ap.parse_args()
    raw = args.rom.read_bytes()
    report = proof(raw)
    if args.preview:
        fonts = json.loads(FONT_JSON.read_text(encoding="utf-8"))
        report["preview_samples"] = make_preview(args.preview, fonts)
    if args.diagnostic_9px:
        if args.diagnostic_9px.resolve() == args.rom.resolve():
            raise ValueError("never overwrite source ROM")
        report["diagnostic_build"] = patch_diagnostic_9px(raw, args.diagnostic_9px)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
