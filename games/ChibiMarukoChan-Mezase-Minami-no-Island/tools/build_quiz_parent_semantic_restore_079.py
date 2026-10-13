#!/usr/bin/env python3
"""Chibi checkpoint079: restore lost Quiz facts in 3 ALREADY-translated fields.

Safe post-stage061 V2 overlay; do NOT mutate stages 057/058/059 or their
historical pinned IPS SHA. This applies only after the real integrated
Vietnamese font+previous Quiz overlays are verified byte-for-byte.

Text and original native 16-bit LoROM pointers are validated from ORIGINAL
Japanese ROM and earlier exact stage manifests. Old V2 glyph bytes in
baseline must match the historical translations before replacement.
This is a guarded static overlay, NOT proof of SNES emulator rendering.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import unicodedata
from pathlib import Path

from build_content_first_040_fortune import apply_ips,make_ips

ROOT=Path(__file__).resolve().parent.parent
CLEAN_SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
MANIFEST="translation/runtime/quiz_parent_semantic_restore_079.json"
PRIOR_MANIFESTS={
    "057":"translation/runtime/quiz_content_first_50_057.json",
    "058":"translation/runtime/quiz_content_first_67_058.json",
    "059":"translation/runtime/quiz_content_first_37_059.json",
}
ORIGINAL_SLOTS={
    0x3272A:(13,"父ヒロシはしゅみがつりで、"),
    0x3274C:(13,"美空ひばりファンの４０才。"),
    0x32977:(14,"いつもクールなおねえちゃんは"),
    0x3299B:(14,"小学６年生。西城秀樹のファン"),
    0x35D84:(13,"よし子さんは、おねえちゃん"),
    0x35DA6:(14,"とおなじ６年２組。小山くんの"),
    0x35DCA:(14,"ことがすきである。まる子たち"),
}
ORIGINAL_FIELDS={
    0x3271A:(0x31399,"059","0x3271E"),
    0x3296D:(0x31171,"058","0x32971"),
    0x35D78:(0x313AD,"057","0x35D7C"),
}

def sha(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()

def codepage(root:Path):
    with (root/"translation/codepage/vi_codepage_v4_fe4_native.csv").open(
        newline="",encoding="utf-8-sig") as f:
        rows=list(csv.DictReader(f))
    mapping={x["unicode"]:x["code_hex"] for x in rows}
    if (len(rows)!=160 or len(mapping)!=160 or mapping.get(" ")!="8440"):
        raise AssertionError("Original V2 codepage/space glyph changed")
    return mapping

def encode(text:str,cap:int,mapping:dict[str,str])->bytes:
    if text!=unicodedata.normalize("NFC",text) or len(text)>cap:
        raise AssertionError("Non-NFC Vietnamese or text exceeds original glyph cells")
    out=bytearray()
    for glyph in text+" "*(cap-len(text)):
        item=mapping.get(glyph)
        if not item or len(item)!=4 or not item.startswith("84"):
            raise AssertionError(f"V2 renderer mapping missing {glyph!r}")
        out.extend(bytes.fromhex(item))
    if len(out)!=2*cap:
        raise AssertionError("Original physical slot size changed")
    return bytes(out)

def audit(root:Path):
    m=json.loads((root/MANIFEST).read_text(encoding="utf-8"))
    if (m.get("schema")!="chibi.quiz.parent_semantic_restore.079.v1"
        or m.get("original_clean_rom_sha256")!=CLEAN_SHA
        or m.get("emulator_tested") is not False
        or m.get("ready_to_release") is not False
        or len(m.get("records",[]))!=3):
        raise AssertionError("079 reviewed source manifest identity changed")
    mapping=codepage(root)
    prior={
        stage:{int(row["file_offset"],0):row
               for row in json.loads((root/path).read_text(
                   encoding="utf-8"))["records"]}
        for stage,path in PRIOR_MANIFESTS.items()
    }
    covered=set();total=0;new_chars=0;real_changes=0
    for record in m["records"]:
        native=int(record["original_record"],0)
        if native not in ORIGINAL_FIELDS:
            raise AssertionError("Unknown physically native Quiz record")
        pointer,stage,source=ORIGINAL_FIELDS[native]
        if (record["prior_stage"]!=stage or
            record["parent_source"]!=source or
            int(record["pointer_word_at"],0)!=pointer):
            raise AssertionError("Incorrect native field original pointer or stage")
        parent=prior[stage].get(int(source,0))
        if parent is None or len(record["lines"])!=len(
            [line for line in parent["vi_runtime_lines"] if line]):
            raise AssertionError("Missing historical Quiz source segment lineage")
        expected_old=[s for s in parent["vi_runtime_lines"] if s]
        old_in_manifest=[x["old"] for x in record["lines"]]
        if expected_old!=old_in_manifest:
            raise AssertionError("079 former lines do not exactly match real stage manifest")
        for line in record["lines"]:
            off=int(line["glyph_offset"],0)
            if off in covered or off not in ORIGINAL_SLOTS:
                raise AssertionError("Duplicate/unknown native source line target")
            covered.add(off)
            cap,jp=ORIGINAL_SLOTS[off]
            if (line["capacity"]!=cap or line["original_jp"]!=jp or
                len(jp.encode("cp932"))!=2*cap):
                raise AssertionError("Original Japanese physical slot drift")
            previous=encode(line["old"],cap,mapping)
            revised=encode(line["new"],cap,mapping)
            real_changes+=sum(a!=b for a,b in zip(previous,revised))
            new_chars+=len(line["new"])
            total+=1
    if (covered!=set(ORIGINAL_SLOTS) or total!=7 or real_changes<45
        or len(m.get("other_original_scanner_offsets_need_context_review",[]))!=15):
        raise AssertionError("079 exact 3 parent fields / 7 nonblank slots changed")
    return {
        "status":"PASS_079_ROM_FREE_THREE_QUIZ_PARENT_SEMANTIC_RESTORATIONS",
        "canonical_parent_fields_reviewed":3,
        "prior_rendered_lines_audited":7,
        "ROM_glyph_line_offsets":[f"0x{x:X}" for x in sorted(covered)],
        "new_Vietnamese_glyph_count":new_chars,
        "expected_V2_byte_differences_in_existing_staged_slots":real_changes,
        "existing_original_glyph_cell_widths_preserved":True,
        "other_parent_scanner_offsets_still_pending_review":15,
        "actual_emulator_rendering_tested":False,
        "original_061_V2_ROM_built_here":False,
        "newly_emulator_accepted_strings":0,
    }

def build(clean:bytes,baseline:bytes,root:Path):
    if (len(clean)!=0x200000 or sha(clean)!=CLEAN_SHA or
        len(baseline)!=len(clean)):
        raise ValueError("Requires exact original 2MiB Japanese SFC and same-size V2 candidate")
    qa=audit(root)
    if int.from_bytes(baseline[0x2975E:0x29760],"little")!=0x9A74:
        raise AssertionError("Cannot patch Quiz text without real integrated V2 glyph pointer")
    mapping=codepage(root)
    m=json.loads((root/MANIFEST).read_text(encoding="utf-8"))
    out=bytearray(baseline)
    allowed=set(range(0x7FDC,0x7FE0))
    for record in m["records"]:
        native=int(record["original_record"],0)
        pointer,stage,source=ORIGINAL_FIELDS[native]
        old_pointer=0x8000+(native-0x30000)
        if (clean[pointer:pointer+2]!=old_pointer.to_bytes(2,"little") or
            baseline[pointer:pointer+2]!=clean[pointer:pointer+2]):
            raise AssertionError("Original Quiz parent pointer moved unexpectedly")
        for line in record["lines"]:
            off=int(line["glyph_offset"],0)
            cap,jp=ORIGINAL_SLOTS[off]
            original=jp.encode("cp932")
            if clean[off:off+len(original)]!=original:
                raise AssertionError("Japanese source SFC contains unexpected physical glyphs")
            earlier=encode(line["old"],cap,mapping)
            replacement=encode(line["new"],cap,mapping)
            if baseline[off:off+len(earlier)]!=earlier:
                raise AssertionError("This is not the unchanged historical 057/058/059 V2 baseline")
            for glyph in set(line["new"]+" "):
                font_code=mapping[glyph]
                font_index=int(font_code[-2:],16)
                font_pointer=0x28000+0x1A74+2*(font_index-0x40)
                if int.from_bytes(baseline[font_pointer:font_pointer+2],"little")==0:
                    raise AssertionError(f"V2 lookup missing real glyph {glyph!r}")
            out[off:off+len(replacement)]=replacement
            allowed.update(range(off,off+len(replacement)))
    out[0x7FDC:0x7FE0]=bytes(4)
    checksum=(sum(out)+0x1FE)&0xFFFF
    out[0x7FDC:0x7FDE]=(checksum^0xFFFF).to_bytes(2,"little")
    out[0x7FDE:0x7FE0]=checksum.to_bytes(2,"little")
    final=bytes(out)
    changed={i for i,(a,b) in enumerate(zip(baseline,final)) if a!=b}
    if changed-allowed or any(
        final[p:p+2]!=baseline[p:p+2] for p,_,_ in ORIGINAL_FIELDS.values()):
        raise AssertionError("079 illegally changed ROM code, pointers or unrelated glyphs")
    patch,count=make_ips(clean,final)
    if apply_ips(clean,patch)!=final:
        raise AssertionError("079 combined source IPS replay failed")
    return patch,{
        **qa,
        "status":"PASS_079_V2_PARENT_SEMANTIC_OVERLAY_STATIC_NOT_EMULATOR",
        "clean_original_ROM_sha256":CLEAN_SHA,
        "candidate_result_ROM_sha256":sha(final),
        "cumulative_original_ROM_IPS_sha256":sha(patch),
        "cumulative_original_ROM_IPS_bytes":len(patch),
        "cumulative_original_ROM_IPS_records":count,
        "changed_vs_existing_V2_baseline_bytes":len(changed),
        "SNES_checksum":f"0x{checksum:04X}",
        "renderer_or_gameplay_tested":False,
        "released":False,
        "copyrighted_ROM_written":False,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("original_clean_Japanese_rom",type=Path)
    p.add_argument("--baseline-ips",type=Path,required=True)
    p.add_argument("--project-root",type=Path,default=ROOT)
    p.add_argument("--ips",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--allow-untested",action="store_true")
    a=p.parse_args()
    if not a.allow_untested:
        p.error("Actual SNES gameplay untested; pass --allow-untested for static IPS")
    paths=[a.original_clean_Japanese_rom,a.baseline_ips,a.ips,a.report]
    if len({x.resolve() for x in paths})!=4:
        p.error("All input/output file paths must be different")
    clean=a.original_clean_Japanese_rom.read_bytes()
    base=apply_ips(clean,a.baseline_ips.read_bytes())
    patch,qa=build(clean,base,a.project_root)
    a.ips.parent.mkdir(parents=True,exist_ok=True)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.ips.write_bytes(patch)
    a.report.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(qa,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
