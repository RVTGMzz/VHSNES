#!/usr/bin/env python3
"""Audit one exact user-reported Probe008 025 runtime failure screenshot.

FAIL-CLOSED on another image: crop, viewport scale and target rows are grounded
only for the 2026-10-10 image. No OCR and no emulator CPU trace. Do not
commit the screenshot itself to this repository.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from io import BytesIO
from pathlib import Path

from PIL import Image

EXPECTED_SHA256 = "5fe322fe15746017ee1362daf9ffe0a275344f91b256bdd30732d033ceb62ee0"
ROM_SHA256 = "d4bd629003812578580e7a380e791d87fdf64614441394f1261df3951b9815dc"
LINES = (
    ("Nói thẳng nhé!", 1, 151, 181),
    ("Du học chớ ngại!", 0, 205, 239),
    ("Luyện phản xạ!", 1, 251, 285),
)


def audit(screenshot: bytes) -> dict:
    if hashlib.sha256(screenshot).hexdigest() != EXPECTED_SHA256:
        raise ValueError("FAIL-CLOSED: only exact original screenshot calibrated")
    im = Image.open(BytesIO(screenshot)).convert("RGB")
    if im.size != (952, 381):
        raise AssertionError("unexpected screenshot dimensions")

    # This snapshot has a cropped game viewport at x=154..951; the 256px
    # native width is a working heuristic, NOT a video-mode measurement.
    scale = (952 - 154) / 256
    rows = []
    for label, quotes, y0, y1 in LINES:
        xs = [
            x for y in range(y0, y1) for x in range(165, 920)
            if max(im.getpixel((x, y))) < 85
        ]
        if not xs:
            raise AssertionError("black ink absent in expected row band")
        span = max(xs) - min(xs)
        count = len(label) + quotes
        approx = span / ((count - 1) * scale)
        rows.append({
            "text": label,
            "symbols_including_native_quote": count,
            "black_ink_horizontal_extent_screen_pixels": span,
            "approx_native_px_per_character_interval": round(approx, 2),
            "closer_to": ("13px wide baseline" if abs(approx - 13) < abs(approx - 9)
                          else "9px compact candidate"),
        })
    if any(row["closer_to"] != "13px wide baseline" for row in rows):
        raise AssertionError("original screenshot metrics changed")

    return {
        "status": "USER_EMULATOR_TYPOGRAPHY_FAIL",
        "checkpoint": 26,
        "tested_rom_checkpoint": 25,
        "tested_rom_sha256": ROM_SHA256,
        "exact_screenshot_sha256": EXPECTED_SHA256,
        "pixel_spans": rows,
        "visual_judgment": "Scattered glyph strokes, gaps and accent placement make Vietnamese unreadable",
        "pitch_inference": "Consistent with native 13px fallback rather than intended 9px",
        "pitch_confirmed_by_CPU_debugger": False,
        "possible_cause": "Source bank and WRAM-pointer gate may be false at runtime; investigate before patching",
        "font_design_issue": "V2 glyphs use sparse narrow outlines; legibility needs separate QA",
        "rom_release_allowed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("screenshot", type=Path)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    if args.screenshot.resolve() == args.report.resolve():
        parser.error("report cannot overwrite screenshot")
    report = audit(args.screenshot.read_bytes())
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
