#!/usr/bin/env python3
"""Probe original ASCII padding reuse for six Chibi Quiz answer labels.

Source-byte-only validation on user's exact headerless Japanese ROM.
No playable localization, no IPS/ROM output, and never count as runtime QA.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,unicodedata
from pathlib import Path
from build_content_first_040_fortune import make_ips,apply_ips

ROOT=Path(__file__).resolve().parent.parent
CLEAN_SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
IPS_SHA="74cc6dd983753e9370228092b404549891ca6e273e32dbd9e59887c284aed5cd"
OVERLAY_SHA="2d0df00692276b4256c888aa71aaf4290a7f449c5bb57a41b90d382271487d96"

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()

def build_report(clean:bytes,root:Path):
    if len(clean)!=0x200000 or sha(clean)!=CLEAN_SHA:
        raise ValueError("Exact original unheadered Japanese 2MiB SNES ROM required")
    manifest=json.loads((root/"translation/runtime/quiz_padding_expansion_PROBE_062.json").read_text(encoding="utf-8"))
    rows=manifest["records"]
    if (manifest["schema"]!="chibi.quiz.padding_expansion.PROBE_062.v1" or
        manifest["approved_for_integration"] is not False or
        manifest["include_in_unique_Quiz_progress"] is not False or
        manifest["probe_only_true_count"]!=6 or len(rows)!=6 or
        manifest["test_only_IPS_sha256"]!=IPS_SHA):
        raise AssertionError("Probe062 scope or safety status changed")
    with (root/"translation/codepage/vi_codepage_v4_fe4_native.csv").open(encoding="utf-8-sig",newline="") as file:
        cp={r["unicode"]:r["code_hex"] for r in csv.DictReader(file)}
    with (root/"translation/source/quiz_batch03_part3_vi.csv").open(encoding="utf-8-sig",newline="") as file:
        source={r["file_offset"].upper():r for r in csv.DictReader(file)}
    result=bytearray(clean)
    whitelisted=set()
    controls=set()
    for r in rows:
        at=int(r["file_offset"],16)
        if at==0x33b8d or not (0x33800<=at<=0x33d00):
            raise AssertionError("Unsafe scanner position")
        orig=source.get(r["file_offset"].upper())
        jp=r["source_jp"]
        if (orig is None or not orig["source_jp_scanner"].startswith(jp)
            or orig["file_offset"].upper()!=r["file_offset"].upper()):
            raise AssertionError("Canonical Japanese scanner text drift")
        native=jp.encode("cp932")
        trail=r["original_ASCII_trailing_padding_bytes"]
        body_glyphs=r["original_native_double_byte_glyphs"]
        if len(native)!=body_glyphs*2 or trail<2:
            raise AssertionError("CP932 physical source width drift")
        marker=at+len(native)+trail
        if marker!=int(r["source_816F_delimiter_offset"],16):
            raise AssertionError("Incorrect terminal offset")
        if (clean[at:at+len(native)]!=native or
            clean[at+len(native):marker]!=b" "*trail or
            clean[marker:marker+2]!=b"\x81\x6f"):
            raise AssertionError("Original Quiz text/padding/terminator changed")
        label=r["vi_probe_caption"]
        if unicodedata.normalize("NFC",label)!=label:
            raise AssertionError("Non-normalized translated text")
        extra=len(label)-body_glyphs
        if (extra<=0 or 2*extra>trail or
            r["padding_reassigned_to_0x84_glyph_bytes"]!=2*extra or
            r["remaining_original_ascii_padding_bytes"]!=trail-2*extra):
            raise AssertionError("Overflow original trailing ASCII padding")
        patched=bytearray()
        for char in label:
            hexcode=cp.get(char)
            if not hexcode or len(hexcode)!=4 or not hexcode.startswith("84"):
                raise AssertionError(f"Glyph unavailable in project codepage: {char!r}")
            patched.extend(bytes.fromhex(hexcode))
        patched.extend(b" "*(trail-2*extra))
        if len(patched)!=len(native)+trail:
            raise AssertionError("Probe width mismatch")
        span=set(range(at,marker))
        if span&whitelisted:
            raise AssertionError("Overlapping padded answer regions")
        whitelisted|=span
        result[at:marker]=patched
        controls.add(marker)
    if len(whitelisted)!=104 or len(controls)!=6:
        raise AssertionError("Original probe physical inventory changed")
    if any(result[m:m+2]!=b"\x81\x6f" for m in controls):
        raise AssertionError("Native 816F line delimiter overwritten")
    data=bytes(result)
    diff={i for i,(a,b) in enumerate(zip(clean,data)) if a!=b}
    patch,records=make_ips(clean,data)
    if (len(diff)!=90 or not diff.issubset(whitelisted) or
        len(patch)!=128 or records!=6 or sha(patch)!=IPS_SHA or
        sha(data)!=OVERLAY_SHA or apply_ips(clean,patch)!=data):
        raise AssertionError("Exact Japanese-ROM source-only pad replay QA drift")
    return {
        "status":"PASS_CLEAN_ROM_BYTE_ONLY_NEEDS_EMULATOR_RENDERER_QA",
        "source_clean_SHA256":CLEAN_SHA,
        "probe_answer_fields":6,
        "changed_original_bytes":90,
        "preserved_816F_markers":6,
        "source_only_IPS_sha256":IPS_SHA,
        "source_only_ROM_SHA256":OVERLAY_SHA,
        "runtime_translation_approved":False,
        "included_in_completion_progress":False,
        "emulator_tested":False,
        "ROM_or_IPS_file_written":False,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("clean_japanese_rom",type=Path)
    p.add_argument("--project-root",type=Path,default=ROOT)
    a=p.parse_args()
    print(json.dumps(build_report(a.clean_japanese_rom.read_bytes(),a.project_root),indent=2))
if __name__=="__main__":main()
