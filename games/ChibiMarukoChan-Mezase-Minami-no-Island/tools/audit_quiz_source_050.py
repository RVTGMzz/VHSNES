#!/usr/bin/env python3
"""Quiz source triage for content-first integration (read-only).

Audit six canonical translated CSVs. Never treat the scanner's curly-brace
line separators or CP932 trailing-byte artifacts as safe writable slots.
The output is a source inventory, NOT proof of ROM integration.
"""
from __future__ import annotations
import argparse
import csv
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
SOURCES=(
    "quiz_batch01_part1_vi.csv","quiz_batch01_part2_vi.csv",
    "quiz_batch02_part1_vi.csv","quiz_batch02_part2_vi.csv",
    "quiz_batch03_part1_vi.csv","quiz_batch03_part2_vi.csv",
)

def run(root: Path):
    runtime=json.loads((root/"translation/runtime/quiz_fortune_exactfit_047.json").read_text(encoding="utf-8"))
    previously={r["file_offset"].upper() for r in runtime["records"] if r["category"]=="quiz"}
    rows=[]; seen=set()
    for name in SOURCES:
        with (root/"translation/source"/name).open(encoding="utf-8-sig",newline="") as f:
            for line in csv.DictReader(f):
                addr=line["file_offset"].upper()
                if addr in seen: raise AssertionError("Duplicate Quiz source offset: "+addr)
                seen.add(addr)
                jp=line["source_jp_scanner"]
                vi=line["vi_full"]
                reasons=[]
                if "｛" in jp: reasons.append("embedded_scanner_layout_separator")
                if re.match(r"^[OPQRWXP]\b",jp): reasons.append("possible_cp932_halfwidth_scanner_alias")
                if jp.startswith((" ", "　")): reasons.append("leading_padding_check_physical_start")
                if re.search(r"scanner|omitted|inside|corrected",line.get("notes",""),re.I):
                    reasons.append("manually_corrected_scanner_span")
                if not jp or not vi: reasons.append("empty_source_or_translation")
                if addr in previously: category="already_integrated_047"
                elif reasons: category="requires_original_rom_layout_verification"
                else: category="candidate_for_original_rom_byte_preflight_only"
                rows.append({"source_file":name,"file_offset":addr,"source_jp_scanner":jp,
                             "vi_full":vi,"status":category,"risks":reasons})
    counts={status:sum(r["status"]==status for r in rows) for status in sorted(set(r["status"] for r in rows))}
    if previously-set(seen): raise AssertionError("Old integrated Quiz row missing from source CSV")
    return {"schema":"chibi.quiz.source_triage.050.v1",
            "source_count":len(rows),"already_integrated_047":len(previously),
            "counts":counts,"runtime_emulator":"NOT_TESTED",
            "note":"No ROM bytes edited; all candidates require physical CP932/control-code verification.",
            "rows":rows}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-root",type=Path,default=ROOT)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=run(a.project_root)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="rows"},ensure_ascii=False,indent=2))
if __name__=="__main__": main()
