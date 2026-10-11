#!/usr/bin/env python3
"""Checkpoint 060: add 21 distinct Quiz fields to verified full stage059 ROM.

Only static byte-source and IPS checks are possible until historical 043 IPS
and fully integrated 059 assets are accessible. Do NOT claim emulator QA.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import unicodedata
from pathlib import Path
from build_content_first_040_fortune import make_ips, apply_ips

ROOT = Path(__file__).resolve().parent.parent
CLEAN_SHA = "e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
MANIFEST = "translation/runtime/quiz_content_first_21_060.json"
PREVIEW_IPS_SHA = "f03313fd1d822c2b3c49b46c3bec520313f3ae3d5b8c62db6d177206238a5822"
PREVIEW_ROM_SHA = "8eb2b3ea0aedafd744039d4b05f2a647d0c4a239e778ef4c604305c2b033fbe9"
SOURCES = ("quiz_batch01_part1_vi.csv", "quiz_batch01_part2_vi.csv",
           "quiz_batch02_part1_vi.csv", "quiz_batch02_part2_vi.csv",
           "quiz_batch02_part3_vi.csv", "quiz_batch03_part2_vi.csv",
           "quiz_batch03_part3_vi.csv")


def sha(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def source_frames(clean: bytes, off: int):
    if off < 0x31D00 or off >= 0x36900:
        raise AssertionError(f"Unapproved Quiz source bank: {off:05X}")
    i = left = off
    frames, markers = [], []
    while i < off + 280:
        first = clean[i]
        if first < 0x20:
            break
        if clean[i:i+2] == b"\x81\x6f":
            frames.append((left, i))
            markers.append(i)
            i += 2
            left = i
            continue
        if first == 0x20:
            i += 1
            continue
        if ((0x81 <= first <= 0x9f or 0xe0 <= first <= 0xfc)
                and i+1 < len(clean) and clean[i+1] >= 0x40):
            i += 2
            continue
        raise AssertionError(f"Unsafe original Quiz byte at {i:05X}: {first:02X}")
    else:
        raise AssertionError(f"Unterminated original Quiz source at {off:05X}")
    if i > left:
        frames.append((left, i))
    if not frames or not markers or clean[i] >= 0x20:
        raise AssertionError(f"Missing original Quiz line control at {off:05X}")
    return frames, markers, i


def build(clean: bytes, baseline059: bytes, root: Path):
    if len(clean) != 0x200000 or sha(clean) != CLEAN_SHA:
        raise ValueError("Exact original 2MiB Japanese SNES ROM required")
    if len(baseline059) != len(clean):
        raise ValueError("Full stage059 ROM length mismatch")
    if int.from_bytes(baseline059[0x2975e:0x29760], "little") != 0x9a74:
        raise AssertionError("Established V2 84xx font pointer missing")
    plan = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    rows = plan["records"]
    offsets = {r["file_offset"].upper() for r in rows}
    if (plan["schema"] != "chibi.quiz.content_first.060.v1"
        or plan["clean_original_rom_sha256"] != CLEAN_SHA
        or len(rows) != 21 or plan["candidate_count"] != 21 or len(offsets) != 21
        or plan["original_line_segments"] != 43
        or plan["source_only_IPS_sha256"] != PREVIEW_IPS_SHA
        or plan["source_only_ROM_sha256"] != PREVIEW_ROM_SHA):
        raise AssertionError("Checkpoint060 verified Quiz source manifest changed")
    canonical = {}
    for filename in SOURCES:
        name = "translation/source/" + filename
        for r in csv_rows(root / name):
            key = r["file_offset"].upper()
            if key in canonical:
                raise AssertionError("Duplicate canonical source Quiz offset " + key)
            canonical[key] = (name, r)
    mapped = {r["unicode"]: r["code_hex"] for r in
              csv_rows(root / "translation/codepage/vi_codepage_v4_fe4_native.csv")}
    if mapped.get(" ") != "8440":
        raise AssertionError("Existing V2 codepage space mapping drift")

    out = bytearray(baseline059)
    preview = bytearray(clean)
    allowed, markers = set(), set()
    segment_count = 0
    for row in rows:
        key = row["file_offset"].upper()
        at = int(key, 16)
        canonical_pair = canonical.get(key)
        if canonical_pair is None:
            raise AssertionError("Quiz offset absent from full translation CSV: " + key)
        source_file, original = canonical_pair
        original_jp = original.get("source_jp_scanner", original.get("source_jp", ""))
        if (source_file != row.get("source_file")
            or original_jp != row.get("source_jp_scanner")
            or original["vi_full"] != row.get("vi_full_reference")
            or row["status"] !=
                "verified_clean_original_byte_overlay_pending_full_059_baseline_and_emulator"):
            raise AssertionError("Canonical Japanese/full Vietnamese changed: " + key)
        frames, breaks, end = source_frames(clean, at)
        captions = row["vi_runtime_lines"]
        expected = row["expected_capacities"]
        if len(frames) != len(captions) or len(frames) != len(expected):
            raise AssertionError("Physical Quiz original frame count changed " + key)
        if baseline059[at:end] != clean[at:end]:
            raise AssertionError("Prior 059 patch already modified Quiz region " + key)
        found = []
        for (start, stop), caption in zip(frames, captions):
            raw = clean[start:stop]
            lead = len(raw) - len(raw.lstrip(b" "))
            tail = len(raw) - len(raw.rstrip(b" ")) if lead < len(raw) else 0
            lo, hi = start+lead, stop-tail
            field = clean[lo:hi]
            if len(field) % 2:
                raise AssertionError("Odd original CP932 byte count " + key)
            cells = len(field)//2
            found.append(cells)
            if (unicodedata.normalize("NFC", caption) != caption
                or len(caption) > cells or (not field and caption)):
                raise AssertionError("Vietnamese doesn't fit original Quiz cells " + key)
            glyphs = bytearray()
            for char in caption + " " * (cells - len(caption)):
                code = mapped.get(char)
                if not code or len(code) != 4 or not code.startswith("84"):
                    raise AssertionError(f"Unavailable V2 font glyph {char!r} at {key}")
                index = int(code[-2:], 16)
                ptr = 0x28000 + 0x1a74 + 2*(index-0x40)
                if (index < 0x40 or
                    int.from_bytes(baseline059[ptr:ptr+2], "little") == 0):
                    raise AssertionError(f"Unmapped V2 glyph {char!r} at {key}")
                glyphs.extend(bytes.fromhex(code))
            region = set(range(lo, hi))
            if allowed & region:
                raise AssertionError("Overlapping 060 records " + key)
            allowed.update(region)
            out[lo:hi] = glyphs
            preview[lo:hi] = glyphs
        if found != expected:
            raise AssertionError("Original Quiz font cells no longer match QA " + key)
        markers.update(breaks)
        segment_count += len(frames)

    if len(allowed) != 816 or len(markers) != 43 or segment_count != 43:
        raise AssertionError("060 physical text inventory changed")
    if any(out[i:i+2] != b"\x81\x6f" for i in markers):
        raise AssertionError("Original 060 text-control delimiter overwritten")
    preview_blob = bytes(preview)
    proof_ips, proof_records = make_ips(clean, preview_blob)
    if (sha(preview_blob) != PREVIEW_ROM_SHA or sha(proof_ips) != PREVIEW_IPS_SHA
        or len(proof_ips) != 1038 or proof_records != 43
        or apply_ips(clean, proof_ips) != preview_blob):
        raise AssertionError("Exact clean ROM 060 byte-QA fingerprint mismatch")

    changed = {i for i,(a,b) in enumerate(zip(baseline059, out)) if a != b}
    if len(changed) != 815 or changed - allowed:
        raise AssertionError("060 would overwrite existing data/script font")
    out[0x7fdc:0x7fe0] = bytes(4)
    checksum = (sum(out) + 0x1fe) & 0xffff
    out[0x7fdc:0x7fde] = (checksum ^ 0xffff).to_bytes(2,"little")
    out[0x7fde:0x7fe0] = checksum.to_bytes(2,"little")
    complete = bytes(out)
    delta = {i for i,(a,b) in enumerate(zip(baseline059,complete)) if a != b}
    if delta - (allowed | set(range(0x7fdc,0x7fe0))):
        raise AssertionError("Out-of-scope byte written by 060")
    full_ips, records = make_ips(clean,complete)
    if apply_ips(clean,full_ips) != complete:
        raise AssertionError("Final combined 060 IPS replay mismatch")
    return full_ips, {
        "status": "060_QUIZ21_STATIC_QA_ONLY_NOT_EMULATOR",
        "source_059_rom_sha256": sha(baseline059),
        "new_distinct_quiz_records": 21,
        "original_line_frames": segment_count,
        "original_816F_controls_unchanged": len(markers),
        "source_editable_bytes": len(allowed),
        "changed_text_bytes": len(changed),
        "source_only_IPS_sha256": PREVIEW_IPS_SHA,
        "result_060_ROM_sha256": sha(complete),
        "full_clean_ROM_IPS_sha256": sha(full_ips),
        "full_clean_ROM_IPS_bytes": len(full_ips),
        "full_clean_ROM_IPS_records": records,
        "SNES_checksum": f"0x{checksum:04X}",
        "SNES_complement": f"0x{checksum ^ 0xffff:04X}",
        "emulator_tested": False, "whole_game_complete": False,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("clean_japanese_rom", type=Path)
    ap.add_argument("verified_full_059_rom", type=Path)
    ap.add_argument("--expected-059-sha", required=True)
    ap.add_argument("--project-root", type=Path, default=ROOT)
    ap.add_argument("--ips", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--allow-untested", action="store_true")
    args = ap.parse_args()
    if not args.allow_untested:
        ap.error("Game emulator not yet tested; pass --allow-untested")
    if (len(args.expected_059_sha) != 64 or
        any(c not in "0123456789abcdef" for c in args.expected_059_sha)):
        ap.error("Expected 059 SHA must be 64 lowercase hex characters")
    paths = [args.clean_japanese_rom,args.verified_full_059_rom,args.ips,args.report]
    if len({p.resolve() for p in paths}) != 4:
        ap.error("Input and output paths must differ")
    baseline = args.verified_full_059_rom.read_bytes()
    if sha(baseline) != args.expected_059_sha:
        ap.error("Supplied full 059 ROM differs from expected baseline SHA")
    ips, report = build(args.clean_japanese_rom.read_bytes(),baseline,
                        args.project_root)
    for file,payload in ((args.ips,ips),
                         (args.report,(json.dumps(report,ensure_ascii=False,indent=2)+"\n").encode("utf-8"))):
        file.parent.mkdir(parents=True,exist_ok=True)
        file.write_bytes(payload)
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
