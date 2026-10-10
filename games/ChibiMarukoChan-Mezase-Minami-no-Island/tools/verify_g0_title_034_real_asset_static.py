#!/usr/bin/env python3
"""Independent QA of the exact 034 G0 startup-title graphics ROM candidate.

This reconstructs the original and modified *real* $82:A087 resource package
into VRAM, compares all non-title tilemap/OBJ bytes and 4bpp tiles referenced
by the other graphics layers, verifies the new G0 logo geometry and checksum.
It does NOT execute SNES CPU/PPU code or claim in-game visual acceptance.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from decompress_chibi_resource import cpu_to_file, decompress_resource, reorder_flag1_blocks
from rom_common import require_clean_rom, validate_internal_header

EXPECTED_SHA256 = "012cdfb87eae1b7c5a9feada4e1c322541e3c91ba45ba0b857e08a2465f47ce0"
SCRIPT = 0x12087
OTHER_MAPS = (0x0400, 0x1000, 0x5000, 0x5800)
ALLOWED_SPANS = ((0x7FDC, 0x7FE0), (0x12095, 0x12098),
                 (0x36907, 0x36907 + 3420),
                 (0xF6456, 0xF6456 + 5570),
                 (0xF1F00, 0xF1F00 + 545))


def reconstruct(rom: bytes) -> tuple[bytes, list[dict]]:
    if rom[SCRIPT:SCRIPT + 2] != b"\x00\x00":
        raise AssertionError("G0 type-0 script identity changed")
    out = bytearray(65536)
    p = SCRIPT + 2
    references = []
    for i in range(16):
        if rom[p] == 0xFF:
            break
        dest = int.from_bytes(rom[p:p + 2], "little")
        cpu = int.from_bytes(rom[p + 2:p + 5], "little")
        file = cpu_to_file(cpu)
        raw, hdr, _stats = decompress_resource(rom, file)
        processed = reorder_flag1_blocks(raw) if hdr.postprocess else raw
        start = 2 * dest
        if start + len(processed) > len(out):
            raise AssertionError("G0 DMA resource exceeds VRAM")
        out[start:start + len(processed)] = processed
        references.append({
            "index": i, "dest_word": f"0x{dest:04X}",
            "source_cpu": f"0x{cpu:06X}", "source_file": f"0x{file:06X}",
            "decoded_bytes": len(processed),
        })
        p += 5
    if len(references) != 10 or rom[p] != 0xFF:
        raise AssertionError("G0 package no longer ten terminated resource entries")
    return bytes(out), references


def pixel(vram: bytes, tile_id: int, dx: int, dy: int) -> int:
    at = 0x4000 + tile_id * 32
    b = 7 - dx
    return ((vram[at + 2 * dy] >> b) & 1
            | (((vram[at + 2 * dy + 1] >> b) & 1) << 1)
            | (((vram[at + 16 + 2 * dy] >> b) & 1) << 2)
            | (((vram[at + 16 + 2 * dy + 1] >> b) & 1) << 3))


def audit(clean: bytes, modified: bytes) -> dict:
    sha = hashlib.sha256(modified).hexdigest()
    if sha != EXPECTED_SHA256 or len(clean) != len(modified):
        raise ValueError("exact locally staged experimental G0 ROM required")
    old, original_resources = reconstruct(clean)
    new, edited_resources = reconstruct(modified)
    if (original_resources[2]["source_cpu"], edited_resources[2]["source_cpu"]) != (
            "0x9EC56D", "0x86E907"):
        raise AssertionError("G0-only third resource was not relocated as proven")
    if [x for i, x in enumerate(original_resources) if i not in (0, 2, 3)] != [
        x for i, x in enumerate(edited_resources) if i not in (0, 2, 3)]:
        raise AssertionError("unrelated G0 package resource pointer or span changed")
    for base in OTHER_MAPS:
        lo = base * 2
        if old[lo:lo + 2048] != new[lo:lo + 2048]:
            raise AssertionError(f"other title/background tilemap modified: {base:#x}")
    if old[0xC000:] != new[0xC000:]:
        raise AssertionError("title-stage original OBJ/character graphics changed")
    if old[704:2048] != new[704:2048]:
        raise AssertionError("title tilemap rows 11..31 were modified")

    protected = set()
    for base in OTHER_MAPS:
        for i in range(1024):
            pos = base * 2 + i * 2
            protected.add(int.from_bytes(old[pos:pos + 2], "little") & 0x03FF)
    for glyph_id in protected:
        if glyph_id >= 768:
            continue
        at = 0x4000 + glyph_id * 32
        if old[at:at + 32] != new[at:at + 32]:
            raise AssertionError(f"shared 4bpp tile modified: {glyph_id}")
    native_protected = sum(0 <= x < 768 for x in protected)

    # Independent 256x88 palette-index glyph presence check.
    counts = []
    for top, bottom in ((4, 28), (34, 59), (65, 80)):
        painted = 0
        for y in range(top, bottom):
            for x in range(256):
                row, col = divmod(x, 8)
                ty, iy = divmod(y, 8)
                pos = (ty * 32 + row) * 2
                entry = int.from_bytes(new[pos:pos + 2], "little")
                glyph = entry & 0x03FF
                xx = 7 - col if entry & 0x4000 else col
                yy = 7 - iy if entry & 0x8000 else iy
                painted += pixel(new, glyph, xx, yy) == 13
        if painted < 50:
            raise AssertionError(f"G0 title line {top}..{bottom} lost its glyphs")
        counts.append(painted)
    hdr = validate_internal_header(modified)
    if not hdr["checksum_matches"] or not hdr["checksum_pair_valid"]:
        raise AssertionError("SNES checksum and complement invalid")
    allowed = set()
    for a, b in ALLOWED_SPANS:
        allowed.update(range(a, b))
    actual = {i for i, (a, b) in enumerate(zip(clean, modified)) if a != b}
    if actual - allowed:
        raise AssertionError("modified bytes escaped title-only ROM spans")
    return {
        "status": "G0_034_STATIC_ROM_RECONSTRUCTION_PASS_ONLY",
        "output_sha256": sha,
        "G0_package_records": len(edited_resources),
        "G0_source_relocated": "0x9EC56D -> 0x86E907",
        "other_tilemaps_byte_identical": len(OTHER_MAPS),
        "protected_4bpp_tiles_checked": native_protected,
        "OBJ_region_byte_identical": True,
        "observed_title_ink_pixels_by_line": counts,
        "rom_byte_changes": len(actual),
        "checksum_hex": f"0x{hdr['checksum']:04X}",
        "real_SNES_emulator": "NOT_TESTED",
        "full_game_localization": False, "release_ready": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exact_clean_rom", type=Path)
    parser.add_argument("exact_g0_034_experiment", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    base = bytes(require_clean_rom(args.exact_clean_rom))
    report = audit(base, args.exact_g0_034_experiment.read_bytes())
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(text)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
