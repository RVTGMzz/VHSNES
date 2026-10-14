LATEST: 089. Read docs/CHECKPOINT_089_VIETNAMESE_QUIZ_COUNTER.md first.
Use build_title_readable_088.py --translate-quiz-counter for the full current
clean-original-ROM IPS (SHA256 7ac471724c3d0867ecea1defb18844798fa647b8c325d9deb309677e6b6508ca).
It includes 087 real Quiz runtime fixes, 088 readable title and 089 Câu counter.
Next checkpoint 090: remaining actual G1/Story/Fortune/G3 content/runtime defects.

CURRENT ARTIFACT: 088 (2026-10-14). Read HEAD and
`docs/CHECKPOINT_088_READABLE_TITLE_GROUP.md` before the earlier 087 material.
088 integrates user-requested readable G0 title/credit; Quiz bank06 is identical
to runtime 087. Rebuild original ROM + historical ZIP + supplied local fonts
with tools/build_title_readable_088.py. Final original-ROM IPS SHA256:
a4c9b5cec15358a11b131c27e812532d2d488074d0de6ac067e5a5d16c95945d.
Next work is remaining real gameplay/content blockers, checkpoint 089.

TIẾP VIỆT HÓA CHIBI MARUKO-CHAN SNES — CHECKPOINT 087 (2026-10-14)
Repo RVTGMzz/VHSNES; branch chibi-maruko-bootstrap-01. Read current HEAD first.

Read HANDOFF_CURRENT.md and docs/CHECKPOINT_087_REAL_BUILD_AND_QUIZ_RUNTIME_LAYOUT.md.
User supplied the exact clean original ROM and original 043 archive locally.
One cumulative 087 test IPS now builds: 67,908 bytes, SHA256
5d380dc6d4a14b38615848236ee6991f9ced0d357d7d451658c00f8866dd49ec.
Never commit or distribute the original/patched ROM or extracted font assets.

087 fixed the actual G0-title/Quiz allocation collision, Quiz clipping/portrait
occlusion, allowance continuation and age-nine omission. Actual Snes9x sweep
exercises 50 question slots / 150 selections via savestates and WRAM injection.
This is not a natural whole-game run or independent proof of all grading keys.
Historical scanner staging remains 279/381, zero new scanner IDs in this round.

Important renderer finding: THREE position consumers must agree, not just the
old two hooks. The bitmap ADC at ROM 0x291DF was why earlier pitch experiments
fragmented text. 087 changes functional Quiz layout only; font bitmaps stay V2.

Continue from real runtime defects: broken/partial G1 menu heading and Story
Start art, Japanese Fortune entry artwork, four Fortune overlong fields,
Japanese Quiz counter, G3 results/ending and remaining source-alias semantics.
Prioritize content and functional game flow before cosmetic font work.
Do not repeat tiny static-only Quiz-caption batches. Keep one cumulative IPS.

Rebuild: tools/recover_merge_061_81_one_ips_076.py (now includes 087).
Runtime harness: tools/run_snes9x_qa_087.py (Python, NumPy/Pillow, supplied Snes9x
64-bit libretro core); pass original ROM, IPS, core DLL, --out LOCAL_QA --sweep.
Record real evidence and remaining limitations in a separate runtime report.
