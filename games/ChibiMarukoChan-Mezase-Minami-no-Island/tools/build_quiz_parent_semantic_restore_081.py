#!/usr/bin/env python3
"""Chibi checkpoint081: preserve quiz narration and restore missing Japanese facts.

Post-080 ONLY: four independent, ALREADY-staged original Quiz text records,
five caption line changes. Original script words, control markers, stage
054/058/059 manifests, and user-owned ROM stay unchanged. No emulator approval.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from build_content_first_040_fortune import make_ips, apply_ips
from build_quiz_parent_semantic_restore_080 import read_codepage, encode

ROOT=Path(__file__).resolve().parent.parent
CLEAN_SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
MANIFEST="translation/runtime/quiz_parent_semantic_restore_081.json"
STAGE={
    "054":"translation/runtime/quiz_content_first_54_054.json",
    "058":"translation/runtime/quiz_content_first_67_058.json",
    "059":"translation/runtime/quiz_content_first_37_059.json",
}
FIELDS={
    0x31E6D:(0x31E69,0x313FF,"059",[(0x31E73,7),(0x31E93,6),(0x31EB3,12)]),
    0x343D2:(0x343CE,0x313A3,"054",[(0x343DA,12),(0x343FC,14),(0x34420,12)]),
    0x33018:(0x33014,0x3139B,"058",[(0x33020,11),(0x33040,13),(0x33062,12)]),
    0x33083:(0x3307F,0x31403,"058",[(0x33089,11),(0x330AB,13)]),
}
CORRECTED_ALIASES={0x31E7B,0x34403,0x33050}

def sha(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()

def audit(root:Path):
    m=json.loads((root/MANIFEST).read_text(encoding="utf-8"))
    if (m.get("schema")!="chibi.quiz.parent_semantic_restore.081.v1"
        or m.get("original_clean_ROM_sha256")!=CLEAN_SHA
        or m.get("emulator_tested") is not False
        or m.get("production_approved") is not False
        or len(m.get("records",[]))!=4):
        raise AssertionError("081 source QA manifest/release status changed")
    mapping=read_codepage(root)
    previous={}
    for stage,filename in STAGE.items():
        rows=json.loads((root/filename).read_text(encoding="utf-8"))["records"]
        previous[stage]={int(item["file_offset"],0):item for item in rows}
    if len({int(r["source"],0) for r in m["records"]})!=4:
        raise AssertionError("Duplicate 081 native source")
    observed_slots=set()
    modified_lines=0
    total_cells=0
    modified_cell_bytes=0
    for record in m["records"]:
        source=int(record["source"],0)
        if source not in FIELDS:
            raise AssertionError("Unreviewed 081 original field source")
        native,pointer,stage,spans=FIELDS[source]
        if (int(record["native_start"],0)!=native
            or int(record["pointer_word"],0)!=pointer
            or record["stage"]!=stage
            or len(record["glyphs"])!=len(spans)):
            raise AssertionError("Native original pointer or frame-count drift")
        prior=previous[stage].get(source)
        if prior is None:
            raise AssertionError("Missing prior 054/058/059 authoritative parent")
        if prior["vi_runtime_lines"]!=[x["old"] for x in record["glyphs"]]:
            raise AssertionError("Original old-staged VN captions changed under QA")
        for item,(at,cap) in zip(record["glyphs"],spans):
            if (int(item["at"],0)!=at or item["capacity"]!=cap
                or len(item["jp"].encode("cp932"))!=2*cap
                or at in observed_slots):
                raise AssertionError("Original physical Quiz source byte span drift")
            observed_slots.add(at)
            old=encode(item["old"],cap,mapping)
            new=encode(item["vi"],cap,mapping)
            modified_lines+=int(old!=new)
            modified_cell_bytes+=sum(x!=y for x,y in zip(old,new))
            total_cells+=cap
    if (len(observed_slots)!=11 or modified_lines!=5 or total_cells!=123
        or modified_cell_bytes<=20
        or {int(r["scanner_alias"],0) for r in m["records"]}!=CORRECTED_ALIASES):
        raise AssertionError("Four records /11 frames /5 text corrections changed")
    return {
        "status":"PASS_ROM_FREE_081_FOUR_QUIZ_CONTEXT_CORRECTIONS",
        "canonical_source_records_covered_by_prior_stages":4,
        "original_glyph_frames_verified":11,
        "actually_changed_glyph_frames":5,
        "original_fixed_width_glyph_cells_preserved":total_cells,
        "changed_original_V2_glyph_bytes_expected":modified_cell_bytes,
        "repaired_original_scanner_aliases":[f"0x{x:X}" for x in sorted(CORRECTED_ALIASES)],
        "new_Quiz_source_IDs_accepted":0,
        "other_unreviewed_scanner_aliases":9,
        "SNES_emulator_tested":False,
        "ROM_or_IPS_written":False,
    }

def build(clean:bytes,baseline:bytes,root:Path):
    if len(clean)!=0x200000 or sha(clean)!=CLEAN_SHA or len(baseline)!=len(clean):
        raise ValueError("Requires the EXACT original headerless Japanese 2MiB SFC")
    qa=audit(root)
    if int.from_bytes(baseline[0x2975E:0x29760],"little")!=0x9A74:
        raise AssertionError("Prior genuine 061 Vietnamese V2 glyph lookup is required")
    mapping=read_codepage(root)
    m=json.loads((root/MANIFEST).read_text(encoding="utf-8"))
    out=bytearray(baseline)
    allowed=set(range(0x7FDC,0x7FE0))
    for record in m["records"]:
        native=int(record["native_start"],0)
        pointer=int(record["pointer_word"],0)
        expected=(0x8000+native-0x30000).to_bytes(2,"little")
        if (clean[native:native+4]!=baseline[native:native+4]
            or clean[native:native+2]!=b"\x0e\x00"
            or clean[pointer:pointer+2]!=expected
            or baseline[pointer:pointer+2]!=expected):
            raise AssertionError("Original 65c816 Quiz script header/pointer changed")
        for item in record["glyphs"]:
            at=int(item["at"],0)
            cap=item["capacity"]
            original_jp=item["jp"].encode("cp932")
            if clean[at:at+cap*2]!=original_jp:
                raise AssertionError(f"Original Japanese glyph bytes not matched at {at:05X}")
            old=encode(item["old"],cap,mapping)
            if baseline[at:at+cap*2]!=old:
                raise AssertionError("Wrong baseline old historical 054/058/059 V2 glyph bytes")
            new=encode(item["vi"],cap,mapping)
            if old==new:continue
            for ch in set(item["vi"]+" "):
                idx=int(mapping[ch][-2:],16)
                fptr=0x28000+0x1A74+2*(idx-0x40)
                if int.from_bytes(baseline[fptr:fptr+2],"little")==0:
                    raise AssertionError(f"Required Vietnamese codepoint has no glyph: {ch!r}")
            out[at:at+cap*2]=new
            allowed.update(range(at,at+cap*2))
    out[0x7FDC:0x7FE0]=bytes(4)
    checksum=(sum(out)+0x1FE)&0xFFFF
    out[0x7FDC:0x7FDE]=(checksum^0xFFFF).to_bytes(2,"little")
    out[0x7FDE:0x7FE0]=checksum.to_bytes(2,"little")
    final=bytes(out)
    diffs={i for i,(a,b) in enumerate(zip(baseline,final)) if a!=b}
    if diffs-allowed:
        raise AssertionError("081 touched a byte outside 11 original glyph frames/checksum")
    patch,count=make_ips(clean,final)
    if apply_ips(clean,patch)!=final:
        raise AssertionError("081 cumulative source IPS cannot replay to the identical ROM")
    return patch,{
        **qa,
        "status":"081_V2_POST080_SEMANTIC_OVERLAY_STATIC_ONLY",
        "input_ROM_sha256":sha(baseline),
        "candidate_ROM_sha256":sha(final),
        "final_cumulative_clean_ROM_IPS_sha256":sha(patch),
        "final_cumulative_clean_ROM_IPS_bytes":len(patch),
        "final_cumulative_clean_ROM_IPS_records":count,
        "LoROM_checksum":f"0x{checksum:04X}",
        "changed_original_V2_ROM_bytes":len(diffs),
        "all_original_game_control_and_pointer_bytes_preserved":True,
        "SNES_emulator_tested":False,
        "release_approved":False,
        "copyrighted_ROM_written":False,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("clean_original_Japanese_sfc",type=Path)
    p.add_argument("--baseline-ips",type=Path,required=True)
    p.add_argument("--project-root",type=Path,default=ROOT)
    p.add_argument("--ips",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--allow-untested",action="store_true")
    a=p.parse_args()
    if not a.allow_untested:
        p.error("SNES emulator/renderer still UNTESTED, pass --allow-untested")
    ps=[a.clean_original_Japanese_sfc,a.baseline_ips,a.ips,a.report]
    if len({x.resolve() for x in ps})!=4:
        p.error("Never overwrite input ROM or existing IPS")
    if a.ips.suffix.lower()!=".ips" or a.report.suffix.lower()!=".json":
        p.error("Only cumulative IPS + QA JSON are emitted")
    clean=a.clean_original_Japanese_sfc.read_bytes()
    baseline=apply_ips(clean,a.baseline_ips.read_bytes())
    ips,qa=build(clean,baseline,a.project_root)
    a.ips.parent.mkdir(parents=True,exist_ok=True)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.ips.write_bytes(ips)
    a.report.write_text(json.dumps(qa,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(qa,indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
