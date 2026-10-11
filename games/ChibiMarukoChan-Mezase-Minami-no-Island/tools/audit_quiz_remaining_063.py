#!/usr/bin/env python3
"""Read-only Chibi SNES Quiz triage: all 381 sources vs staged 041..061.

No copyrighted bytes are written. This only establishes byte boundaries and
remaining source capacity, not Vietnamese font rendering or emulator success.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLEAN_SHA = "e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
SOURCE_FILES = (
    "quiz_batch01_part1_vi.csv", "quiz_batch01_part2_vi.csv",
    "quiz_batch02_part1_vi.csv", "quiz_batch02_part2_vi.csv",
    "quiz_batch02_part3_vi.csv", "quiz_batch03_part1_vi.csv",
    "quiz_batch03_part2_vi.csv", "quiz_batch03_part3_vi.csv",
)
STAGED = (
    ("041", "quiz_answers_exact_fit_041.csv", "csv"),
    ("047", "quiz_fortune_exactfit_047.json", "mixed"),
    ("054", "quiz_content_first_54_054.json", "json"),
    ("057", "quiz_content_first_50_057.json", "json"),
    ("058", "quiz_content_first_67_058.json", "json"),
    ("059", "quiz_content_first_37_059.json", "json"),
    ("060", "quiz_content_first_21_060.json", "json"),
    ("061", "quiz_content_first_19_061.json", "json"),
)
EXPECTED_COUNTS = {
    "041": 21, "047": 15, "054": 54, "057": 50,
    "058": 67, "059": 34, "060": 21, "061": 17,
}
EXPECTED_UNSAFE_SOURCE_STARTS = {
    0x34403, 0x34A99, 0x352AC, 0x352C2, 0x353F3,
    0x35A69, 0x35DB3, 0x361A4, 0x364B1, 0x33B8D,
}
EXPECTED_PADDING_SOURCES = {
    0x34245, 0x31E50, 0x31E7B, 0x32874, 0x33050,
    0x338D8, 0x338F7, 0x33AC5, 0x33C27, 0x33C3E, 0x33C55,
}
UNAPPROVED_062 = {0x338D8, 0x338F7, 0x33AC5, 0x33C27, 0x33C3E, 0x33C55}


def load_csv(file: Path):
    with file.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def key(offset: str) -> int:
    x = int(offset, 0)
    if not 0 <= x < 0x200000:
        raise AssertionError("Invalid original ROM source offset")
    return x


def scan_native(rom: bytes, offset: int):
    i = left = offset
    frames, markers = [], []
    while i < offset + 280:
        first = rom[i]
        if first < 0x20:
            break
        if rom[i:i+2] == b"\x81\x6f":
            frames.append((left, i))
            markers.append(i)
            i += 2
            left = i
            continue
        if first == 0x20:
            i += 1
            continue
        if ((0x81 <= first <= 0x9F or 0xE0 <= first <= 0xFC)
                and i + 1 < len(rom) and rom[i + 1] >= 0x40):
            i += 2
            continue
        raise ValueError("not an independent CP932 text boundary")
    else:
        raise ValueError("source text exceeds 280-byte safety bound")
    if i > left:
        frames.append((left, i))
    if not frames or not markers or rom[i] >= 0x20:
        raise ValueError("source does not finish at an independently safe script stop")
    capacities, trailing_ascii, approved_slots = [], [], []
    for a, b in frames:
        raw = rom[a:b]
        lead = len(raw) - len(raw.lstrip(b" "))
        tail = len(raw) - len(raw.rstrip(b" ")) if lead < len(raw) else 0
        start, end = a+lead, b-tail
        if (end-start) % 2:
            raise ValueError("original text contains odd-width bytes")
        capacities.append((end-start)//2)
        trailing_ascii.append(tail)
        approved_slots.append([start, end])
    return {
        "line_count": len(frames),
        "native_markers": [f"0x{x:X}" for x in markers],
        "glyph_cell_capacity": capacities,
        "trailing_ascii_pad_bytes": trailing_ascii,
        "text_byte_spans": approved_slots,
    }


def run(clean: bytes, root: Path):
    if len(clean) != 0x200000 or hashlib.sha256(clean).hexdigest() != CLEAN_SHA:
        raise ValueError("Exact original Japanese 2MiB Chibi Maruko ROM required")
    # The 0xFF region is physical blank storage, not verified free code space.
    # Its addressing/pointer mechanism and game runtime uses are not proven.
    candidate_ff_start, candidate_ff_end = 0x36907, 0x38000
    if clean[candidate_ff_start:candidate_ff_end] != b"\xff" * 5881:
        raise AssertionError("Original Quiz bank-end 0xFF fill changed")
    source = {}
    for fname in SOURCE_FILES:
        for row in load_csv(root/"translation/source"/fname):
            off = key(row["file_offset"])
            if off in source or not row.get("vi_full") or not row.get("source_jp_scanner"):
                raise AssertionError(f"Duplicate or incomplete original Quiz source: {off:X}")
            source[off] = {"file": fname, "source_jp_scanner": row["source_jp_scanner"],
                           "vi_full": row["vi_full"]}
    if len(source) != 381:
        raise AssertionError(f"Original Quiz inventory drift: {len(source)} (expected 381)")

    selected = {}
    counts = {}
    for stage, fname, typ in STAGED:
        path = root/"translation/runtime"/fname
        rows = load_csv(path) if typ == "csv" else json.loads(
            path.read_text(encoding="utf-8"))["records"]
        if typ == "mixed":
            rows = [r for r in rows if r.get("category") == "quiz"]
        for row in rows:
            off = key(row["file_offset"])
            if off not in source or off in selected:
                raise AssertionError(f"Staged Quiz duplicates/unknown address: 0x{off:X}")
            selected[off] = stage
        counts[stage] = len(rows)
        if counts[stage] != EXPECTED_COUNTS[stage]:
            raise AssertionError(f"Stage {stage} total changed: {counts[stage]}")
    if len(selected) != 279:
        raise AssertionError("Expected 279 staged distinct Quiz source addresses")

    remaining = sorted(set(source) - set(selected))
    if len(remaining) != 102:
        raise AssertionError(f"Expected 102 genuinely unselected Quiz sources: {len(remaining)}")
    result = []
    unsafe = set()
    padded = set()
    for off in remaining:
        record = {"file_offset": f"0x{off:X}", "source_file": source[off]["file"],
                  "canonical_vi": source[off]["vi_full"]}
        try:
            physical = scan_native(clean, off)
            record.update(physical)
            record["source_status"] = "text_frames_byte_valid_not_renderer_approved"
            if any(physical["trailing_ascii_pad_bytes"]):
                padded.add(off)
                record["padding_policy"] = (
                    "unapproved_062_visual_probe" if off in UNAPPROVED_062 else
                    "must_review_overlaps_and_layout_before_using_padding")
            else:
                record["padding_policy"] = "none_require_accurate_fit_or_relocation"
        except ValueError as exc:
            unsafe.add(off)
            record["source_status"] = "unsafe_scanner_offset_do_not_patch_independently"
            record["failure_reason"] = str(exc)
        result.append(record)
    if unsafe != EXPECTED_UNSAFE_SOURCE_STARTS:
        raise AssertionError("Original CP932 scanner-safe/unsafe offsets changed")
    if padded != EXPECTED_PADDING_SOURCES:
        raise AssertionError("Exact native ASCII padding inventory changed")
    totals = {
        "status": "PASS_SOURCE_ROM_INVENTORY_NOT_EMULATOR_QA",
        "original_clean_ROM_SHA256": CLEAN_SHA,
        "canonical_quiz_source_count": len(source),
        "staged_quiz_distinct_offsets": len(selected),
        "current_remaining_unstaged": len(remaining),
        "independent_CP932_text_frame_starts": 92,
        "unsafe_scanner_starts_not_standalone_patchable": len(unsafe),
        "remaining_records_with_trailing_ASCII_padding": len(padded),
        "unapproved_062_padding_experiments_already_catalogued": len(UNAPPROVED_062),
        "other_padded_fragments_needing_overlap_review": len(padded - UNAPPROVED_062),
        "records_without_trailing_ascii_padding": 81,
        "bank_end_0xFF_fill_candidate": {
            "start": "0x36907", "end_exclusive": "0x38000", "bytes": 5881,
            "approved_as_relocation_storage": False,
            "script_pointer_relocation_understood": False,
            "altered_in_this_audit": False,
        },
        "stage_counts": counts,
        "emulator_tested": False,
        "patch_generated": False,
        "full_game_translated": False,
    }
    assert totals["independent_CP932_text_frame_starts"] == sum(
        x["source_status"] == "text_frames_byte_valid_not_renderer_approved" for x in result)
    return {"summary": totals, "remaining": result}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("clean_original_japanese_rom", type=Path)
    ap.add_argument("--project-root", type=Path, default=ROOT)
    ap.add_argument("--report", type=Path)
    args = ap.parse_args()
    report = run(args.clean_original_japanese_rom.read_bytes(), args.project_root)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n",
                               encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
