#!/usr/bin/env python3
"""Read-only exact-source search for G3 result/ending Japanese labels.

Reports where candidate strings occur in actual retail 2MiB ROM. This
prevents accidental use of internal QA scene-descriptor phrases as a
retail graphic or editable player-facing direct text. It does NOT locate
the executed result render path, decompress an asset or patch any ROM.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

EXPECTED_SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
INTERNAL_START=0x2865E
INTERNAL_END=0x28800
TERMS=("勝ち","敗けた","コンティニュー","やめる","最終勝利","エンディング")
EXPECTED_LOCATIONS={
    "勝ち":[0x1C04F,0x1C25C,0x1D03A],
    "敗けた":[0x2876E],
    "コンティニュー":[0x2878C],
    "やめる":[0x287C4],
    "最終勝利":[0x287E2],
    "エンディング":[0x287FE],
}

def occurrences(blob:bytes,term:str)->list[int]:
    needle=term.encode("cp932")
    result=[]
    offset=0
    while True:
        offset=blob.find(needle,offset)
        if offset<0:return result
        result.append(offset)
        offset+=1

def audit(rom:bytes)->dict:
    if len(rom)!=0x200000 or hashlib.sha256(rom).hexdigest()!=EXPECTED_SHA:
        raise ValueError("exact clean unheadered Japanese ROM required")
    entries=[]
    for term in TERMS:
        found=occurrences(rom,term)
        if found!=EXPECTED_LOCATIONS[term]:
            raise AssertionError(f"unexpected G3 CP932 source matches {term}: {found}")
        rows=[]
        for off in found:
            if INTERNAL_START<=off<INTERNAL_END:
                kind="INTERNAL_DEMO_DESCRIPTOR_NOT_RETAIL"
            elif 0x181CC<=off<0x1DE82:
                kind="STORY_DIALOGUE_NOT_RESULT_BANNER"
            else:
                kind="OTHER_UNVERIFIED"
            rows.append({"source_offset":f"0x{off:06X}","type":kind})
        entries.append({"Japanese":term,"raw_CP932_occurrences":len(found),
                        "locations":rows})
    return {
        "status":"G3_LITERAL_SOURCE_SCOPE_VERIFIED_NOT_RENDER_ASSET",
        "rom_sha256":EXPECTED_SHA,
        "target_labels":entries,
        "actual_result_graphic_asset":"NOT_PROVEN",
        "actual_result_screen_callback":"NOT_TRACED",
        "runtime_or_graphics_patch_produced":False,
        "do_not_patch_descriptor_span":"0x2865E..0x287FF",
        "note":"No matching direct title label outside known story dialogue and internal descriptor for these exact tokens. Different words/graphics or dynamic text may exist elsewhere.",
        "release_ready":False,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("clean_rom",type=Path)
    p.add_argument("--report",type=Path)
    a=p.parse_args()
    result=audit(a.clean_rom.read_bytes())
    raw=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    print(raw)
    if a.report:
        a.report.parent.mkdir(parents=True,exist_ok=True)
        a.report.write_text(raw,encoding="utf-8")

if __name__=="__main__":
    main()
