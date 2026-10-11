#!/usr/bin/env python3
"""Reconstruct exact historical Chibi 043 from ANY approved 039-043 IPS/ZIP.

Original Japanese retail SFC + verified IPS or historical ZIP; all missing
stages are rebuilt from canonical translations with existing guarded builders.
Then rebuild 044..061 and write final CLEAN-ROM IPS plus QA JSON only.
No licensed ROM or font asset is redistributed. Emulator QA still required.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from build_content_first_040_fortune import build as build040, apply_ips
from build_content_first_041_quiz import build as build041
from build_content_first_042_story_safe_segments import build as build042
from build_content_first_043_story_58 import build as build043
from rebuild_content_first_061_full_chain import run as rebuild061

ROOT=Path(__file__).resolve().parent.parent
CLEAN_SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
# Verified historical hashes on the exact same original 2MiB SFC.
KNOWN_IPS={
    "039":(21130,"97c0e41b354b0dda3ea7c0c292b5aef236586e279870962fd0d4f3398285008c"),
    "040":(21727,"2bfdcc64973bc31ce268fa7e68a6118808c633b10d1437b7f811ac290616e580"),
    "041":(22100,"2117bc6e165f2c86263e74a637b6961a13f79257fccd9f02152a769fe1deb962"),
    "042":(23105,"3e3c3de245a9a0a6648b2e62eff44a72093ef1e2e9cfcb1cf013ff6c4cbb5035"),
    "043":(28135,"d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50"),
}
BUILD_STAGES={"040":build040,"041":build041,"042":build042,"043":build043}
STAGE_ORDER=("039","040","041","042","043")

def sha(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()

def identify_ips(data:bytes)->str|None:
    if len(data)<8 or not data.startswith(b"PATCH") or not data.endswith(b"EOF"):
        return None
    digest=sha(data)
    for stage,(expected_len,expected_sha) in KNOWN_IPS.items():
        if len(data)==expected_len and digest==expected_sha:
            return stage
    return None

def select_historical_ips(path:Path):
    if not path.is_file():
        raise FileNotFoundError("Historical Chibi archive/IPS not accessible: "+str(path))
    if path.suffix.lower()==".ips":
        blob=path.read_bytes()
        stage=identify_ips(blob)
        if stage is None:
            raise ValueError("IPS is not an exact verified Chibi checkpoint039..043")
        return stage,blob,{"archive_kind":"ips","archive_file":path.name}
    if path.suffix.lower()!=".zip":
        raise ValueError("Expected a user-owned .ips or original historical .zip")
    try:
        with ZipFile(path,"r") as archive:
            entries=archive.infolist()
            if len(entries)>100 or sum(x.file_size for x in entries)>16*1024*1024:
                raise ValueError("Refusing overlarge or excessively nested historical ZIP")
            matches={}
            for entry in entries:
                if entry.is_dir() or not entry.filename.lower().endswith(".ips"):
                    continue
                if entry.file_size not in {size for size,_ in KNOWN_IPS.values()}:
                    continue
                # Read in-memory; do not extract ZIP paths or write ROMs.
                blob=archive.read(entry)
                stage=identify_ips(blob)
                if stage:
                    if stage in matches and matches[stage][1]!=blob:
                        raise AssertionError("Two incompatible verified IPS for one checkpoint")
                    matches[stage]=(entry.filename,blob)
            if not matches:
                raise ValueError("ZIP has no EXACT SHA-matched checkpoint039..043 IPS")
            # If an archive contains several historical stages, use the most
            # advanced verified one, never infer a stage from filename alone.
            stage=max(matches,key=int)
            name,blob=matches[stage]
            return stage,blob,{"archive_kind":"zip","archive_file":path.name,
                               "matched_member":name,
                               "other_verified_stages":sorted(matches,key=int)}
    except BadZipFile as exc:
        raise ValueError("Not an intact historical ZIP") from exc

def rebuild(clean:bytes,base_stage:str,base_ips:bytes,project:Path):
    if len(clean)!=0x200000 or sha(clean)!=CLEAN_SHA:
        raise ValueError("Incorrect original Japanese Chibi retail 2MiB SFC")
    if base_stage not in STAGE_ORDER or identify_ips(base_ips)!=base_stage:
        raise AssertionError("Historical IPS identity or stage mismatch")
    baseline=apply_ips(clean,base_ips)
    if len(baseline)!=len(clean):
        raise AssertionError("Historical IPS modified retail ROM size")
    stage_proofs=[{"stage":base_stage,
                   "verified_IPS_sha256":sha(base_ips),
                   "full_ROM_sha256":sha(baseline),
                   "rebuilt_from_source":False}]
    stage_ips=base_ips
    next_index=STAGE_ORDER.index(base_stage)+1
    for stage in STAGE_ORDER[next_index:]:
        build=BUILD_STAGES[stage]
        new_rom,new_ips,source_qa=build(clean,stage_ips,project)
        if (len(new_rom)!=len(clean) or apply_ips(clean,new_ips)!=new_rom
            or identify_ips(new_ips)!=stage):
            raise AssertionError("Historical stage "+stage+" failed exact IPS replay/SHA")
        stage_proofs.append({
            "stage":stage,"verified_IPS_sha256":sha(new_ips),
            "full_ROM_sha256":sha(new_rom),
            "rebuilt_from_source":True,
            "guarded_source_report_status":source_qa.get("status","not_reported"),
        })
        stage_ips=new_ips
    if identify_ips(stage_ips)!="043":
        raise AssertionError("Full historical source chain did not end on verified 043")
    final_ips,final_qa=rebuild061(clean,stage_ips,project)
    rom061=apply_ips(clean,final_ips)
    if (len(rom061)!=len(clean)
        or sha(rom061)!=final_qa["result_061_ROM_sha256"]):
        raise AssertionError("061 composite clean-ROM IPS/ROM fingerprint changed")
    report={
        "status":"REBUILT_EXACT_043_AND_061_STATIC_ONLY_EMULATOR_UNTESTED",
        "original_clean_ROM_sha256":CLEAN_SHA,
        "historical_baseline_stage":base_stage,
        "restored_historical_stage_evidence":stage_proofs,
        "final_061_ROM_sha256":sha(rom061),
        "final_061_clean_ROM_IPS_sha256":sha(final_ips),
        "final_061_IPS_bytes":len(final_ips),
        "no_intermediate_ROM_files_written":True,
        "original_sfc_emulator_tested":False,
        "localized_font_visual_QA_passed":False,
        "whole_game_translation_complete":False,
        "release_approved":False,
        "full_061_source_report":final_qa,
    }
    return final_ips,report

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("original_japanese_sfc",type=Path)
    ap.add_argument("historical_039_to_043_zip_or_ips",type=Path)
    ap.add_argument("--project-root",type=Path,default=ROOT)
    ap.add_argument("--ips",type=Path,required=True)
    ap.add_argument("--report",type=Path,required=True)
    ap.add_argument("--allow-untested",action="store_true")
    args=ap.parse_args()
    if not args.allow_untested:
        ap.error("Real emulator QA has not passed: use --allow-untested")
    paths=(args.original_japanese_sfc,args.historical_039_to_043_zip_or_ips,
           args.ips,args.report)
    if len({x.resolve() for x in paths})!=len(paths):
        ap.error("Inputs and IPS/JSON output paths must all be distinct")
    if args.ips.suffix.lower()!=".ips" or args.report.suffix.lower()!=".json":
        ap.error("Output extensions must be .ips and .json")
    clean=args.original_japanese_sfc.read_bytes()
    stage,base,provenance=select_historical_ips(args.historical_039_to_043_zip_or_ips)
    ips,report=rebuild(clean,stage,base,args.project_root)
    report["historical_archive_provenance"]=provenance
    # Never write partial/corrupt output if any source/ROM/checksum QA fails.
    args.ips.parent.mkdir(parents=True,exist_ok=True)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.ips.write_bytes(ips)
    args.report.write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:report[k] for k in
        ("status","historical_baseline_stage","final_061_clean_ROM_IPS_sha256",
         "final_061_IPS_bytes","release_approved")},indent=2))

if __name__=="__main__":
    main()
