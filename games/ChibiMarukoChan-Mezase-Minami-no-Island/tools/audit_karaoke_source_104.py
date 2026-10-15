#!/usr/bin/env python3
"""Checkpoint 104: source-only Karaoke inventory and cross-layer safety audit.

NO game ROM, IPS, song timing, graphics or emulator is accessed here.
Checks the 28 original source identities and the parallel singable drafts.
Does NOT certify lyrical meaning, byte fit or a playable translation.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OFFSETS = tuple(int(x, 16) for x in (
    "2B380 2B3A8 2B3C0 2B3D5 2B3FD 2B428 2B452 2B47D "
    "2B4A5 2B4BB 2B4D2 2B4FA 2B525 2B54D 2B578 2B5A2 "
    "2B5CD 2B5F5 2B60B 2B622 2B64A 2B675 2B69D "
    "2B6C8 2B6F0 2B71B 2B743 2B76E"
).split())
SOURCE = "translation/source/karaoke_batch01_vi.csv"
DRAFT = "translation/source/karaoke_batch01_singable_v1_vi.csv"
JP_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uff66-\uff9f]")
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
PLACEHOLDER_RE = re.compile(r"\{[A-Za-z0-9_]+\}|%(?:\d+\$)?[-+0-9.]*[sdi]|\\[nrt]")

def read_rows(root: Path, path: str, expected_fields: tuple[str, ...]):
    with (root / path).open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        if tuple(reader.fieldnames or ()) != expected_fields:
            raise AssertionError(f"{path}: unexpected columns")
        rows = list(reader)
    if len(rows) != 28:
        raise AssertionError(f"{path}: expected exactly 28 records, got {len(rows)}")
    offsets = []
    for row in rows:
        if None in row or any(v is None for v in row.values()):
            raise AssertionError(f"{path}: malformed CSV row")
        raw = row["file_offset"]
        if not re.fullmatch(r"0x[0-9A-F]{5}", raw):
            raise AssertionError(f"{path}: malformed canonical source offset {raw!r}")
        offsets.append(int(raw, 16))
        if not row["source_jp"] or not row["vi_full"]:
            raise AssertionError(f"{path}: missing original or translation")
        if CONTROL_RE.search("".join(row.values())):
            raise AssertionError(f"{path}: embedded binary/control character")
        try:
            row["source_jp"].encode("cp932")
        except UnicodeEncodeError as exc:
            raise AssertionError(f"{path}: Japanese source not CP932 encodable") from exc
        for key in ("vi_full", "vi_singable_v1"):
            if key not in row:
                continue
            vi = row[key]
            if not vi.strip() or vi != unicodedata.normalize("NFC", vi):
                raise AssertionError(f"{path}: empty/non-NFC Vietnamese at {raw}")
            if JP_RE.search(vi):
                raise AssertionError(f"{path}: unlocalized Japanese script at {raw}")
            if PLACEHOLDER_RE.findall(row["source_jp"]) != PLACEHOLDER_RE.findall(vi):
                raise AssertionError(f"{path}: source placeholder mismatch at {raw}")
    if tuple(offsets) != OFFSETS:
        raise AssertionError(f"{path}: 28 original offsets reordered/changed")
    return rows

def audit(root: Path = ROOT):
    original = read_rows(root, SOURCE,
        ("file_offset", "source_jp", "vi_full", "status", "notes"))
    singable = read_rows(root, DRAFT,
        ("file_offset", "source_jp", "vi_full", "vi_singable_v1", "status", "notes"))
    for src, draft in zip(original, singable):
        if (src["file_offset"], src["source_jp"], src["vi_full"]) != (
            draft["file_offset"], draft["source_jp"], draft["vi_full"]
        ):
            raise AssertionError(f"Original/source-draft mismatch at {src['file_offset']}")
        if src["status"] != "translated_karaoke_batch01":
            raise AssertionError("Unexpected source translation stage")
        if draft["status"] != "karaoke_singable_draft_v1":
            raise AssertionError("Draft misrepresented as runtime-certified")
        if "timing" not in draft["notes"].lower():
            raise AssertionError("Timing limitations must remain explicit")
    index = {int(row["file_offset"], 16): row for row in singable}
    for repeated in ((0x2B4A5, 0x2B5F5),
                     (0x2B6C8, 0x2B6F0, 0x2B71B, 0x2B743)):
        for key in ("source_jp", "vi_full", "vi_singable_v1"):
            if len({index[off][key] for off in repeated}) != 1:
                raise AssertionError(f"Repeated refrain diverged: {key}")
    return {
        "status": "PASS_KARAOKE_SOURCE_IDENTITY_ONLY",
        "canonical_original_offsets": len(OFFSETS),
        "meaning_first_translated_source_rows": len(original),
        "aligned_singable_draft_rows": len(singable),
        "repeated_refrain_groups_consistent": 2,
        "source_Japanese_cp932_encodable": True,
        "Vietnamese_NFC_and_placeholders_preserved": True,
        "original_ROM_bytes_checked": False,
        "runtime_lyrics_inserted_or_tested": False,
        "syllable_timing_or_singability_certified": False,
        "graphics_and_menu_QA": False,
        "whole_game_complete": False,
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = audit(args.root)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n",
                               encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
