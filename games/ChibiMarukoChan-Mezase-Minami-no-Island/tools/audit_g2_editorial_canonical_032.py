#!/usr/bin/env python3
"""Audit canonical Vietnamese meaning rows against all 10 editorial passes.

Content-first checkpoint 032. Does not modify ROM, font, source CSV,
graphics, or historical editorial reviews. Uses stdlib only.

Revision ordering matters: later passes win on overlapping file_offset keys.
CSV inputs may start with UTF-8 BOM. A PASS means every latest editorial
vi_revised is ACTUALLY in translation/source/*.csv vi_full; it does not
mean whole-game translation or SNES runtime acceptance.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "translation/source"
EDITORIAL = ROOT / "translation/editorial"

PASSES = (
    "tone_consistency_pass01.csv",
    "tone_consistency_pass02.csv",
    "tone_consistency_pass03.csv",
    "quiz_naturalness_pass01.csv",
    "tone_consistency_pass04_story_early.csv",
    "tone_consistency_pass05_story_mid.csv",
    "fortune_naturalness_pass01.csv",
    "quiz_naturalness_pass02.csv",
    "ui_menu_naturalness_pass01.csv",
    "ui_auxiliary_pass03.csv",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            raise ValueError(f"no CSV header: {path}")
        rows = list(reader)
    if any(not r.get("file_offset") for r in rows):
        raise ValueError(f"missing ROM-offset source identity in {path}")
    return rows


def audit() -> dict:
    latest: dict[tuple[str, str], tuple[str, dict[str, str]]] = {}
    all_edits = 0
    counts_by_pass: dict[str, int] = {}
    superseded = []
    for name in PASSES:
        path = EDITORIAL / name
        rows = read_csv(path)
        counts_by_pass[name] = len(rows)
        for row in rows:
            source_file = row["apply_to"]
            if Path(source_file).name != source_file or not source_file.endswith(".csv"):
                raise ValueError(f"unsafe canonical target in {name}: {source_file}")
            if not row["vi_revised"].strip():
                raise ValueError(f"empty Vietnamese revision {name}: {row['file_offset']}")
            key = (source_file, row["file_offset"])
            if key in latest:
                superseded.append({
                    "target": source_file,
                    "file_offset": row["file_offset"],
                    "earlier_pass": latest[key][0],
                    "winning_pass": name,
                })
            latest[key] = (name, row)
            all_edits += 1

    touched = sorted({filename for filename, _ in latest})
    actual: dict[str, dict[str, dict[str, str]]] = {}
    source_row_counts: dict[str, int] = {}
    errors: list[dict] = []
    for file in touched:
        path = SOURCE / file
        rows = read_csv(path)
        source_row_counts[file] = len(rows)
        index = {}
        for row in rows:
            off = row["file_offset"]
            if off in index:
                errors.append({"source": file, "file_offset": off, "error": "duplicate_offset"})
            index[off] = row
        actual[file] = index

    for (filename, offset), (winner, ed) in latest.items():
        source_row = actual[filename].get(offset)
        if source_row is None:
            errors.append({"source": filename, "file_offset": offset,
                           "pass": winner, "error": "source_missing"})
            continue
        if not source_row.get("vi_full", "").strip():
            errors.append({"source": filename, "file_offset": offset,
                           "pass": winner, "error": "empty_vi_full"})
            continue
        if source_row["vi_full"] != ed["vi_revised"]:
            errors.append({
                "source": filename, "file_offset": offset,
                "pass": winner, "error": "canonical_editorial_mismatch",
                "expected": ed["vi_revised"], "found": source_row["vi_full"],
            })

    report = {
        "status": "CANONICAL_EDITORIAL_PASS" if not errors else "CANONICAL_EDITORIAL_FAIL",
        "editorial_passes": len(PASSES),
        "revision_events": all_edits,
        "unique_canonical_offsets": len(latest),
        "historical_revisions_superseded": len(superseded),
        "canonical_source_files": len(touched),
        "source_rows_scanned_in_touched_files": sum(source_row_counts.values()),
        "pass_event_counts": counts_by_pass,
        "superseded_detail": superseded,
        "errors": errors,
        "changed_rom_bytes": 0,
        "font_work_this_checkpoint": False,
        "runtime_gameplay_claim": False,
        "release_ready": False,
        "notes": "Meaning layer only; ROM/build, graphics and full-game runtime not certified.",
    }
    if all_edits != 220 or len(latest) != 216 or len(superseded) != 4 or len(touched) != 20:
        report["status"] = "CANONICAL_EDITORIAL_FAIL"
        report["errors"].append({
            "error": "unexpected_editorial_inventory",
            "expected": "220 edits, 216 unique offsets, 4 superseded, 20 files",
        })
    return report


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json", type=Path, help="optional report JSON path")
    args = p.parse_args()
    report = audit()
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(output)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(output, encoding="utf-8")
    return 0 if report["status"] == "CANONICAL_EDITORIAL_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
