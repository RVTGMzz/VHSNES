#!/usr/bin/env python3
"""ROM-free unit tests for exact SHA-anchored 039..043 Chibi recovery.

Only synthetic fake .ips/.zip inputs are created in a temporary directory;
no copyrighted game image/font required or written.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from zipfile import ZipFile

import build_content_first_040_fortune as s040
import build_content_first_041_quiz as s041
import build_content_first_042_story_safe_segments as s042
import build_content_first_043_story_58 as s043
from recover_from_any_039_to_043_archive_071 import (
    BUILD_STAGES,KNOWN_IPS,STAGE_ORDER,identify_ips,select_historical_ips,
)

def expect_error(fn,message):
    try:
        fn()
    except (ValueError,FileNotFoundError):
        return
    raise AssertionError("Expected safe reject for "+message)

def run():
    if STAGE_ORDER!=("039","040","041","042","043"):
        raise AssertionError("039→043 stage traversal unexpectedly reordered")
    hashes={
        "039":s040.BASE_IPS_SHA,
        "040":s040.FINAL_IPS_SHA,
        "041":s041.OUTPUT_IPS_SHA,
        "042":s042.OUTPUT_IPS_SHA,
        "043":s043.OUTPUT_IPS_SHA,
    }
    if {key:v[1] for key,v in KNOWN_IPS.items()}!=hashes:
        raise AssertionError("Historical source builder SHA identities differ from 071")
    if set(BUILD_STAGES)!={"040","041","042","043"}:
        raise AssertionError("Missing source rebuild function")
    for key,func in BUILD_STAGES.items():
        if not callable(func):
            raise AssertionError("Missing stage builder "+key)
    if identify_ips(b"PATCH"+b"EOF") is not None:
        raise AssertionError("Header-only IPS wrongly accepted")
    if identify_ips(b"PATCH"+b"\x00"*28127+b"EOF") is not None:
        raise AssertionError("Spoofed 043 IPS of known length wrongly accepted")
    with tempfile.TemporaryDirectory() as temporary:
        folder=Path(temporary)
        missing=folder/"missing.zip"
        expect_error(lambda:select_historical_ips(missing),"missing archive")
        bad_ips=folder/"checkpoint043.ips"
        bad_ips.write_bytes(b"PATCH"+b"\x00"*28127+b"EOF")
        expect_error(lambda:select_historical_ips(bad_ips),"spoofed archive SHA")
        bad_zip=folder/"checkpoint043.zip"
        with ZipFile(bad_zip,"w") as archive:
            archive.writestr("fake_043.ips",bad_ips.read_bytes())
            archive.writestr("../../not_a_rom.sfc",b"TEST")
        expect_error(lambda:select_historical_ips(bad_zip),
                     "ZIP with no exact verified 039–043 IPS")
    return {
        "status":"PASS_ROM_FREE_HISTORY_SHA_AND_NEGATIVE_ARCHIVE_TESTS",
        "all_stage_SHA_anchors_match_existing_builders":True,
        "source_stage_build_functions_available":True,
        "rejects_forged_IPS_even_if_size_matches":True,
        "rejects_missing_or_unverified_ZIP":True,
        "ever_reads_or_writes_original_ROM":False,
        "has_run_exact_historical_043_rebuild":False,
        "has_run_emulator":False,
    }

if __name__=="__main__":
    print(json.dumps(run(),indent=2))
