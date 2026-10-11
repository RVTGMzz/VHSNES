#!/usr/bin/env python3
"""Rebuild Chibi cumulative stage061 from exact checkpoint043 ZIP or .ips.

Use only user-owned original Japanese ROM and the original historical archive.
Examines ZIP contents in memory; never extracts copyrighted ROM to disk.
The resulting clean-ROM IPS is still UNTESTED on an SNES emulator.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from build_content_first_040_fortune import apply_ips
from rebuild_content_first_061_full_chain import run as rebuild061

ROOT=Path(__file__).resolve().parent.parent
CLEAN_SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
BASE_IPS_SHA="d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50"
BASE_IPS_SIZE=28135

def sha(blob:bytes)->str:
    return hashlib.sha256(blob).hexdigest()

def validate_043(candidate:bytes)->bool:
    return (len(candidate)==BASE_IPS_SIZE
            and sha(candidate)==BASE_IPS_SHA
            and candidate.startswith(b"PATCH") and candidate.endswith(b"EOF"))

def inspect_archive(path:Path):
    """Return exact user-owned 043 IPS bytes and safe provenance information."""
    if not path.is_file():
        raise FileNotFoundError(f"Checkpoint043 archive not accessible: {path}")
    if path.suffix.lower()==".ips":
        data=path.read_bytes()
        if not validate_043(data):
            raise ValueError("Provided .ips does not match the original checkpoint043 SHA")
        return data,{"kind":"exact_ips","original_filename":path.name}
    if path.suffix.lower()!=".zip":
        raise ValueError("Provide original checkpoint043 ZIP archive or exact .ips")
    try:
        with ZipFile(path) as archive:
            names=archive.infolist()
            if (len(names)>100 or
                sum(entry.file_size for entry in names)>16*1024*1024):
                raise ValueError("ZIP has too many entries or excessive expanded size")
            candidates=[]
            for entry in names:
                if entry.is_dir() or not entry.filename.lower().endswith(".ips"):
                    continue
                if entry.file_size!=BASE_IPS_SIZE:
                    continue
                raw=archive.read(entry)
                if validate_043(raw):
                    candidates.append((entry.filename,raw))
            if len(candidates)!=1:
                raise ValueError(
                    f"Expected exactly ONE IPS with original checkpoint043 SHA in ZIP; "
                    f"found {len(candidates)}")
            name,data=candidates[0]
            return data,{"kind":"historical_zip","original_filename":path.name,
                         "ips_entry":name}
    except BadZipFile as exc:
        raise ValueError("Not a valid checkpoint043 ZIP archive") from exc

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("original_japanese_rom",type=Path)
    p.add_argument("exact_043_zip_or_ips",type=Path)
    p.add_argument("--project-root",type=Path,default=ROOT)
    p.add_argument("--ips",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--allow-untested",action="store_true")
    args=p.parse_args()
    if not args.allow_untested:
        p.error("Actual emulator gameplay NOT tested: pass --allow-untested")
    paths=[args.original_japanese_rom,args.exact_043_zip_or_ips,args.ips,args.report]
    if len({path.resolve() for path in paths})!=len(paths):
        p.error("Inputs, patch output and QA report must use distinct paths")
    if args.ips.suffix.lower()!=".ips" or args.report.suffix.lower()!=".json":
        p.error("Outputs must be .ips and .json respectively")
    clean=args.original_japanese_rom.read_bytes()
    if len(clean)!=0x200000 or sha(clean)!=CLEAN_SHA:
        p.error("Wrong original retail Japanese 2MiB ROM identity")
    base,provenance=inspect_archive(args.exact_043_zip_or_ips)
    rom043=apply_ips(clean,base)
    if len(rom043)!=len(clean):
        raise AssertionError("043 source patch failed to preserve original ROM length")
    patch,qa=rebuild061(clean,base,args.project_root)
    final_rom=apply_ips(clean,patch)
    if len(final_rom)!=len(clean) or sha(final_rom)!=qa["result_061_ROM_sha256"]:
        raise AssertionError("Full 061 generated patch replay/ROM hash mismatch")
    qa=dict(qa)
    qa["checkpoint_043_source_archive"]=provenance
    qa["checkpoint_043_IPS_sha256"]=BASE_IPS_SHA
    qa["final_clean_ROM_IPS_sha256"]=sha(patch)
    qa["actual_SNEmulator_tested"]=False
    qa["release_approved"]=False
    # Validation is complete before any output is written.
    args.ips.parent.mkdir(parents=True,exist_ok=True)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.ips.write_bytes(patch)
    args.report.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",
                           encoding="utf-8")
    print(json.dumps({"status":"061_COMPOSITE_SOURCE_REPLAY_ONLY",
                       "patch":str(args.ips),"sha256":sha(patch),
                       "bytes":len(patch),"emulator_tested":False},indent=2))

if __name__=="__main__":
    main()
