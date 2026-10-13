#!/usr/bin/env python3
"""Checkpoint083: name Sugiyama accurately in the existing Ono sailor-dream Quiz.

ROM-free stage058/canonical JP/Unicode audit plus optional fail-closed V2
post-082 cumulative clean-original IPS. No ROM file, no font and no relocation.
Does not claim SNES emulator QA or any new distinct source IDs.
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
MANIFEST = "translation/runtime/quiz_sugiyama_ono_083.json"
STAGE = "translation/runtime/quiz_content_first_67_058.json"
SOURCE = "translation/source/quiz_batch03_part2_vi.csv"
EXPECTED_GLYPHS = ((0x32BCA, 11), (0x32BE8, 13))
EXPECTED_BREAKS = (0x32BC0, 0x32BE0, 0x32C02)

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def audit(root: Path) -> dict:
    plan = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    stage = json.loads((root / STAGE).read_text(encoding="utf-8"))
    if (plan.get("schema") != "chibi.quiz.sugiyama_ono_context.083.v1"
        or plan.get("clean_original_sha256") != CLEAN_SHA
        or plan.get("original_stage") != "058"
        or int(plan.get("source", "0"), 0) != 0x32BBE
        or int(plan.get("native_header", "0"), 0) != 0x32BBA
        or plan.get("source_file") != SOURCE
        or len(plan.get("frames", [])) != 3
        or tuple(int(x, 0) for x in plan.get("original_816f_offsets", [])) != EXPECTED_BREAKS
        or plan.get("changed_existing_V2_frames") != 2
        or plan.get("new_canonical_source_offsets_added") != 0
        or plan.get("emulator_tested") is not False
        or plan.get("release_approved") is not False
        or len(stage.get("records", [])) != 67):
        raise AssertionError("083 Ono native/stage/release source contract drift")
    matches = [row for row in stage["records"]
               if int(row["file_offset"], 0) == 0x32BBE]
    if len(matches) != 1:
        raise AssertionError("Missing exact historical Ono/Sugiyama explanation")
    original_stage = matches[0]
    with (root / SOURCE).open(encoding="utf-8-sig", newline="") as file:
        canonical = [row for row in csv.DictReader(file)
                     if int(row["file_offset"], 0) == 0x32BBE]
    if len(canonical) != 1:
        raise AssertionError("Missing original Ono Quiz source row")
    canonical = canonical[0]
    if (canonical["source_jp_scanner"] != plan["original_source_jp_scanner"]
        or canonical["vi_full"] != plan["source_vi_full"]
        or original_stage["source_jp_scanner"] != canonical["source_jp_scanner"]
        or original_stage["vi_full_reference"] != canonical["vi_full"]
        or original_stage["vi_runtime_lines"] !=
            [item["caption_old"] if i == 0 else item["old"]
             for i, item in enumerate(plan["frames"])]):
        raise AssertionError("Canonical Japanese text / historical captions drift")
    first = plan["frames"][0]
    if (int(first["at"], 0) != 0x32BBE
        or first["kind"] != "ascii_only_indent"
        or first["original_byte_count"] != 2
        or first["caption_old"] != "" or first["caption_new"] != ""):
        raise AssertionError("Original leading indentation is not mutable Quiz text")
    mapping = read_codepage(root)
    changes = 0
    for item, (at, cap) in zip(plan["frames"][1:], EXPECTED_GLYPHS):
        if (int(item["at"], 0) != at or item["capacity"] != cap
            or len(item["jp"].encode("cp932")) != 2*cap):
            raise AssertionError("083 physical 2-byte Japanese Quiz span drift")
        prior = encode(item["old"], cap, mapping)
        update = encode(item["vi"], cap, mapping)
        changes += int(prior != update)
    if changes != 2:
        raise AssertionError("083 must replace exactly two caption frames")
    return {
        "status":"PASS_083_SUGIYAMA_NAMED_IN_ONO_QUIZ_SOURCE_STATIC",
        "old_stage_058_parent_unchanged":True,
        "original_816f_line_breaks":3,
        "changed_V2_caption_frames":changes,
        "corrected_existing_native_parent_count":1,
        "new_Quiz_source_IDs":0,
        "SNES_emulator_tested":False,
        "ROM_or_IPS_written":False,
    }


def build(clean: bytes, baseline: bytes, root: Path):
    if len(clean) != 0x200000 or sha(clean) != CLEAN_SHA or len(baseline) != len(clean):
        raise ValueError("Requires exact headerless original Japanese 2MiB ROM")
    report = audit(root)
    if int.from_bytes(baseline[0x2975E:0x29760], "little") != 0x9A74:
        raise AssertionError("The genuine previous V2 Vietnamese font is missing")
    plan = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    if (clean[0x32BBA:0x32BBE] != baseline[0x32BBA:0x32BBE]
        or clean[0x32BBA:0x32BBC] != bytes.fromhex("0E 00")
        or clean[0x32BBE:0x32BC0] != b"  "
        or clean[0x32BBE:0x32BC2] != baseline[0x32BBE:0x32BC2]):
        raise AssertionError("Original real Ono native script header/layout changed")
    expected_ptr = (0x8000+0x32BBA-0x30000).to_bytes(2, "little")
    locations = [p for p in range(0x31100, 0x31500)
                 if clean[p:p+2] == expected_ptr]
    if not locations or any(baseline[p:p+2] != expected_ptr for p in locations):
        raise AssertionError("Original 16-bit LoROM record pointer absent or modified")
    if any(clean[x:x+2] != b"\x81\x6f"
           or baseline[x:x+2] != b"\x81\x6f" for x in EXPECTED_BREAKS):
        raise AssertionError("Native Quiz 816F separators cannot change")
    mapv2 = read_codepage(root)
    result = bytearray(baseline)
    allowed = set(range(0x7FDC, 0x7FE0))
    for item in plan["frames"][1:]:
        at, cap = int(item["at"], 0), item["capacity"]
        original = item["jp"].encode("cp932")
        if clean[at:at+cap*2] != original:
            raise AssertionError(f"Actual original Quiz JP glyphs mismatch at 0x{at:X}")
        prior = encode(item["old"], cap, mapv2)
        if baseline[at:at+cap*2] != prior:
            raise AssertionError("Previous 082 ROM is missing exact historical V2 caption")
        updated = encode(item["vi"], cap, mapv2)
        for ch in set(item["vi"]+" "):
            idx = int(mapv2[ch][-2:], 16)
            ptr = 0x28000+0x1A74+2*(idx-0x40)
            if int.from_bytes(baseline[ptr:ptr+2], "little") == 0:
                raise AssertionError(f"No real V2 font glyph for {ch!r}")
        result[at:at+2*cap] = updated
        allowed.update(range(at,at+2*cap))
    result[0x7FDC:0x7FE0] = b"\0"*4
    checksum = (sum(result)+0x1FE) & 0xFFFF
    result[0x7FDC:0x7FDE] = (checksum^0xFFFF).to_bytes(2, "little")
    result[0x7FDE:0x7FE0] = checksum.to_bytes(2, "little")
    final = bytes(result)
    diffs = {i for i,(a,b) in enumerate(zip(baseline, final)) if a!=b}
    if diffs - allowed:
        raise AssertionError("083 attempted write outside 2 approved glyph fields/checksum")
    ips, n = make_ips(clean, final)
    if apply_ips(clean, ips) != final:
        raise AssertionError("083 clean-ROM cumulative IPS replay mismatch")
    return ips, {
        **report,
        "status":"083_QUIZ_SUGIYAMA_RESTORED_SOURCE_CANDIDATE_UNTESTED",
        "candidate_ROM_sha256":sha(final),
        "cumulative_clean_ROM_IPS_sha256":sha(ips),
        "cumulative_IPS_bytes":len(ips),
        "cumulative_IPS_records":n,
        "last_stage_checksum":f"0x{checksum:04X}",
        "modified_baseline_ROM_bytes_including_checksum":len(diffs),
        "ROM_or_IPS_written":False,
        "SNES_emulator_tested":False,
        "release_approved":False,
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=ROOT)
    parser.add_argument("--audit-only", action="store_true")
    parser.add_argument("--original-sfc", type=Path)
    parser.add_argument("--previous-cumulative-ips", type=Path)
    parser.add_argument("--ips", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--allow-untested", action="store_true")
    args=parser.parse_args()
    if args.audit_only:
        print(json.dumps(audit(args.project_root), ensure_ascii=False, indent=2))
        return
    paths=[args.original_sfc,args.previous_cumulative_ips,args.ips,args.report]
    if not args.allow_untested or any(x is None for x in paths):
        parser.error("Need exact Japanese SFC, post082 IPS, report and --allow-untested")
    if len({x.resolve() for x in paths}) != 4:
        parser.error("Input and output files must not overlap")
    clean=args.original_sfc.read_bytes()
    previous=apply_ips(clean,args.previous_cumulative_ips.read_bytes())
    ips,qa=build(clean,previous,args.project_root)
    args.ips.parent.mkdir(parents=True,exist_ok=True)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.ips.write_bytes(ips)
    args.report.write_text(json.dumps(qa,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(qa,indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
