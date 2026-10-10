#!/usr/bin/env python3
"""Fail-closed G0 startup-title Vietnamese copy consistency check.

Checks approved title/credit wording across translation source, graphics queue,
glossary, G0 pipeline and pre-integration JSON contract. Never modifies ROM,
inserts graphics, or claims emulator acceptance.
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TITLE = "Chibi Maruko-chan"
SUBTITLE = "Tiến tới đảo phương Nam!!"
CREDIT = "Việt hóa bởi Votri Valley"
OLD_CREDIT = "VôtriValley"
CONTRACT = ROOT / "translation/runtime/g0_startup_title_copy_v1.json"
GRAPHICS = ROOT / "translation/source/graphics_text_targets_vi.csv"
QUEUE = ROOT / "translation/runtime/content_first_graphics_queue_032.csv"
GLOSSARY = ROOT / "translation/UI_GLOSSARY_VI.md"
G0_RUNNER = ROOT / "tools/run_g0_title_reverse_pipeline.py"
MASTER_RUNNER = ROOT / "tools/run_all_graphics_reverse.py"


def csv_records(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def check() -> dict:
    obj = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if obj["schema"] != "chibi.g0.startup_title_copy.v1":
        raise AssertionError("G0 title schema mismatch")
    if obj["priority"] != "P0":
        raise AssertionError("G0 title is no longer urgent")
    if [layer["text"] for layer in obj["layers"]] != [TITLE, SUBTITLE, CREDIT]:
        raise AssertionError("G0 title copy or order drift")
    flags = obj["constraints"]
    if flags["exact_credit_spelling"] != CREDIT:
        raise AssertionError("G0 credit spelling drift")
    if (not flags["preserve_original_publisher_and_copyright"]
            or not flags["preserve_original_character_artwork"]
            or not flags["do_not_patch_internal_debug_descriptors"]
            or flags["title_graphics_source_offset"] is not None
            or flags["runtime_gameplay_verified"] is not False):
        raise AssertionError("title artwork/asset/runtime assertions are unsafe")

    src = {r["source_jp"]: r for r in csv_records(GRAPHICS)}
    if src["ちびまる子ちゃん めざせ！南のアイランド！！"]["vi_full"] != f"{TITLE}: {SUBTITLE}":
        raise AssertionError("title translation disagrees with canonical source")
    if src["__LOCALIZATION_CREDIT__"]["vi_full"] != CREDIT:
        raise AssertionError("canonical user credit is incorrect")
    rows = {r["source_jp"]: r for r in csv_records(QUEUE)}
    for key, phrase in (("ちびまる子ちゃん めざせ！南のアイランド！！", f"{TITLE}: {SUBTITLE}"),
                        ("__LOCALIZATION_CREDIT__", CREDIT)):
        if rows[key]["batch"] != "G0" or rows[key]["priority"] != "P0":
            raise AssertionError("startup title/credit must be G0 priority P0")
        if rows[key]["vi_target"] != phrase:
            raise AssertionError(f"graphics backlog text drift: {key}")
    if rows["ちびまる子ちゃん めざせ！南のアイランド！！"]["asset_source_state"] != "UNRESOLVED":
        raise AssertionError("asset claim changed without verified replacement")

    checked=[CONTRACT,GRAPHICS,QUEUE,GLOSSARY,G0_RUNNER,MASTER_RUNNER]
    for path in checked:
        contents=path.read_text(encoding="utf-8-sig")
        if OLD_CREDIT in contents:
            raise AssertionError(f"old credit spelling in {path}")
    for path in (GLOSSARY,G0_RUNNER,MASTER_RUNNER):
        contents=path.read_text(encoding="utf-8")
        if CREDIT not in contents:
            raise AssertionError(f"new credit absent in {path}")

    return {
        "status":"G0_STARTUP_TITLE_COPY_CONSISTENCY_PASS",
        "title": TITLE,"subtitle": SUBTITLE,"credit": CREDIT,
        "batch":"G0","priority":"P0",
        "source_assets_resolved":False,
        "emulator_runtime_pass":False,
        "copyright_and_original_character_artwork_preservation_required":True,
        "files_verified":len(checked),
        "rom_modified":False,
        "release_ready":False,
    }


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report",type=Path,default=None)
    args=parser.parse_args()
    result=check()
    data=json.dumps(result,indent=2,ensure_ascii=False)+"\n"
    print(data)
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(data,encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
