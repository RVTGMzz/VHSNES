# HANDOFF CURRENT — Chibi Maruko-chan SNES Việt hóa

## CHECKPOINT 049 — 2026-10-11: FULL-CHAIN REBUILDER COMMITTED (NOT YET EXECUTED)

- Added `tools/rebuild_content_first_048_full_chain.py` to turn exact clean ROM + 043 clean IPS into validated 044, 045, 046, 047 and merged 048 entirely in memory, then write only final clean-ROM IPS + QA JSON. Uses each existing stage's full CP932/source/offset/SHA/IPS safety checks and independently replays every stage.
- This specifically eliminates the missing intermediate 047 ROM/IPS dependency documented in checkpoint048. It DOES NOT eliminate need for user's clean original ROM and exact 043 IPS to actually execute it.
- **No binary integration has been run in this chat:** clean ROM and 043 IPS are not mounted here. Therefore 048 complete physical merge remains **UNVERIFIED**, despite the runner being committed. No emulator testing or release approval.
- Command (technical only): `python tools/rebuild_content_first_048_full_chain.py clean.sfc 043-clean.ips --ips final-048.ips --report final-048-qa.json --allow-untested`.
- Next: run against exact local inputs, review merged SHA and checksum, then proceed with large Quiz sweep, six remaining Fortune entries, G2 rules and G3 results. User preference: CONTENT FIRST, font later; do not send interim patches.


## NEW CHECKPOINT 048 — 2026-10-11: +103 REAL FORTUNE GLYPH OVERLAY QA, 047 REBASE PENDING

**User preference:** finish significant game content, no intermediate IPS/ZIP download links, no font microtests. Read `docs/CONTENT_FIRST_FORTUNE_103_CHECKPOINT_048.md` FIRST and 047 below.

- **103 additional Fortune text entries authored with context and FULL canonical `vi_full` unchanged**. Each matches an actual clean Japanese ROM CP932 source field, exact original physical two-byte capacity including double ASCII-space nuance, terminal `816F`, nonzero legacy 0x84 V2 glyph code. 103/103 passed. Fields cover wishes, money, love, school, daily tips, lucky colors. Preserve full source meaning; compact in-game variants are a distinct editorial layer and still need runtime screenshot review.
- **ACTUAL LOCAL ROM BYTE-QA:** ROM clean `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`, exact old integrated checkpoint043 reconstructed from local ZIP SHA `45ffca7db5db83bc2734e885ee90c77f33746e2c4a54d1c99f1502f3e992a6ae`. Applied 103 new Fortune edits physically to this ROM as a **text-only unchecksummed QA overlay**, approved 2,002 source glyph bytes, 1,997 actual changed byte positions. Text-only IPS `/mnt/data/chibi048_fortune_103_overlay_no_checksum.ips` SHA **`3eb7dcc55d0c0b585beb4b27d6d2ca08c5facd39196042756eae0cf0dc68379c`**, 2,545 B/108 records. Separate local IPS replay -> exact 043+103 preview ROM SHA **`4f461333d171fc21c3541ae29393056f0c9234ea0f5c4de46f97589afd20378b`**, original `816F` markers all intact, no changes outside these glyph fields, legacy font and previous 043 assets untouched. Local QA `/mnt/data/chibi048_local_qa.json`; local verifier `/mnt/data/chibi_048_build_local.py`.
- **IMPORTANT: 048 FULL MERGE NOT YET DONE!** Exact 047 ROM SHA `1f6430064b70671a4f3ba94f0fd256764db54690950519c22d9e03ec74230dd9` is not in active container; only exact clean and 043 ROM/IPS available. The 043+103 preview ROM has *outdated cartridge checksum by design* and is **NOT A PLAYABLE RELEASE**. **DO NOT SAY 151 FORTUNE ALREADY IN FULL 047+048 ROM.** Need rebuild 047 from source or find exact user-owned 047 binary, then run strict 048 guarded merger.
- New GitHub `translation/runtime/fortune_content_first_103_048.json`: 103 source offsets + canonical full Japanese/full `vi_full`, existing physical source byte budgets, manually edited compact text. Confirmed live cross-intersection with prior `fortune_exact_fit_040.csv` 33 and `quiz_fortune_exactfit_047.json` 15 Fortune = ZERO collisions. New `tools/build_content_first_048_fortune_103.py` supports explicit `--static-check-043` exact overlay QA and SHA-locked **full 047 ROM** merge (recompute SNES checksum, generate clean-ROM IPS, byte diff whitelist, independent IPS replay), failing closed when 047 binary wrong/missing. GitHub builder source committed; *not* CI-run.
- Verified canonical Fortune rows **157**: 48 already in full published 047; 103 additional prepared and physical 043-byte-layer verified; 6 source items need expansion or additional editorial QA. **Potential** 151/157 after confirmed 047+048 merge. The remaining six: `0x2BD5E,0x2C413,0x2C601,0x2C86B,0x2CA7D,0x2CADD`. Do NOT create silly clipping to force these.
- **NEXT HIGH VALUE:** reproduce 047 from all source patches 044–047 (full 047 binary absent), do actual protected 047+103 merge and checksum. Then large Quiz/source remaining integration, G2 rules, G3 result. ONE eventual SNES emulator comprehensive test and font cleanup AFTER content. User does NOT want any interim IPS/ZIP links or testing requests.


## ACTIVE CHECKPOINT 047 — 2026-10-11: STORY SCANNER FIX +45 ACTUAL ROM TEXT PATCHES

**READ `docs/CONTENT_FIRST_STORY_ALIGN_AND_QUIZ_FORTUNE_CHECKPOINT_047.md` FIRST**, then 045. User has repeatedly insisted on **CONTENT-FIRST, FONT LATER**, no endless tiny checkpoints and **NO UNREQUESTED INTERMEDIATE IPS/ZIP DOWNLOAD LINKS**. Push edits and reproducible tools to GitHub, do not ask user to test every mini-build.

**MAJOR CORRECTION:** 23 apparently untranslated Story source CSV rows at 045 were not 23 unique on-ROM text windows. **8 scanner offsets incorrectly begin in the second CP932 byte of Japanese fullwidth `０/１/２/３`**, misread as Latin `O/P/Q/R`: 4 were already translated within prior 043/044 full-parent fields, and 4 must be translated by writing their complete real parent (not a bad half-glyph). Three tutorial Story lines at 181CC/18245/182BE were already localized. **15 unique physical Story records actually required new patches**. Some begin suspicious 2-byte `E6F3/88F3/FAF3/92F3` glyph-like prefixes: **PRESERVED exactly**, only following original text glyphs rewritten; do not assume definitively these prefix bytes are renderer metadata without runtime proof.

**REAL ROM046:** 15 newly patched Story physical records, 31 original native spans, 30 original page/line markers kept, zero changes to other data except checksum. 616 writable glyph bytes; 620 actually different bytes vs045. Exact ROM SHA **`c10c0f444a97d6bea7f8f669d67bb6c0c5b6889b654d99d6e6dfa25e3d061624`**; original-clean IPS SHA **`11abac1b8e0f48e6580822bcdcd3b1b3568ae08676020b86c819ae641f53367d`**, 44,450 bytes/1,599 records; checksum/complement F71E/08E1.

**ALL STORY SOURCE ROWS NOW ACCOUNTED FOR AT STATIC FIELD LEVEL**: GitHub live recomputed 7 canonical CSV sources **336 rows** and checked set equality against previous 042/043/044/045 manifest offsets (310 rows) + 15 new 046 true records + 8 false scanner alias offsets + 3 previously localized tutorial rows = **336/336**, zero unknown/extra. Distinct original physical Story records patched = 310+15+3 = **328**. This is NOT in-game user testing and NOT proof no visible Story beyond source CSVs.

**REAL ROM047:** +30 further original direct-text slots **15 Quiz +15 Fortune** (numeric birthdates/ages/classes/prices, ten luck digits/three large numbers, `Gọi thử!`, `Văn hên!`). Original Japanese CP932 source exact, length and `816F` terminator intact, V2 old font unchanged; 222 approved glyph bytes, 174 actual changed positions vs046 incl. checksum. Final ROM SHA **`1f6430064b70671a4f3ba94f0fd256764db54690950519c22d9e03ec74230dd9`**, clean-ROM IPS SHA **`725ca433dfeb919bd19bde6903a1e2e7d95cde1889980677863724007090cd6c`**, **44,980 bytes/1,671 records**, checksum **EB53/14AC**. Another separately implemented clean-ROM IPS decoder applied all patch records to exact Japanese ROM and reproduced full 2MiB ROM/ SHA and checksum (PASS).

**CURRENT TRIAL COUNTS:** 38 original UI direct slots + **48 Fortune** (33+15) + **36 Quiz** (21+15) + **328 distinct Story** = **450 translated direct text fields** in experimental ROM; separate G0/G1 actual Vietnamese artwork including `Việt hóa bởi Votri Valley` retained. **Not complete game**: Quiz canonical source has 381 rows, Fortune 157, and many longer questions/messages not integrated. G2 rules and G3 result assets still pending. Real emulator NOT TESTED; user previously reported poor V2 font, **FONT FIX AFTER CONTENT**.

**NEW ON GITHUB:** `translation/runtime/story_special_cp932_alignment_046.json`, `tools/build_content_first_046_story_special.py`, `translation/runtime/quiz_fortune_exactfit_047.json`, `tools/build_content_first_047_quiz_fortune_30.py`, `docs/CONTENT_FIRST_STORY_ALIGN_AND_QUIZ_FORTUNE_CHECKPOINT_047.md`. Source code uses pinned exact ROM and IPS SHA, aliases and native width guards. Local working files `/mnt/data/chibi046_local.sfc`, `/mnt/data/chibi046_local.ips`, `/mnt/data/chibi047_local.sfc`, `/mnt/data/chibi047_local.ips`, `/mnt/data/chibi046_story_static.json`, `/mnt/data/chibi047_static_qa.json`; DO NOT UPLOAD copyrighted ROM/TTF or send intermediate IPS links. GitHub CI not run; static/local verify only.

**NEXT MEANINGFUL WORK:** Quiz and Fortune full text records that need field expansion/wrapping; prioritise substantial content and keep complete `vi_full` translation. Then G2 real direct rule text and actual G3 result render assets. Do not return to minute 9px/65816 font tweaks until content is done. ONE meaningful full emulator QA when genuinely integrated.


## ACTIVE CHECKPOINT 045 — 2026-10-11: +139 ACTUAL STORY B02/B03, 313/336 STATIC COVERAGE

**USER explicitly dislikes month-long drip-feed and piecemeal IPS links. DO NOT SEND INTERMEDIATE IPS/ZIP LINKS.** Prioritize LARGE content edits and true ROM builds, font later. Read `docs/CONTENT_FIRST_STORY_BATCH02_03_CHECKPOINT_045.md` first, plus 044 below.

- **139 NEW actual original-ROM Story fields physically replaced** across Batch02 **58** and Batch03 **81**, on the exact clean-based 044 experiment. 368 native physical glyph segments, **367 immutable original line/page 816F/81A5 controls in edited rows**, and entire Story bank original line/page marker offsets unchanged. Other script opcodes untouched; zero edits to old font glyphs or G0/G1 Vietnamese game title/credit.
- **FINAL exact 045 experimental ROM SHA `7ddf449c2266838c3d55415f14aeee34fc21334c1ed0a490590647eb75e047b5`**. Clean-ROM IPS SHA `685d7e9f0146950ca030fd8469f57313a0b368be98e0a9c95999bda48cb65379`, size **43,679B /1,568 records**; independent clean-ROM IPS replay verified target ROM byte-for-byte. SNES checksum/complement **E4C1/1B3E**. Source ROM044 exact SHA `2312b9ba52c0cf6ac491e71117d5c537ad7dc61828dc9e87d838826e5165f322`. Relative to 044, **7,915 actually different byte positions** contained in **7,918 writable source glyph bytes + checksum**, no unexpected overlap.
- **Critical final preflight rejection**: earlier 045 draft had 140 rows, but `0x1A916` begins `88F3` potential internal text metadata; removed rather than corrupting technical stream. Final on-ROM count is **139**, NOT 140. Other such prefixes `FAF3`/`92F3`/`88F3` excluded. GitHub superseded `tools/build_content_first_045_story_140.py` deleted.
- **FINAL measured Story text coverage in this experiment**: Batch01 **120/126**, Batch02 **112/126**, Batch03 **81/84** = **313/336 Story source rows** containing Vietnamese codepoint bytes, **23 remain** with split Q/R/P number script/data or metadata. 402 directly tracked integrated source fields = prior 263 + 139, plus 3 separate preexisting tutorial rows; total **405** static direct-language source addresses incl. UI/Fortune/Quiz/Story. Separate graphics artwork G0/G1 and the exact startup credit **`Việt hóa bởi Votri Valley`** unchanged. NOT whole-game content coverage.
- New GitHub `translation/runtime/story_batch02_03_content_first_045.json` (139 runtime displays + canonical full `vi_full` and Japanese source references), `tools/build_content_first_045_story_139.py` (SHA/codepage/native line guards, explicitly blocks FF3 scanner prefixes, optionally rebuilds checkpoint044 from exact 043 IPS using `--rebuild-044-from-043` to avoid missing intermediate binary), `docs/CONTENT_FIRST_STORY_BATCH02_03_CHECKPOINT_045.md`.
- Local original Japanese ROM `/mnt/data/Chibi Maruko-chan - Mezase! Minami no Island!! (Japan)(1).sfc` SHA `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`. Local 043 IPS extracted from 043 user-facing ZIP, local exact 044 rebuilt from checked source `/mnt/data/chibi044_local.ips`, local 045 experimental IPS `/mnt/data/chibi045_local.ips`, local exact 045 ROM `/mnt/data/chibi045_local.sfc`; **DO NOT COMMIT COPYRIGHTED ROM OR SEND IPS DOWNLOAD LINKS WITHOUT USER ASK**. Local QA `/mnt/data/chibi045_qa_report.json`; local builder `/mnt/data/build_chibi045.py`.
- **RUNTIME STILL UNTESTED in SNES emulator**; previous user-reported font visual problem remains pending; user told us font AFTER content. Never claim game is finished or emulator PASS based on exact IPS and checksum alone.
- **NEXT:** resolve remaining 23 Story split-script/metadata safely, then large remaining Quiz/Fortune/G2/G3 real visible UI/ending content sweep. After content, one genuinely comprehensive emulator QA package. Do NOT do 10-row micro-checkpoints; commit real text/ROM work. Do not ask user to download/test until worthwhile.


## ACTIVE LARGE CONTENT CHECKPOINT 044 — 2026-10-11: +87 ACTUAL STORY DIALOGUES IN SAME ROM

**USER COMPLAINT**: project took too long with small checkpoints/pointless IPS links. **DO NOT OFFER DAILY IPS DOWNLOADS OR MAKE USER TEST EACH ONE.** FINISH CONTENT FIRST, FONT AFTER; make LARGE coherent batches. READ `docs/CONTENT_FIRST_LARGE_STORY_CHECKPOINT_044.md` FIRST.

- **ACTUAL patch from exact clean 2MiB retail ROM + checkpoint043** has inserted **87 additional Story records**: Batch01 **33**, Batch02 **54**, with **214 original line/page 816F/81A5 markers kept** across new fields, and all original Story bank break-marker positions unchanged. Full `vi_full` canonical meaning/character voice retained in source CSV; compact runtime separately reviewed in `translation/runtime/story_batch01_02_content_first_044.json`. G0/G1 Votri Valley title and 176 previously counted direct-text fields remain binary unchanged.
- **STATS CORRECTION:** `translation/source/story_batch01_vi.csv` has **126** canonical rows, NOT 123 as older handoffs claimed. At checkpoint043 exactly **84** rows tracked as newly patched 042/043. An additional **three** original tutorial rows at `0x181CC/0x18245/0x182BE` were ALREADY localized by an earlier unrelated layer in checkpoint043 ROM; script044 correctly refused to overwrite them. After +33 in 044, **117 tracked Batch01 rows** PLUS **3 preexisting Vietnamese** = **120/126** static-level translated, **6 remaining**. Batch02 current **54/126** translated, **72 remaining**; Batch03 **0/84** rebuilt in this sequence. This is raw-ROM codepoint evidence, NOT emulator runtime proof.
- Previous tracked total 176 (38 UI+33 Fortune+21 Quiz+84 Story). New **tracked 263 direct text records =176+87**. The three already-present tutorial records are identified separately, NOT double counted. Full game still missing longer Story, Quiz, Fortune, G2/G3.
- **Exact 044 target ROM SHA256 `2312b9ba52c0cf6ac491e71117d5c537ad7dc61828dc9e87d838826e5165f322`**. Clean original SHA `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`, input ROM043 SHA `45ffca7db5db83bc2734e885ee90c77f33746e2c4a54d1c99f1502f3e992a6ae`. New original-clean IPS **SHA `823009a95534b851b238efc439fa39c5b8af6af75a97075d1925e98f879c144d`, 33,893B / 1,193 records**. SNES checksum/complement **2DC9/D236**. LOCAL independent exact-clean IPS replay PASS; **4,682 modified bytes vs 043, whitelist exact; 2,340 writable source glyph units**. No font/glyph changes, emulator NOT TESTED.
- GitHub reproducible files: `translation/runtime/story_batch01_02_content_first_044.json` (87 reviewed runtime line sequences + canonical complete Vietnamese references), `tools/build_content_first_044_story_87.py` (exact SHA pins, source/capacity/control/offset guards), and `docs/CONTENT_FIRST_LARGE_STORY_CHECKPOINT_044.md`. Local patch only `/mnt/data/Chibi_044_Story87_Content_First_UNTESTED.ips`; **NOT FOR USER TO DOWNLOAD NOW**, user explicitly asked not to be sent intermediate downloads. Never upload copyrighted ROM or fonts.
- **NEXT IMPORTANT WORK**: continue remaining **72 Batch02 + 84 Batch03** as large meaningful scene batches. Six held Batch01 records with variable data or special script: `0x18408, 0x18708, 0x1873E, 0x189EE, 0x1A1B0, 0x1A334`; don't blindly alter. Design safe larger text/relocation if exact boxes lack full meaning. Then one combined emulator QA later. No font work per user.


## ACTIVE CONTENT-FIRST CHECKPOINT 043 — 2026-10-11: 58 ADDITIONAL ACTUAL STORY RECORDS IN ROM

**READ `docs/CONTENT_FIRST_STORY_CHECKPOINT_043.md` FIRST**, then checkpoint042 and 041. User's standing instruction: **FINISH CONTENT FIRST, FONT LATER**, preserve natural character voices and don't demand repeated tiny tests.

- New **58** manually context-edited Story Batch01 records have been PHYSICALLY WRITTEN to a clean-ROM-based IPS over exact 042 baseline, with **170 original physical line segments and 167 original `81 6F`/`81 A5` line/page controls preserved**. Canonical full `vi_full` texts in `translation/source/story_batch01_vi.csv` remain unchanged; each record in `translation/runtime/story_batch01_safe_segments_043.json` includes source offset, full Vietnamese reference, edited compact runtime lines, exact per-segment capacities. Offsets from 042 are excluded and existing prior patched ROM bytes are explicitly guarded.
- User-important writing consistency: Maruko/Tama-chan informal speech, Maruo's catchphrase `Nói thẳng ra!`, Hanawa's `Baby`, parents' dialogue and cartoon narration were maintained where old fixed ROM slots permit. Other longer natural canonical dialogue remains pending safe field expansion rather than machine truncation.
- Exact 043 local binary SHA256 **`45ffca7db5db83bc2734e885ee90c77f33746e2c4a54d1c99f1502f3e992a6ae`**, clean-ROM IPS SHA **`d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50`** (**28,135 bytes / 977 records**); 042 ROM base SHA `901744ff2edb6bbf667e225e68478009f426a4d1358c1c35ccb34cdc29254691`, source Japanese SHA `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`.
- Independent IPS apply to exact clean ROM reproduces entire 2MiB 043 ROM **byte-identical**; 4,144 changed byte positions vs 042 wholly within 58 Story text regions and SNES checksum/complement `E83A/17C5`. All existing Story bank `816F`/`81A5` marker positions untouched. **No font/gfx modifications**.
- **Cumulative current experiment: 176 direct translated fields =38 UI (039)+33 Fortune (040)+21 Quiz (041)+84 Story (26 in 042 +58 in 043)**, plus first-boot/selection G0/G1 artwork and required `Việt hóa bởi Votri Valley`. Story Batch01 now **84/123 text rows physically patched, 39 still pending**; other Story batches plus G2/G3, longer natural full text and complete Quiz/Fortune remain incomplete. SNES gameplay and old bad font visual appearance **NOT TESTED/FIXED**. Do NOT report release ready.
- GitHub new reproducibility: `translation/runtime/story_batch01_safe_segments_043.json`, `tools/build_content_first_043_story_58.py`, `docs/CONTENT_FIRST_STORY_CHECKPOINT_043.md`. Local exact IPS `/mnt/data/Chibi_043_Story58_Content_First_UNTESTED.ips` and independent QA JSON in local **`/mnt/data/Chibi_043_G0G1_176Fields_Story58_Content_First_UNTESTED.zip`**. Only patch/source, no copyrighted ROM or TTF committed to GitHub. GitHub CI **not configured**.
- **NEXT:** handle 39 remaining Batch01 long/exception Story frames with larger capacity proof (or meaningful next safe Batch02 coverage), not another lengthy report. Restore Story Batch02/03 from canonical `vi_full` and exact original script segmentation, no deceptive clipped text. Then G2 rule fix 0x1E325, G3 real result asset. One later comprehensive emulator test. **FONT LAST**.


## ACTIVE CONTENT-FIRST CHECKPOINT 042 — 2026-10-11: 26 REAL STORY DIALOGUE RECORDS PHYSICALLY PATCHED

**READ `docs/CONTENT_FIRST_STORY_CHECKPOINT_042.md` FIRST**, then checkpoint041 for Quiz. **USER DIRECTIVE: complete CONTENT first, font after.** Do not return to 9px/65816 font microtests.

- **ACTUAL NEW ROM PATCH (NOT MERELY CSV):** 26 first-arc Story Batch01 player-facing dialogue/narrator source records were safely rewritten through the existing V2 codepage over the verified clean-ROM-based checkpoint041 baseline (SHA `56c36cbc8e477d262216d3aa0f06909e09b9929ba0f6f544dccbaa3671bf48fb`). They occupy **41** source physical text segments. Real Japanese raw CP932 spans and original layout breaks understood, exact strict per-segment sizes validated. User-facing compact variants remain natural (`Cô có tin vui!`, `Tớ cũng muốn đi!`, `Tama-chan thi?`, `Tớ nói gì đâu...`, etc.) and **do not replace canonical full `vi_full`**.
- **Updated experimental 042 ROM SHA256 `901744ff2edb6bbf667e225e68478009f426a4d1358c1c35ccb34cdc29254691`**, header checksum/complement **3988/C677**. New exact CLEAN-ROM IPS SHA `3e3c3de245a9a0a6648b2e62eff44a72093ef1e2e9cfcb1cf013ff6c4cbb5035`; **23,105 bytes / 799 IPS records**. IPS replay via independent code -> exact byte-for-byte 042 output, only **794 byte positions changed vs 041**, all inside 26 approved Story glyph regions and checksum.
- **40 original `816F` (line) / `81A5` (page) delimiters preserved** within 26 records, and an independent scan confirmed unchanged positions of ALL corresponding marker pairs across entire Story ROM bank `0x18000..0x1DFFF`. Script low controls `00/08/0E/0F/12/14` kept. Font V2 codepage and G0/G1 original Vietnamese artwork bytes unchanged. One source at `0x18408` with raw ASCII `P` dynamic placeholder, and `印` scanner-artifact row skipped rather than corrupting game.
- TOTAL IN EXPERIMENT: **92 prior UI/Fortune/Quiz direct fields + 26 Story = 118 direct Vietnamese text records**, PLUS separate translated G0/G1 graphics (startup title/credit **Việt hóa bởi Votri Valley**, mode heading, Start/Password). **NOT whole-game translated**; old Story Build027 once logged 328 records but did not retain runtime candidate-builder, and this session recovers only first26. Many Story full phrases require more layout/relocation work.
- **NEW SOURCE IN GITHUB:** `translation/runtime/story_batch01_safe_segments_042.json` (26 choices, canonical full `vi_full` references, expected segment capacities); `tools/build_content_first_042_story_safe_segments.py` (exact raw 041 IPS+clean SHA, source reference audit, 84xx glyph mapping, byte-whitelist, control guard, output SHA and IPS replay); `docs/CONTENT_FIRST_STORY_CHECKPOINT_042.md`.
- Local patch-only ZIP `/mnt/data/Chibi_042_G0G1_118Fields_Story26_Content_First_UNTESTED.zip`, contains 042 IPS+Vietnamese README+two JSON QA; **not ROM/font**. Local verified original clean ROM remains `/mnt/data/Chibi Maruko-chan - Mezase! Minami no Island!! (Japan)(1).sfc`. Physical 042 ROM file local `/mnt/data/Chibi_042_26Story_Content_First_UNTESTED.sfc`, **DO NOT UPLOAD commercial ROM**. GitHub tool itself not CI-run; locally equivalent construction + independent ROM diff verifier passed. SNES emulator **NOT TESTED**, previous font visual FAIL not cleared, no release ready.
- **NEXT MEANINGFUL CONTENT:** continue segment-aware Story batch01/02/03 for remaining natural lines and true physical script capacities (no random truncated dialogue), then safe field expansion/relocation for long dialogue. G2 rules direct source offset fixed 0x1E325; G3 real win/lose graphics still pending. User prefers fewer bigger tests, so don't ask to run 042.


## ACTIVE CONTENT-FIRST CHECKPOINT 041 — 2026-10-11: 21 ACTUAL QUIZ CHOICES ADDED; 92 DIRECT VI FIELDS IN ROM

**Read docs/CONTENT_FIRST_QUIZ_CHECKPOINT_041.md FIRST**, then docs/CONTENT_FIRST_FORTUNE_CHECKPOINT_040.md, docs/CONTENT_FIRST_REAL_UI_ROM_CHECKPOINT_039.md. User asked to finish CONTENT and GRAPHICS first, font after. No 65816/spacing font experiments in 041.

- Starting from exact CLEAN 2MiB Japanese ROM SHA `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`, apply exact 040 clean-ROM IPS SHA `2bfdcc64973bc31ce268fa7e68a6118808c633b10d1437b7f811ac290616e580`; base040 ROM SHA `d892c51576c103f5881f1481c65fd2746635d222b1d387f9666cd7f44b1da3ac`.
- **21 new REAL Quiz answer labels** were encoded in original fixed two-byte CP932 fields (ages, birthdays, classes, floor labels, short answers), preserving original `816F` controls and byte budget. No partial-question scanner artifacts were patched. Five Quiz canonical source files were cross-checked live with 21/21 exact Japanese/full Vietnamese matches. New runtime `translation/runtime/quiz_answers_exact_fit_041.csv`; builder `tools/build_content_first_041_quiz.py`.
- Current 041 ROM SHA **`56c36cbc8e477d262216d3aa0f06909e09b9929ba0f6f544dccbaa3671bf48fb`**; exact clean-ROM IPS SHA `2117bc6e165f2c86263e74a637b6961a13f79257fccd9f02152a769fe1deb962`, length **22,100B/756 records**. SNES checksum/complement **327D/CD82**. Diff from 040 **132 bytes**, completely inside 21 Quiz fields+checksum.
- Independent local IPL IPS parser replay with actual exact Japanese ROM => byte-for-byte correct 041 ROM, checksum computed, all other bytes unchanged. Local ZIP **`/mnt/data/Chibi_041_G0G1_92UIFortuneQuiz_Content_First_UNTESTED.zip`** contains IPS + README + two QA reports, **NO copyrighted ROM/fonts**. GitHub builder not run in CI; real game emulator still **NOT TESTED**.
- Cumulative actual direct text in this branch's trial = **38 menu/VS/quiz UI from 039 +33 Fortune from 040 +21 Quiz answer choices from 041 =92**, plus G0/G1 translated title/credit/mode/start/password graphics from 036. This is NOT all 1,021 meaning rows: most Story/Quiz/Fortune, Karaoke and Credits **not in ROM**. 216 editorial `vi_full` source improvements from 032 were not automatically runtime integrated.
- **Important discovery for next handoff:** The GitHub repository still contains `translation/source/story_batch01_vi.csv` (123), Story batch02/03 source, and `docs/RUNTIME_STORY_BUILD_027.md` documenting old **328 field** segment-aware insertion, but **NO reproducible story runtime compact CSV / full Story builder in the current GitHub tree**, nor old exact direct-text Build035 binary. Must reconstruct segment-aware safe Story insertion from original ROM/layout; do NOT fill with stilted one-word dialogue to fake completion.
- G2 rules source offset fix 037 already committed; G3 result asset source still untraced. Actual font visual failure not cleared; user's priority remains font LATER. Avoid requesting user test a partial patch 041.

**NEXT:** Reconstruct real Story text stream boundaries incl. `816F` delimiters, 0E/0F metadata and soft layout spacing from original ROM. Build high-quality compact runtime candidates from canonical `vi_full` where they fit *each frame*; avoid overwriting control bytes or shortening character names. If dialogue cannot fit, research safe text allocation/relocation. Next integrate meaningful Quiz/Fortune from source and G3 result art, then a single LARGE real SNES emulator test.


## ACTIVE CONTENT-FIRST CHECKPOINT 039 — 2026-10-11: REAL G0/G1 + 38 VI DIRECT-UI FIELDS IN ROM

**IMPORTANT: NEW ACTUAL COMBINED LOCAL ROM BUILT**, not historical direct-text Build035. Read `docs/CONTENT_FIRST_REAL_UI_ROM_CHECKPOINT_039.md` FIRST, then 038, 037 and 036. User explicitly wants **all content/graphics first, typography fixes later**.

- Exact original clean SNES `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`, recovered existing V2 font/codepage baseline `2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd`, actual graphics036 (G0 title/credit + G1 Start/Password/Chọn gì đây?) `2c8beee73e985c9a2690cc36ace335f05115c1a3e81b369e09d0cfb132117090` were bytewise THREE-WAY combined from clean. **0 V2/graphics byte collisions** outside SNES checksum header. No changes to existing font glyph bitmaps.
- **38 ACTUAL DIRECT UI LABELS WRITTEN INTO NEW ROM** using source `translation/runtime/main_menu_compact_v1.csv` (10) + only accepted `runtime_candidate_exact_fit` records of `ui_choices_compact_v1.csv` (28). Every original CP932 two-byte source character, field length, terminator `816F`, ASCII and fullwidth 8140 padding checked. Each VI Unicode char mapped by `vi_codepage_v4_fe4_native.csv` through real V2 0x84 lead table. **Five `runtime_needs_expansion` fields deliberately untouched**, not abbreviated to gibberish: 28B28,28B40,28BC6,28BDE,31D3A.
- Local experimental ROM `/mnt/data/Chibi_039_Integration_38UI_UNTESTED.sfc` SHA256 **`a1f4459942e3a757cc314d12c959168046b4a6dd66018d55b014c70d052e98ce`**, checksum/complement **`7485/8B7A`**, changed 17,752 source bytes. Exact clean-Japanese IPS `/mnt/data/Chibi_039_Integration_38UI_UNTESTED.ips` **21,130B/674 records**. An independent IPS decoder reapplied all IPS records to original Japanese ROM and returned identical SHA. Exact graphic G0+G1 resource bytes and V2 lookup/glyph data compared and unchanged.
- **NO COMMERCIAL ROM committed**. IPS+README+two reports in local ZIP `/mnt/data/Chibi_039_G0G1_38UI_Content_First_UNTESTED.zip`, SHA safeguards described in `docs/CONTENT_FIRST_REAL_UI_ROM_CHECKPOINT_039.md`. Code in repo `tools/build_content_first_g0g1_v2_38_ui_039.py`; local equivalent built and executed from verified 38 reviewed source candidates and real ROM, final exact output independent QA PASS. GitHub script itself NOT run in CI, no CI checks configured.
- This **is NOT a complete translation**: historical direct-text Build035 (Story/Quiz/Fortune/Credits etc) binary absent and no source replay to main storyline yet. 032 completed 216 `vi_full` reviews in canonical CSV, but those do not magically appear in 039 ROM. Old 025 typography user FAIL; 039 live emulator **NOT TESTED**, legacy V2 font **NOT FIXED**, do not ask user to test this partial candidate.
- G2 rule fix 037 offset `0x1E325` remains source-only and G3 result assets still unproven. Keep working on **reproducible direct-text Story/Quiz/Fortune insertion from canonical CSV** or find actual 035 binary/patch, and G3 proper executed result. Aim one large later runtime test.


## ACTIVE CONTENT-FIRST CHECKPOINT 038 — 2026-10-11: G3 FALSE-LABEL EXCLUSION + DIRECT-TEXT/GRAPHICS MERGE GATE

**READ:** `docs/G3_RESULT_AND_GRAPHICS_TEXT_MERGE_CHECKPOINT_038.md` before checkpoint037 and 036. User still wants to finish all CONTENT/TEXT/GRAPHICS BEFORE returning to font. Do not return to 65816 9px probes.

- **NO G3 retail result image verified yet.** Exact clean ROM searched for CP932 six target labels: `勝ち` only at `0x1C04F/0x1C25C/0x1D03A` in Story dialogues; `敗けた`, `コンティニュー`, `やめる`, `最終勝利`, `エンディング` each has a sole exact phrase in **internal QA descriptor block** `0x2865E..0x287FF`. Not player-facing Win/Lose/Continue labels; DO NOT patch as result art. Tools: `tools/audit_g3_literal_source_scope_038.py`, local report `Chibi_G3_Result_Literal_Source_Audit_038.json`. Queue G3 six entries now accurately classified.
- **NEW REAL THREE-WAY INTEGRATION PREFLIGHT SCRIPT:** `tools/merge_graphics036_directtext035_preflight_038.py` requires exact original Japanese ROM SHA `e62768e8...`, historical DIRECT-TEXT Build035 SHA `f8fb662a...`, and actual clean-based GRAPHICS checkpoint036 SHA `2c8beee7...`. Full occupied-resource safeguards for G0 title graphics/title map/bank86 relocation `0x36907..0x37662`/G1 Story sprite/G1 main heading/pointer. Byte whitelist validates all **13,129 changed bytes** from exact graphics036, **0 outside known regions**. Refuses to merge if Build035 changed any byte in any reserved graphics allocation; separate loader signatures checked. Only explicit opt-in can generate an untested merged ROM/Build035-relative IPS after PASS.
- **NO ACTUAL FULL MERGE THIS TURN**: exact direct-text Build035 ROM binary absent from active container, repository's 265-entry tree contains no direct-text Build035 ROM or patch, and available Library/conversation filename search found no candidate. DO NOT pretend the synthetic test is Build035 or that graphics036 already includes Story/Quiz/Fortune text.
- Offline local REAL exact-clean+GRAPHICS036 and **synthetic unrelated text fixture** test: two text edits outside graphics survive a hypothetical merge, FIVE injected G0/relocation/G1 conflicts are rejected. Report `/mnt/data/Chibi_038_Graphics_Text_Merge_Simulated_Preflight.json`. Selftest source: `tools/selftest_merge_graphics036_directtext035_038.py`. The test is **simulated text**, not live Build035, no gameplay QA or CI check.
- G2 prior checker typo fixed: expected `vi_full` bullet spacing matches actual `translation/source/rules_tutorial_vi.csv`; no ROM modifications.

**NEXT WORK:** (1) retrieve exact Build035 original binary or reproducible exact direct-text patch if available; run 038 safe merge preflight, preserve all Vietnamese canonical content; (2) trace G3 actual result-screen CALLBACK/pointer to prove retail win/lose/continue graphics before edits; (3) test actual SNES emulator after one large combined build; (4) **FONT AFTER**. User prefers real localization work, not endless checklists/rounds of font tests.


## ACTIVE CONTENT-FIRST CHECKPOINT 037 — 2026-10-11: G2 DIRECT TEXT ORIGINS AND CP932 OFFSET FIX

**Read `docs/G2_RULE_TEXT_ACTUAL_ROM_SOURCE_CHECKPOINT_037.md` first.** Continue Vietnamese text/graphics first, NO font/9px/65816 patch at this time per explicit user direction.

**VERIFIED NEW EVIDENCE ON THE EXACT CLEAN ROM:**
- G2 rules/source phrases `ルールをせつめいするよ`, `２本先取だよ`, `ゲームの時間は勝つまでだよ` are real **CP932 DIRECT-TEXT** at file offsets `0x1E307`, `0x1E325`, `0x1E339`, respectively. First source record layout begins `0x1E2FF`. Two source full-width bullets are at `0x1E323` and `0x1E337`; three `816F` delimiter pairs checked. Their actual retail render callback still untraced; DO NOT claim direct language is already active in 036 graphics-only ROM.
- **FIXED BAD SOURCE OFFSET** `translation/source/rules_tutorial_vi.csv`: old `0x1E326` was the second byte of Japanese fullwidth digit ２ (`82 51`). Correct is `0x1E325`. Updated Vietnamese rule wording to `Ai thắng 2 ván trước sẽ thắng / Chơi đến khi phân thắng bại`, still bullets semantically. One source-row offset correction and one `vi_full` wording edit in repo.
- **35 known G2 VS/minigame menu/UI labels** at ROM offsets `0x288C2..0x28BFF` were individually checked for CP932 and UI source record identity; three rule rows intentionally begin with TWO ASCII spaces before the Japanese label. All 35 have existing semantic Vietnamese in `minigame_ui_batch01_vi.csv`. New reproducible tool `tools/audit_g2_rules_direct_sources_037.py`. Local report `/mnt/data/Chibi_G2_CP932_Source_Audit_037.json` PASS using exact clean ROM and locally reconstructed representative source rows; GitHub live full CSV separately reviewed, **NO CI result claimed**. Negative control with original wrong offset `0x1E326` fails as intended.
- Reclassified three G2 graphics-queue entries to `DIRECT_CP932_TEXT_SOURCE_FOUND`, NOT graphics patches. Need actual text renderer/line-wrap integration from Build035.
- Read-only resource scouts generated `chibi_g2_candidate_sprite_sheet_1.png` (42 near G2 packages) and `Chibi_G3_Result_Sprite_Atlas_037_[1-3].png` (52 sprite source+dest pairs). None conclusively identified a real G3 victory/lose/continue text source or a verified new graphics patch. **Do not infer paths from contact sheet alone.**
- G2 label `今からやるよ` exact CP932 hit `0x286EA` is in internal descriptor/debug area; DO NOT patch that offset as retail label, visible source still unproven.
- Historical GRAPHICS-only checkpoint036 ROM/IPS remains SHA256 `2c8beee73e985c9a2690cc36ace335f05115c1a3e81b369e09d0cfb132117090` and **SNES emulator UNTESTED**; G0 first boot title + Votri Valley credit, G1 main-mode heading + Start/Password are real static ROM patch assets. Original Story/Quiz/Fortune DIRECT-TEXT Build035 separately exists by SHA256 `f8fb662a9e1b8fc5a5ff689f690ceaf332055ed86983e52b476a78852e4fd58d`, but binary not available in current runtime. **Do not overlay the graphics-only IPS on Build035 blindly** or claim whole-game patch.

**NEXT PRACTICAL PRIORITIES:** (1) trace G3 RESULT screen callback/pointer to actual visible Win/Lose graphics/text; (2) trace G2 rule-field live use and integrate corrected CP932 source offset into direct-text patch pipeline; (3) find exact Build035 candidate and collision-audit G0/G1 036 against it; (4) deliver one LARGE combined test build when ready, font LATER.


## ACTIVE CONTENT-FIRST CHECKPOINT 036 — 2026-10-11: MAIN MENU “CHỌN GÌ ĐÂY?” ACTUAL PATCH

**Read first:** docs/G1_MAINMENU_HEADING_ACTUAL_PATCH_CHECKPOINT_036.md, then checkpoint035 (Story buttons), checkpoint034 (start title), and translation/runtime/content_first_graphics_queue_032.csv.

- **New REAL original heading asset FOUND AND EDITED**. Main-mode initializer ROM file 0x20047: LDX #$A213; JSL $80:E255. Package $82:A213 file 0x12213 resource index6 -> CPU $98:F06F, file0xC706F, VRAM word0x7000. Directly decompressed/visually confirmed Japanese two-row mode-select heading in 256 4bpp sprite tiles. First 192 tile IDs hold other Japanese mode labels and arrow; last 64 tile IDs 192..255 hold question heading.
- Patched only tiles192..255 into two native 16px rows **“Chọn gì” / “đây?”**; original first 192×32=6144 decoded bytes remain IDENTICAL. Graphic codec source 3485 compressed bytes -> **2428**, in-place (no relocated source or package pointer edits). Thick shadow draft rejected; final uses clean 14px raster.
- Merged onto exact GRAPHICS checkpoint035 G0+G1 ROM, keeping actual first-boot **Chibi Maruko-chan / Tiến tới đảo phương Nam!! / Việt hóa bởi Votri Valley**, and Story choice **Bắt đầu / Mật khẩu** bit-identical. New combined **GRAPHICS-ONLY** ROM SHA256 **2c8beee73e985c9a2690cc36ace335f05115c1a3e81b369e09d0cfb132117090**, SNES checksum/complement 3A35/C5CA. Clean Japanese ROM IPS **14452 bytes, 263 records** independent replay exact PASS. Local zip **Chibi_G0_G1_ChonGiDay_036_UNTESTED.zip** (IPS, README, rendered tile preview, two QA JSON). NO ROM or font binaries in GitHub.
- **13 original UI package scripts share $98:F06F / VRAM0x7000**. All pointers were checked, no collision or corrupted data. Exact screen rendering of each using this asset is UNPROVEN; real emulator regressions are required.
- Source docs + two scripts on GitHub: tools/build_g1_mode_heading_vietnamese_036.py and tools/verify_g1_mode_heading_036_independent.py. G1 heading has advanced from UNRESOLVED to EXPERIMENTAL_PATCH_STATIC_RECONSTRUCTED in graphics queue.
- **DO NOT CONFUSE** local “graphics checkpoint035” (clean-ROM graphics, SHA77a2...) with historical direct-text “Build035”. FULL STORY/QUIZ/FORTUNE source translations (1,021 tracked rows; 216 editorial final revisions) are NOT included in graphics036 ROM. Runtime SNES emulator is still NOT TESTED. No claim of game completion.
- User explicit order remains CONTENT/GRAPHICS FIRST, FONT LATER. Continue real G2 VS rule-panel and G3 result/ending assets, then stage collision-checked combined Story+Graphics test build. Do not re-enter 65816 font microtests now.


## ACTIVE CHECKPOINT 035 — 2026-10-11: G1 TWO VISIBLE CHOICE GRAPHICS ACTUALLY VIETNAMESED

**USER DIRECTIVE: finish content/graphics first, font after.** New actual G1 **Start/Password** sprite source is decoded and patched; no 65816 font work. Read `docs/G1_START_PASSWORD_ACTUAL_ROM_PATCH_CHECKPOINT_035.md` first, then checkpoint034 for G0.

- G1 first Story choice screen initializer `$85:E97F` loads type-0 resource package **`$82:AF23`**. Its resource entry 8 at ROM `0x12F4D` uploads **`$97:F95E` / file `0xBF95E`** into VRAM word **0x7800**. Original game decompresses **436 compressed bytes -> 992 bytes = 31 8×8 SNES 4bpp sprite tiles**, directly decoded and visibly confirmed to contain `はじめから` and `パスワード` plus the two-tile icon. This was also present in historical `tools/extract_g1_story_select_assets.py` but was still incorrectly marked unresolved in the content queue; now corrected.
- G1-only actual clean-ROM graphics patch rasterizes **`Bắt đầu`** and **`Mật khẩu`** to the original tile slots (0..14, 16..28). Original 15 spacer + 29,30 game icon preserved exactly. Original 992-byte resource footprint, **new compressed span 331B (<436B original)**, in-place at `0xBF95E`, source package pointer unchanged. New G1-only ROM SHA256 **`9a7bddb9afb7062a63c775e647c9ee04c226202bd16d23a7d5aadf091ea1bdaf`**. All sprite resource and byte-whitelist static checks pass, **NO emulator/runtime QA**.
- Merged G1 in-place sprite bytes into exact G0 checkpoint034 title-only ROM, no shared edit offset except checksum (0 collisions), keeping G0 relocation bank86 at file0x36907 and G0 logo gfx resources unchanged. G0+G1 **CLEAN JAPANESE ROM GRAPHICS-ONLY** experimental SHA256 **`77a207589857d2886059057151eaf3d47530032b726744fe739e991ff81a5b80`**, SNES checksum/complement **470A/B8F5**, joint IPS **10,880 bytes /225 records** tested by independent clean-ROM IPS replay. Local bundle `Chibi_G0_G1_Title_Start_Password_035_UNTESTED.zip`.
- **Important:** this is **NOT** full Vietnamese ROM; earlier direct-text Story/Quiz/Fortune Build035 not integrated. No emulator installed. 8px G1 sprite style may need final readability QA. **Pink heading `どれにする？` / `Chọn gì đây?` STILL UNPATCHED**, its source is not the G1 Story option sprite. Continue graphics asset extraction, don't regress into font-only patches.
- GitHub new tools `tools/build_g1_start_password_vietnamese_035.py`, `tools/verify_g0_g1_graphics_035_independent.py`; queue `translation/runtime/content_first_graphics_queue_032.csv` now marks only G1 Start/Password `EXPERIMENTAL_PATCH_STATIC_RECONSTRUCTED`, while G1 heading remains `UNRESOLVED`.
- Next practical work: trace remaining G1 heading or G2 rules/G3 result display assets; add actual visible graphics translation; then explicitly collision-audit clean-ROM G0+G1 against historical direct-text Build035 before assembling full game. Do not blindly overlay IPS from Japanese clean onto Build035. Don't demand another player test per tiny asset.


## ACTIVE CHECKPOINT 034 — 2026-10-11: ACTUAL G0 TITLE GAME GRAPHICS PATCH CREATED

**NEW HIGH-IMPACT CONTENT/GRAPHICS WORK — READ FIRST:** `docs/G0_ACTUAL_TITLE_ASSET_REPACK_CHECKPOINT_034.md`.

- **Actual title asset DISCOVERED** by decoding clean SNES ROM. Initializer near file `0xFEE`: `LDX #$A087; JSL $80:E255`. This loads exact ten-resource retail graphics package `$82:A087` (file `0x12087`). Its title BG tilemap resource `$9E:9F00` (file `0xF1F00`), 2048B VRAM word0, and 4bpp title graphics `$9E:E456` (file `0xF6456`), 8192B VRAM word0x2000. Offline render visibly reproduces original Japanese `ちびまる子ちゃん めざせ！南のアイランド！！`; this is not inferred from descriptors.
- **Real binary graphics edit** made to user's exact clean ROM: SNES 4bpp/tilemap for `Chibi Maruko-chan`, `Tiến tới đảo phương Nam!!`, `Việt hóa bởi Votri Valley`, each line visually decoded back FROM THE PATCHED ROM offline. Main 25px, subtitle 18px, credit 11px, 256x88 pixel title layer, 166 isolated new tile IDs.
- **Protected original characters and copyright graphics**: four non-title tilemaps `0x400/0x1000/0x5000/0x5800` and 583 shared 4bpp IDs remain byte-identical, entire OBJ VRAM 0xC000..FFFF unchanged, title map lower rows preserved. Initial destructive version was REJECTED; do not reuse. Source screen art/palettes on other layers preserved offline, not in-game verified.
- Gfx bank0 modified at ROM `0xF6456` compressed **4582 of 5570** slot; title tilemap `0xF1F00` compressed **506 of 545**; middle bank `0xF5005` unchanged; bank2 modified 3420 bytes exceeds old `0xF456D` 2712B slot, therefore moved to originally free ROM file **`0x36907` / CPU `$86:E907`**, with exactly 3 pointer bytes updated at `0x12095` inside G0 package. Original bank2 stream left untouched.
- Local G0 title-only **UNTESTED experimental ROM** SHA256 `012cdfb87eae1b7c5a9feada4e1c322541e3c91ba45ba0b857e08a2465f47ce0`, 9317 bytes changed from clean, checksum/complement `20C8/DF37`. **IPS patch 10,415B, 218 records**, independent application reproduces exact ROM SHA. G0 resource roundtrip / other maps and sprites checks PASS. Local zip `Chibi_G0_TieuDe_VotriValley_Only_UNTESTED.zip`; no ROM binaries uploaded to GitHub.
- **Critical:** G0 demo is based on CLEAN Japanese ROM only, NOT Build035, so story/menu/quiz remain Japanese. Never claim a complete Vietnamese game. Don't overlay IPS on Build035 until checking resource and relocation conflicts. No emulator installed here, **actual title gameplay Runtime UNTESTED**. Do not mistake asset decode / IPS roundtrip for emulator acceptance.
- New GitHub scripts `tools/build_g0_first_boot_title_votri_experimental.py`, `tools/verify_g0_title_034_real_asset_static.py`, source contract `translation/runtime/g0_startup_title_copy_v1.json` now marks actual G0 source proven, and graphics queue G0 priority P0 has experiment recorded.
- Continue **CONTENT FIRST**: next work should be G1 actual Start/Password graphics or safe layering G0 title delta onto confirmed Vietnamese build after collision checks. Font probes 025–031 remain deferred per user instruction. Runtime screen test only when one meaningful combined build exists; avoid many tiny test ROMs.


## G0 STARTUP TITLE — USER CONFIRMED 2026-10-11 (PRIORITY P0)

**EXACT DISPLAY COPY:** `Chibi Maruko-chan` / `Tiến tới đảo phương Nam!!` / small `Việt hóa bởi Votri Valley`. This is the **title screen seen immediately at boot**, not an internal descriptor or later Story option. Preserve original copyright/publisher marks and game operation. Graphics targets + glossary + G0 reverse pipeline must use the exact spelling **Votri Valley**, with a space and without the previous branded form. Title artwork asset/layout still unproven; no in-ROM title rendering or gameplay PASS is claimed. Proceed with content/graphics work, leave font checkpoint031 frozen.


## ACTIVE CONTENT-FIRST CHECKPOINT 032 — 2026-10-11 — VIỆT HÓA TRƯỚC, FONT SAU

**USER DIRECTION OVERRIDES PRIOR FONT PRIORITY:** finish all recoverable Japanese-language content and graphics wording before returning to font/9px/65816 runtime experiments. Do not make another 032+ font probe next. Font history 025 user FAIL, 029 static-only, 031 parser audit stays preserved/on hold.

**READ FIRST:** `docs/CONTENT_FIRST_CANONICAL_MERGE_CHECKPOINT_032.md`, `translation/TRANSLATION_PROGRESS.md`, `translation/runtime/content_first_graphics_queue_032.csv`, then graphics reverse docs from handoff below.

**ACTUAL CONTENT WORK COMMITTED:**
- Translated/edited Vietnamese from 10 older review CSVs has NOW BEEN APPLIED TO REAL `translation/source/*.csv` canonical `vi_full`, not merely archived editorial suggestions.
- **220 editorial events**, **216 distinct verified `(source file, ROM offset)` keys**; 4 later-pass overrides. **209 value-changing editorial operations**, 11 values already in place. 20 canonical source CSV files in Story, Maruko Q, Fortune, main menu/quiz UI/minigame/stages.
- Post-write LIVE GITHUB verification individually compared all 216 final `vi_full` strings against the winning editorial revision. **Story 85/85, Quiz 54/54, Fortune 24/24, UI 53/53; TOTAL 216/216 PASS, ZERO conflicts.** JavaScript CSV merge preserved Japanese originals, file offsets, technical fields, notes and UTF8 BOM where present. Three editorial conflicts manually resolved with source context.
- New standard-library reproducible QA: `tools/audit_g2_editorial_canonical_032.py`, checks 220 edit events -> 216 latest row identities in 20 source files.
- Language counts reconciled: **1,018** existing regular release-intent meaning rows + **3** G2 demo rows = **1,021 historical known source-row records**. Not whole ROM coverage, not 1,021 newly translated lines and not runtime pass.
- New concrete **16-target G0–G3 graphics localization queue** `translation/runtime/content_first_graphics_queue_032.csv`: source Japanese, frozen target Vietnamese, visual-evidence level, asset blocker, next actions, release gate. One VS original Latin unchanged, one user-requested new credit, 14 existing Japanese labels requiring original asset identification/redraw/insertion.
- G0 title and credit, G1 choice/Start/Password, G2 rules/banner, G3 results/ending wording already prepared. **Actual graphics source path still pending**, so don't patch internal debug descriptors as if retail graphics. Old known direct-text banks already meaning-covered; no new Japanese source rows invented this round.
- No ROM, font glyph, codepage, or renderer was modified this checkpoint. No new build or emulator runtime PASS.

**NEXT WORK MUST BE CONTENT/GRAPHICS, NOT FONT:** use existing G1/G0 rendering pipeline to prove actual bitmap/tilemap or compressed asset feeding visible Start/Password/heading; prepare real Vietnamese graphic replacements for verified assets, then G2 and G3. Add new meaning rows only when source and retail visibility are grounded. Keep runtime integration/acceptance separate from language completion. ROM remains off GitHub.


## ACTIVE CHECKPOINT 031 — 2026-10-11: RECOVERED V2 + EXCLUSIVE CALLGRAPH + QUOTE PREFLIGHT

**Read first:** `docs/G2_PROBE008_RECOVERY_CALLGRAPH_CHECKPOINT_031.md`, then checkpoint030, checkpoint029 and the user screenshot failure checkpoint026.

- Locally **recovered exact canonical Probe008 V2 font-only ROM** from the user's uploaded FAILED checkpoint025 binary by reverting only its two renderer JSL calls, injected staging bytes and recalculating checksum. Recovered 2MiB SHA256 `2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd` EXACT, 191 reversed byte positions, SNES checksum `622E/9DD1`. **This is not a new runtime-good candidate.** Tool: `tools/recover_g2_probe008_v2_from_failed025.py`.
- New actual-ROM direct call scan finds exactly ONE `JSL $85:8E7B` parser->renderer (0x28413), and ONE `JSL $85:8E05` renderer->helper (0x28E83); no same-bank direct JSR to either. Parser restores **A16 with REP #$20** immediately before loading mapped glyph ID and calling renderer. Strengthens justification for the 029 word-hook `PHA` stack model; indirect calls/live flags remain unproved. **7/7 mutation guards reject corruption**. Tool: `tools/audit_g2_probe008_031_direct_call_graph.py`.
- New physical font/lead-map preflight on exact CLEAN + recovered V2: native quotes `8175/8176` map to `0159/015A`; proposed `8574/8575` map entries are empty; `0A54/0A55` 12×12 font cells are physically blank. Three 106-byte G2 fields each contain exactly one opening/closing quote and original 816F controls at pair indices 16/34/52. Zero original raw `8574/8575` pairs in Story bank, 13/6 raw matches elsewhere in full ROM: **global 0x85 safety still UNPROVEN**. Tool: `tools/audit_g2_probe008_031_alias_preflight.py`.
- Both read-only audits executed on exact original and recovered V2 ROM locally; JSON reports generated. No new binary distributed/uploaded to GitHub. **029 is still static-only; 025 is confirmed user RUNTIME TYPOGRAPHY FAIL; SNES emulator absent.**
- Next highest priority: real SNES debugger trace for 029 word/shift hooks and V3 font screenshot quality. Then test Japanese punctuation/UI and story, and continue G0/title, G2/G3/menu/minigames after font gate.


## ACTIVE CHECKPOINT 030 — 2026-10-11: ORIGINAL RENDERER STACK & ALIAS OCCUPANCY

**Read first:** `docs/G2_PROBE008_RENDERER_STACK_AUDIT_CHECKPOINT_030.md`, then checkpoint029 and checkpoint026.

- Read-only analysis of exact original ROM verified **9 instruction anchors** from text parser → renderer `PHB;PHX;PHY;PHA` → word lookup `0x28E0C` → atlas-pointer x/y → shift lookup `0x290EE`. Saved original glyph ID in A is at **`$0A,S` (X8)** or **`$0C,S` (X16)** under a 16-bit A assumption. 9 mutated original-code fixtures rejected; this is a structural/static check, NOT actual 65816 runtime trace.
- Original Japanese quote IDs `0159/015A` each have 11 lit bitmap pixels and width four pixels in their original page1 cells, so duplicate G2-only glyphs need no shape alteration.
- New G2-only quote code pairs `8574` and `8575` occur **13** and **6** times as raw bytes in original ROM, but **ZERO times inside full bank file `0x18000..0x1FFFF`** containing G2 Story. Other banks may contain code/data matches; full global 0x85 safety remains UNPROVEN.
- Committed `tools/audit_g2_probe008_030_renderer_stack_contract.py` and doc 030; local JSON `Chibi_Probe008_030_stack_contract_report.json`. No ROM changes made this round, no emulator installed/accessible. 
- **029 remains ONLY STATIC PASS / emulator UNTESTED. 025 remains USER RUNTIME TYPOGRAPHY FAIL. Do not claim fixed gameplay, and do not send a release ROM yet.** Continue with real debugger at `$85:8E0C` and `$85:90EE`, font V3 tone/quote/wrap and native Japanese UI QA, then remaining content.


## ACTIVE CHECKPOINT 029 — 2026-10-10: QUOTE-ISOLATED G2 9px + V3, STATIC ONLY

**Read first:** `docs/G2_PROBE008_ISOLATED_QUOTES_CHECKPOINT_029.md` then checkpoints 028, 027 and **026 user screenshot RUNTIME FAIL**.

- Critical 028 risk: original Japanese quotes `8175` and `8176` appear as raw bytes 121 and 123 times respectively outside three G2 records; globally selecting 9px for their native glyph IDs `0159/015A` could disrupt other scenes (raw occurrences ≠ guaranteed visible text).
- New 029 experimental strategy: **copy the two native quote bitmaps into two spare G2-only 9px glyph slots** `0A54/0A55`. Extend already-staged lead `0x85` with `8574/8575`, and change ONLY the 3 G2 opening +3 closing quote code-pairs `8175/8176` -> `8574/8575`. This **intentionally changes 12 bytes of original G2 text** while preserving all other dialogue, strict 2-byte record lengths 3×106, separators `816F` at 32/68/104, D038, scene, native Japanese glyphs and 13px lookup tables. **Do not claim all G2 payload bytes remain identical.**
- Word/shift 9px selectors now cover custom IDs `083A..0863`, `090A..0963`, `0A00..0A55` and EXCLUDE native quotes `0159/015A`, preserving Japanese original 13px spacing outside G2.
- Locally built 029 ROM SHA256 `a23304cedff0eac959a6455d90b866c49543ca381425b089771b65da264e928e`, 180 diff bytes vs exact 028 V3 geometry diagnostic SHA256 `59f4c45b14a24e6cf67de1c9c7cbe1d9b862eaa2eb4c6518bbc4bcbd6dd006fb`, checksum/complement `9309/6CF6`, hook sizes 61/86 bytes.
- All 83,600 micro-executions of both new 65816 lookup stubs, 1,100 slots × 19 positions × 2 X widths × 2 hooks, STATIC PASS. Every G2 drawable token uses 9px; native quote glyph IDs use 13px; new quote IDs bitmap-identical to originals.
- New GitHub tools: `tools/build_g2_probe008_029_isolated_quotes_diagnostic.py`, `tools/selftest_g2_probe008_029_isolated_quotes_opcode.py`. Explicit `--allow-untested-diagnostic` required for ROM output. No ROM uploaded.
- **Not fixed in-game yet.** No emulator accessible here; container outbound DNS cannot resolve GitHub, apt package lists unavailable. Checkpoint 025 has user-confirmed RUNTIME TYPOGRAPHY FAIL. 029 is diagnostic only; do not offer user another "fixed" ROM until live 65816/PPU test. New lead `0x85` can still conflict with untraced native data and must be audited.
- Next: verify both lookups in a REAL SNES debugger and check font V3 readability/line wrap and Japanese UI; only then resume G0/title, G2/G3 images, menu/minigames translation.


## ACTIVE CHECKPOINT 028 — 2026-10-10: REAL GLYPH / ATLAS 9px + V3 MEDIUM STATIC ONLY

**Read first:** `docs/G2_PROBE008_GLYPH_GEOMETRY_V3_CHECKPOINT_028.md`, then checkpoint 027 and checkpoint 026.

- **Checkpoint025 user runtime typography FAIL is still binding.** No 028 gameplay test/emulator screenshot; DO NOT release any 028 ROM yet.
- Fixed an old conceptual mistake: glyph ID in actual renderer comes from input A saved by `PHA` at `$85:8E7B`, **not from `$001FB2`**. Old 023 glyph-aware selector based on $1FB2 was not justified. Old 025 scene-bank DBR/pointer gate likely fell back at runtime and visually FAILED.
- In word table hook at `$85:8E0C`, actual glyph ID is on CPU stack at `$0A,S` for X8 or `$0C,S` for X16. At shift hook `$85:90EE`, renderer has already computed font-page pointer `$18` and atlas offsets `$08/$0A`; neither requires assumed DBR source bank. Quote glyph IDs 0159/015A handled explicitly.
- New **READ-ONLY** `tools/audit_g2_probe008_renderer_glyph_geometry_028.py`: 1,100/1,100 font page-cell IDs matched between two lookups, 218 glyph IDs eligible for 9px (including original Japanese quotes), 882 keep 13px. The exact three G2 106-byte records have 50 drawable 2-byte codes + 3 separators each; **all 150 drawable codes match 9px selection**.
- New opt-in `tools/build_g2_probe008_glyph_geometry9_diagnostic.py`: local UNTESTED ROM SHA256 `a3d2e75da5f9dac36750ef77e249fae7613ffd35f8185c50cd6f6197ca8a8688`, 258 bytes diff vs V2 font-only, SNES checksum `C1E2/3E1D`. 71-byte word and 120-byte shift 65816 hooks. Original G2 records and 13px tables intact.
- New `tools/selftest_g2_probe008_geometry9_opcode_028.py`: executes generated 65816 subset for **83,600** combinations (1,100 IDs ×19 positions ×2 X widths ×2 lookup hooks); all static PASS; **not real SNES**.
- New `tools/build_g2_probe008_v3_medium_geometry9_experiment.py`: local V3 combo SHA256 `59f4c45b14a24e6cf67de1c9c7cbe1d9b862eaa2eb4c6518bbc4bcbd6dd006fb`, 1,183 diff bytes from geometry-only, checksum `7587/8A78`, 178 custom glyphs weight-increased, 32 relocated native glyphs preserved, 210 full bitmap roundtrips and 44,100 glyph-pair 9px collision checks PASS, 5,055 total ink pixels. Both builders reject calls unless user explicitly opts into UNTESTED diagnostic. No ROM committed to GitHub.
- **CAVEAT:** native Japanese quote IDs 0159/015A select 9px anywhere in game (even outside G2), so Japanese UI/Story quoting is not guaranteed unchanged. Real SNES debugger and screenshot are mandatory, plus 0x85 lead/page integrity checks. Only after font passes, resume G0 title, G2/G3 graphics, rest of translation.


## ACTIVE CHECKPOINT 027 — 2026-10-10 V3 MEDIUM FONT (DATA-ONLY)

**READ FIRST:** `docs/G2_PROBE008_V3_MEDIUM_FONT_CHECKPOINT_027.md`, then `docs/G2_PROBE008_USER_RUNTIME_FAIL_CHECKPOINT_026.md`.

- **Probe008 025 remains USER SCREENSHOT RUNTIME TYPOGRAPHY FAIL.** No new ROM has passed gameplay. 025's 9px selector is quarantined and must NOT be reused as a known-good baseline.
- Static renderer re-audit: parser `$85:8340` uses `$1F94` to read source; renderer `$85:8E7B` calls word table at `0x28E0C` through helper `$85:8E05`; shift lookup at `0x290EE` after DBR bank switch. Screen's ~13px pitch is consistent with fallback, but needs live emulator DBR/`$1F94` trace. Columns and wrap are separate from physical glyph spacing.
- Proposed **V3 medium-weight font only**, NO ROM patch: 178 custom physical glyphs strengthened by one pixel right on body rows y>=4, 32 relocated native glyphs preserved, 212 Unicode mappings untouched, 210 physical glyphs, 180 mapping rows changed due aliasing. Total proposed ink 5,055 (baseline V2 3,651), **zero collisions for 44,100 ordered glyph pairs at 9px**.
- Added `tools/propose_g2_probe008_v3_medium_font.py`. It generates JSON only from exact V2 13px font-only source (sha256 `2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd`), audits bitmap identity and refuses wrong input. Renderer hooks, codepage assignments and original commercial ROM remain untouched.
- Local offline comparative image `Chibi_Probe008_V3_Font_Weight_Prototype_027.png` has 2x2 full-line layouts for 13px V2, 9px V2, 9px V3 medium, 9px V3 dense. This image is **not emulator output**.
- Need real emulator trace for runtime 9px activation BEFORE offering another experimental ROM. Do not claim V3 runtime PASS, Japanese menu compatibility, or full-game translation. Finish G0/G2/G3 content afterward.


## ACTIVE CHECKPOINT 026 — 2026-10-10 USER SCREENSHOT RUNTIME TYPOGRAPHY FAIL

**READ FIRST:** `docs/G2_PROBE008_USER_RUNTIME_FAIL_CHECKPOINT_026.md`.

- The user ACTUALLY ran checkpoint 025 (`d4bd629003812578580e7a380e791d87fdf64614441394f1261df3951b9815dc`) and showed a real in-game screenshot. **G2 renders but font is UNREADABLE due to fragmented/narrow strokes, excessive inter-glyph gaps and disordered-looking accents. CHECKPOINT 025 IS RUNTIME VISUAL FAIL — DO NOT RELEASE.**
- Exact user screenshot SHA256 `5fe322fe15746017ee1362daf9ffe0a275344f91b256bdd30732d033ceb62ee0` (user conversation attachment, do NOT commit to GitHub). Row black-ink widths 599/672/638 px; approximate native advance 13.73/14.37/14.62 px, **much closer to original 13px than intended 9px**. Source-bank/WRAM offset gating likely falls back at runtime, but requires actual debugger to prove DBR/`$1F94` values.
- All 18,696 025 synthetic microtests still describe offline code behavior, NOT runtime compatibility. Static PASS must never override user screenshot FAIL.
- Quarantined `tools/build_g2_probe008_line_scoped_9px_diagnostic.py`; it now REJECTS build by default unless explicitly invoked with `--reproduce-known-runtime-fail-025`. Structural verifier marks RUNTIME VISUAL FAIL as well.
- Added fail-closed actual-image regression script `tools/audit_g2_probe008_runtime_screenshot_025.py` and checkpoint 026. Original screenshot stays private; code/reports only in GitHub.
- **No new ROM offered.** Need live parser/renderer debugger trace at `$85:8340`, `$85:8E0C`, `$85:90EE` and font redesign/readability QA before any subsequent user build. Keep a copy of original clean ROM.
- Previously current checkpoints 023/024/025 are history / failed diagnostic. Continue from exact Probe008 V2 font-only baseline for further experiments, NOT from released 025.


## ACTIVE CHECKPOINT 025 — 2026-10-10: corrected G2 9px renderer bank handling

**READ FIRST:** `docs/G2_PROBE008_STACK_BANK_SAFE_CHECKPOINT_025.md`. Supersedes the status of checkpoint 024: the 024 line-scoped 9px microhook is **not correct** because the renderer changes DBR from text source to `$7F` between its two lookups.

- Original renderer at file `0x28E7B`: `PHB; PHX; PHY; PHA`. At `0x28E95`: `PEA $7F00; PLB; PLB`. The byte lookup at `0x290EE` thus cannot test live source DBR.
- New corrected byte hook dynamically reads the bank saved on CPU stack, using `$07,S` if X=8-bit, `$09,S` if X=16-bit (based on saved P's X flag). Word hook at `0x28E0C` checks original live DBR before the bank switch. Both include the same three G2 source ranges, preserving original 13px outside G2 and 9px for all glyphs/quotes inside.
- **New build**: SHA256 `d4bd629003812578580e7a380e791d87fdf64614441394f1261df3951b9815dc`; 191 changed bytes vs V2 font-only, checksum/complement `0xED96/0x1269`; 57-byte word and 67-byte byte hook. **18,696** static 65816 subset tests PASS, independent verifier PASS, 5/5 deliberate corruption checks rejected.
- All 3 original G2 payloads remain byte-identical and 13px native tables unchanged. No runtime/emulator test; do not distribute as final.
- GitHub script updates: `tools/build_g2_probe008_line_scoped_9px_diagnostic.py` and `tools/verify_g2_probe008_line_scoped_9px_diagnostic.py`, and docs checkpoint 025. No commercial ROM committed.
- **Still must validate live DBR/`$1F94` source bank/pointer, actual new font page, wrap, typography, Japanese modes in emulator.** Also audit 0x85 new lead beyond the G2 source record.
- Previous checkpoints 023 (per-glyph-selective) and 024 (per-source but live-DBR check at both lookups) are **REJECTED FOR RELEASE**. Only 025 is current *static diagnostic* baseline.


## ACTIVE CHECKPOINT 024 — 2026-10-10: G2 source-scoped 9px (supersedes glyph-scoped fail)

**READ FIRST:** `docs/G2_PROBE008_LINE_SCOPED_9PX_CHECKPOINT_024.md`.

- Instead of choosing 9px by individual glyph ID (which left Japanese closing quote `8176` 64px out of place), the new diagnostic chooses **9px by original G2 ROM source bank/range**: DBR=`$83`, `$1F94` in `$81CE..$8238`, `$8247..$82B1`, or `$82C0..$832A`. This gives the entire known G2 text, including native quotes, a consistent step while leaving other Japanese content at original 13px.
- Built from **exact Probe008 V2 13px**, SHA256 `2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd`.
- New local diagnostic SHA256 `feb7215a67046128ff67113fd921b6479d956df6018a3ae4e74992d03b0c978a`; **181** changed bytes, checksum/complement `0xF4D6/0x0B29`, two **57-byte** 65816 hooks.
- **12,464** CPU-instruction-subset tests PASS. Independent ROM verifier PASS and **5/5** negative corruption controls PASS. Original Probe003 framing, 3x106 source records, `816F` at 32/68/104, D038, original 13px tables, palette and scene untouched.
- No persistent WRAM flag or added memory reservation. A local offline bitmap image shows correct closing quote x148 vs previous broken x212, but it is **NOT** an emulator screenshot.
- **CRITICAL RUNTIME BLOCKER:** live DBR and `$1F94` source pointer in G2 must be checked in emulator debugger; do not claim source-scoped 9px runs in-game merely because static emulated-subset PASS. No SNES emulator accessible during this turn.
- Code `tools/build_g2_probe008_line_scoped_9px_diagnostic.py`, `tools/verify_g2_probe008_line_scoped_9px_diagnostic.py` and docs committed; ROM excluded.
- Full 0x85 native-code safety, complete typography QA, remaining G0/title and G2/G3 graphics, and whole-game playtesting remain pending.


## Current priority checkpoint 023 — 2026-10-10

**Read `docs/G2_PROBE008_SELECTIVE_SPACING_CHECKPOINT_023.md` FIRST.** This supersedes the earlier notion that a font-glyph-only 9px gate would fully solve spacing.

- Exact Probe008 V2 13px font-only: static build/bitmap/map PASS, SHA-256 `2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd`; 212 mappings and 210 physical glyphs.
- New independent LoROM mapping reachability test: **212/212 mappings resolve through the actual 2-byte parser, lead pointer table and expanded 11th font page to expected raw 12x12 bitmaps**, including **84 page-$A4:D000 lookups**. This is STATIC evidence, not gameplay.
- New *diagnostic-only* 9px glyph-gated renderer hook built locally (SHA256 `dffdec30af4c3ef4d02c58414a25fa8312dcffdd168691ed4add755de1582328`, 157 changed bytes, checksum `0xF9AF/0x0650`). It leaves original native 13px lookup tables untouched and passes 4,028 VI + 190 native microhook cases; independent byte verifier PASS. Tools and documentation on GitHub, ROM local only.
- **BLOCKER:** glyph-gated 9px is not line-aware. The original closing quote `0x8176` remains native glyph `0x015A`, so the G2 line `Rèn gu mỹ thuật!` followed by that quote has **64px excess spacing** in offline renderer math. Do NOT ship the selective diagnostic. The global 9px variant also must NOT be released while Japanese UI side effects are unknown.
- Existing Japanese `0x85` usage still **UNPROVEN SAFE** (32 raw candidate pairs in broad bank range are not proof of rendered use).
- No SNES emulator/runtime font validation in this session; no new Runtime PASS. Need line- or scene-aware pitch selection including native quotes, in-game font review, and remaining G0/G2/G3 graphics and text work after font stabilizes.
- Scripts: `tools/build_g2_probe008_selective_9px_diagnostic.py`, `tools/verify_g2_probe008_selective_9px_diagnostic.py`, `tools/verify_g2_probe008_codepage_pointer_chain.py`.
- No ROM was committed.


## Active checkpoint 022 — 2026-10-10 (supersedes earlier Probe008 NOT BUILT status)

**Read `docs/G2_PROBE008_LOCAL_STATIC_BUILDS_CHECKPOINT_022.md` FIRST.**

- Clean ROM and Probe003 SHA-1/SHA-256 **exact reconstruction PASS**.
- **Probe008 V2 font-only ROM has now been BUILT LOCALLY**, with exact SHA-256 `2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd`. It is 2 MiB, 4,034 changed bytes versus Probe003, header checksum `0x622E / 0x9DD1`. 212 Unicode codepoints, 210 physical bitmaps, 84 additional page0x0A cells; A crossbar and stacked-tone construction repaired.
- Font page-pointer relocation MUST patch BOTH opcode sources: `0x28EA8` and `0x28EAE` (not `0x28EAD`).
- Independent static verifier PASS: all mapped glyphs, bitmap reads, preserved framing and positions, checksum and diff surface. Four local negative-corruption fixtures rejected.
- **Actual renderer pitch 13px**; all 44,944 ordered glyph pairs have **zero bitmap-ink overlap at 9px**. V2 glyph pixels rendered from resulting ROM in offline 13-versus-9 preview.
- Separate **GLOBAL 9px diagnostic ROM built locally**, SHA-256 `7b982dbbcd683fa981b2a20da10850d61b6f34fd9f25970baa5f32dab75440f8`. Only 35 changed bytes versus V2 13px; checksum `0x60CE / 0x9F31`. Because it shifts remaining native Japanese UI, this is **not a release patch**.
- **No emulator available/tested**. No runtime PASS. Need prove new 0x85 lead/game use and 11th page in-game, refine selectively applied 9px, check aesthetics and other scenes before new ROM distribution.
- Code/JSON/SVG/checkpoints/validators pushed to GitHub; **no ROM committed**.


## Latest active checkpoint — 2026-10-10 (Probe008-021)

**Start with `docs/G2_PROBE008_COMPLETE_FONT_CHECKPOINT_021.md`**, then `docs/G2_PROBE008_RENDERER_SPACING_PROOF_020.md` and `docs/G2_PROBE008_SPACING_HANDOFF_019.md`. This supersedes prior "renderer spacing unknown" claims.

- **Measured original pitch: 13px** (both 19-entry renderer tables verified), NOT preview-assumed 12px. Local 13/12/9 sample preview and committed SVG are available. At 9px five sample rows have no literal ink collision in the offline simulation.
- Fixed accented A crossbar and centered stacked hỏi/ngã in **V2 candidate**. V2 generated data committed: **212 entries / 210 unique glyph bitmaps**, covers **49 additional uppercase + 3 lowercase** with proposed separate lead `0x8540..0x8573`. No V2 ROM/runtime PASS.
- **126 unique existing custom glyph slots** audited blank/unreferenced in clean ROM, all reserved by 128 existing codepage rows; not free for 52 extras. Candidate spare page `0x125000`, pointer relocation `0x2F800`, extended lead table `0x2FA00` all read-only byte-level preflight only; unknown indirect ownership and 0x85 native proprietary use remain blockers.
- `tools/probe008_spacing_evidence.py`, `tools/repair_g2_probe008_full_font.py`, `tools/audit_g2_probe008_font_expansion.py`, V2 candidate JSON and SVG previews are on GitHub.
- 9px is **not** a release ROM patch: a global table change would also alter remaining Japanese glyphs. Vietnamese-only conditional advance remains to design.
- Probe003 strict framing, quote bytes, line separators at 32/68/104, D038, palettes, scene logic are frozen. No commercial ROM in GitHub.
- **No emulator test in this session.** Neither Probe008 ROM nor font/runtime PASS can be claimed.


## Current task checkpoint — 2026-10-10

**Read `docs/G2_PROBE008_SPACING_HANDOFF_019.md` first.** User requests saving progress now. ROM source is available and verified; Probe 003 reconstruction matches. Probe 008 font has visual defects and fresh-slot capacity FAIL (6 candidates vs 161 unique bitmaps). User wants tighter spacing: investigate 9 px advance; no spacing patch implemented. No Probe 008 ROM or runtime PASS. Older sections below are historical where superseded.

Updated: 2026-09-19 +07  
Branch: `chibi-maruko-bootstrap-01`  
Repo: `RVTGMzz/VHSNES`


## Latest font design checkpoint — 2026-10-09

Read `docs/G2_PROBE008_CUSTOM_FONT_018.md` first for the current font task.
User rejected the first Probe 008 preview; a wider custom monoline candidate and side-by-side comparison are now available. Preview-only, 163 current-map candidate entries, no ROM built and no runtime PASS. Read-only slot preflight and ROM-free regression checks are added; local tests PASS, actual ROM preflight pending input. GitHub push blocked by automatic approval review; changes are local only until explicit publication authorization.

## Latest checkpoint — G1 Runtime PASS / G2 school-front trace

Read first:

- `docs/G1_LABEL_ASSET_PROOF_009.md`
- `docs/G2_REVERSE_CHECKPOINT_010.md`

G1 Start/Password is no longer unresolved:

- exact package: `$82:AF23`, record **#8**
- compressed source: `$97:F95E` / file `0x0BF95E`
- VRAM: `$7800`
- original packed span: `0x1B4`
- decompressed output: `0x3E0`
- Vietnamese packed size: `0x16A`
- probe: `G1_LABEL_PROBE_001_CLEAN.sfc`
- changed bytes: **360**
- SHA-1: `904435c61153fd7f41649ab25e8f50318d3ec72f`
- SHA-256: `16c2975f431edc74754b8b6ad9272b78e4cc37852df653d1581094efb5d15edb`
- checksum/complement: `0x28CA / 0xD735`
- user-confirmed visible labels **Bắt đầu / Mật khẩu**: **RUNTIME PASS**

`どれにする？` is a separate target and is not included in that replacement claim.

Current G2 target:

`今からやるよ` -> **Bắt đầu thôi!**

Current execution checkpoint:

`Start -> A1 -> $80:E131 -> $80:E169 -> $88:8139 -> $88:CB4E -> group 4 -> school-front scene`

- QA descriptor `0x286EA`: clue only, **do not patch**
- candidate `$9A:CB34`: **rejected**, decoded graphics do not match
- exact G2 overlay asset: **UNPROVEN**
- G2 graphics write: **NO**
- G2 Runtime PASS: **NO**

Continue from the school-front scene and trace the retail overlay callback/resource for `今からやるよ`.

## Current milestone

The project has finished the large **direct-text insertion sweep** for the currently discovered coherent player-facing banks and has now moved to the **graphics/tilemap/asset reverse track** for the remaining visible Japanese.

Latest large direct-text candidate:

`Chibi_Maruko_Build_035_QUIZ01_CREDITS_PASS_READY.sfc`

Do **not** commit ROMs to GitHub.

Build 035 runtime status: **UNTESTED**. Do not call whole-game Runtime PASS.

The user prefers **fewer, larger tests**. Avoid tiny sequential test builds unless a narrow diagnostic probe is technically necessary.

## Canonical clean ROM contract

- size `0x200000` / 2 MiB
- SHA-1 `08a2415362f69788ec76b1a36044dc1f1a5f2ea1`
- SHA-256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`
- internal title `RS051 CHIBIMARUKOCHAN`
- LoROM / FastROM
- header file `0x7FC0`
- no copier header
- clean checksum `0x1115`, complement `0xEEEA`

Always derive reproducible work from this exact clean-ROM contract.

## Translation meaning layer

Committed player-facing / release-intent meaning layer remains **1,018 source rows**.  
Tracker: `translation/TRANSLATION_PROGRESS.md`.

Meaning-covered banks include:

- main Story through the discovered ending sequence;
- Maruko Q / Quiz banks;
- Maruko Fortune;
- Minigame UI / rules / setup;
- Karaoke meaning layer + singable V1 draft;
- stage names;
- credits;
- quiz misc/result UI;
- main-menu meanings and seed strings.

`vi_full` is canonical meaning-first Vietnamese. Compact runtime forms are a separate layer.

Tone stays cute school/family comedy, not combat RPG.

## Renderer / font / codepage architecture

Proven visible-text architecture:

```text
2-byte game code -> 16-bit glyph ID -> 12x12 raw 1bpp bitmap
```

Key reverse facts:

- parser: file `0x283D8`, CPU `$85:83D8`
- per-lead mapping pointer table: file `0x29756`
- renderer: file `0x28E7B`, CPU `$85:8E7B`
- font page pointer table: file `0x295EE`
- 10 raw 1bpp pages at `0x128000 .. 0x12C800`, step `0x800`
- each page: 128x128 bitmap, logical 10x10 grid of 12x12 cells
- glyph ID high byte = page; low byte = cell index

Vietnamese codepage:

- dedicated lead `0x84`
- mapping base `0x29A74`
- 160 Unicode entries
- canonical runtime map: `translation/codepage/vi_codepage_v4_fe4_native.csv`

Do not restart font reverse from scratch.

### Golden Sun donor status

The Golden Sun GBA donor-font experiment was rejected by the user for Chibi.  
Do **not** reuse it unless explicitly reopened.

### Font runtime feedback and current repair state

The user screenshots after Build 033 showed:

- `T` too thick;
- `V` still thin;
- uppercase `A/K/L` thin;
- lowercase `e` thin and floating;
- lowercase `g` unclear / clipped;
- circumflex looked reversed / breve-like;
- dot-below marks disappeared in runtime.

Build 034 applied targeted static repairs:

- medium `T`;
- thicker `V`;
- thicker `A/K/L`;
- lower/thicker `e` family;
- redrawn `g`;
- corrected circumflex orientation;
- dot-below moved upward to survive bottom-row clipping.

These repairs are inherited by Build 035, but **font release PASS is still unconfirmed**.

See: `docs/RUNTIME_BUILD_035_CHECKPOINT.md`.

## Runtime insertion history

### Build 024

Compact Vietnamese main-menu direct fields:

- `Truyện`
- `Đấu`
- `Đấu đội`
- `M.Q`
- `Tập vẽ`
- `Bói`
- `Hát`
- `Âm`
- `ST`
- `Mono`

### Build 027

Large Story checkpoint:

- Story Batch01: 123 runtime fields
- Story Batch02: 121
- Story Batch03: 84
- cumulative Story direct runtime fields: **328**

See `docs/RUNTIME_STORY_BUILD_027.md`.

### Build 028+

Subsequent candidates expanded the direct-text runtime layer with:

- Minigame UI / setup / rules;
- stage labels;
- quiz misc/result UI;
- story wording hotfixes;
- Fortune insertion;
- Karaoke direct-text candidates;
- large Maruko Q / Quiz insertion;
- direct credits-role labels;
- targeted font corrections.

### Build 035 — latest direct-text checkpoint

Artifact:

`Chibi_Maruko_Build_035_QUIZ01_CREDITS_PASS_READY.sfc`

Static facts:

- base: Build 034
- new Quiz/direct entries: **65**
- new Credits role-token patches: **22**
- changed bytes vs Build034: **3129**
- checksum `0x6547`
- complement `0x9AB8`
- SHA-1 `054380f9b452f245471e6309eb33c7486d581462`
- SHA-256 `f8fb662a9e1b8fc5a5ff689f690ceaf332055ed86983e52b476a78852e4fd58d`
- runtime status: **UNTESTED**

See `docs/RUNTIME_BUILD_035_CHECKPOINT.md`.

## Latest translation/editorial work

Meaning-first player-facing coverage remains **1,018 source rows**. No scanner noise was promoted as new translation.

Latest editorial additions:

- Story Batch 02 tone consistency pass 05: **32** rows;
- Maruko Fortune naturalness pass 01: **24** rows;
- Maruko Q naturalness pass 02: **36** rows;
- cumulative explicit editorial row revisions: **192**.

Files:

- `translation/editorial/tone_consistency_pass05_story_mid.csv`
- `translation/editorial/fortune_naturalness_pass01.csv`
- `translation/editorial/quiz_naturalness_pass02.csv`

These refine existing `vi_full` meanings and do not change the Build 035 runtime claim.

## UI / game-choice localization pass

Added:

- `translation/editorial/ui_menu_naturalness_pass01.csv`: **31** UI/menu/stage revisions;
- `translation/runtime/ui_choices_compact_v1.csv`: fixed-field compact candidates.

Frozen UI direction now includes:

- difficulty: **Dễ / Vừa / Khó**;
- slot states: **Chơi / CPU / Nghỉ**;
- stage selector: **Màn**;
- start instruction: **Bấm START**;
- quiz continue: **Tiếp tục câu đố?**, compact **Tiếp tục?**;
- yes/no remains **Có / Không** in the natural layer.

Important quality rule: do not degrade Vietnamese into `Ko`, `No`, or `Off` merely because a fixed field is too short. Mark those fields for relocation/expansion instead.

Cumulative explicit editorial row revisions are now **223**.

## Unified game-flow UI glossary

Added:

- `translation/editorial/ui_choice_flow_pass02.csv`
- `translation/runtime/graphics_ui_labels_v1.csv`

Frozen recurring game-flow labels:

- Start: **Bắt đầu**
- Password: **Mật khẩu**
- Continue: **Tiếp tục**
- Quit Story: **Thoát**
- Yes / No: **Có / Không**
- Difficulty: **Dễ / Vừa / Khó**
- Player slot: **Chơi / CPU / Nghỉ**
- Results: **Thắng / Thua**
- Ending: **Kết thúc**

`やめる` is no longer ambiguous: internal QA text explicitly identifies it as the Story Mode quit screen, so **Thoát** is the canonical Vietnamese target.

Do not promote descriptor-only graphics to Runtime PASS without verifying the actual retail asset/screen.

## Auxiliary UI localization pass

Added:

- `translation/editorial/ui_auxiliary_pass03.csv`: **24** additional UI revisions;
- `translation/runtime/ui_auxiliary_compact_v2.csv`: compact runtime candidates;
- `translation/UI_GLOSSARY_VI.md`: canonical Vietnamese UI glossary.

The glossary now freezes wording across:

- main menu;
- Start / Password / Continue / Quit;
- Yes / No;
- difficulty and match setup;
- player/controller states;
- minigame controls;
- quiz results;
- karaoke start options;
- win/lose/ending;
- title/intro localization.

Cumulative explicit editorial row revisions are now **247**.

Do not re-invent UI wording in later build scripts; derive from the glossary unless new runtime evidence changes context.

## UI localization coverage audit

Added `docs/UI_LOCALIZATION_COVERAGE_001.md`.

Current UI-language conclusion:

- proven direct-text menu/setup/control/quiz/karaoke UI has Vietnamese wording coverage;
- graphics G0–G3 wording is frozen;
- remaining UI bottleneck is now asset recovery / layout, not untranslated wording;
- fields marked `runtime_needs_expansion` should be expanded instead of degraded into poor abbreviations;
- internal QA descriptors remain excluded from retail UI.

## G2/G3 + master graphics reverse pipeline

Added:

- `tools/scan_graphics_shape_targets.py`
- `tools/run_g2_g3_graphics_reverse_pipeline.py`
- `tools/selftest_g2_g3_reverse_tools.py`
- `tools/run_all_graphics_reverse.py`
- `docs/G2_G3_GRAPHICS_REVERSE_PIPELINE_005.md`

G2 targets:

- **Bắt đầu thôi!**
- **Luật chơi**
- **Thắng 2**
- **Đến khi thắng**

G3 targets:

- **Thắng**
- **Thua**
- **Tiếp tục**
- **Thoát**
- **Chiến thắng cuối cùng!**
- **Kết thúc**

The shared target-shape scanner keeps G2 and G3 independent and reuses the proven 12x12 glyph-shape engine. Weak/no shape evidence does not prove absence because screen graphics may be stylized.

Master runner:

```bash
python tools/run_all_graphics_reverse.py clean.sfc
```

It executes the G0, G1 and G2/G3 pipelines and writes one `graphics_master_summary.json`.

The static workflow now includes G0, G1 and G2/G3 ROM-free self-tests, but no GitHub workflow run/status has been observed yet. **CI PASS is not claimed.**

## Graphics Build 036 guarded pipeline

Added:

- `tools/apply_graphics_patch_manifest.py`
- `tools/verify_graphics_patch_build.py`
- `tools/make_graphics_patch_entry.py`
- `tools/plan_graphics_asset_fit.py`
- `tools/rasterize_vi_text_to_snes_tiles.py`
- `tools/prepare_graphics_patch_bundle.py`
- `tools/encode_indexed_pnm_to_snes_tiles.py`
- `tools/prepare_custom_graphics_patch_bundle.py`
- `tools/assemble_graphics_manifest.py`
- `tools/build_036_graphics.py`
- `translation/runtime/graphics_patch_manifest_B036.template.json`
- `docs/GRAPHICS_BUILD_036_PIPELINE_006.md`

Build 036 base contract is frozen to exact Build 035:

- SHA-1 `054380f9b452f245471e6309eb33c7486d581462`
- SHA-256 `f8fb662a9e1b8fc5a5ff689f690ceaf332055ed86983e52b476a78852e4fd58d`

G1-G3 replacement path:

`Build 035 Vietnamese 12x12 glyphs -> SNES 2bpp/4bpp tiles -> fit gate -> patch fragment`

G0 custom-title path:

`indexed P1/P2 pixel art -> SNES 2bpp/4bpp tiles -> fit gate -> patch fragment`

Manifest assembly rejects duplicate IDs, overlaps and replacement hash mismatches.

Builder permits changes only inside declared graphics spans + SNES checksum bytes.

Independent verifier checks replacement spans, whole-ROM diff surface and checksum.

Final Build 036 wrapper requires `ready=true` manifest and still reports runtime as **UNTESTED**.

Static workflow now includes reverse, patcher, rasterizer, fit planner, assembler and custom graphics encoder selftests. GitHub workflow execution is still **NOT OBSERVED**, therefore CI PASS is not claimed.

## Vietnamese SNES reference-ROM findings

Read:

- `docs/REFERENCE_VI_ROM_TECHNIQUES_001.md`

Three user-provided Vietnamese SNES ROMs were analyzed as technical references only:

- Rockman X2 Vietnamese
- Rockman X3 Vietnamese
- Stoneboat Clock Tower VN / AowVN

High-value findings:

1. Rockman X2/X3 both begin with `JML $66:8000` into expanded ROM at file `0x330000`, then later `JML $00:8006` back to the original engine.
2. Their expanded code includes an explicit DMA helper writing A1T/A1B/DAS and uploading to VRAM through BBAD `$18`, plus a sister CGRAM path.
3. `0x310000..0x32FFFF` is byte-identical between X2 and X3, strongly indicating a reusable localization/bootstrap payload.
4. Clock Tower visually decodes as raw 4bpp graphics around `0x330000` for title artwork and around `0x340000` for Vietnamese text with diacritics.

Implications for Chibi:

- in-place bounded G0-G3 replacement remains preferred;
- if a replacement does not fit, expanded-ROM relocation + explicit DMA is a proven practical SNES strategy;
- if editing the original G0 title proves too fragile, an optional pre-title localization splash is now a justified fallback;
- G1-G3 pre-rendered Vietnamese graphics remain a strong strategy.

Do not copy reference ROM bytes/assets/addresses. Reuse only the architectural ideas.

## G1 Story entry execution proof 008

Read:

- `docs/G1_STORY_ENTRY_SCREEN_PROOF_008.md`

Current proven retail route:

`main menu Story index 0 -> route $A0 -> $70=$A0 -> $80:D328 -> $88:F5F1 -> $85:E959`

The G1 module loads:

- `$82:AF23` — stage/background package
- `$82:AA30` — OBJ tile package at VRAM `0x6000`
- `$82:AA50` — OBJ tile package at VRAM `0x7000`
- `$82:B364` — standalone type-FF metasprite/layout script using source `$A3:9AB3`

The module state table is:

- `$85:E97F`
- `$85:EA09`
- `$85:EAB8`
- `$85:EB84`
- `$85:EB8C`

Input state `$85:EAB8` toggles `$1404` between 0/1. Result state returns `$1406=$1404+1`, proving result 1 = first choice and result 2 = second choice.

Offline reconstruction of `$82:AF23` reproduces the Story entry stage-curtain background.

Therefore:

- G1 screen execution path: **STATIC PASS**
- G1 stage/background identity: **STATIC PASS**
- G1 two-choice logic: **STATIC PASS**
- visible G1 label source: **UNPROVEN**
- graphics ROM write: **NO**
- Runtime PASS: **NO**

Important correction: `$82:B364` terminates at its own trailing `0x80`. Neighboring `$82:B36B..$82:B38E` entries and `$82:B395` are separate scripts, not an inline continuation. The G1 initializer explicitly loads only `$82:B364` in this cluster unless later execution evidence proves otherwise.

Added reproducible tool:

`tools/trace_g1_story_entry_flow.py`

## Direct-text audit after Build 035

Whole-ROM audit found only 13 unchanged kana-rich candidates.

They are not established normal player-facing direct text:

- internal review/debug descriptors around `0x2865E..0x287FC`;
- likely effect/debug-like data;
- binary false positives.

Therefore the still-visible Japanese reported in screenshots should now be treated as **graphics/tilemap/compressed-asset/alternate-renderer work**, not another broad direct-text sweep.

## Graphics / tilemap track — CURRENT PRIORITY

See `docs/GRAPHICS_TILEMAP_PASS_001_AUDIT.md`.

A descriptor/debug block names the same screens but is **not the retail visible asset**:

- `0x286B4`: Start / Password screen descriptor
- `0x286EA`: `今からやるよ` demo descriptor
- `0x28714`: VS demo descriptor
- `0x28732`: win-demo descriptor
- `0x2875E`: lose-demo descriptor
- `0x2878A`: Continue-screen descriptor
- `0x287AC`: quit-story descriptor
- `0x287E0`: final-victory descriptor
- `0x287FC`: ending descriptor

Do **not** patch these descriptors and claim the visible Japanese graphic is fixed.

### Graphics Batch G0 — title / intro screen

User explicitly requested the first title screen be localized too.

Visible Japanese title:

- `ちびまる子ちゃん めざせ！南のアイランド！！`

Frozen Vietnamese presentation:

- **Chibi Maruko-chan**
- **Tiến tới đảo phương Nam!!**
- small added credit: **Việt hóa bởi Votri Valley**

Preserve the original publisher/production copyright artwork. The Votri Valley line is an additional localization credit, not a replacement copyright.

See `docs/GRAPHICS_G0_TITLE_SCREEN_PLAN.md`.

Actual title asset path is still **UNPROVEN**; no ROM write or Runtime PASS claim yet.

### G0 boot/title trace 001

Added read-only title-path tracer:

- `tools/trace_g0_title_boot.py`
- `docs/G0_BOOT_TITLE_TRACE_001.md`

Known boot anchor:

- reset vector: `0xFF90`
- mapped file reset entry: `0x7F90`

The tracer expands boot-near control-flow candidates and prioritizes routines with BG tile/tilemap setup plus VRAM/DMA activity.

Static tests: **PASS**.

Current limitation:

- exact clean ROM / Build 035 binary unavailable in active runtime;
- no real G0 trace report yet;
- no title asset offset proven;
- no G0 ROM write;
- no Runtime PASS claim.

Proof gate:

`reset/title setup -> BG/VRAM/DMA path -> DMA source -> decoded title asset -> visible title artwork`

### Graphics asset render probe 001

Added:

- `tools/render_snes_graphics_probe.py`
- `docs/GRAPHICS_ASSET_RENDER_PROBE_001.md`

Purpose: once G0/G1 tracing proves a source graphics range, render candidate SNES 2bpp/4bpp tiles or a raw 16-bit tilemap to PNG for visual identity proof.

Static tests:

- Python compile: **PASS**
- synthetic 2bpp decode: **PASS**
- synthetic 4bpp decode: **PASS**
- tile flip handling: **PASS**
- dependency-free PNG writer: **PASS**

A recognizable render is not enough by itself; screen setup / DMA / pointer reachability still has to prove the asset path.

### G0 DMA source trace 002

Added:

- `tools/reconstruct_dma_sources.py`
- `tools/correlate_g0_dma_sources.py`
- `docs/G0_DMA_SOURCE_TRACE_002.md`

The G0 pipeline can now move from boot/title routine ranking to conservative DMA source reconstruction:

- A1T / A1B source pointer;
- DAS transfer size;
- BBAD destination;
- DMAP mode;
- LoROM file offset mapping.

The correlator then prioritizes boot-near VRAM transfers with ROM-backed, tile-aligned sources and prints candidate render commands for `render_snes_graphics_probe.py`.

Static validation: **PASS**.

Current limitation remains the missing canonical binary in the active runtime, so no real DMA source or title asset offset is claimed yet.

If top ROM-backed candidates fail visual decode, investigate compressed/WRAM staging rather than guessing offsets.

### G0 WRAM staging trace 003

Added:

- `tools/trace_wram_staging_candidates.py`
- `docs/G0_WRAM_STAGING_TRACE_003.md`

This is the fallback when a title DMA source lives in WRAM `$7E/$7F` rather than directly in ROM.

The tracer reports conservative staging/decompressor candidates via:

- exact 24-bit WRAM literals;
- long stores into the DMA source span;
- MVN/MVP block moves touching the source bank.

Static validation: **PASS**.

Do not interpret weak WRAM hits as asset proof. If needed, move to targeted disassembly/emulator tracing around the proven title DMA path.

### G0/G1 one-command reverse pipeline 004

Added:

- `tools/run_g0_title_reverse_pipeline.py`
- `tools/run_g1_graphics_reverse_pipeline.py`
- `tools/selftest_g0_reverse_tools.py`
- `tools/selftest_g1_reverse_tools.py`
- `.github/workflows/chibi-g0-reverse-tools-static.yml`
- `docs/G0_G1_ONE_COMMAND_PIPELINE_004.md`

G0 runner now performs boot trace -> boot-filtered DMA reconstruction -> correlation -> direct-ROM candidate PNG rendering -> WRAM staging trace -> JSON summary.

G1 runner now performs render-path trace -> bitmap-shape scan -> evidence correlation -> JSON summary.

`reconstruct_dma_sources.py` now supports `--sites-csv` so G0 can reconstruct only MDMAEN sites already surfaced by the boot/title trace instead of scanning every DMA trigger in the ROM.

CI note: the workflow and ROM-free selftests are committed, but GitHub returned no workflow run/status for the branch commits. **CI PASS is therefore NOT claimed.**

File Library was rechecked by keyword and recent-upload metadata; no Chibi clean ROM / Build 035 binary was found.

### Graphics Batch G1

Reverse the actual rendered asset path for:

- `どれにする？` -> **Chọn gì đây?**
- `はじめから` -> **Bắt đầu**
- `パスワード` -> **Mật khẩu**

### Graphics Batch G2

Then:

- `今からやるよ` -> **Bắt đầu thôi!**
- VS/rule-panel visible graphics:
  - `ルールをせつめいするよ` -> **Luật chơi**
  - `２本先取だよ` -> **Thắng 2**
  - `ゲームの時間は勝つまでだよ` -> **Đến khi thắng**

### Graphics Batch G3

Then:

- win graphic `勝ち` -> **Thắng**
- lose-result graphic -> **Thua**
- Continue -> **Tiếp tục**
- quit-story -> **Hủy / Thoát** after exact screen-context verification
- ending / chapter / large title cards

## Pink heading reverse

The visible pink `どれにする？` heading is not a simple contiguous direct string.

Prior searches already rejected:

- exact CP932 sequence;
- simple alternate/full-width sequence guesses;
- proven glyph-ID sequence;
- simple sparse/interleaved representations;
- simple 16-bit tilemap/index sequence searches.

Docs:

- `docs/HEADING_REVERSE_001.md`
- `docs/HEADING_REVERSE_002.md`

Do not guess offsets.

## G1 render-path trace infrastructure

Added read-only tracer:

`tools/trace_g1_render_path.py`

Checkpoint note:

`docs/G1_RENDER_PATH_TRACE_003.md`

The tracer is designed to connect the G1 screens to an actual render source by reporting:

- xrefs to descriptor/menu anchors;
- direct calls to the proven parser/renderer;
- bank `$85` VRAM/PPU/DMA register stores;
- nearby control-flow targets;
- candidate 16-bit and 24-bit pointer tables.

Important current status:

- tool syntax check: **PASS**;
- clean-ROM execution in the current session: **NOT RUN** because the commercial ROM/build binary was not available in the active runtime;
- proven G1 asset offset: **NO**;
- G1 ROM write: **NO**;
- G1 Runtime PASS: **NO**.

Do not convert this infrastructure checkpoint into an asset-path claim. The next proof must connect screen setup -> renderer/DMA/pointer -> source asset before any graphics write.

## G1 Shape Probe 004

Added read-only bitmap-shape reverse layer:

- `tools/scan_g1_shape_fingerprints.py`
- `tools/correlate_g1_evidence.py`
- `docs/G1_SHAPE_PROBE_004.md`

Probe 004 uses the already-proven Chibi 12x12 font bitmaps as visual fingerprints for all three G1 targets, then scans raw 1bpp and SNES 2bpp/4bpp hypotheses. Candidate clusters are cross-ranked against pointer/DMA/xref evidence from `trace_g1_render_path.py`.

Static status:

- shape scanner Python compile: **PASS**
- synthetic 1bpp / 2bpp / 4bpp fixtures: **PASS**
- cluster / target-coverage fixtures: **PASS**
- evidence correlator compile: **PASS**
- synthetic pointer-in-cluster ranking: **PASS**
- strong-candidate gate fixture: **PASS**

Current limitation remains unchanged: the canonical clean ROM / Build 035 binary was not available in the active runtime, so no clean-ROM Probe 004 report has been produced and **no G1 asset offset is proven yet**.

Proof gate before any Build 036 write:

`screen setup -> pointer/DMA/render path -> decoded source asset -> visible G1 text`

Do not patch a visually plausible cluster without that chain.

## Next high-value work

1. Stay on the graphics/tilemap track.
2. Reverse the **actual rendered asset path** for Graphics Batch G1.
3. Determine whether the asset is:
   - raw 2bpp / 4bpp graphics;
   - a tilemap using reusable character tiles;
   - compressed graphics;
   - or another renderer.
4. Keep graphics edits as a separately auditable layer on top of Build 035.
5. Prefer one high-information graphics probe or one larger coherent batch.
6. Do not reopen broad direct-text scanning unless new runtime evidence proves a genuine untranslated direct-text bank.
7. Do not call Runtime PASS without user screenshot/gameplay evidence.

## Frozen workflow

Use Gaia Master-style guardrails, not Gaia Master hardware assumptions.

Preserve:

- exact clean-ROM identity;
- source identity before writes;
- control bytes;
- fixed-field byte-fit where applicable;
- overlap rejection;
- diff-surface validation;
- checksum/complement validation;
- separate source meaning, runtime compact text, font/codepage, and graphics/tilemap layers.

No ROMs in GitHub.

### G2 targeted tracer / CI

Added:

- `tools/trace_g2_start_flow.py`
- `tools/selftest_g2_start_flow.py`

Workflow run **#39** at commit `6c7026cf4b857c24e2efbeebac544cc71e055850` is **CI PASS**, including the dedicated G2 targeted selftest.

This is a tooling/static CI claim only. Exact G2 asset identity and G2 Runtime PASS remain **NO** until the tracer is run against the canonical clean ROM and the resulting source is decoded/verified.

### G2 school-front resource collector checkpoint 011

Read:

`docs/G2_SCHOOL_FRONT_RESOURCE_COLLECTOR_011.md`

Added:

- `tools/trace_g2_school_front_resources.py`
- `tools/selftest_g2_school_front_resources.py`

The collector starts at `$88:8139` and `$88:CB4E`, walks a bounded local call neighborhood, finds exact `LDX #script ; JSL $80:E255` resource calls, parses referenced type-0/type-FF resources, and exports 2bpp/4bpp previews for tile-aligned type-0 records.

CI run #42 on commit `3755af52f3ea7e5499afa6914143be379c3f7274` passed every substantive test step observed, including the dedicated school-front collector selftest.

The clean ROM was not recoverable from File Library in this session, so no real G2 resource list or asset identity is claimed yet.

### G2 D038 disable probe 012

Read:

`docs/G2_D038_DISABLE_PROBE_012.md`

Canonical clean ROM was re-uploaded and revalidated.

New static proof:

- `$88:CB4E` group 4 first list -> `$82:AB4E`, `$82:AE66`
- `$82:AB4E` offline render reproduces the retail school-front scene: **STATIC PASS**
- group 4 second list -> `$88:CE80`, `$88:D038`
- `$88:D038` is shared by many groups
- `$82:AAB0` is too small to contain the full six-character target and is rejected as the complete overlay asset

Added reproducible probe builder:

`tools/build_g2_d038_disable_probe.py`

Probe 001 changes group-4 second-list from:

`CE80 -> D038 -> end`

to:

`CE80 -> end`

Local artifact:

`Chibi_Maruko_G2_D038_DISABLE_PROBE_001.sfc`

SHA-1 `da3cf951acd8d772df1b60a54fc0c81eb412f755`

Runtime retest required. Do not call D038 the final dialogue path until the probe result is known.

### G2 conversation demo direct-text correction 013

Read:

`docs/G2_CONVERSATION_DEMO_DIRECT_TEXT_013.md`

Runtime feedback from Probe 001 showed palette/background instability after removing D038. Because Probe 001 was built from the clean ROM, Japanese dialogue in that build was expected and is not a regression.

Critical model correction:

- internal descriptor `0x286EA` says `『今からやるよ』の会話デモです。`
- `今からやるよ` is an internal semantic label for the conversation demo, not established visible player-facing graphics
- the actual screenshot dialogue is normal direct CP932 text

New player-facing direct-text records:

- `0x181CE` — reflex-training variant
- `0x18247` — do-not-fall-from-island variant
- `0x182C0` — art-sense variant

All are exact **106-byte** payloads with the original 32/34/34 line layout.

Added:

- `translation/source/g2_conversation_demo_vi.csv`
- `translation/runtime/g2_conversation_demo_compact_v1.csv`
- `tools/build_g2_conversation_direct_probe.py`
- `tools/selftest_g2_conversation_direct_probe.py`

Release-intent meaning count is now **1,021** rows.

Local Probe 002:

`Chibi_Maruko_G2_DIRECT_TEXT_PROBE_002.sfc`

- D038: **ORIGINAL**
- total diff: **642 bytes**
- SHA-1: `60968e7dfb6f38158003cc57723569d88f66a849`
- SHA-256: `4c526be4554cbec58153e11c11afc95f42aa132466a7b631a20155fea807df9b`
- checksum/complement: `0x4C21 / 0xB3DE`
- runtime: **RETEST REQUIRED**

Do not resume graphics hunting for literal `今からやるよ` unless exact visible runtime evidence later proves those characters appear.

### G2 Probe 002 Runtime FAIL / Probe 003 strict 2-byte

Read:

`docs/G2_DIRECT_TEXT_PROBE_003_014.md`

User runtime result for Probe 002:

**black screen when entering the target dialogue screen**

Therefore Probe 002 is **RUNTIME FAIL** and its mixed-width payload must not be reused.

Root-cause correction:

- Build 027 Story insertion uses the proven `0x84xx` 2-byte Vietnamese codepage inside fixed fields.
- Probe 002 incorrectly mixed `0x84xx` glyphs with raw 1-byte spaces `0x20` and SJIS `0x8149` exclamation.
- Probe 003 encodes letters, spaces, punctuation and padding as 2-byte `0x84xx` units.
- original `8175/8176` quotes and `816F` separators are preserved.
- separator offsets remain exactly 32 / 68 / 104.
- D038 remains original.

Probe 003 artifact:

`Chibi_Maruko_G2_DIRECT_TEXT_PROBE_003.sfc`

Static identity:

- SHA-1 `d0f7969aea3cad0a167dca3889ee9960be6415e0`
- SHA-256 `5208bec10147f478cc17955c4f262a5cde08e5b85708caa2717370f6835fbacd`
- checksum/complement `0x4FE8 / 0xB017`
- total diff bytes vs clean: **621**
- Runtime: **RETEST REQUIRED**

If Probe 003 still black-screens, stop iterating field encoding and reconstruct/test from the exact Build 023/024/027 baseline instead of clean ROM.

### Probe 003 text-path pass / Probe 004 medium font

Read:

`docs/G2_PROBE_004_MEDIUM_FONT_015.md`

User screenshot for Probe 003 proves the target scene loads and Vietnamese text renders. Therefore strict 2-byte direct-text framing is now a **RUNTIME PATH PASS**.

However the text is visually very difficult to read. Probe 003 typography is **FAIL**.

Cause: Probe 003 installed the old `vi_glyphs_v5_fe4_thin` experiment, which the user had already rejected as too thin/inconsistent.

Probe 004 is built directly on Probe 003 and changes only 27 custom glyph cells by adding one pixel to the right of each lit pixel. Text payload, D038, separators and scene logic are unchanged.

Artifact:

`Chibi_Maruko_G2_DIRECT_TEXT_PROBE_004_MEDIUM_FONT.sfc`

- base: Probe 003
- font diff bytes: 215
- total diff vs Probe 003: 219
- SHA-1: `850b3e794dbcb4e8d46d7738efc078d944b5e1f0`
- SHA-256: `00e9be78b0532f34d13bb8f352de16bbc453637d38184b9400e83bf3e36153b5`
- checksum/complement: `0x69BF / 0x9640`
- typography: **RETEST REQUIRED**

Do not call Probe 003 or Probe 004 a whole G2 Runtime PASS.

### Probe 004 typography fail / Probe 005 clean dialogue font

Read:

`docs/G2_PROBE_005_CLEAN_DIALOGUE_FONT_016.md`

User screenshot confirms Probe 004 is visually unacceptable: thickening merges strokes into blocky letterforms.

Therefore Probe 004 typography is **RUNTIME FAIL** and the dilation approach is abandoned.

Probe 005 keeps the proven Probe-003 text path unchanged and replaces only the 32 glyphs required by the three recovered conversation variants with a new clean 12x12 1bpp dialogue face.

To avoid mixed font styles, Probe 005 also temporarily remaps `! / L / y / R / T` to clean blank custom slots.

Artifact:

`Chibi_Maruko_G2_DIRECT_TEXT_PROBE_005_CLEAN_DIALOGUE_FONT.sfc`

Static identity:

- base: Probe 003
- glyphs: 32
- font diff bytes: 471
- mapping diff bytes: 10
- total diff vs Probe 003: 485
- SHA-1: `36c2aff02d471e6d49bab48c783c1179eb0e91f4`
- SHA-256: `c98934c7233f032a2dd6b369f8b7858042aed606bb1dfe69301be55d3b9b1940`
- checksum/complement: `0x68E4 / 0x971B`
- text payload: unchanged from Probe 003
- D038 / scene / palette logic: unchanged
- typography: **RETEST REQUIRED**

Do not return to Probe 004 thickening.

### Full Vietnamese font harmonization checkpoint 017

Read:

`docs/G2_FULL_VI_FONT_HARMONIZATION_017.md`

Latest runtime/font conclusions:

- Probe 003: strict 2-byte direct-text path **RUNTIME PATH PASS**
- Probe 004: **TYPOGRAPHY FAIL**
- Probe 005: superseded by request for a thinner overall face
- Probe 006: **current best runtime direction**; user says it is broadly okay, but `ơ` is unclear
- Probe 007: isolated `ơ/ớ` repair **REJECTED IN PREVIEW**; do not test/promote it

Current local Probe 006 identity:

- SHA-1 `1e658ec71360a1d5a8cd0437b39cea0251b41682`
- SHA-256 `0ad309c4cfede4791cd5891714e487d2c1e933965f3e5b4064be3ee66c2b1efd`

The next task is **not another one-glyph patch**.

Build a coherent full Vietnamese thin-clean font pass covering:

- `a/ă/â` families
- `e/ê`
- `i`
- `o/ô/ơ`
- `u/ư`
- `y`
- `d/đ` plus uppercase `D/Đ`

Highest-priority defects are the Vietnamese **hỏi** and **ngã** marks across all families. The user specifically flagged those two accent systems as broadly wrong.

Planned next probe:

**Probe 008 — Full Vietnamese Harmonized Thin-Clean Set**

Preview the full atlas and actual runtime sample lines before producing another ROM.

Keep Probe 003's text/control path frozen. Do not alter D038, scene, palette or controller logic.
