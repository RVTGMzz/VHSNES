#!/usr/bin/env python3
"""Read-only audit of Quiz script delimiters and special trailers on original ROM.

Do NOT infer a pointer table, writable free space or emulator-safe relocation
from this structural scan. No patched ROM, IPS or binary is emitted.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

ORIGINAL_SHA = "e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
ROM_SIZE = 0x200000
SCRIPT_START, SCRIPT_END = 0x31C00, 0x36907
BLANK_END = 0x38000
EXPECTED = {"ordinary_0E_0F_prefix": 355,
            "extended_10_0E_0F_prefix": 4,
            "seven_byte_record_footer": 50}
END_OF_TEXT = b"\x81\x6f\x00"


def classify_suffix(suffix: bytes):
    if len(suffix) < 8:
        raise AssertionError("Incomplete Quiz script prefix")
    if suffix[0] == 0x0E and suffix[2] == 0x0F:
        return "ordinary_0E_0F_prefix"
    if (suffix[0] == 0x10 and suffix[2] == 0x0E
            and suffix[4] == 0x0F):
        return "extended_10_0E_0F_prefix"
    if suffix[5] == 0xC6 and suffix[7] == 0x00:
        return "seven_byte_record_footer"
    return "unknown_do_not_relocate"


def analyze(clean: bytes):
    if len(clean) != ROM_SIZE or hashlib.sha256(clean).hexdigest() != ORIGINAL_SHA:
        raise ValueError("Exact 2MiB Japanese SNES Chibi clean ROM required")
    counters = Counter()
    examples = {}
    anomalous_offsets = []
    discovered = []
    for pos in range(SCRIPT_START, SCRIPT_END-11):
        if clean[pos:pos+3] != END_OF_TEXT:
            continue
        tag = classify_suffix(clean[pos+3:pos+11])
        counters[tag] += 1
        examples.setdefault(tag, f"0x{pos:X}")
        discovered.append(pos)
        if tag == "unknown_do_not_relocate":
            anomalous_offsets.append(f"0x{pos:X}")
    for k,v in EXPECTED.items():
        if counters[k] != v:
            raise AssertionError(f"Original Quiz grammar drift: {k} {counters[k]} != {v}")
    if (counters["unknown_do_not_relocate"] != 0 or
            sum(counters.values()) != 409 or
            len(set(discovered)) != 409):
        raise AssertionError("Quiz control-prefix / delimiter inventory changed")
    blank_len = BLANK_END - SCRIPT_END
    if blank_len != 5881 or clean[SCRIPT_END:BLANK_END] != b"\xff"*blank_len:
        raise AssertionError("Original bank-end FF candidate changed")
    return {
        "status": "PASS_SOURCE_ROM_STRUCTURE_ONLY_NOT_RELOCATION_OR_EMULATOR",
        "original_ROM_sha256": ORIGINAL_SHA,
        "quiz_segment_window": [f"0x{SCRIPT_START:X}", f"0x{SCRIPT_END:X}"],
        "native_816F_then_00_control_boundaries": sum(counters.values()),
        "category_counts": dict(counters),
        "first_example_offset_by_class": examples,
        "unrecognized_control_transitions": anomalous_offsets,
        "bank_end_FF_candidate": {
            "start": f"0x{SCRIPT_END:X}",
            "end_exclusive": f"0x{BLANK_END:X}",
            "length_bytes": blank_len,
            "approved_for_relocation": False,
        },
        "script_pointer_table_found": False,
        "length_extension_validated": False,
        "gameplay_and_emulator_tested": False,
        "binary_modified": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("clean_japanese_rom", type=Path)
    p.add_argument("--report", type=Path)
    args = p.parse_args()
    result = analyze(args.clean_japanese_rom.read_bytes())
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",
                               encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
