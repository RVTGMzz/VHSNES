#!/usr/bin/env python3
"""Checkpoint082: restore two omitted Quiz narration facts in original staged fields.

Source-only CI and a fail-closed optional post-081 ROM overlay. Never rewrite
old stage058 records, font, Japanese opcode separators or source game files.
This is NOT gameplay/emulator acceptance.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from build_content_first_040_fortune import make_ips, apply_ips
from build_quiz_parent_semantic_restore_080 import read_codepage, encode

ROOT = Path(__file__).resolve().parent.parent
CLEAN_SHA = "e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
MANIFEST = "translation/runtime/quiz_parent_semantic_restore_082.json"
STAGE = "translation/runtime/quiz_content_first_67_058.json"
SOURCE_CSV = "translation/source/quiz_batch03_part2_vi.csv"
# Native source = original 0E 00 0F xx header at source-4. Exact Japanese
# glyph spans verified at rebuild against the user's SHA-pinned Japanese ROM.
EXPECTED = {
    0x328E5: (0x328E1, [(0x328EB, 14), (0x3290F, 8), (0x32929, 9)]),
    0x32A38: (0x32A34, [(0x32A40, 13), (0x32A62, 12), (0x32A82, 14)]),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def audit(root: Path) -> dict:
    plan = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    if (plan.get("schema") != "chibi.quiz.parent_semantic_restore.082.v1"
        or plan.get("original_clean_ROM_sha256") != CLEAN_SHA
        or plan.get("emulator_tested") is not False
        or plan.get("production_approved") is not False
        or plan.get("new_independent_scanner_IDs") != 0
        or len(plan.get("records", [])) != 2):
        raise AssertionError("082 semantic manifest/release status changed")

    old_stage = json.loads((root / STAGE).read_text(encoding="utf-8"))
    if old_stage.get("candidate_count") != 67:
        raise AssertionError("Historical 058 stage identity changed")
    old = {int(row["file_offset"], 0): row for row in old_stage["records"]}
    with (root / SOURCE_CSV).open(encoding="utf-8-sig", newline="") as f:
        sources = {int(row["file_offset"], 0): row for row in csv.DictReader(f)}
    mapping = read_codepage(root)
    seen = set()
    frames = changed = cells = 0
    for entry in plan["records"]:
        src = int(entry["source"], 0)
        if src in seen or src not in EXPECTED:
            raise AssertionError("Unexpected or duplicate native parent")
        seen.add(src)
        native, locations = EXPECTED[src]
        if (int(entry["native_start"], 0) != native
            or entry.get("stage") != "058"
            or len(entry.get("glyphs", [])) != 3
            or src not in old or src not in sources):
            raise AssertionError("Quiz native field/stage/source drift")
        previous = old[src]
        if (previous["source_jp_scanner"] != sources[src]["source_jp_scanner"]
            or previous["vi_full_reference"] != sources[src]["vi_full"]
            or previous["vi_runtime_lines"] != [g["old"] for g in entry["glyphs"]]):
            raise AssertionError("Canonical source or old 058 captions changed")
        for frame, (offset, cap) in zip(entry["glyphs"], locations):
            if (int(frame["at"], 0) != offset
                or frame["capacity"] != cap
                or len(frame["jp"].encode("cp932")) != 2 * cap):
                raise AssertionError("Japanese source glyph offset/capacity drift")
            before = encode(frame["old"], cap, mapping)
            after = encode(frame["vi"], cap, mapping)
            changed += int(before != after)
            frames += 1
            cells += cap

    if seen != set(EXPECTED) or frames != 6 or changed != 5 or cells != 70:
        raise AssertionError("082 actual corrected physical record count changed")
    if (plan["original_fixed_width_cells"] != cells
        or plan["changed_glyph_frames"] != changed
        or plan["original_physical_glyph_frames"] != frames):
        raise AssertionError("082 original widths/review metadata drift")
    return {
        "status": "PASS_082_ROM_FREE_TWO_QUIZ_SEMANTIC_REPAIRS",
        "existing_native_Quiz_explanation_records": 2,
        "original_physical_caption_frames": 6,
        "corrected_caption_frames": 5,
        "original_fixed_width_glyph_cells": 70,
        "newly_accepted_Quiz_scanner_source_IDs": 0,
        "emulator_tested": False,
        "ROM_or_IPS_written": False,
    }


def build(clean: bytes, baseline: bytes, root: Path):
    if len(clean) != 0x200000 or sha(clean) != CLEAN_SHA or len(baseline) != len(clean):
        raise ValueError("Exact 2 MiB headerless original Japanese SFC required")
    report = audit(root)
    if int.from_bytes(baseline[0x2975E:0x29760], "little") != 0x9A74:
        raise AssertionError("Actual stage061 Vietnamese V2 font lookup absent")
    mapping = read_codepage(root)
    plan = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    output = bytearray(baseline)
    allowed = set(range(0x7FDC, 0x7FE0))
    offsets = set()
    for entry in plan["records"]:
        source = int(entry["source"], 0)
        native, _ = EXPECTED[source]
        # Verify original Quiz native-script header and discover the actual
        # original 16-bit LoROM pointer, never write guessed pointer offsets.
        if (clean[native:native + 2] != bytes.fromhex("0E 00")
            or baseline[native:native + 4] != clean[native:native + 4]):
            raise AssertionError("Expected native Quiz record header changed")
        cpu_ptr = (0x8000 + native - 0x30000).to_bytes(2, "little")
        pointers = [p for p in range(0x31100, 0x31500)
                    if clean[p:p + 2] == cpu_ptr]
        if not pointers or any(baseline[p:p + 2] != cpu_ptr for p in pointers):
            raise AssertionError("Original native Quiz LoROM pointer missing/modified")
        for part in entry["glyphs"]:
            offset, cap = int(part["at"], 0), part["capacity"]
            original = part["jp"].encode("cp932")
            if clean[offset:offset + 2 * cap] != original:
                raise AssertionError(f"Original Japanese physical slot mismatch at {offset:05X}")
            expected_old = encode(part["old"], cap, mapping)
            if baseline[offset:offset + 2 * cap] != expected_old:
                raise AssertionError("082 requires EXACT already-staged post081 V2 old caption")
            proposed = encode(part["vi"], cap, mapping)
            if proposed == expected_old:
                continue
            # Verify new letters actually have real V2 font lookup entries.
            for ch in set(part["vi"] + " "):
                index = int(mapping[ch][-2:], 16)
                font_ptr = 0x28000 + 0x1A74 + 2 * (index - 0x40)
                if int.from_bytes(baseline[font_ptr:font_ptr + 2], "little") == 0:
                    raise AssertionError(f"Missing installed Vietnamese V2 glyph {ch!r}")
            region = set(range(offset, offset + 2 * cap))
            if region & offsets:
                raise AssertionError("Overlapping original Quiz text spans")
            offsets |= region
            output[offset:offset + 2 * cap] = proposed
            allowed |= region
    # Only after the exact source/old-font/old-caption checks succeed.
    output[0x7FDC:0x7FE0] = bytes(4)
    checksum = (sum(output) + 0x1FE) & 0xFFFF
    output[0x7FDC:0x7FDE] = (checksum ^ 0xFFFF).to_bytes(2, "little")
    output[0x7FDE:0x7FE0] = checksum.to_bytes(2, "little")
    final = bytes(output)
    differences = {i for i, (a, b) in enumerate(zip(baseline, final)) if a != b}
    if differences - allowed:
        raise AssertionError("082 changed data outside approved five lines and checksum")
    patch, records = make_ips(clean, final)
    if apply_ips(clean, patch) != final:
        raise AssertionError("082 original-ROM cumulative IPS replay mismatch")
    return patch, {
        **report,
        "status": "082_TWO_PREEXISTING_QUIZ_EXPLANATIONS_FIXED_STATIC_ONLY",
        "input_ROM_sha256": sha(baseline),
        "candidate_ROM_sha256": sha(final),
        "cumulative_clean_ROM_IPS_sha256": sha(patch),
        "final_IPS_record_count": records,
        "final_IPS_bytes": len(patch),
        "changed_ROM_bytes_including_checksum": len(differences),
        "LoROM_checksum": f"0x{checksum:04X}",
        "emulator_tested": False,
        "release_approved": False,
        "copyrighted_ROM_written": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("clean_original_Japanese_SFC", type=Path, nargs="?")
    parser.add_argument("--baseline-ips", type=Path)
    parser.add_argument("--project-root", type=Path, default=ROOT)
    parser.add_argument("--ips", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--audit-only", action="store_true")
    parser.add_argument("--allow-untested", action="store_true")
    args = parser.parse_args()
    if args.audit_only:
        print(json.dumps(audit(args.project_root), ensure_ascii=False, indent=2))
        return
    if not args.allow_untested or not all((args.clean_original_Japanese_SFC, args.baseline_ips, args.ips, args.report)):
        parser.error("Requires original SFC, post081 IPS, two output paths and --allow-untested")
    paths = [args.clean_original_Japanese_SFC, args.baseline_ips, args.ips, args.report]
    if len({p.resolve() for p in paths}) != 4:
        parser.error("Do not overwrite a game ROM or prior IPS")
    clean = args.clean_original_Japanese_SFC.read_bytes()
    baseline = apply_ips(clean, args.baseline_ips.read_bytes())
    ips, qa = build(clean, baseline, args.project_root)
    args.ips.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.ips.write_bytes(ips)
    args.report.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(qa, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
