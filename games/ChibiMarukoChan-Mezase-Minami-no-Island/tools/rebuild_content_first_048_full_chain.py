#!/usr/bin/env python3
"""Rebuild Chibi 044 -> 045 -> 046 -> 047 -> 048 from exact clean ROM + 043 IPS.

No intermediary ROM is required. Intermediate IPS blobs remain in memory.
Only the final clean-ROM IPS and static report are written. Actual gameplay
is untested; this is a reproducible guarded binary integration tool.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from build_content_first_044_story_87 import build as build044
from build_content_first_045_story_139 import build as build045
from build_content_first_046_story_special import build as build046
from build_content_first_047_quiz_fortune_30 import build as build047
from build_content_first_048_fortune_103 import build as build048
from build_content_first_040_fortune import apply_ips

ROOT = Path(__file__).resolve().parent.parent
ROM_SHA = {
    "044": "2312b9ba52c0cf6ac491e71117d5c537ad7dc61828dc9e87d838826e5165f322",
    "045": "7ddf449c2266838c3d55415f14aeee34fc21334c1ed0a490590647eb75e047b5",
    "046": "c10c0f444a97d6bea7f8f669d67bb6c0c5b6889b654d99d6e6dfa25e3d061624",
    "047": "1f6430064b70671a4f3ba94f0fd256764db54690950519c22d9e03ec74230dd9",
}
IPS_SHA = {
    "043": "d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50",
    "044": "823009a95534b851b238efc439fa39c5b8af6af75a97075d1925e98f879c144d",
    "045": "685d7e9f0146950ca030fd8469f57313a0b368be98e0a9c95999bda48cb65379",
    "046": "11abac1b8e0f48e6580822bcdcd3b1b3568ae08676020b86c819ae641f53367d",
    "047": "725ca433dfeb919bd19bde6903a1e2e7d95cde1889980677863724007090cd6c",
}
CLEAN_SHA = "e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def run(clean: bytes, ips043: bytes, project: Path):
    if len(clean) != 0x200000 or sha(clean) != CLEAN_SHA:
        raise ValueError("Wrong original headerless Japanese ROM")
    if sha(ips043) != IPS_SHA["043"] or len(ips043) != 28135:
        raise ValueError("Wrong checkpoint043 clean-ROM IPS")
    stages = [
        ("044", build044),
        ("045", build045),
        ("046", build046),
        ("047", build047),
    ]
    patch = ips043
    checked = []
    for name, builder in stages:
        rom, next_patch, report = builder(clean, patch, project)
        if sha(rom) != ROM_SHA[name] or sha(next_patch) != IPS_SHA[name]:
            raise AssertionError("stage "+name+" mismatch")
        if apply_ips(clean, next_patch) != rom:
            raise AssertionError("stage "+name+" independent IPS replay failed")
        checked.append({
            "stage": name, "rom_sha256": sha(rom),
            "clean_ips_sha256": sha(next_patch),
            "static_status": report["status"]
        })
        patch = next_patch
    combined, final_ips, report048 = build048(clean, rom, project, False)
    if apply_ips(clean, final_ips) != combined:
        raise AssertionError("final 048 clean-ROM replay failed")
    if not report048["full_047_plus_048_integrated"]:
        raise AssertionError("048 has not integrated full checkpoint047")
    result = {
        "status": "048_FULL_CHAIN_STATIC_VERIFIED_EMULATOR_NOT_TESTED",
        "stages": checked, "final_048": report048,
        "gameplay_tested": False, "release_approved": False,
    }
    return final_ips, result

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("clean_japanese_rom", type=Path)
    p.add_argument("checkpoint043_clean_ips", type=Path)
    p.add_argument("--project-root", type=Path, default=ROOT)
    p.add_argument("--ips", required=True, type=Path)
    p.add_argument("--report", required=True, type=Path)
    p.add_argument("--allow-untested", action="store_true")
    a = p.parse_args()
    if not a.allow_untested:
        p.error("Only byte-level static QA; pass --allow-untested to build")
    paths = [a.clean_japanese_rom, a.checkpoint043_clean_ips, a.ips, a.report]
    if len({v.resolve() for v in paths}) != len(paths):
        p.error("Inputs and outputs must be different files")
    patch, report = run(
        a.clean_japanese_rom.read_bytes(),
        a.checkpoint043_clean_ips.read_bytes(), a.project_root)
    for output, content in [
        (a.ips, patch),
        (a.report, (json.dumps(report, ensure_ascii=False, indent=2)+"\n").encode("utf-8")),
    ]:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(content)
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
