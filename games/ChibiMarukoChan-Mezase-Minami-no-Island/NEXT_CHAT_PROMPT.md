## CHECKPOINT 102 — 2026-10-15: BOTH TEAM-SELECTION LABELS

Read docs/CHECKPOINT_102_TEAM_SELECTION_LABELS.md first.
Latest: tools/build_cumulative_102.py; IPS SHA256:
08ccd04e2fc6fc8c6d8eb2855283ce5b7eab907092bc1d40219b9d578d625b6e.
Includes101 plus both Đội labels in native team selection. Native mascots,
frames and palette preserved; zero Japanese ink in the two word regions.
Next: minigame names/intros, character nameplates, victory/ending and full QA.
Whole-game completion remains false. Earlier checkpoints below are historical.
## CHECKPOINT 101 — 2026-10-15: FIVE NATIVE SETUP HEADINGS

Read docs/CHECKPOINT_101_NATIVE_SETUP_HEADINGS.md first.
Current builder: tools/build_cumulative_101.py; IPS SHA256:
9cc673b08d2097b1733bff6f6d21e047f1403dc2c5ae28f4003ec80b90c949bb.
Native selection/VS headings are Vietnamese; private palette jobs preserve
other palette owners. Main-menu/intro and all nonheading live OBJ cells were
checked against100. Remaining: minigame titles, character/team nameplates,
victory/ending artwork, source aliases and complete gameplay QA. Not finished.
## CHECKPOINT 100 — 2026-10-14: FONT, FORTUNE AND NATIVE RESULTS

Read docs/CHECKPOINT_100_FONT_FORTUNE_AND_NATIVE_RESULTS.md first.
Latest cumulative IPS SHA256: 33158e9a0c1927f5dc283c3bd530d4e80c7b5388ad81a12a8304aec99dbded0b.
Rebuild with tools/build_cumulative_100.py. Native VS now has both Đội labels.
Synthetic Story-to-VS screenshots are invalid acceptance; their stray skin
fragments do not occur in native VS. Pink rabbit cheeks are original artwork.
Next: remaining minigame/VS setup, victory/ending graphics, aliases and full QA.
Whole-game completion remains false. Earlier checkpoint records are historical.
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
