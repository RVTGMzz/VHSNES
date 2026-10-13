#!/usr/bin/env python3
"""Checkpoint 083: audit exactly four unresolved Fortune strings and inspect ROM refs.

Source-only mode proves translated captions, original JP CP932 glyph widths,
canonical IDs and V2 codepoints without creating an unplayable patch.
The optional original-ROM mode discovers ONLY raw pointer-shaped hypotheses:
it explicitly does NOT establish actual code reachability or screen layout.
No writes to ROM, no IPS, no false completion metrics.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE_SHA = "e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
MANIFEST = "translation/runtime/fortune_expansion_083.json"
PRIOR = "translation/runtime/fortune_exceptions_2_056.json"
OFFSETS = (0x2BD5E, 0x2C86B, 0x2CA7D, 0x2CADD)
SOURCE_FILES = (
    "translation/source/fortune_batch01_part1_vi.csv",
    "translation/source/fortune_batch01_part2_vi.csv",
    "translation/source/fortune_batch01_part3_vi.csv",
)

def audit(project: Path) -> dict:
    data = json.loads((project / MANIFEST).read_text(encoding="utf-8"))
    old = json.loads((project / PRIOR).read_text(encoding="utf-8"))
    if (data.get("schema") != "chibi.fortune.expansion.083.v1"
        or data.get("original_clean_sha256") != SOURCE_SHA
        or len(data.get("rows", [])) != 4
        or data.get("allow_static_inplace_patch") is not False
        or data.get("verified_native_pointer_tables") is not False
        or data.get("renderer_visual_width_verified") is not False
        or data.get("emulator_tested") is not False
        or data.get("release_ready") is not False
        or old.get("translated_additional_fortune") != 2):
        raise AssertionError("083 expansion/old 056 release safety contract drift")

    source = {}
    for filename in SOURCE_FILES:
        with (project / filename).open(encoding="utf-8-sig", newline="") as file:
            for line in csv.DictReader(file):
                addr = int(line["file_offset"], 0)
                if addr in source:
                    raise AssertionError("Duplicate original Fortune source address")
                source[addr] = (filename, line)
    if len(source) != 157:
        raise AssertionError("Original canonical Fortune inventory changed")

    with (project / "translation/codepage/vi_codepage_v4_fe4_native.csv").open(
        encoding="utf-8-sig", newline="") as file:
        glyph_records = list(csv.DictReader(file))
    glyphs = {row["unicode"]: row["code_hex"] for row in glyph_records}
    if len(glyphs) != 160 or glyphs.get(" ") != "8440":
        raise AssertionError("Reviewed V2 codepage changed")

    previous = {int(v, 0) for v in old["unresolved_source_offsets"]}
    if previous != set(OFFSETS):
        raise AssertionError("Four previous 056 blockers changed without review")
    rows = data["rows"]
    if tuple(int(row["file_offset"], 0) for row in rows) != OFFSETS:
        raise AssertionError("083 four distinct original Fortune offsets/order changed")

    report = []
    for row in rows:
        offset = int(row["file_offset"], 0)
        canonical = source.get(offset)
        if (canonical is None or row["source_file"] != canonical[0]
            or canonical[1]["source_jp"] != row["source_jp"]
            or canonical[1]["vi_full"] != row["vi_full"]
            or row["vi_display"] != row["vi_full"]
            or row["fixed_field_edit_allowed"] is not False):
            raise AssertionError(f"083 missing canonical JP/VI or source identity at {offset:05X}")
        jp = row["source_jp"]
        vn = row["vi_display"]
        n = row["source_glyph_capacity"]
        if (len(jp.encode("cp932")) != 2 * n or
            len(vn) <= n or
            vn != unicodedata.normalize("NFC", vn)):
            raise AssertionError("Expansion request not based on real overflow/source")
        for letter in vn:
            code = glyphs.get(letter)
            if code is None or len(code) != 4 or not code.startswith("84"):
                raise AssertionError(f"Missing V2 glyph for {letter!r} in {offset:05X}")
        report.append({
            "original_ROM_offset": f"0x{offset:X}",
            "Japanese": jp,
            "natural_Vietnamese": vn,
            "original_glyph_cells": n,
            "required_V2_glyph_cells": len(vn),
            "minimum_additional_cells": len(vn) - n,
            "status": "REQUIRES_POINTER_OR_RENDERER_EXPANSION_NOT_PATCHABLE_IN_PLACE",
        })
    return {
        "status": "PASS_083_FOUR_FORTUNE_SOURCE_TEXTS_VALIDATED_RELOCATION_NOT_PROVEN",
        "canonical_fortune_sources": len(source),
        "source_only_known_fortune_exact_fit_candidates": 153,
        "pending_four_original_offsets": [f"0x{x:X}" for x in OFFSETS],
        "four_meaning_preserving_full_diacritic_captions": len(report),
        "minimum_extra_glyph_cells_if_same_renderer": sum(x["minimum_additional_cells"] for x in report),
        "reflow_and_visual_width_verified": False,
        "ROM_binary_or_IPS_generated": False,
        "emulator_tested": False,
        "rows": report,
    }


def inspect_source_rom(original: bytes, project: Path) -> dict:
    if len(original) != 0x200000 or hashlib.sha256(original).hexdigest() != SOURCE_SHA:
        raise ValueError("Requires exact user-owned headerless 2MiB Japanese retail ROM")
    audit(project)
    plan = json.loads((project / MANIFEST).read_text(encoding="utf-8"))
    references = []
    for row in plan["rows"]:
        offset = int(row["file_offset"], 0)
        raw = row["source_jp"].encode("cp932")
        if original[offset:offset+len(raw)] != raw:
            raise AssertionError(f"Source ROM CP932 differs at 0x{offset:X}")
        end = offset + len(raw)
        if original[end:end+2] != bytes.fromhex("81 6F"):
            raise AssertionError("Original Fortune native 816F line terminator absent")
        # SNES LoROM physical 0x28000..0x2FFFF -> bank $85:$8000..$FFFF.
        # Find low-word and 24-bit pointer-shaped matches to EITHER the
        # textual glyph start or a hypothetical four-byte native header.
        # They are HYPOTHESES, never proof of an actual pointer table.
        shapes = {}
        for displacement in (0, -4):
            target = offset + displacement
            bank = target // 0x8000 | 0x80
            addr = 0x8000 + (target % 0x8000)
            low = addr.to_bytes(2, "little")
            long = low + bytes((bank,))
            positions_low = []
            start = 0
            while True:
                found = original.find(low, start)
                if found < 0:
                    break
                if len(positions_low) < 24:
                    positions_low.append(f"0x{found:X}")
                start = found + 1
            positions_long = []
            start = 0
            while True:
                found = original.find(long, start)
                if found < 0:
                    break
                if len(positions_long) < 24:
                    positions_long.append(f"0x{found:X}")
                start = found + 1
            shapes[f"source{displacement:+d}"] = {
                "hypothetical_CPU_address": f"${bank:02X}:{addr:04X}",
                "raw_16bit_matches_limited_to_24": positions_low,
                "raw_24bit_matches_limited_to_24": positions_long,
                "pointer_validated": False,
                "controlling_instruction_verified": False,
            }
        references.append({
            "source_offset": row["file_offset"],
            "original_CP932_byte_match": True,
            "original_816F_terminator_match": True,
            "unproven_pointer_shapes": shapes,
        })
    return {
        "status": "ORIGINAL_ROM_BYTE_ANCHORS_VERIFIED_POINTERS_UNPROVEN",
        "original_ROM_sha256": SOURCE_SHA,
        "records": references,
        "safe_relocation_write_permitted": False,
        "gameplay_rendered": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=ROOT)
    parser.add_argument("--original-sfc", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    qa = audit(args.project_root)
    if args.original_sfc:
        qa["original_ROM_hypothesis_scan"] = inspect_source_rom(
            args.original_sfc.read_bytes(), args.project_root)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(qa, ensure_ascii=False, indent=2)+"\n",
                               encoding="utf-8")
    print(json.dumps(qa, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
