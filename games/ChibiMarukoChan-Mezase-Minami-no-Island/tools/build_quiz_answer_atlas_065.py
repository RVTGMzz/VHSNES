#!/usr/bin/env python3
"""Quiz question/answer source atlas on exact original Japanese Chibi SNES ROM.

Maps 50 original question blocks to exactly 150 *physical* three-choice answer
fields, and cross-checks all eight canonical Japanese/full-Vietnamese CSVs and
the 041..061 approved text manifests. READ ONLY. Does not derive a jump table,
a correct-answer key, a safe text relocation, or a playable ROM.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
CLEAN_SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
START,END=0x31C00,0x36907
TAG=b"\x81\x6f\x00"
FILES=("quiz_batch01_part1_vi.csv","quiz_batch01_part2_vi.csv",
       "quiz_batch02_part1_vi.csv","quiz_batch02_part2_vi.csv",
       "quiz_batch02_part3_vi.csv","quiz_batch03_part1_vi.csv",
       "quiz_batch03_part2_vi.csv","quiz_batch03_part3_vi.csv")
STAGES=(
    ("041","quiz_answers_exact_fit_041.csv","csv"),
    ("047","quiz_fortune_exactfit_047.json","mixed"),
    ("054","quiz_content_first_54_054.json","json"),
    ("057","quiz_content_first_50_057.json","json"),
    ("058","quiz_content_first_67_058.json","json"),
    ("059","quiz_content_first_37_059.json","json"),
    ("060","quiz_content_first_21_060.json","json"),
    ("061","quiz_content_first_19_061.json","json"),
)
EXPECTED_STAGE_COUNTS={"041":21,"047":15,"054":54,"057":50,
                       "058":67,"059":34,"060":21,"061":17}
EXPECTED_CONFIG_COUNTS={"06_12":151,"00_0E":99,"00_08":49,"00_14":48}


def read_csv(file:Path):
    with file.open(encoding="utf-8-sig",newline="") as fh:
        return list(csv.DictReader(fh))


def analyze(clean:bytes,root:Path):
    if len(clean)!=0x200000 or hashlib.sha256(clean).hexdigest()!=CLEAN_SHA:
        raise ValueError("Exact original unheadered 2MiB Chibi Japanese ROM required")
    if clean[END:0x38000]!=b"\xff"*5881:
        raise AssertionError("Original Quiz bank-end FF padding changed")
    src={}
    for file in FILES:
        for item in read_csv(root/"translation/source"/file):
            off=int(item["file_offset"],0)
            if off in src or not item["vi_full"] or not item["source_jp_scanner"]:
                raise AssertionError(f"Missing/duplicate canonical Quiz source: {off:X}")
            src[off]={"file":file,
                      "source_jp_scanner":item["source_jp_scanner"],
                      "vi_full":item["vi_full"]}
    if len(src)!=381:
        raise AssertionError(f"Canonical 381 Quiz record inventory drift: {len(src)}")
    staged={}
    counts={}
    for name,file,typ in STAGES:
        rows=read_csv(root/"translation/runtime"/file) if typ=="csv" else json.loads(
            (root/"translation/runtime"/file).read_text(encoding="utf-8"))["records"]
        if typ=="mixed":
            rows=[x for x in rows if x.get("category")=="quiz"]
        counts[name]=len(rows)
        if counts[name]!=EXPECTED_STAGE_COUNTS[name]:
            raise AssertionError(f"Stage {name} record count changed")
        for row in rows:
            off=int(row["file_offset"],0)
            if off not in src or off in staged:
                raise AssertionError(f"Unknown/duplicate staged Quiz source 0x{off:X}")
            staged[off]=name
    if len(staged)!=279:
        raise AssertionError("Staged Quiz unique count != 279")

    event_counts=Counter()
    configs=Counter()
    answer_tokens=[]
    footer_positions=[]
    for pos in range(START,END-11):
        if clean[pos:pos+3]!=TAG:
            continue
        next8=clean[pos+3:pos+11]
        if next8[0]==0x0e and next8[2]==0x0f:
            event_counts["ordinary"]+=1
            configs[f"{next8[1]:02X}_{next8[3]:02X}"]+=1
            if next8[1:4]==b"\x06\x0f\x12":
                answer_tokens.append(pos)
        elif (next8[0]==0x10 and next8[2]==0x0e
              and next8[4]==0x0f):
            event_counts["extended"]+=1
        elif next8[5]==0xc6 and next8[7]==0:
            event_counts["footer"]+=1
            footer_positions.append(pos)
        else:
            raise AssertionError(f"Unclassified original script grammar at {pos:05X}")
    if (event_counts!=Counter({"ordinary":355,"extended":4,"footer":50})
        or any(configs[k]!=v for k,v in EXPECTED_CONFIG_COUNTS.items())
        or len(answer_tokens)!=151 or len(footer_positions)!=50):
        raise AssertionError("Native question/control inventory drift")
    if configs["06_10"]!=1:
        raise AssertionError("Early yes option has changed")

    blocks=[]
    distinct_answer_offsets=set()
    previous=START
    anomalous_footers=[]
    option_staged=Counter()
    for index,footer in enumerate(footer_positions,1):
        located=[p for p in answer_tokens if previous<=p<footer]
        if len(located)!=(4 if index==1 else 3):
            raise AssertionError(f"Question {index}: expected exactly three native answers")
        if index==1:
            # Prologue also has an unassociated 'いいえ' confirmation option.
            if clean[located[0]+7:located[0]+13]!=bytes.fromhex("82a282a282a6"):
                raise AssertionError("Question prologue extra choice differs from source")
        options=[]
        for ordinal,pos in enumerate(located[-3:],1):
            off=pos+7
            marker=clean.find(b"\x81\x6f",off,off+100)
            if marker<0:
                raise AssertionError(f"Answer text at {off:X} has no native marker")
            raw=clean[off:marker].strip(b" ")
            if not raw or len(raw)%2:
                raise AssertionError(f"Answer CP932 cells invalid at {off:X}")
            original=raw.decode("cp932")
            reference=src.get(off)
            if not reference or off in distinct_answer_offsets:
                raise AssertionError(f"Answer ROM source absent/duplicate 0x{off:X}")
            distinct_answer_offsets.add(off)
            stage=staged.get(off)
            option_staged["prepared" if stage else "remaining"]+=1
            options.append({"ordinal":ordinal,"original_file_offset":f"0x{off:X}",
                            "original_japanese":original,"source_file":reference["file"],
                            "canonical_full_vietnamese":reference["vi_full"],
                            "original_glyph_cells":len(raw)//2,
                            "already_prepared_stage":stage,
                            "gameplay_verified":False})
        a=clean[footer+3:footer+11]
        b=clean[footer+13:footer+21]
        first_sep=clean[footer+11:footer+13]
        second_sep=clean[footer+21:footer+23]
        if (a[5]!=b[5] or a[5]!=0xc6 or a[7]!=b[7] or a[7]!=0
            or first_sep[1]!=0 or second_sep[1]!=0):
            raise AssertionError(f"Question footer 2-record shape drift at {footer:X}")
        if a[:6]!=b[:6]:
            anomalous_footers.append(f"0x{footer:X}")
        if (clean[footer+23:footer+27] !=
            (b"\xff"*4 if index==50 else b"\x0e\x00\x0f\x0a")):
            raise AssertionError(f"Unknown footer transition at question {index}")
        blocks.append({"question_index":index,"original_question_region_start":f"0x{previous:X}",
                       "original_footer_at":f"0x{footer:X}","answer_choices":options,
                       "uninterpreted_footer_record_A":a.hex(),
                       "uninterpreted_footer_record_B":b.hex(),
                       "footer_records_same_first_six":a[:6]==b[:6]})
        previous=footer+23
    if (len(distinct_answer_offsets)!=150 or
        option_staged!=Counter({"prepared":69,"remaining":81}) or
        anomalous_footers!=["0x35618"]):
        raise AssertionError("Physical choice/source/stage cross-check drift")
    return {"summary":{
        "status":"PASS_EXACT_CLEAN_ROM_QUESTION_ATLAS_NOT_EMULATOR",
        "original_rom_sha256":CLEAN_SHA,
        "native_control_events":dict(event_counts),
        "original_question_blocks":50,
        "genuine_three_choice_fields":150,
        "all_genuine_choices_present_in_canonical_source":True,
        "answer_choices_already_staged_for_ROM":69,
        "answer_choices_remaining_unstaged":81,
        "all_Quiz_source_rows":381,
        "all_Quiz_source_rows_prepared":len(staged),
        "ordinary_0E0F_parameter_frequency":dict(configs),
        "footer_original_template_exception":"0x35618",
        "footer_semantics_decoded":False,
        "correct_answer_indicators_decoded":False,
        "text_pointer_relocation_approved":False,
        "emulator_tested":False,
        "wrote_ROM_or_IPS":False,
    },"blocks":blocks}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("clean_original_japanese_rom",type=Path)
    ap.add_argument("--project-root",type=Path,default=ROOT)
    ap.add_argument("--report",type=Path)
    args=ap.parse_args()
    report=analyze(args.clean_original_japanese_rom.read_bytes(),args.project_root)
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report["summary"],ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
