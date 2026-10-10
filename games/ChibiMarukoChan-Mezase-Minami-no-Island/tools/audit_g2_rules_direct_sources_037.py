#!/usr/bin/env python3
"""Read-only G2 rules and VS/minigame direct-text CP932 audit (checkpoint 037).

Requires exact 2MiB retail Japanese ROM. Checks known Japanese source bytes,
3 control delimiters, both bullet glyph codes, 35 separate direct UI labels
and the Vietnamese canonical source records. No ROM write or runtime claim.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path

SHA="e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
RULES=((0x1E307,"ルールをせつめいするよ"),
       (0x1E325,"２本先取だよ"),
       (0x1E339,"ゲームの時間は勝つまでだよ"))
# Prefix records include two layout spaces before Japanese "ルール".
UI=((0x288C2,"ルール",2),(0x28958,"ルール",2),
    (0x28A0A,"ペンキをぬる",0),(0x28A1E,"ルール",2),
    (0x28A70,"投げる",0),(0x28A7C,"移動",0),(0x28A86,"体当り",0),
    (0x28A94,"何本先取？",0),(0x28AA4,"コンピュータの",0),
    (0x28AB8,"つよさ",0),(0x28AC4,"１ゲームの時間",0),
    (0x28AD6,"１本",0),(0x28ADE,"２本",0),(0x28AE6,"３本",0),
    (0x28AEE,"４本",0),(0x28AF6,"５本",0),
    (0x28AFE,"よわい",0),(0x28B08,"ふつう",0),(0x28B12,"つよい",0),
    (0x28B1C,"１８０秒",0),(0x28B28,"勝つまで",0),
    (0x28B34,"１８０秒",0),(0x28B40,"勝つまで",0),
    (0x28B50,"プレイヤー１",0),(0x28B62,"プレイヤー２",0),
    (0x28B74,"プレイヤー３",0),(0x28B86,"プレイヤー４",0),
    (0x28B96,"対戦するよ",0),(0x28BA6,"コンピュータ",0),
    (0x28BB6,"おやすみだよ",0),(0x28BC6,"接続なし",0),
    (0x28BD2,"パッド",0),(0x28BDE,"マウス",0),
    (0x28BEA,"スコープ",0),(0x28BFF,"ステージ",0))

def csv_rows(path):
    with path.open("r",encoding="utf-8-sig",newline="") as fp:
        return list(csv.DictReader(fp))

def audit(rom,project):
    if len(rom)!=0x200000 or hashlib.sha256(rom).hexdigest()!=SHA:
        raise ValueError("exact clean unheadered retail 2MiB ROM required")
    if len(RULES)!=3 or len(UI)!=35:raise AssertionError("reviewed inventory changed")
    for off,text in RULES:
        bs=text.encode("cp932")
        if rom[off:off+len(bs)]!=bs or rom.count(bs)!=1:
            raise AssertionError(f"rule source absent/ambiguous/mid-CP932 at 0x{off:X}")
        if rom[off+len(bs):off+len(bs)+2]!=bytes.fromhex("816F"):
            raise AssertionError(f"Japanese original line delimiter moved: 0x{off:X}")
    for off in (0x1E323,0x1E337):
        if rom[off:off+2]!=bytes.fromhex("8145"):
            raise AssertionError(f"original fullwidth bullet not at 0x{off:X}")
    if rom[0x1E2FF:0x1E307]!=b" "*8 or rom[0x1E355]!=0:
        raise AssertionError("rule source framing changed")
    base=project/"translation"/"source"
    source={x["file_offset"].upper():x for x in csv_rows(base/"rules_tutorial_vi.csv")}
    if "0X1E326" in source or not {"0X1E325","0X1E2FF"}<=set(source):
        raise AssertionError("G2 source CSV contains wrong mid-CP932 field offset")
    accepted="・ Ai thắng 2 ván trước sẽ thắng / ・Chơi đến khi phân thắng bại"
    if source["0X1E325"]["vi_full"]!=accepted:
        raise AssertionError("approved Vietnamese rule text changed")
    ui_source={int(x["file_offset"],16):x
               for x in csv_rows(base/"minigame_ui_batch01_vi.csv")}
    checks=[]
    for off,text,prefix in UI:
        if rom[off:off+prefix]!=b" "*prefix:
            raise AssertionError(f"expected {prefix} layout spaces at 0x{off:X}")
        at=off+prefix
        bs=text.encode("cp932")
        if rom[at:at+len(bs)]!=bs:raise AssertionError(f"G2 UI CP932 mismatch 0x{off:X}")
        if off not in ui_source or not ui_source[off]["vi_full"].strip():
            raise AssertionError(f"missing translated canonical UI row 0x{off:X}")
        checks.append({"record_offset":f"0x{off:X}","glyph_offset":f"0x{at:X}",
                       "original_Japanese":text,"leading_spaces":prefix})
    return {"status":"G2_DIRECT_TEXT_SOURCE_AUDIT_PASS",
        "clean_sha256":SHA,"rule_Japanese_locations":[{"offset":hex(off),"text":t}
                                                  for off,t in RULES],
        "fullwidth_bullets_preserved":2,"original_line_delimiters":3,
        "wrong_offset_0x1E326_rejected":True,
        "correct_fullwidth_2_start":"0x1E325",
        "direct_UI_label_sources_verified":len(checks),
        "canonical_UI_translation_rows_verified":len(checks),
        "UI_details":checks,"original_ROM_modified":False,
        "rules_screen_execution_binding":"UNTRACED",
        "sprite_patch_made":False,"SNES_emulator_runtime":"NOT_TESTED",
        "release_ready":False}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("clean_rom",type=Path)
    p.add_argument("--project-root",type=Path,default=Path(__file__).resolve().parent.parent)
    p.add_argument("--report",type=Path)
    a=p.parse_args()
    result=audit(a.clean_rom.read_bytes(),a.project_root)
    content=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    if a.report:
        a.report.parent.mkdir(parents=True,exist_ok=True)
        a.report.write_text(content,encoding="utf-8")
    print(content)

if __name__=="__main__":
    main()
