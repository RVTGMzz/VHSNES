#!/usr/bin/env python3
"""Checkpoint 086: seven original Quiz explanation fixes without touching stage057 hashes.

No ROM-free check claims gameplay acceptance. Optional original Japanese SFC
builder requires SHA-pinned exact 2 MiB original and a genuine post085 V2
baseline, checks actual CP932 frames, historical V2 bytes, and restores only
the reviewed 16 existing caption spans plus native SNES checksum.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from build_content_first_040_fortune import apply_ips, make_ips
from build_content_first_057_quiz_50 import native_frames
from build_quiz_parent_semantic_restore_080 import read_codepage, encode

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = "translation/runtime/quiz_context_semantics_086.json"
STAGE = "translation/runtime/quiz_content_first_50_057.json"
CLEAN_SHA = "e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
APPROVED = {
    0x35AC3: (9, 9, 9),
    0x35B94: (11, 4),
    0x35C63: (9, 7, 9),
    0x35EDE: (12, 4),
    0x35F38: (14, 14, 14),
    0x360FA: (12, 13, 13),
    0x36661: (11, 11, 6),
}
SOURCE_CSV_FILES = (
    "translation/source/quiz_batch02_part2_vi.csv",
    "translation/source/quiz_batch02_part3_vi.csv",
)

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def audit(root: Path) -> dict:
    manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    rows = manifest.get("records", [])
    if (manifest.get("schema") != "chibi.quiz.context_semantics.086.v1"
        or manifest.get("original_clean_ROM_sha256") != CLEAN_SHA
        or manifest.get("apply_after") != "085 cumulative V2 Quiz candidate"
        or manifest.get("source_history_immutable") is not True
        or manifest.get("original_source_parent_count") != 7
        or manifest.get("original_physical_frame_count") != 19
        or manifest.get("revised_existing_caption_count") != 16
        or manifest.get("original_fixed_glyph_cells") != 191
        or manifest.get("new_canonical_scanner_source_IDs") != 0
        or manifest.get("emulator_tested") is not False
        or manifest.get("release_approved") is not False
        or manifest.get("actual_binary_patch_produced_this_session") is not False
        or len(rows) != 7):
        raise AssertionError("086 pinned stage/content/non-release contract drift")
    previous = {
        int(v["file_offset"], 0): v
        for v in json.loads((root / STAGE).read_text(encoding="utf-8"))["records"]
    }
    sources = {}
    for filename in SOURCE_CSV_FILES:
        with (root / filename).open(encoding="utf-8-sig", newline="") as file:
            for line in csv.DictReader(file):
                at = int(line["file_offset"], 0)
                if at in sources:
                    raise AssertionError("Duplicate original Quiz source")
                sources[at] = (filename, line)
    mapped = read_codepage(root)
    unique = set()
    changed = 0
    frame_count = 0
    glyph_count = 0
    reviewed = []
    for rec in rows:
        at = int(rec["original_source_offset"], 0)
        if at not in APPROVED or at in unique:
            raise AssertionError("Repeated/unapproved stage057 Quiz field")
        unique.add(at)
        prior = previous.get(at)
        source = sources.get(at)
        caps = rec["original_two_byte_glyph_cell_caps"]
        old = rec["previous_native_V2_captions"]
        new = rec["revised_native_V2_captions"]
        if (rec.get("historical_stage") != "057"
            or prior is None or prior.get("vi_runtime_lines") != old
            or prior.get("status") !=
                "clean_rom_source_verified_pending_056_baseline_and_emulator"
            or tuple(caps) != APPROVED[at]
            or len(old) != len(caps) or len(new) != len(caps)
            or not rec.get("editorial_reason")
            or source is None
            or source[0] != rec["source_file"]
            or source[1]["source_jp_scanner"] != rec["original_japanese_scanner"]
            or source[1]["vi_full"] != rec["canonical_vi_full"]):
            raise AssertionError(f"Original 057/canonical CSV drift at 0x{at:X}")
        scanner_frames = [x.strip() for x in
                          rec["original_japanese_scanner"].split("｛")
                          if x.strip()]
        if (len(scanner_frames) != len(caps)
            or [len(s) for s in scanner_frames] != caps):
            raise AssertionError(f"Actual Japanese text slots drift at 0x{at:X}")
        this_changed = 0
        for cap, prev, curr in zip(caps, old, new):
            before = encode(prev, cap, mapped)
            after = encode(curr, cap, mapped)
            this_changed += int(before != after)
            frame_count += 1
            glyph_count += cap
        changed += this_changed
        reviewed.append({
            "original_source_offset": f"0x{at:X}",
            "original_two_byte_glyph_capacities": caps,
            "changed_existing_caption_frames": this_changed,
            "previous": old,
            "revised": new,
        })
    if (unique != set(APPROVED) or changed != 16
        or frame_count != 19 or glyph_count != 191):
        raise AssertionError("086 counts don't match seven original native fields")
    return {
        "status": "PASS_086_SEVEN_QUIZ_NATIVE_SEMANTIC_REPAIRS_SOURCE_ONLY",
        "reviewed_prior_stage057_source_records": 7,
        "changed_existing_V2_caption_frames": changed,
        "original_native_text_frames": frame_count,
        "original_native_V2_glyph_cells": glyph_count,
        "new_canonical_Quiz_source_offsets": 0,
        "historical_stage057_manifest_edited": False,
        "ROM_or_IPS_generated_by_source_audit": False,
        "SNES_emulator_tested": False,
        "records": reviewed,
    }

def build(clean: bytes, baseline: bytes, root: Path):
    if len(clean) != 0x200000 or digest(clean) != CLEAN_SHA:
        raise ValueError("Wrong Japanese retail ROM: need exact 2MiB original SHA")
    if len(baseline) != len(clean):
        raise ValueError("Incorrect previous cumulative V2 ROM size")
    qa = audit(root)
    if int.from_bytes(baseline[0x2975E:0x29760], "little") != 0x9A74:
        raise AssertionError("Required prior V2 font address not installed")
    mapped = read_codepage(root)
    manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    updated = bytearray(baseline)
    changed_lines = 0
    allowed = set(range(0x7FDC, 0x7FE0))
    markers_checked = 0
    for record in manifest["records"]:
        at = int(record["original_source_offset"], 0)
        native_start = at - 4
        # Quizzing script is part of one of the genuine native bank tables.
        # Verify the record header and that a 16-bit original LoROM pointer
        # into the record exists; never relocate without proven ownership.
        if (clean[native_start:native_start+2] != b"\x0e\x00"
            or baseline[native_start:at] != clean[native_start:at]):
            raise AssertionError(f"Original Quiz script header drift: 0x{at:X}")
        pointer_word = (0x8000 + native_start - 0x30000).to_bytes(2, "little")
        refs = [p for p in range(0x31100, 0x31500)
                if clean[p:p+2] == pointer_word]
        if not refs or any(baseline[p:p+2] != pointer_word for p in refs):
            raise AssertionError(f"Original native Quiz pointer missing: 0x{at:X}")
        frames, markers, stop = native_frames(clean, at)
        caps = record["original_two_byte_glyph_cell_caps"]
        if len(frames) != len(caps) or len(markers) < len(caps) - 1:
            raise AssertionError("Original 816F native line frame count drift")
        jp_scanner = [s.strip() for s in
                      record["original_japanese_scanner"].split("｛") if s.strip()]
        for frame_i, ((left, right), cap, old, new, jp) in enumerate(zip(
            frames, caps, record["previous_native_V2_captions"],
            record["revised_native_V2_captions"], jp_scanner
        )):
            physical = clean[left:right]
            lead = len(physical)-len(physical.lstrip(b" "))
            tail = len(physical)-len(physical.rstrip(b" ")) if lead<len(physical) else 0
            start, end = left+lead, right-tail
            if (len(clean[start:end]) != cap*2
                or clean[start:end] != jp.encode("cp932")):
                raise AssertionError(f"Actual Japanese glyph bytes mismatch 0x{at:X} line {frame_i}")
            previous_bytes = encode(old, cap, mapped)
            new_bytes = encode(new, cap, mapped)
            if baseline[start:end] != previous_bytes:
                raise AssertionError("Genuine post085 V2 stage lacks expected previous Quiz caption")
            if previous_bytes == new_bytes:
                continue
            area = set(range(start, end))
            if area & allowed:
                raise AssertionError("Illegal overlap with previous 086 Quiz field")
            for letter in set(new+" "):
                idx = int(mapped[letter][-2:], 16)
                look = 0x28000 + 0x1A74 + 2*(idx-0x40)
                if int.from_bytes(baseline[look:look+2], "little") == 0:
                    raise AssertionError(f"Real V2 font glyph is absent for {letter!r}")
            allowed.update(area)
            updated[start:end] = new_bytes
            changed_lines += 1
        for marker in markers:
            if clean[marker:marker+2] != b"\x81\x6f" or baseline[marker:marker+2] != b"\x81\x6f":
                raise AssertionError("Native 816F Quiz control modified")
        markers_checked += len(markers)
    if changed_lines != 16:
        raise AssertionError("086 changed different native caption count")
    updated[0x7FDC:0x7FE0] = bytes(4)
    checksum = (sum(updated)+0x1FE) & 0xFFFF
    updated[0x7FDC:0x7FDE] = (checksum ^ 0xFFFF).to_bytes(2, "little")
    updated[0x7FDE:0x7FE0] = checksum.to_bytes(2, "little")
    final = bytes(updated)
    changes = {i for i,(a,b) in enumerate(zip(baseline,final)) if a != b}
    if changes - allowed:
        raise AssertionError("086 modified bytes outside reviewed Quiz V2 captions/checksum")
    ips,n = make_ips(clean, final)
    if apply_ips(clean, ips) != final:
        raise AssertionError("086 final clean-ROM cumulative IPS replay failed")
    qa.update({
        "status": "086_STATIC_REBUILT_CANDIDATE_NOT_EMULATOR_VERIFIED",
        "candidate_ROM_sha256": digest(final),
        "cumulative_clean_IPS_sha256": digest(ips),
        "cumulative_IPS_bytes": len(ips),
        "cumulative_IPS_records": n,
        "verified_native_816F_markers": markers_checked,
        "modified_baseline_bytes_including_checksum": len(changes),
        "final_SNES_checksum": f"0x{checksum:04X}",
        "SNES_emulator_tested": False,
        "release_approved": False,
    })
    return ips, qa

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project-root", type=Path, default=ROOT)
    ap.add_argument("--audit-only", action="store_true")
    ap.add_argument("--original-sfc", type=Path)
    ap.add_argument("--post085-ips", type=Path)
    ap.add_argument("--ips", type=Path)
    ap.add_argument("--report", type=Path)
    ap.add_argument("--allow-untested", action="store_true")
    args = ap.parse_args()
    if args.audit_only:
        print(json.dumps(audit(args.project_root), ensure_ascii=False, indent=2))
        return
    files=(args.original_sfc,args.post085_ips,args.ips,args.report)
    if not args.allow_untested or any(p is None for p in files):
        ap.error("Requires genuine original SFC, post085 IPS and --allow-untested")
    if len({p.resolve() for p in files}) != 4:
        ap.error("Never overwrite originals or earlier cumulative IPS")
    clean = args.original_sfc.read_bytes()
    baseline = apply_ips(clean, args.post085_ips.read_bytes())
    ips, qa = build(clean, baseline, args.project_root)
    args.ips.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.ips.write_bytes(ips)
    qa["IPS_file_written"] = True
    args.report.write_text(json.dumps(qa, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(qa, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
