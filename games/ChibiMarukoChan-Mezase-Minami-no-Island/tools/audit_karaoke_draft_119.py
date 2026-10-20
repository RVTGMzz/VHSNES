#!/usr/bin/env python3
"""Checkpoint119: audit five Japanese-grounded edits applied to draft CSV only.

Does not read a ROM, create an IPS, certify lyric syllable timing or alter the
already-built checkpoint118 release. The original Japanese and vi_full fields
remain authoritative; the singable column is an untested editorial draft.
"""
from __future__ import annotations

import argparse
import json
import unicodedata
from pathlib import Path

from audit_karaoke_source_104 import ROOT, SOURCE, DRAFT, audit as source_audit, read_rows

MANIFEST = "translation/runtime/karaoke_draft_editorial_117.json"
RUNTIME_113 = "translation/runtime/karaoke_semantic_113.json"
EXPECTED = {0x2B47D, 0x2B4FA, 0x2B622, 0x2B675, 0x2B69D}


def audit(root: Path = ROOT) -> dict:
    source_report = source_audit(root)
    manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    if (manifest.get("schema") != "chibi.karaoke.singable_editorial_117.v1"
            or manifest.get("source_inventory") != SOURCE
            or manifest.get("draft_inventory") != DRAFT
            or manifest.get("runtime_override") != RUNTIME_113
            or manifest.get("source_104_audit") != "tools/audit_karaoke_source_104.py"
            or len(manifest.get("changes", [])) != 5
            or manifest.get("source_only") is not True
            or any(manifest.get(flag) is not False for flag in (
                "canonical_vi_full_changed", "runtime_106_113_changed",
                "stage_116_IPS_changed", "rom_or_ips_built",
                "emulator_tested", "lyric_singability_certified"))):
        raise AssertionError("117 draft-only provenance/release safety contract drift")

    source = read_rows(root, SOURCE,
                       ("file_offset", "source_jp", "vi_full", "status", "notes"))
    draft = read_rows(root, DRAFT,
                      ("file_offset", "source_jp", "vi_full",
                       "vi_singable_v1", "status", "notes"))
    original_by_offset = {int(row["file_offset"], 16): row for row in source}
    draft_by_offset = {int(row["file_offset"], 16): row for row in draft}
    offsets = [int(row["source_offset"], 16) for row in manifest["changes"]]
    if len(offsets) != len(set(offsets)) or set(offsets) != EXPECTED:
        raise AssertionError("117 five editorial source identities changed")

    for item in manifest["changes"]:
        off = int(item["source_offset"], 16)
        src, row = original_by_offset[off], draft_by_offset[off]
        before, after = item["previous_draft"], item["revised_draft"]
        if (src["source_jp"] != item["original_Japanese"]
                or row["source_jp"] != src["source_jp"]
                or row["vi_full"] != src["vi_full"]
                or row["vi_singable_v1"] != after
                or before == after):
            raise AssertionError(f"Japanese/source/draft mismatch at {off:05X}")
        if (not item.get("whitespace_token_count_preserved")
                or len(before.split()) != len(after.split())):
            raise AssertionError(f"Draft phrase count changed at {off:05X}")
        if (not item.get("meaning_guard")
                or after != unicodedata.normalize("NFC", after)
                or any(ord(ch) < 32 or ord(ch) == 127 for ch in after)):
            raise AssertionError(f"Editorial safety guard failed at {off:05X}")

    # The separately reviewed runtime113 obligation fix is already in 118.
    # Do not accidentally replace it with a proposed, untested singable line.
    runtime = json.loads((root / RUNTIME_113).read_text(encoding="utf-8"))
    if (runtime.get("source_offset") != "0x2B675"
            or runtime.get("original_Japanese") != original_by_offset[0x2B675]["source_jp"]
            or runtime.get("Vietnamese") != "Phải làm ngay, khi vẫn còn kịp"):
        raise AssertionError("Protected runtime113 karaoke correction changed")

    return {
        "status": "PASS_119_FIVE_DRAFT_EDITS_SOURCE_ONLY",
        "canonical_Japanese_source_rows": len(source),
        "draft_rows_aligned": len(draft),
        "meaning_restorations_applied_to_draft": len(offsets),
        "corrected_offsets": [f"0x{x:05X}" for x in sorted(offsets)],
        "repeated_refrain_groups_consistent":
            source_report["repeated_refrain_groups_consistent"],
        "canonical_vi_full_unchanged": True,
        "runtime113_override_unchanged": True,
        "ROM_or_IPS_built": False,
        "emulator_tested": False,
        "syllable_timing_certified": False,
        "whole_game_complete": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = audit(args.root)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                               encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
