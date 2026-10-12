#!/usr/bin/env python3
"""Chibi Quiz source-only 81-choice bank06 copy-safe storage planner.

The ORIGINAL 65c816 Quiz copier at file 0x30762 reads 33 words = 66 bytes
from each answer pointer. Unlike the previous packed experiment, this plans
68-byte disjoint slots for 81 complete original Vietnamese answers:
  0x36A00 + slot*68  (slot=0..80)
Each 66-byte native read stays in its own cell and the original bank 06.
This is SOURCE + memory geometry QA only, not proven game rendering.
"""
from __future__ import annotations

import argparse,csv,hashlib,json,unicodedata
from pathlib import Path
from audit_quiz_repo_no_rom_070 import check as check_source

ROOT=Path(__file__).resolve().parent.parent
CLEAN_SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
START,END=0x36A00,0x38000
CELL_BYTES=68
NATIVE_COPY_BYTES=66
COPIER_OFFSET=0x30762
COPIER=bytes.fromhex("A9 20 00 85 08 B9 00 00 9F 00 80 7E E8 E8 C8 C8 C6 08 10 F1 60")
CALLERS=((0x30730,"00"),(0x307AA,"20"),(0x3081B,"40"))
SOURCE_FILES=(
 "quiz_batch01_part1_vi.csv","quiz_batch01_part2_vi.csv",
 "quiz_batch02_part1_vi.csv","quiz_batch02_part2_vi.csv",
 "quiz_batch02_part3_vi.csv","quiz_batch03_part1_vi.csv",
 "quiz_batch03_part2_vi.csv","quiz_batch03_part3_vi.csv",
)
STAGE_FILES=(
 ("quiz_answers_exact_fit_041.csv","csv"),
 ("quiz_fortune_exactfit_047.json","mixed"),
 ("quiz_content_first_54_054.json","json"),
 ("quiz_content_first_50_057.json","json"),
 ("quiz_content_first_67_058.json","json"),
 ("quiz_content_first_37_059.json","json"),
 ("quiz_content_first_21_060.json","json"),
 ("quiz_content_first_19_061.json","json"),
)
KANJI_EXCEPTIONS={0x33DDF:{"一","雄"},0x33DFD:{"和","雄"}}

def rows(file:Path):
 with file.open(encoding="utf-8-sig",newline="") as f:
  return list(csv.DictReader(f))

def plan(root:Path,clean:bytes|None=None):
 report=check_source(root,None)
 if (report["canonical_Quiz_sources"]!=381
     or report["distinct_staged_Quiz_sources"]!=279
     or report["pending_original_choice_answers"]!=81):
  raise AssertionError("Canonical Quiz source/target count changed")
 source={}
 for filename in SOURCE_FILES:
  for line in rows(root/"translation/source"/filename):
   k=int(line["file_offset"],0)
   if k in source: raise AssertionError("Duplicate canonical Quiz source")
   source[k]=line["vi_full"]
 staged=set()
 for filename,fmt in STAGE_FILES:
  path=root/"translation/runtime"/filename
  content=rows(path) if fmt=="csv" else json.loads(path.read_text(encoding="utf-8"))["records"]
  if fmt=="mixed":content=[r for r in content if r.get("category")=="quiz"]
  staged.update(int(r["file_offset"],0) for r in content)
 atlas=json.loads((root/"translation/runtime/quiz_answer_pointer_offsets_070.json").read_text(encoding="utf-8"))
 pending=[]
 originals=set()
 for slot,triplet in enumerate(atlas["selection_slot_answer_source_offsets"]):
  for ordinal,hexoff in enumerate(triplet):
   original=int(hexoff,0)
   if original in originals: raise AssertionError("Duplicate answer pointer")
   originals.add(original)
   if original not in staged:
    pointer_offset=(0x31217,0x3127F,0x312E7)[ordinal]+slot*2
    pending.append((original,slot,ordinal,pointer_offset))
 if len(pending)!=81:raise AssertionError("Expected 81 original unpatched answers")
 cp={r["unicode"]:r["code_hex"] for r in rows(root/"translation/codepage/vi_codepage_v4_fe4_native.csv")}
 if cp.get(" ")!="8440" or len(cp)!=160:
  raise AssertionError("Original codepage drift")
 assignments=[]
 for index,(original,qslot,ordinal,ptr) in enumerate(sorted(pending)):
  full=source[original]
  if full!=unicodedata.normalize("NFC",full):
   raise AssertionError("Non-NFC Vietnamese Quiz full caption")
  missing={c for c in full if c not in cp}
  if missing!=KANJI_EXCEPTIONS.get(original,set()):
   raise AssertionError(f"Wrong missing source glyph(s) at {original:05X}: {missing}")
  raw=bytearray()
  for ch in full:
   if ch in cp:
    hx=cp[ch]
    if len(hx)!=4 or not hx.startswith("84"):raise AssertionError("Invalid V2 glyph")
    raw.extend(bytes.fromhex(hx))
   else:
    encoded=ch.encode("cp932")
    if len(encoded)!=2:raise AssertionError("Unexpected CP932 source Kanji width")
    raw.extend(encoded)
  record=b"\x0e\x06\x0f\x12"+bytes(raw)+b"\x81\x6f\x00"
  if len(record)>NATIVE_COPY_BYTES:
   raise AssertionError(f"Quiz answer too long for copied 66-byte record: 0x{original:X}")
  target=START+index*CELL_BYTES
  if target+NATIVE_COPY_BYTES>END or target+CELL_BYTES>END:
   raise AssertionError("Native 66-byte copy runs over bank06 boundary")
  if assignments and target < assignments[-1]["copy_window_end_exclusive"]:
   raise AssertionError("Copied native answer windows overlap")
  assignments.append({
   "source_offset":f"0x{original:X}",
   "pointer_table_slot":qslot,"answer_ordinal":ordinal+1,
   "pointer_word_ROM":f"0x{ptr:X}",
   "source_full_vietnamese":full,
   "experimental_dest_ROM":f"0x{target:X}",
   "experimental_bank06_CPU_pointer":f"0x{target-0x30000+0x8000:04X}",
   "record_size":len(record),
   "copy_window_end_exclusive":target+NATIVE_COPY_BYTES,
   "source_only_emulator_tested":False,
  })
 if (len(assignments)!=81 or
     START+81*CELL_BYTES!=0x37F84 or
     END-(START+81*CELL_BYTES)!=124 or
     max(x["record_size"] for x in assignments)!=53):
  raise AssertionError("81-choice native-safe slot plan drift")
 opc=False
 if clean is not None:
  if len(clean)!=0x200000 or hashlib.sha256(clean).hexdigest()!=CLEAN_SHA:
   raise ValueError("Exact original Japanese retail 2MiB SFC required")
  if clean[COPIER_OFFSET:COPIER_OFFSET+len(COPIER)]!=COPIER:
   raise AssertionError("Original Quiz native 33-word copy changed")
  for at,xvalue in CALLERS:
   code=bytes.fromhex("BC E7 92 80 08 BC 7F 92 80 03 BC 17 92 A2 "+xvalue+" 00 20 62 87")
   if clean[at:at+len(code)]!=code:
    raise AssertionError("Native answer caller source changed")
  if clean[START:END]!=b"\xff"*(END-START):
   raise AssertionError("Proposed unused bank06 area no longer all FF")
  for r in assignments:
   at=int(r["source_offset"],16);pt=int(r["pointer_word_ROM"],16)
   ptr=int.from_bytes(clean[pt:pt+2],"little")
   if ptr<0x8000 or 0x30000+ptr-0x8000+4!=at:
    raise AssertionError("Real 16bit pointer/source mismatch")
  opc=True
 return {"summary":{
  "status":"PASS_SOURCE_BUDGET_AND_66_BYTE_COPIER_GEOMETRY_NOT_EMULATOR",
  "canonical_answers_pending":81,"distinct_original_game_pointer_targets":81,
  "start":f"0x{START:X}","end_exclusive":f"0x{END:X}",
  "bank06_space_bytes":END-START,"reserved_cell_bytes":CELL_BYTES,
  "original_native_copy_bytes":NATIVE_COPY_BYTES,
  "all_81_writable_slots_in_bank06":True,
  "max_payload_record_size":53,
  "reserved_bytes":len(assignments)*CELL_BYTES,
  "remaining_bank_end_bytes":124,
  "original_rom_copier_and_pointer_contract_checked":opc,
  "original_067_target_at_0x37FE0_crosses_bank_by_bytes":34,
  "original_072_two_64B_spaced_copy_windows_overlap_by_bytes":2,
  "production_relocation_approved":False,
  "SNES_emulator_tested":False,
  "binary_IPS_or_ROM_written":False,
 },"slots":assignments}

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--project-root",type=Path,default=ROOT)
 p.add_argument("--original-rom",type=Path)
 p.add_argument("--report",type=Path)
 a=p.parse_args()
 if a.report and a.original_rom and a.report.resolve()==a.original_rom.resolve():
  p.error("Never overwrite user ROM with diagnostics")
 data=plan(a.project_root,a.original_rom.read_bytes() if a.original_rom else None)
 if a.report:
  a.report.parent.mkdir(parents=True,exist_ok=True)
  a.report.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(data["summary"],ensure_ascii=False,indent=2))

if __name__=="__main__":main()
