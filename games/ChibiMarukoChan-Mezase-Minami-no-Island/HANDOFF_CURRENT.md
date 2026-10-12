# HANDOFF CURRENT — Chibi Maruko-chan SNES Việt hóa

## CHECKPOINT 076 — 2026-10-12: REAL INDEPENDENT 81-SOURCE IPS SHA MATCH + FIX 071/075 QA + ONE ARCHIVE → ONE FULL TEST IPS

**Read `docs/CHECKPOINT_076_ONE_ARCHIVE_TO_FULL_QUIZ_CANDIDATE.md` first.** User's exact ORIGINAL Japanese 2,097,152B SFC SHA `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956` was **actually mounted and programmatically read in this session**. An **independently authored local Python builder**, not the existing GitHub 075 script, took all 81 complete canonical Vietnamese answer strings and original offsets retrieved from GitHub, used original three × 50 pointer arrays to resolve one-to-one sources, encoded full V2 Unicode + four original Nagasawa name Kanji CP932 glyph occurrences, placed 81 padded 66B native text records into 81 unique bank06 68B cells `0x36A00–0x37F84` (end-exclusive), repointed 81 corresponding original 16-bit addresses, recomputed SNES checksum and generated IPS strictly *in memory* (no source ROM/IPS distributed). **INDEPENDENTLY REPRODUCED old 075 pinned exact sha fingerprints**: clean original-ROM source-only IPS **6,139B/124 records SHA `58f284de922c3e44d2616c0de73918f6a2a86ee552c19cdc4e2cc51643f5f109`**, candidate original-source ROM SHA `5b8ed66e2ed43936703b99393607c552b5e3697d59eb22e4b3cb6ee94ed23aaa`, checksum `0x1C5D`, 5,511 changed ROM bytes, largest full record 53B. NO Vietnamese V2 font in original Japanese retail ROM; source-only patch is NOT gameplay-playable. Source-render-job wait was confirmed in original 075 65816; never overclaim onscreen UI/quiz success without emulator.

**REAL NEW INTEGRATION BUG FIXED:** previous `tools/build_quiz_relocated_81_jobwait_075.py --baseline-qa-json` demanded ONLY `result_061_ROM_sha256`, but valid `tools/recover_from_any_039_to_043_archive_071.py` returns `final_061_ROM_sha256` plus nested `full_061_source_report.result_061_ROM_sha256`. So even correct 071 outputs would fail 075. Added fail-closed `validate_061_baseline_report()`: accepts exact 061 direct, 070 original043 ZIP or 071 any039–043 recovery JSON forms; verifies all present ROM SHA fingerprints agree with actual recovered bytes, all reported IPS SHA with real IPS, original Japanese clean-SFC identity, expected static/untested report status and 071 stage label; it also checks genuine V2 glyph pointer `0x9A74` at actual 061 ROM offset `0x2975E` before merging. This is needed for real integrated font patch acceptance, not just a report tweak.

**NEW SINGLE-COMMAND BUILDER** `tools/recover_merge_061_81_one_ips_076.py`: with original retail Japanese SFC and ANY user-owned original 039–043 ZIP or IPS, selects stage via SHA, rebuilds all missing stages to exact043→061 preserving G0/G1 graphics/title+V2 font, verifies 061 SHA and font, then combines ALL 81 complete Quiz long choice source relocations using guarded 075 builder. Outputs **ONE cumulative clean-ROM-derived IPS** plus full JSON QA only, without writing any intermediate copyrighted original game ROM. Command:
`python tools/recover_merge_061_81_one_ips_076.py clean_original.sfc original_any_039_to_043.zip --ips Chibi_061_plus_81_TEST_ONLY.ips --report Chibi_061_plus_81_QA.json --allow-untested`.
**NOT ACTUALLY EXECUTED WITH 039–043 BYTES** because original archived ZIP/IPS files still inaccessible: old Library entries exist as metadata but no authorized raw-file materialization. DO NOT CLAIM integrated V2+81 patch built or playable before actual file supplied and emulator verified.

New `tools/selftest_merge_076.py` tests three correct 061/070/071 report shapes and eight corrupt/swap/false-release cases, now enforced by `.github/workflows/chibi-snes-source-qa.yml` **GITHUB CI PASS at [run 38217131132](https://github.com/RVTGMzz/VHSNES/actions/runs/38217131132)**. This is source/contract CI; no ROM or emulator on GitHub runner. Repro independent local source-only stats in docs. **Official Quiz progress remains 279/381 already staged**, NOT +81 accepted. 21 other non-answer Quiz source IDs, four Fortune long cases, G3 graphics, real emulator/screen/font/answer correctness/end-to-end title and Story QA outstanding. User priority: content first, final font styling later, avoid serial unplayable IPS micro-downloads.


## CHECKPOINT 075 — 2026-10-12: IMPORTANT CORRECTION: ORIGINAL QUIZ **WAITS FOR TEXT JOB AFTER EACH CHOICE**

**READ `docs/CHECKPOINT_075_QUIZ_PER_ANSWER_RENDER_WAIT.md` FIRST.** Earlier 074 correctly found three 66-byte copied buffers starting at original WRAM `$7E8000/$7E8020/$7E8040`, only 32 bytes apart, 29/81 Vietnamese answer source records need >32 bytes and 18 first/second choice records would lose bytes if all 3 copies were done before consuming any. However the categorical 074 conclusion that these 18 will definitely render corrupted, so RAM expansion is mandatory, was **WRONG/NOT ESTABLISHED**. Actual user-owned clean original 2MiB Japanese SFC SHA `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956` machine-code inspection shows EACH individual answer routine immediately invokes its renderer and **WAITs for text-job completion**, using `JSL $858160; BCC -6` after `JSL $85804B`. Exact original code locations: answer caller1 PC `0x30740`, caller2 `0x307BA`, caller3 `0x3082B`; renderer wrapper `0x28044`; text job setup `0x28156` sets `$1F80=2` and stores Y text pointer into `$1F94`; job status poll `0x28160` returns CLC while active and SEC when inactive, so caller BCC loops until done. All exact opcode bytes, including 3 caller `90 FA` branches, verified on REAL source SFC locally.

Therefore if rendering consumes each string before next copy, **all 81 full source strings are intact at each individual text-job handoff**, despite overlapping WRAM after all three writes. A *hypothetical* deferred-snapshot after all 3 leaves 63/81 intact, but actual original caller order explicitly waits between copies, so **DO NOT assume visible corruption or automatically demand WRAM buffer relocation**. Still require actual SNES emulator tests for 23-glyph-long choice, mixed CP932 Kanji, screen width, selection highlight and answer correctness.

New `tools/audit_quiz_copy_render_order_075.py` validates copy→`$85804B`→`$858160`/BCC order, wrapper, `$1F80/$1F94` initializers, poll/SEC logic against exact clean SFC via `--original-rom`. ROM-free CI test models immediate-handoff 81/81 intact vs hypothetical post-three-copies 63/81. Earlier first CI failed because simulator used identical filler for all records, hiding overlap; fixed with unique record byte tokens and reran CI successfully. Corrected old 074 WRAM audit/test field semantics and annotated `docs/CHECKPOINT_074_REAL_WRAM_STRIDE_GUARD_AND_52_SAFE_CHOICES.md`. `.github/workflows/chibi-snes-source-qa.yml` runs all cases; check latest actual run before declaring current HEAD PASS.

New **static-only experimental full 81-choice candidate** `tools/build_quiz_relocated_81_jobwait_075.py` restores full canonical 81 answers from the initial source-byte prototype, in 81 separate bank06 68-byte source-copy slots, but now fails closed unless ORIGINAL retail 65c816 has all three confirmed render/wait opcode paths. Original Japanese 2MiB source lacks V2 font, historical 039–043 raw IPS still unavailable, and **THIS IS NOT A PLAYABLE VN PATCH; no original-ROM integrated test or emulator QA**. Earlier 052-choice <=32-byte candidate remains conservative, but no longer evidence that other 29 *must* fail visually. Previous 81 source-only checksum/hash anchors are included in 075 builder; end-to-end build from full clone not yet performed.

**Progress remains 279/381 unique Quiz source IDs staged**, 102 unstaged, 81 long original answer records have full canonical translations but are not gameplay-accepted. Still need 039–043 original user-owned patch archive for real V2 integration; corrected Japanese-native 073 diagnostic available for optional actual SNES emulator test. Four long Fortune items, G3 results/ending assets, and final title/menu/font QA outstanding. Content-first/font-polish-last; don't claim full release before actual gameplay.


## CHECKPOINT 074 — 2026-10-12: **IMPORTANT WRAM CORRECTION** + 52 EXACT FULL VIETNAMESE CHOICE SOURCE PATCHES

**Read `docs/CHECKPOINT_074_REAL_WRAM_STRIDE_GUARD_AND_52_SAFE_CHOICES.md` before continuing.** Checkpoint073's original-ROM 68-byte answer-copy cell geometry is real, but it missed a second constraint: original 65c816 routine copies 66 bytes to **WRAM $7E8000, $7E8020, $7E8040** (X=0,0x20,0x40), **32 bytes apart**, so following copies **overwrite 34 bytes of preceding buffer**. On the 81 exact full canonical answer strings (2 bytes/glyph +4 native prefix +3 terminator), **29/81 exceed 32 bytes**; among these **18 first/second-choice strings are DEFINITELY TRUNCATED/CORRUPTED after all 3 native 66-byte copies** (actual independent simulated RAM copying on original-ROM candidate), and **11 third-choice strings exceed original destination stride, visual/memory safety unproven**. The old packed81 patch of 069 and the all81 untested source-bank plan in 073 are NOT production-safe. **Stop assuming that original-ROM source length alone proves working long answers.** The old 067 and 072 diagnostic problems were also annotated previously.

**New real source-level progress:** Created guarded `tools/build_quiz_relocated_81_074.py`. It retains every original full canonical Vietnamese choice but only *writes 52 of the 81* whose native encoded records are **<=32 bytes**, reserving their existing unique 68-byte cells at original bank06 `0x36A00+index*68`, with full 66-byte source copied windows zero-padded and two untouched FF guard bytes. Leaves the other 29 candidate pointers/text untouched, never truncates proper names; all original Japanese records/control data remain byte-identical; updates only 52 real Quiz choice pointers and accepted reserved bank06 bytes, then writes SNES checksum and source-based IPS in memory. Independent original clean Japanese 2MiB SFC byte test (SHA `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`) yielded **52 source candidates patched, 29 deferred**, exactly **3,539 changed original-ROM bytes**, **3,982-byte/87-record** clean-original IPS, SHA256 `17b9d03fd42a732d6f0348816c540ca06e21175cde588fc25b0d60d62bfd6446`, candidate 2MiB ROM SHA `5f640db8539312bf3ac01f25daff80357e4ecddffb66b7d86dcbbbb722648b10`, checksum `0xB592`; independent IPS replay verified every ROM byte. Original Japanese clean ROM has NO Vietnamese V2 font, therefore this is only an isolated *source patch candidate*, NOT a playable/tested localized ROM. Script supports optional merge over cumulative 061 V2 baseline IPS+SHA-verified QA **WHEN ORIGINAL 039–043 ZIP/IPS IS AVAILABLE**, still impossible now. The full newly committed repo builder has NOT been run end-to-end in the complete full-source local checkout; independent actual original-ROM Python matched the expected algorithm/hashes.

New `tools/audit_quiz_wram_stride_074.py` fails closed if original 81 source-width audit differs from **52 safe/29 unsafe/18 guaranteed overwrite/11 third-choice visual risk**. New `tools/selftest_quiz_wram_layout_074.py` actually simulates 3 successive 66-byte copies into 32-spaced WRAM and asserts **exactly 18 full source answers overwritten, 52 intact and within 32 bytes, 11 third-choice long surviving the copies but visually unverified**. These run in `.github/workflows/chibi-snes-source-qa.yml` on push. Source CI has PASSED on commits through `a598fd56...`; check [latest source CI run](https://github.com/RVTGMzz/VHSNES/actions) for final current commit before claiming its success. NO SNES emulator has run; do NOT count 52 as fully gameplay-localized.

**Official Quiz prepared/integrated source baseline remains 279/381 unique staged entries**, 81 original answer alternatives not integrated; of the 81, 52 now have a verified source-only full-Vietnamese 32-byte-safe patch candidate, 29 still need WRAM and renderer engineering. 21 other canonical Quiz source labels/aliases remain. 039–043 historical raw IPS is still unavailable; checkpoint071 supports any exact old 039–043 ZIP/IPS when user supplies. Four long Fortune items, G3 win/lose/result assets and final font/visual QA outstanding. Next meaningful work: reverse-engineer all references to destination buffer and text rendering to devise truly safe WRAM stride enhancement for 29 long choices, plus recover historical V2 base and emulator test. User priority: content first, final font polish last, avoid distributing unplayable patchlets.


## CHECKPOINT 073 — 2026-10-12: REAL QUIZ ENGINE COPY WINDOW DISCOVERED; SAFER 81 ANSWER CAPACITY PLAN

**Read `docs/CHECKPOINT_073_QUIZ_ENGINE_66_BYTE_COPY.md` FIRST.** Important safety correction based on actual clean retail user-owned ROM SHA `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`. Native bank06 65c816 at PC `0x30762` contains exact **`A9 20 00 85 08 B9 00 00 9F 00 80 7E E8 E8 C8 C8 C6 08 10 F1 60`**. In its verified 16bit accumulator context it copies **33 16bit words =66 bytes** from answer source Y into WRAM $7E8000+X. Three actual call sites at **`0x30730`, `0x307AA`, `0x3081B`** read choice pointer tables using `BC E7 92`, `BC 7F 92`, `BC 17 92` and invoke `JSR $8762`. This is *actual code-side evidence* the game uses the discovered Quiz pointer tables, not mere byte pointer correlation. Still **NO EMULATOR DONE**.

**Two historical safety risks now established:** 067 relocated one option at `0x37FE0` just 32 bytes before bank06 end `0x38000`, so full 66B source copy crosses bank by **34B**; its IPS SHA success did NOT make it a safe emulator fixture. Old 072 relocated two options at `0x37000`/`0x37040` (64 apart), causing **2-byte overlap of their respective 66B source read windows**. It may not necessarily crash because each string terminates earlier, but **DISCARD OLD 072 ZIP as preferred diagnostic**. Docs 067/069/072 explicitly annotated as historical/provisional. Old 069 tight 2,431B packing of 81 full Vietnamese answers also may copy bytes of adjacent relocated records due to fixed-size transfer; do NOT integrate without revised layout+emulator QA.

**Corrected optional minimal engine test 073:** original Japanese `３０円`→`３０円です` at new `0x37000`, `７６才`→`７６才です` at new `0x37080`, two unmodified original strings, two 16bit pointer words, two new 17B records in FF bank06, checksum. Two **disjoint** 66B source windows, no crossing bank. Actual clean-ROM independently reproduced source-only **70-byte/4-record IPS SHA `d02a6c2aaf9f1f95d252d9c3c7947b142becd73f4bc7cb74d31e55de50c071cf`**, resulting test-ROM SHA `e52565fa299dfd35d15a6dc80cb778658be6f82ed44655bf7373e3ce1b3d8611`, checksum `0xFBEC`, 42 changed ROM bytes; IPS replay PASS, emulator NOT RUN. Corrected one-ZIP test artifact `Chibi-Quiz-Engine-Relocation-CopierSafe-PROBE073.zip` generated this conversation, replaces old 072 ZIP. Repro code `tools/build_native_quiz_relocation_probe_073.py` pins exact source, three callsites, window disjointness, hashes, and outputs only IPS and JSON when explicitly `--allow-untested`. The two pointer-table slots may NOT be first two gameplay quiz questions.

**81 full source-answer options now have strictly DISJOINT reservation plan:** new `tools/plan_quiz_bankcopy_slots_073.py` reads all original canonical CSVs, stages 041–061, 50x3 original answer atlas and V2 codepage; validates 81 pending choices (including two distinct native CP932 Kanji Nagasawa spellings), and allocates 81 original bank06 all-FF regions of **68 bytes each** beginning `0x36A00`, last end-exclusive `0x37F84`, total **5,508B** leaving **124B** until bank06 boundary. Every answer's full Unicode text record fits **<=53B** inside 66B copied window; every source-copy interval disjoint and bank-local. `--original-rom` optionally additionally verifies exact 65c816 copier bytes, callers, real pointers and FF area. No actual 81-answer ROM/IPS produced in this 073 plan. **GitHub Actions source CI new 81-slot test PASS at run 38202883789**. This is ROM-free source-budget QA and NOT emulator/visual width proof (43 answers >10 glyphs, some 23 glyphs).

**Progress unchanged:** 279/381 unique Quiz source fields prepped, 102 not staged; 81 long answers NOT integrated in real VN font ROM and NOT counted complete. User's clean retail SFC is accessible but old raw ZIP/IPS checkpoint039–043 is missing from tool-accessible paths, so checkpoint071 recover-from-any-stage script cannot yet restore cumulative 061 for gameplay. Four long Fortune items, G3 result sprites, final font/rendering QA outstanding. Next actual gate is user SNES emulator testing corrected 073 fixture or original 039–043 patch archive available. No claim of playable full localization. Content-first, font-polish-last.


## CHECKPOINT 072 — 2026-10-12: ACTUAL RETAIL-ROM QUIZ ENGINE SMOKE-TEST IPS READY; EMULATOR NOT TESTED

**Read `docs/QUIZ_NATIVE_RELOCATION_SMOKE_072.md` and `tools/build_native_quiz_relocation_probe_072.py` first.** Key change: unlike old 067 (Quiz #6) this minimal **native Japanese** relocation fixture changes the first two pointer-table slots in the recovered original bank06 50×3 question pointer data. **This does not rely on inaccessible 043 IPS, modified V2 font or any commercial ROM in GitHub.** User's exact original Japanese 2MiB SFC SHA `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956` is locally available and was actually patched *in memory* and replay-verified.

- Pointer slot 0 answer 1: original `0x31217` points to `0x320FB` `３０円`, moved complete original native record to `0x37000` with longer `３０円です`.
- Pointer slot 1 answer 1: original `0x31219` points to `0x32273` `７６才`, moved complete native record to `0x37040` with longer `７６才です`.
- Preserve BOTH old Japanese records untouched; preserve all original script except **2 two-byte pointers**, **2 x 17-byte new records inside original all-FF bank space** and SNES checksum bytes. Actual changed original ROM bytes **42**. Original 2MiB clean-ROM IPS **70 bytes /4 records**, SHA `3d29135ff3712b4d8ee74b0afb690ec852a1537b3a713ac22866a734f8cc44ea`. Exact patched full-ROM SHA `fae23a8f7744313e5977b44eaeaeaf6177bdcd7312c78b671a30851b6599e2ee`; header checksum `0xFBAC`. Independently applying IPS to exact Japanese SFC reproduced all bytes, PASS.
- A single optional diagnostic ZIP `Chibi-Quiz-Engine-Relocation-PROBE072.zip` was generated in the conversation (IPS + report + Vietnamese README). This is NOT Vietnamese and NOT any gameplay-verified release; user dislikes repeated micro-patches, so only use it if they choose to validate critical engine behavior. NO emulator exists in this runtime, so no actual screen/choice/navigation QA. **Pointer-table order may differ from gameplay order**; do not falsely assert these are necessarily first two questions shown.
- Original user's historical 039/041/042/043 archives remain Library metadata only; the 071 recover-any-stage code cannot execute positive baseline rebuild without raw ZIP/IPS. The Japanese original SFC is available, and no new user file was provided. Source CI was green at checkpoint071. New 072 Python tool currently requires exact original ROM, and source syntax CI will check it.
- Game QA next: apply 072 IPS to a *copy* of clean Japanese SFC and enter `まるこＱ`; when a 30-yen or 76-years choice appears, check visible `です` suffix, selection/highlight, transition and answer correctness. If proven, revisit checkpoint069 81 full Vietnamese choice relocations with real V2 font/043 integrated base and small on-screen display constraints. **Do not add the 81 to translated progress before emulator acceptance.** Existing 279/381 Quiz source staging, four Fortune exceptions and G3 result/ending graphics all remain.


## CHECKPOINT 071 — 2026-10-12: RECOVER FULL 061 FROM **ANY** EXACT 039, 040, 041, 042 OR 043 ZIP/IPS

**Read `docs/CHECKPOINT_071_ANY_039_TO_043_RECOVERY.md` first.** Critical production-blocker improvement: old recovery tool required ONLY the exact historical original 043 ZIP/IPS (28,135B, SHA `d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50`). The user's Library shows original 039, 041, 042 and 043 ZIP metadata; archived bytes remain unavailable to model via repeated `files.materialize` attempts. In current runtime the exact Japanese original 2MiB SFC SHA `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956` is available.

NEW `tools/recover_from_any_039_to_043_archive_071.py` accepts **one original user-owned .ips or .zip from any stage 039–043**, identifies exact matching historical stage by **SHA256 and IPS length, not basename**, reads ZIP entries in memory and rejects forged/oversized archives. For 039, it runs `build_content_first_040_fortune.build(clean,ips039,root)` then 041/042/043 in source order; for 041, it runs only 042+043; for 042, only 043; for an exact 043 it skips earlier stages. Every stage is guarded by its original recorded IPA SHA256 plus clean-ROM IPS replay, no intermediate ROM output. Finally invokes the existing `rebuild_content_first_061_full_chain.run(clean,ips043,root)` and writes cumulative **061 clean-ROM IPS + JSON QA only**, release/emulator status false. Verified original IPS SHA/bytes: 039 `97c0e41b354b0dda3ea7c0c292b5aef236586e279870962fd0d4f3398285008c` /21130; 040 `2bfdcc64973bc31ce268fa7e68a6118808c633b10d1437b7f811ac290616e580` /21727; 041 `2117bc6e165f2c86263e74a637b6961a13f79257fccd9f02152a769fe1deb962` /22100; 042 `3e3c3de245a9a0a6648b2e62eff44a72093ef1e2e9cfcb1cf013ff6c4cbb5035` /23105; 043 above.

NEW `tools/selftest_recovery_071.py` checks those hashes against source module constants, checks original source build imports and must reject same-size forged IPS, fake ZIP, missing archive. Added this no-ROM test to `.github/workflows/chibi-snes-source-qa.yml`; source CI at [run 38165060169](https://github.com/RVTGMzz/VHSNES/actions/runs/38165060169) **PASSED**, including negative ZIP/SHA test. 043 or cumulative 061 was **NOT ACTUALLY REBUILT** because raw authorized 039/041/042/043 archive bytes are still missing; selftest green is NOT emulator or full build acceptance. New docs `docs/CHECKPOINT_071_ANY_039_TO_043_RECOVERY.md`.

When user supplies ANY original archive, example:
`python tools/recover_from_any_039_to_043_archive_071.py clean.sfc Chibi_041_G0G1_92UIFortuneQuiz_Content_First_UNTESTED.zip --ips combined061.ips --report qa061.json --allow-untested`
(The ZIP is just an example of an accepted stage if SHA matches, not currently accessible.) After exact actual build, emulator-test Quiz and title/UI first before integrating the 81 experimental full-length answers.

**Accurate Quiz content staging remains 279/381**, 81 proposed full-length answer replacements from prior 069 still byte-experimental, four Fortune overlong cases and G3 results outstanding. User content-first, fonts-last, no release of game ROM or dummy patches. Do not claim integrated ROM or all translations done.


## CHECKPOINT 070 — 2026-10-12: REAL GITHUB CI PASS AFTER REPAIRING 3 BLOCKING PYTHON ERRORS

**Read `docs/CHECKPOINT_070_REAL_CI_UNBLOCKED.md` FIRST.** Very important: after dozens of historical CI red runs, actual CI failure logs exposed **THREE serious source-code errors** preventing tool execution, not ROM crashes: checkpoint042 Story build Python SyntaxError in output loop line187; checkpoint043 Story build identical SyntaxError line202; checkpoint055 G2 rules contained literal `\\n` and IndentationError around line72. All fixed and **GITHUB ACTIONS VERIFIED PASS** on commit `13f727366319615b21eb3083ef1603fb8edc734c`:
- `Chibi SNES source localization checks` run [38164080900](https://github.com/RVTGMzz/VHSNES/actions/runs/38164080900): **SUCCESS** — Python syntax + source QA.
- `Chibi graphics reverse and build static` run [38164080910](https://github.com/RVTGMzz/VHSNES/actions/runs/38164080910): **SUCCESS** — original graphics self-tests formerly entirely skipped.
Actual fix commits: `f1d487bd637ba832fee0bd2523fd17ec431f900b`, `62382c1107e4f8e619454747eaa55aacf9923de8`, `13f727366319615b21eb3083ef1603fb8edc734c`.

New `translation/runtime/quiz_answer_pointer_offsets_070.json` is a compact original-ROM-derived **50×3 choice-source-offset atlas**, no copyrighted game text/font binary. New `tools/audit_quiz_repo_no_rom_070.py` proves in **REAL green GitHub CI**: all **381 original Quiz records**, **279 nonduplicate staged**, **150 original multiple-choice source addresses**, **69/150 prepared**, **81/150 not runtime-prepared**, **79 V2-compatible full strings** and **two CP932-native Kanji exceptions**. It optionally verifies the 150 actual LoROM pointer words on user-owned clean Japanese SFC with `--original-rom`. New `.github/workflows/chibi-snes-source-qa.yml` runs this automatically on branch pushes and rejects committed ROM/IPS binaries; this addresses the user's daily automated continuation goal with true CI quality checks (still not automated gameplay).

New `tools/rebuild_from_checkpoint043_archive_070.py` accepts the exact historical user-owned original **043 ZIP directly** or exact extracted 043 IPS, checks original 28,135B IPS SHA `d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50`, and invokes the 043→061 in-memory chain (clean-ROM cumulative IPS/report only, emulator untested). **NOT yet successfully built** because still no authorized raw 043 archive bytes. In this session an explicit Library `files.materialize` for original `Chibi_043_G0G1_176Fields_Story58_Content_First_UNTESTED.zip` again returned `This Project file does not have an authorized raw-byte materialization path`; ZIP metadata is NOT actual raw bytes. The user's original Japanese 2MiB SFC remains locally verified SHA `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`.

When 043 raw ZIP is made available, from game project root:
`python tools/audit_quiz_repo_no_rom_070.py --original-rom clean.sfc`
`python tools/rebuild_from_checkpoint043_archive_070.py clean.sfc 043-original.zip --ips final061.ips --report qa061.json --allow-untested`
Then actual SNES emulator gameplay/title/font checks and minimum Japanese 067→Vietnamese 069 relocated-choice test, before claiming any of 81 experimental long answers done.

**Accurate progress still 279/381 prepared Quiz source fields, NOT a finished playable localization.** The 81 hybrid CP932/V2 batch strings in checkpoint069 are experimental, not approved. Four Fortune original too-long cases, G3 result/end UI graphics, real integrated run and full QA remain. User wants **content-first; font polish later; no repeated tiny unplayable downloads**. Do not repeat prior CI-failure claims now that runs 38164080900 and 38164080910 are green; don't confuse static CI success with game/emulator QA.


## CHECKPOINT 069 — 2026-10-12: ALL 81 FULL QUIZ CHOICES BYTE-ENCODABLE, HYBRID NATIVE CP932/V2 PROOF (EMULATOR NOT TESTED)

**Read `docs/QUIZ_MIXED_CP932_V2_81_PROOF_069.md` first.** The previous 068 source-only batch could encode 79/81 longer canonical Quiz answer strings with the existing V2 Vietnamese glyph codepage. **New 069 fixes two ambiguous original Japanese answer alternatives without truncating either**: source `0x33DDF Nagasawa Kazuo (一雄)` and `0x33DFD Nagasawa Kazuo (和雄)`. The V2 font map does not include `一`, `和`, `雄`, but the clean original Quiz ROM already contains their exact 2-byte CP932 encodings `88EA`, `9861`, `9759`, each in at least three native source occurrences. New experimental per-character encoder uses existing V2 `84xx` for all Latin/Vietnamese and **four native Japanese CP932 Kanji glyph occurrences** across those two choices. This is a byte-level mix only; native CP932 glyph availability in the future integrated VN V2 font is **NOT PROVEN**.

**Actual original user SFC exact 2MiB SHA `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956` local independent byte QA PASS:** All **81/81** pending full canonical Quiz choices (150 total in-game answer alternatives, 69 previously staged) were repacked into test-only original bank06 all-FF space `0x37000–0x3797E`, end-exclusive `0x3797F`, **2,431B used** out of 4,096B and **1,665B still unused**. All **81** corresponding original LoROM two-byte choice pointers were updated in memory; original Japanese source strings/scripts and bank boundary preserved. Standard SNES checksum `0xC3BC`. Exactly **2,517 changed ROM bytes** incl. pointers and checksum. Original clean-ROM in-memory IPS **3,145 bytes /124 records**, SHA `3777df4895046d8342d421f8da5d2ccabdfd01cec7b5f8e567759ba1d4e5c213`; in-memory resulting 2MiB image SHA `c61471d70f0025e075d6dd94366940bc8990e1cfc910cf99f421dc15ff47f184`. Independent IPS replay on real original ROM matched each byte. NO source ROM/IPS files were created for public release.

**EXPLICIT DISPLAY RISK:** All 81 relocated Vietnamese captions are longer than the actual original Japanese glyph count (excluding ASCII padding). **43 >10 glyphs**, **15 >14**, **1 >20**, largest **23 glyphs** (`Trường Tiểu học Shimizu`). This means ROM space and correct pointer bytes alone do NOT establish that the Quiz single-line choice/selection UI can display these names or grade choices correctly. **DO NOT APPROVE all-81 relocation until real native-Japanese #067 emulator screen/navigation/correctness test and then integrated Vietnamese V2 font rendering + mixed CP932 Kanji test.**

New committed `tools/plan_quiz_long_answers_069_mixed.py` replays the 81-choice hybrid source/IPS experiment with strict original SHA, codepage, literal Kanji and screen-width-count guards; `tools/verify_quiz_technical_069.py` runs earlier 061/063/064/065/066/067/068/069 original-ROM checks and emits JSON-only report. Both require a full local checkout with original ROM; local *independent* Python verified their modeled byte output metrics but the exact committed full-repo scripts have NOT yet run end-to-end there. Document above records all checks. **No gameplay/emulator testing, no production patch and no completed-string increment:** current official staged Quiz **279/381 distinct source offsets**, **102 unstaged**; 81/81 long Quiz answer candidates are **technically bytes-addressable only** and are not integrated.

**Hard blocker remains:** real checkpoint043 clean-ROM IPS raw bytes SHA `d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50` remain unavailable (historical ZIP only Library metadata). Therefore no actual 061+ VN font/content composite is rebuilt; SNES emulator absent here. Next task: obtain exact user-owned 043 IPS from historical ZIP, validate source chain and render first long-name choice, then approve a 79/81 batch; keep four Fortune long cases and G3 results on TODO. User: **CONTENT FIRST; font polish last**, do not distribute tiny unplayable patches.


## CHECKPOINT 068 — 2026-10-12: 79 FULL VIETNAMESE LONG QUIZ CHOICES BYTE-REPOINTED IN MEMORY; NOT EMULATOR-APPROVED

**READ `docs/QUIZ_LONG_ANSWERS_DRYRUN_068.md` and `tools/plan_quiz_long_answers_068.py` first.** This is new **real technical progress** on actual original user-uploaded 2MiB Japanese SFC SHA `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`, beyond the single sample of 067.

- Confirmed 81 of the 150 in-game Quiz answer alternatives remain unstaged. Of those, **79 FULL CANONICAL Vietnamese `vi_full` strings** encode using the current V2 `84xx` codepage **without shortening or adding glyphs**; 2 remain blocked due to distinctive Japanese Kanji in original Quiz choices: `0x33DDF Nagasawa Kazuo (一雄)` and `0x33DFD Nagasawa Kazuo (和雄)` (codepage lacks `一`, `和`, `雄`). Never collapse them into identical Latin answer names.
- A local original-ROM Python in-memory packing proof used all 79 FULL Vietnamese strings in original-offset order, verified 79 actual corresponding 16-bit bank06 pointer words (from the nine recovered 066 arrays), and installed longer `0E 06 0F 12` + Vietnamese V2 text + `81 6F 00` records in **unapproved original FF area `0x37000–0x37922`** (start `0x37000`, end-exclusive `0x37923`), allocating **2,339 bytes** of an experimental 4096-B end-of-bank window; **1,757 B still physically empty**. Left the original Quiz texts and earlier `0x36907–0x36FFF` `FF` data untouched. 79 pointer words changed; total **2,422 physical changed ROM bytes** including checksum. Standard LoROM checksum recomputed `0xF8B6`. **Source-only in-memory IPS 3,030 bytes / 120 records**, SHA256 `1e0552688e1b06271fa9d8597d049eb66787697c6d4412ba9178bf696bf229df`; resulting in-memory 2MiB ROM SHA `cc730fa76611155c203ac1fa9175b7a749290b1d5c05bac4a01d0dcd4d6ad087`. Independent IPS replay reproduced every ROM byte exactly.
- **NO PRODUCTION APPROVAL.** The Japanese clean original ROM does NOT include Vietnamese font V2, and emulator renderer, answer correctness/selection navigation, native interpreter jump, and original FF space production safety are NOT TESTED. The 79 long strings are NOT merged into real 061 VN build and MUST NOT be added to staged completion metrics. **Quiz remains 279/381 already prepared** (69/150 actual answers staged, 81 choice rows pending runtime acceptance). The pending long-choice preparations are a researched future approach; DO NOT distribute text-only original-ROM IPS or copyrighted ROM.
- New reproducible GitHub script `tools/plan_quiz_long_answers_068.py` consumes original real SFC, 065/066 source/pointer atlas, 381 canonical Quiz CSVs and existing V2 codepage. Re-creates 79 relocation choices/checksum/IPS in memory, pins SHA hashes and emits **JSON report only**, no ROM/IPS file. Document `docs/QUIZ_LONG_ANSWERS_DRYRUN_068.md` has the full evidence. Independent local Python validated the data and fingerprints; committed full-repo script still needs a real checkout end-to-end CI smoke-test.
- Next gate: **emulator verify minimal native-Japanese moved choice** (067), then regain exact 043 IPS raw bytes (SHA `d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50`) and rebuild real font V2+graphics VN ROM, verify long Vietnamese question/choice selection, only then integrate bulk 79. Existing 043 old ZIP Library metadata is not raw bytes and materialization previously failed. Also four Fortune overlong cases, G3 result art, eventual final font polish. USER: content-first, font-last, avoid tiny unplayable downloads and inflated completion statistics.


## CHECKPOINT 065–067 — 2026-10-12: ALL 50×3 QUIZ ANSWERS INDEXED; 9 COMPLETE POINTER ARRAYS FOUND; LONG-ANSWER REPOINT BYTE PROBE PASS

**READ `docs/QUIZ_50_QUESTION_ANSWER_ATLAS_065.md` and `docs/QUIZ_POINTER_TABLES_066_RELOCATION_PROBE_067.md` FIRST.** Huge structural breakthrough on **actual original unheadered 2MiB Japanese SFC**, SHA `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`.

- **065**: Original Quiz script region `0x31C00..0x36907` yields **50 question blocks**, exactly **three choices per question (150 actual Quiz answer fields)**. The control string `81 6F 00 0E 06 0F 12` occurs **151 times**; the very first is an unrelated startup `いいえ` (“No”), so exclude it. **150/150 original choice offsets** match canonical Quiz source CSVs; **69/150** already have original-ROM byte-staged translation records, **81/150** remain. Checkpoint065 tool `tools/build_quiz_answer_atlas_065.py` creates a read-only 50-question answer/source/translated-reference atlas and crosschecks all stages 041–061.
- **066 CRITICAL DISCOVERY**: At `0x310DF`, the original ROM contains **NINE distinct 50-word 16-bit LoROM bank06 pointer arrays**, at `0x310DF`, `0x31147`, `0x311AF`, `0x31217`, `0x3127F`, `0x312E7`, `0x3134F`, `0x313B7`, `0x3141F`. They correspond respectively to each question's footer metadata, main question, continuation, answer choices 1–3, explanation parts 1–3. All nine arrays have **the SAME permutation of 50 distinct question groups**, 50 verified pointer targets per array; **two 16-bit sentinel words after every array repeat the respective pointer to question #50**. Total **450 real references +18 sentinel words**, table extent through `0x31487`. Choice pointers land exactly **4 bytes before each original answer text**, preserving `0E 06 0F 12`. Main q1 exception `0x31D43` is pinned. Read-only `tools/audit_quiz_pointer_tables_066.py` verifies all against original ROM/065 atlas. These are truly physical pointer table locations, not speculative byte patterns.
- **067 TWO ACTUAL SOURCE-ROM IN-MEMORY REPOINTING PROOFS**: Quiz #6 answer #1 `じてんしゃ` at `0x3256B` has upstream 16-bit pointer **`0x3123D: 67 A5`** pointing to `0x32567`. Repoint just that word to **`E0 FF`**, a longer source string at original all-`FF` bank padding `0x37FE0`, while retaining original source bytes, correct native `0E 06 0F 12` prefix and `81 6F 00` terminator. Source-only Japanese `じてんしゃです` (7 glyphs) experiment: **27 changed bytes, 50B/3-record IPS**, sha `29575dfce7b27cfdad91fa1647e07f1dc8032a460fe919bcc2052d58580452a4`; ROM sha `c014ea1aae6b36b137899687ea65b19134610623ec23fa92d8ace6df4a51f221`; checksum `0x072D`. Vietnamese **`Xe đạp`** V2 `84xx` full-correct answer (6 glyphs): **25 changed bytes, 48B/3-record IPS**, sha `339f1426a87bba18fdd227f32e1eb32fe43c534cc722d42934efa1e40d565dc6`; ROM sha `017db9ebc59190c0dd131d6b175b75c8cc98e42bb05483e4decfcfb8a740b05f`; checksum `0x0637`. Both test IPS were **independently applied back to exact 2MiB Japanese source ROM and compared byte-for-byte**. Source-only, NO ROM or IPS file distributed; `tools/probe_quiz_relocation_067.py` reproduces in memory and emits report only. End-of-bank 0x37FE0 keeps original 0x36907 FF sentinel untouched.
- **VERY IMPORTANT LIMIT:** This establishes that the 16-bit bank06 pointer can be *represented and repointed in bytes*, NOT that the SNES interpreter actually renders/reaches the relocated text safely. **NO EMULATOR/QUIZ MENU/ANSWER SELECTION TEST WAS DONE, NO production relocation approved, NO V2 font was present in original Japanese source**. Do not count #6 `Xe đạp` or any of the 81 pending answers as finished. Full original 043 IPS and cumulative VN ROM still unavailable. Current Quiz count remains **279/381 original source targets staged**, **102 source rows unstaged**, 81 of them actual Quiz choice rows.
- Repo source: `tools/build_quiz_answer_atlas_065.py`, `tools/audit_quiz_pointer_tables_066.py`, `tools/probe_quiz_relocation_067.py` and both above docs. Independent local Python runs established 409 control transitions, 50 question groups and 150 option offsets; connector source cross-check confirmed 150/150 canonical matches and staged 69/pending81. Repo scripts were committed but not yet executed end-to-end inside complete local clone with all source CSVs—confirm on checkout.
- Next concrete acceptance gate: validate **one native-Japanese relocated option in an SNES emulator**, verify question #6 choice visibility, answer selection, correctness and control flow. Then repeat with real full VN V2 renderer and approve batch long-name relocation. The necessary 043 IPS SHA `d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50` remains inaccessible (Library ZIP only metadata), so can't assert final playable. Four Fortune long-slot exceptions, G3 results, and later font QA still pending. User priority: **CONTENT FIRST, FONT LAST**, no pointless micro IPS downloads or retroactive double counting.


## CHECKPOINT 064 — 2026-10-12: SCRIPT GRAMMAR READ-ONLY QA; DAILY AUTOMATED CONTINUATION ENABLED

**Read `docs/QUIZ_SCRIPT_STRUCTURE_CHECKPOINT_064.md` first.** User requested automated continuation even when active chat ends. A recurring **daily 10 AM (Vietnam local time, flexible)** ChatGPT task titled `Tiếp tục Việt hóa Chibi` has been enabled. Future execution is **separate bounded runs**, not an infinite Work chat/background process; tasks should check this handoff, read latest repository code, make a **real audited change**, commit safe source when applicable, report truthfully, and avoid repeating work. Do not auto-create duplicate reminders. As before, all old historical checkpoints are informative, not evidence of emulator acceptance.

**NEW ORIGINAL-JAPANESE ROM SCRIPT RESEARCH:** Read exact clean 2MiB source SHA `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`. In native Quiz script region `0x31C00–0x36907`, classified **409** exact native `81 6F 00` end-of-text transitions into **355 ordinary `0E ?? 0F ??`**, **4 extended introductory `10 ?? 0E ?? 0F ??`**, and **50 special 7-byte record footers** (6th `C6`, 8th `00`); **zero unclassified**. Counts reproduced independently via raw byte scan. Seven-byte footer semantics are **unknown**: do NOT assert they are pointers. The existing 5881-byte `FF` at `0x36907–0x38000` is still UNAPPROVED for relocation; original script/pointer table or CPU interpreter not decoded. Committed reproducible read-only `tools/probe_quiz_script_grammar_064.py` and `docs/QUIZ_SCRIPT_STRUCTURE_CHECKPOINT_064.md`; **NO text newly patched in 064, no ROM/IPS emitted, no emulator test**.

**Previous 063 remains:** **279/381** uniquely staged Quiz source target IDs, 546 original staged physical glyph frames (no overlaps), 102 unstaged source IDs, 82 standalone valid original text starts + nested/unsafe scanner fragments. Historical 043 clean-ROM IPS SHA `d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50` still NOT materialized; archived ZIP visible only as library metadata. Therefore **FULL INTEGRATED 061 ROM NOT BUILT/NOT TESTED**. Do not send standalone clean Japanese ROM text overlays as playable patches; do not commit copyright-bearing ROM/font binaries.

**Next concrete work:** trace record/footer/entrypoint behavior in SNES engine to safely relocate long Quiz text, or tackle canonical translation/QA without inappropriate truncation. Proper names must remain full in canonical text. Also four Fortune width cases, G3 result/menu art, and eventual complete SNES emulation test. User explicitly wants **CONTENT FIRST; FONT LAST**.


## CHECKPOINT 063 — 2026-10-12: INDEPENDENT PHYSICAL TRIAGE OF REMAINING 102 QUIZ ENTRIES

Read `docs/QUIZ_REMAINING_SOURCE_TRIAGE_063.md` **before** adding more byte patches. The previous 061 snapshot remains **279/381 uniquely staged source IDs; 102 IDs unstaged**. This checkpoint adds **no** counted translations.

Actual exact user-supplied Japanese 2MiB SFC SHA `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956` has been examined at byte level. All **279** selected Quiz source addresses parsed into **546** original physical writable glyph windows: **zero overlapping staged byte spans**, beyond just zero duplicate addresses. Of the remaining 102 canonical Quiz source IDs: **92 valid native CP932 text starts / 10 unsafe raw start offsets**; of the 92, **10 actually overlap a previously staged larger text record**, while **8 of the 10 unsafe starts lie within already staged text**. There are **82 independent parsable physical source fields** left to address; this does not imply 20 extra translations completed! (20 are nested/unsafe fragments needing parent semantic QA, and two unsafe source positions need script tracing.)

Of those 82 independently parsable fields, only **7** have any native trailing ASCII padding: six previous **UNAPPROVED** 062 text-width experiments, plus `0x34245` (one spare glyph, still insufficient to display Hanawa Akira). The other **75** have no trailing padding; correct rendering/Quiz answer choices need safe interpretation or relocation, **not forced incorrect abbreviations**. Full Japanese and `vi_full` in canonical CSVs are intact.

Original Quiz bank-end has **5,881 consecutive `0xFF` bytes at `0x36907–0x37FFF`** (end-exclusive 0x38000), a possible **UNAPPROVED** area for future relocated strings. No interpreter jump, string pointer model, or in-emulator proof was established. This space is NOT safe to use merely because it contains `FF`; no bytes changed.

New read-only tool `tools/audit_quiz_remaining_063.py` verifies original ROM SHA, all eight canonical source CSVs, stages 041–061, 279 actual original source ranges, remaining 102 inventory, overlap counts, padding, and raw `FF` region. It writes JSON reports only, no IPS/ROM; checked its essential physical counts independently locally on clean SFC. New file `docs/QUIZ_REMAINING_SOURCE_TRIAGE_063.md` details safe/unsafe offsets and next step. Full end-to-end repo checkout execution of the newly committed tool is still pending (connected GitHub source only), so validate script in checkout before acceptance.

**Hard blocker remains** missing raw original 043 clean-ROM IPS SHA `d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50` (old Library ZIP metadata could not be materialized). Consequently no full 061 ROM rebuilt, no emulator QA. User wants **CONTENT FIRST, FONT LAST**, no repeated small patch downloads. Next work: reverse engineer Quiz interpreter/control pointers on original ROM for one reversible long-name example, verify in emulator before treating 82 standalone labels as installable; four Fortune exceptions and G3 screen/result UI after. DO NOT inflate completion count from physically nested scanner fragments.


## CHECKPOINT 061 + PROBE 062 — 2026-10-11: 17 REAL-SOURCE QUIZ FIELDS; 6 UNAPPROVED PADDING PROBES

**READ `docs/QUIZ_061_AND_PADDING_PROBE_062.md` FIRST.**

- Original user-owned Japanese headerless 2MiB SFC is still available, exact SHA256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`.
- Old initial 061 draft had 19 compact Quiz answers. **RETRACT TWO BAD ABBREVIATIONS:** `0x36579 Rolls` truncated the proper name Rolls-Royce; `0x32108 1tr` ambiguously represented one million yen. Both removed from 061 (historical file name still says 19), flagged for safe expansion. **17 truly new 061 records**; clean source byte QA confirmed 17/17 original `816F` markers retained, 182 approved source bytes, 180 changed bytes. **283B /19-record QA-only IPS SHA256 `89ba15c82f8b66b74bd0055ec5255ec3e512bca08d0a842d46ddbe4c63a08de6`**, overlay SHA256 `50181b14eedf96845f9428a2809536e891829a6455e7afe51f2e1ee85d3cfb5f`. QA ONLY, Japanese clean-ROM overlay lacks production Vietnamese font, SNES checksum and runtime proof.
- Committed `translation/runtime/quiz_content_first_19_061.json` (17 records), `tools/build_content_first_061_quiz_17.py`, `tools/rebuild_content_first_061_full_chain.py`, `tools/audit_quiz_unique_061.py`. **Live GitHub all-stage manifest cross-check completed after edits:** 041 21 + 047 15 + 054 54 + 057 50 + 058 67 + 059 34 + 060 21 + 061 17 = **279 DISTINCT QUIZ SOURCE RECORDS /381**, 0 duplicate exact addresses, **102 remain**. NOT all playable; do not confuse byte QA with emulator acceptance. The 061 integrated builder has NOT run against real missing 060 merged binary.
- **Experimental PROBE 062 (DO NOT COUNT):** Found six original Quiz answer slots containing unused native single-byte ASCII spaces before immutable `816F` markers. Exact clean-ROM byte experiment changed 90 bytes within a 104-byte safe source scope, all six `816F` controls untouched. **128B /6-record QA-only IPS SHA256 `74cc6dd983753e9370228092b404549891ca6e273e32dbd9e59887c284aed5cd`**, source-overlay SHA `2d0df00692276b4256c888aa71aaf4290a7f449c5bb57a41b90d382271487d96`. Candidates `0x338D8`, `0x338F7`, `0x33AC5`, `0x33C27`, `0x33C3E`, `0x33C55` only. `0x33B8D` was a BAD scanner alias into script-control bytes; excluded. **Replacing layout spaces with more glyphs may overflow rendered UI; no runtime emulator QA => ALL SIX UNAPPROVED.** Docs `translation/runtime/quiz_padding_expansion_PROBE_062.json` and `tools/probe_quiz_padding_062.py` record/reproduce byte-only experiment, do not emit ROM/IPS.
- **Hard blocker unchanged:** exact historical 043 clean IPS with SHA256 `d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50` still inaccessible as raw bytes; only old Library ZIP metadata visible and materialization previously denied. **FULL 061 COMBINED ROM NOT BUILT. EMULATOR NOT TESTED.** User preference **content-first, fonts-last**, no pointless intermediate downloadable IPS per checkpoint.
- When exact 043 available: `python tools/audit_quiz_unique_061.py`; `python tools/rebuild_content_first_061_full_chain.py clean.sfc exact043.ips --ips final061.ips --report qa061.json --allow-untested`; `python tools/probe_quiz_padding_062.py clean.sfc`. Never commit copyrighted ROM or font bytes.
- Continue 102 remaining source Quiz entries, especially names/long choices with **true text relocation/layout QA**, four Fortune exceptions and G3 result screens, then one full emulator test pass. No ungrounded completion percentage.


## CHECKPOINT 060 — 2026-10-11: CORRECTED 059 DUPLICATES + 21 NEW BYTE-VERIFIED QUIZ RECORDS

**Read `docs/CONTENT_FIRST_QUIZ_21_CHECKPOINT_060.md` first.** Source-only physical QA is on the *actual user-supplied exact* original Japanese 2MiB SFC SHA256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`.

**CORRECTION TO HISTORICAL CHECKPOINT 059:** 0x31F75 / 0x31F84 / 0x31F95 (three birthday date answers) were previously included in 047. Old 059 duplicate claims and 244/381 cumulative count were wrong. They have now been removed from 059, and `tools/build_content_first_059_quiz_37.py` explicitly rejects reintroduction. Corrected 059 count **34 records**, **73 native `816F` markers**, 1544 writable text bytes /1541 changed, **1914B /73 record** isolated source IPS SHA256 `d383a705336236b3ff2c992ab3ce28c4605d1a5afd809bb8f8eb630035802a81`. Corrected source test ROM SHA256 `7a6c5cb411738706b019ea4b320e20d4bb131888ba2acdf3bd3aae3fdd3be0c2`. The earlier 059 source-only IPS SHA was reproduced byte-for-byte before the correction, proving the investigation used the same clean input. Note that the two 059 filenames containing `37` are historical and now hold/build 34 source records.

**NEW 060 ORIGINAL CLEAN-ROM SOURCE BYTE QA PASS:** 21 additional distinct Quiz records, 43 original text frames with all **43 immutable `816F` line markers**, **816 allowed** physical text bytes / **815 changed**; isolated nonplayable source IPS **1038B /43 records**, SHA256 `f03313fd1d822c2b3c49b46c3bec520313f3ae3d5b8c62db6d177206238a5822`; overlay ROM SHA256 `8eb2b3ea0aedafd744039d4b05f2a647d0c4a239e778ef4c604305c2b033fbe9`. An independently implemented IPS parser reproduced the entire 2MiB source overlay exactly. New captions cover Hanawa/Kazuhiko, Maruo glasses, Migiwa/Mark, Pusadi farewell, caring brother, Rolls-Royce plus short recognizable answer alternatives `Ono`, `Jump`, `Idol`, `Sáo`. Canonical full `vi_full` and original Japanese scans unchanged.

Repo committed: `translation/runtime/quiz_content_first_21_060.json`, `tools/build_content_first_060_quiz_21.py`, `tools/rebuild_content_first_060_full_chain.py`, `tools/audit_quiz_unique_060.py`, plus QA document. The unique-offset inventory was cross-checked from 8 source CSV + all 7 staged manifests, **262 distinct Quiz targets /381 original**, **119 remain**. The audit tool now fails closed if previously integrated offsets recur.

**DO NOT claim a playable build:** the 043 clean-source IPS SHA `d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50` is still inaccessible as raw bytes, despite archived ZIP metadata in Library. The exact original clean ROM is accessible; its source overlay checks PASS, but the **FULL 060 COMBINED ROM IS NOT BUILT, EMULATOR NOT TESTED**. Once authorized historical checkpoint043 IPS is accessible, run from the game directory:

`python tools/audit_quiz_unique_060.py`
`python tools/rebuild_content_first_060_full_chain.py clean.sfc checkpoint043.ips --ips full060.ips --report full060_qa.json --allow-untested`

Next: 119 remaining Quiz source rows, mostly proper-name answer alternatives requiring safe text expansion, four Fortune too-small fields, G3 result/title graphics, then SNES emulator/full font test. User wants content-first, font last, and no useless intermediate patch downloads.


## CHECKPOINT 059 — 2026-10-11: 37 MORE QUIZ FIELDS, EXACT ORIGINAL-ROM BYTE TEST PASS

Read `docs/CONTENT_FIRST_QUIZ_37_CHECKPOINT_059.md`.

- Added 37 distinct original Quiz03 part1 content slots, not included in old 047 numeric-answer layer or 058. New runtime manifest `translation/runtime/quiz_content_first_37_059.json`, validated source Japanese + full Vietnamese references and per-line capacities, no lossy truncation of missing complex answers.
- Performed **ACTUAL CLEAN 2MiB JAPANESE ROM SOURCE QA** on attached `Chibi Maruko-chan - Mezase! Minami no Island!! (Japan)(1).sfc` SHA `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`. **37/37 fields, 76/76 physical rows, 76/76 native `816F` controls retained; 1,572 byte source windows / 1,568 physically changed positions.** Real source-only IPS 1,961B /77 records SHA `15e12c50f501f6455c4b31dc837231ca23dbccdfe94bd07ef5a4d4384f844856`; applying separately via independent IPS parser reproduced entire 2MiB source overlay SHA `3dcdaca24ed47d92c7f11d8851fcf1c3516a41412f224a123fb3fe4234e51aaf`. **That source-only overlay is not playable**, never send it as a finished patch.
- Critical careful byte coverage: do NOT separately patch scanner offsets 0x31E50 /0x31F33 /0x3275E as their physical text windows overlap earlier records. Do NOT add 0x32874 because it extends into 058 source window at 0x3288E. Preserve too-small source alternatives (`Xe đạp`, `Hành lá`, `Nepal`, one million yen) for future layout expansion rather than invent incorrect abbreviations. All original full translations remain untouched in `translation/source/quiz_batch03_part1_vi.csv`.
- Newly authored `tools/build_content_first_059_quiz_37.py` safely patches existing full 058 ROM and recomputes checksum, replays clean IPS; `tools/rebuild_content_first_059_full_chain.py` reproduces 043->059 in memory. These new GitHub scripts have **not been run on the missing original 058 full integrated ROM**; any source-only QA PASS must not be confused with an emulator PASS.
- Conditional Quiz physical inventory **244/381 distinct source targets** = 21 (041)+15(047)+54(054)+50(057)+67(058)+37(059); **137 need further safe runtime selection**. Do not count duplicated old 053 rows. These 244 are not yet assembled into a working 059 game.
- **Blocker unchanged:** raw bytes of exact earlier checkpoint043 clean IPS SHA `d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50` remain unavailable; old ZIP metadata in user's Library cannot currently materialize. User's original clean ROM is available. **FULL 059 COMBINED ROM NOT BUILT, EMULATOR NOT TESTED.**
- Once checkpoint043 .ips is made accessible, run `python tools/rebuild_content_first_059_full_chain.py clean.sfc exact043.ips --ips full059.ips --report qa059.json --allow-untested`. Still need 4 Fortune too-long cases and G3 ending/result UI and last QA. No commercial ROM/font uploads; user wants CONTENT FIRST, FONT LAST and no endless micro IPS downloads.


## CHECKPOINT 058 — 2026-10-11: 67 MORE REAL ORIGINAL-ROM QUIZ SOURCE FIELDS, 149 NATIVE LINE CONTROLS

**READ `docs/CONTENT_FIRST_QUIZ_67_CHECKPOINT_058.md` first.** New reviewed canonical-source-anchored files: `translation/runtime/quiz_content_first_67_058.json`, `tools/build_content_first_058_quiz_67.py`, and `tools/rebuild_content_first_058_full_chain.py`.

- The current, user-uploaded, exact clean Japanese 2MiB SFC SHA `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956` was actually read. An isolated **original-ROM source-only text overlay** wrote exactly **67 new nonduplicate Quiz narrative/question fields** from Batch03 part2 + part3 into 149 original frame windows. **3,180 source-byte positions approved; 3,174 changed**, all **149 original `816F` separators** and script stops retained, no overlap between selected source records. Its **3,937-byte /151-record** clean Japanese QA-only IPS was reapplied by a separate IPS parser and recreated byte-identical 2MiB output. QA IPS SHA `6403b2937ac1f82e33809954c6693b196bd425a830dfb79be4f18741a15da7d7`; QA-only source image SHA `510f1f64a765f16f00235fa2218b9919fab1e5fb977f7ed8afc633fbf4565ff8`. **This text-only original clean ROM experiment is not playable; do not distribute.**
- Source rows are anchored to untouched canonical `source_jp_scanner` and full `vi_full` in both `quiz_batch03_part2_vi.csv` and `quiz_batch03_part3_vi.csv`. Corrected name ordering **Honami Tamae**, kept **Utsui Ken** intact, and preserved the context of Ono moving to Tokyo, Nagasawa's father's name and school/character trivia. Actual runtime language is still constrained by original physical cell count and needs real emulator proof.
- Cross-check against earlier selected Quiz: 041 21 +047 15 +054 54 +057 50 +058 67 = **207 distinct source target fields**, out of 381 original source entries (**174 remain**). **This is a potential merged coverage count, not gameplay-validated completion**. The old 053 was 15/16 duplicated with 041 and must not be counted.
- A smoke test of the **058 merge algorithm** on a **synthetic font-table source ROM** passed byte whitelisting, fixed-source trailer preservation, regenerated checksum and clean IPS replay; real 057 font/graphic baseline and emulator were **NOT** used. Repo 058 builder has been written and source inspected, but not executable against missing actual 057 merged ROM. Fixed two bugs in the freshly authored GitHub tooling: 058 chain originally used wrong variable order (`3addf45`), 058 builder originally referenced stale manifest preview field keys (`ca863b8`). Use the corrected revisions.
- **Major hard blocker unchanged:** exact historical checkpoint043 clean-ROM IPS raw bytes with SHA `d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50` unavailable; old ZIP appears in user's Library metadata but Files materialization was denied, no bytes extracted. User's clean SFC remains accessible. **FULL 058 COMBINED ROM NOT BUILT. EMULATOR NOT TESTED.**
- Once exact IPS043 is made accessible: `python tools/rebuild_content_first_058_full_chain.py clean.sfc checkpoint043.ips --ips combined058.ips --report qa058.json --allow-untested`. Only then run actual emulator/menu/story/Quiz QA. Next missing long Quiz/name answers (174 target records), four Fortune old-capacity exceptions, G3 end/result artwork and then typography. User prefers **CONTENT FIRST**, no repeated tiny patch downloads or font distraction.


## CHECKPOINT 057 — 2026-10-11: 50 NEW NONDUPLICATE QUIZ RECORDS BYTE-VALIDATED

**Read `docs/CONTENT_FIRST_QUIZ_50_CHECKPOINT_057.md` before proceeding.** Newly committed `translation/runtime/quiz_content_first_50_057.json` adds **50 distinct Quiz source records** not included in 039/041/047/054, in part2/3 of Quiz Batch02. Real user-uploaded clean Japanese 2MiB ROM SHA `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`.

- **ACTUAL SOURCE-ROM BYTE QA PASS**, including refined natural wording: 50/50 logical records, 105 original physical text frames and **105 original `816F` separators preserved**. Exactly 2,106 source text bytes modified, only within approved original text cells, no control bytes or padding overwritten. Independent standalone clean-ROM text-only IPS apply/replay reproduced all 2MiB bytes byte-for-byte. Current QA preview IPS **SHA `73829cb20f1b182142e428ba55366227417258d8e87f9e7da6de4fa1d093b749`**, **2,614 bytes /100 records**. Preview ROM SHA `525575f7d178d3a2df4d616934484b8e5ae4a15db60c264c607db5fd3f1c4b98`.
- **Existing V2 codepage limitations are real**: several characters (e.g. `R`, `X`, `ệ`) cannot be encoded in old 0x84 table. Consequently character-name answer choices and difficult captions not fitting original cells are **deferred**, not mangled for inflated completion stats. Full `vi_full` remains intact in canonical CSVs.
- `tools/build_content_first_057_quiz_50.py` adds **056 -> 057** strict whole-ROM checksum and final IPS replay; `tools/rebuild_content_first_057_full_chain.py` invokes the 043->056 chain then 057. A **synthetic font-table baseline** test (not the true missing 056 ROM) passed local full 057 builder constraints (50 fields, 105 controls, checksum, IPS replay); the actual main original clean ROM was separately used for physical source-only QA. **Do NOT call this a playable release or real 056 merge.**
- Candidate count math if assembled: Quiz **21 in 041 + 15 in 047 +54 in 054 +50 in 057 =140 unique source fields**, out of 381 canonical (remaining 241 original Quiz records), **NOT yet combined to one verified ROM**. Do not count 15 repeated old 053 rows again.
- Still missing original 043 clean-ROM IPS raw bytes (SHA `d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50`), despite visible Library ZIP metadata and failed authorization for old file raw materialization. Full integrated 057 ROM **NOT BUILT**, SNES emulator **NOT TESTED**. Once exact 043 IPS available, run `python tools/rebuild_content_first_057_full_chain.py clean.sfc exact-043.ips --ips final-057.ips --report qa057.json --allow-untested`. Never distribute clean Japanese source ROM or font files on GitHub.
- Keep user preference: **CONTENT FIRST, font last; no intermediate test patch downloads**. Continue remaining long Quiz, 4 Fortune name/color capacity exceptions, G3 ending/result graphics. Do not claim final localization done.


## CHECKPOINT 056 — 2026-10-11: TWO REAL-SOURCE FORTUNE EXCEPTIONS + G2 BUILD BUG FIX

**Read `docs/CONTENT_FIRST_FORTUNE_EXCEPTIONS_056.md` before editing!** Actual mounted clean Japanese 2MiB ROM hash matched `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`.

- Completed **2 of 6** formerly excluded Fortune original text fields as exact CP932 static source-only overlays: `0x2C413` **体育が開運のカギ -> Vận động** (8 cells) and `0x2C601` **プリンを食べてみよう -> Ăn pudding** (10 cells). The canonical full `vi_full` strings remain unchanged. Both original `81 6F` terminators preserved. 36/36 source text bytes changed under whitelist; independent original-ROM IPS replay PASS. QA-only text overlay: **54B /2 records**, SHA `84e30fe4f1bad5621934de99dcc9e0c3a11efd64152f36af676b42e56eca31be`. No altered font or game ROM shared; QA-only overlay is NOT playable.
- Four **genuine capacity exceptions** retained for safe display-slot relocation, **not gibberish abbreviations**: `0x2BD5E` Heaven's voice, `0x2C86B` see you next week, `0x2CA7D` Yellow, `0x2CADD` White. Full original Vietnamese maintained in canonical Fortune source files. Conditional Fortune physical count would become **153/157**, not yet built or emulator-tested.
- Fixed a **real guard error in 055**: native G2 line padding is 8 / **4 / 4** ASCII spaces, not 8/2/2; corrected `tools/build_content_first_055_g2_rules.py`. Original clean ROM bytes at all 3 positions personally checked.
- GitHub source: `translation/runtime/fortune_exceptions_2_056.json`, `tools/build_content_first_056_fortune_2.py`, `tools/rebuild_content_first_056_full_chain.py`, plus QA doc. No old checkpoint043 IPS bytes accessible; Library's 043 ZIP and Probe008 ROM raw materialization both denied. **Full 056 integrated ROM NOT built; SNES emulator NOT TESTED.**
- When exact 043 clean-ROM IPS available (SHA `d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50`), run `python tools/rebuild_content_first_056_full_chain.py clean.sfc checkpoint043.ips --ips final056.ips --report qa056.json --allow-untested`.
- Continue **content first**, especially remaining 291 Quiz source entries and 4 long Fortune fields and G3 graphics, then font/renderer QA. Avoid mini-patch downloads and repeated empty checkpoint claims.


## CHECKPOINT 055 — 2026-10-11: G2 RULES TRANSLATED, QUIZ 054 EDITORIAL QA

Read `docs/CONTENT_FIRST_G2_RULES_CHECKPOINT_055.md`.

- **REAL CLEAN-ROM QA PASS:** Three G2 rule captions translated with original physical Japanese fields **0x1E307 / 0x1E323 / 0x1E337**: `Luật chơi!`, `Thắng 2`, `Tới khi thắng`. Native Japanese CP932 sources 64 editable text bytes; 64 text-byte modifications; all 3 original `816F` delimiters and ASCII indentation unchanged. Original bullet `・` is ordinary CP932 punctuation, legally repurposed as a text cell without changing a control opcode. Independent 87-byte /3-record text-only IPS replay PASS, SHA `b2372df59679573167cd82f0c95b2c30de24eb088b323d91a2b4a8d72f494f04`. **Text-only clean-ROM overlay is NOT playable.**
- **REAL CLEAN-ROM QA PASS after semantic revision:** 12 awkward runtime Quiz captions improved among the same 54 already-authored fields, with Fujiki/Nagasawa role correction, Hanawa/Tomozo pension joke and Valentine chocolate narrative clarified. 54/54 original Quiz spans and 123/123 `816F` markers preserved. Updated 3,279-byte /127-record source overlay IPS SHA `792b0ccb6f60b77d6cc93f7ec91f87006e9d17a2c723344379df96731faf7ee9`, independent IPS replay PASS. 54/54 entries now cross-check exact canonical Japanese and complete `vi_full` in source CSV before final build.
- Committed `translation/runtime/g2_rules_content_first_055.json`, `tools/build_content_first_055_g2_rules.py`, and `tools/rebuild_content_first_055_full_chain.py`; improved guarded 054 builder now pins updated source physical-IPS fingerprint.
- **Full 054/055 combined ROM remains NOT BUILT and emulator NOT TESTED.** User's original clean ROM is available and exact SHA verified. The historical checkpoint043 IPS is still missing as raw attached bytes (Library metadata not materializable). Until its original clean-ROM IPS is made available, do not claim a final patch/game.
- User preference: content-first, no repeated standalone test IPS downloads; after exact 043 bytes available run `python tools/rebuild_content_first_055_full_chain.py clean.sfc exact-043.ips --ips final-055.ips --report qa055.json --allow-untested`. Next: remaining 6 Fortune exceptions, Quiz long names/layout, G3 results, then runtime font QA.


## CHECKPOINT 054 — 2026-10-11: +54 NONDUPLICATE QUIZ PHYSICAL SOURCE FIELDS (INTEGRATED BUILD PENDING)

**Read `docs/CONTENT_FIRST_QUIZ_54_CHECKPOINT_054.md` first.** Actual user-supplied Japanese clean ROM SHA `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956` verified. **54 new original Quiz records**, 123 physical line spans, 123 original `816F` controls preserved, 2,642 permitted editable source bytes and 2,636 actual changed bytes were physically tested on the clean ROM as a **text-only, non-checksummed, NONPLAYABLE QA overlay**. Independently reapplying its 3,279B /127-record IPS returned the same 2MiB bytes; overlay IPS SHA `9f5069f7a105e371a71f9cf8bf5fdd38bae099d774c184a272f9abec9c8908ad`. No emulator test.

**Historical 053 correction:** 15 of the 16 supposedly new Quiz entries were already integrated in 041. Only `0x340C0` was additional, and it is now included in 054 once. 053 standalone builder disabled; do not count or apply those 15 again. All new 054 offsets have zero collision with the 039/041/047 tracked source offsets.

**Pushed to GitHub:** `translation/runtime/quiz_content_first_54_054.json`, `tools/build_content_first_054_quiz_54.py`, `tools/rebuild_content_first_054_full_chain.py`, and QA document. These new source-committed Python builders have **not** run against a 048 ROM in this session. Full 054 integrated ROM still **NOT BUILT**, because historical original-clean `043.ips` is not accessible: old ZIP is only visible in Library metadata and raw materialization failed. To run once user supplies exact 043 bytes:

`python tools/rebuild_content_first_054_full_chain.py clean.sfc exact-043.ips --ips final-054.ips --report qa054.json --allow-untested`

Do not upload copyrighted ROM or release a text-only IPS. User prefers content-first, font and emulator visual cleanup last; do not send unsolicited mini-patches. Remaining work includes long Quiz names/questions, G2 rules, G3 result assets.


## 2026-10-11 — LIVE USER ROM CHECK / 053 SOURCE CORRECTION

### Uploaded ROM physical 053 Quiz16 overlay — STATIC PASS, still not playable

Read `docs/QUIZ_053_UPLOADED_ROM_BYTE_QA.md`. On the actual user-uploaded clean ROM, all **16** Quiz captions were written as a text-only in-memory byte overlay, 134 writable bytes, 112 changed positions, 310B/38-record text-only IPS SHA `8ae0adc95fcb69c9aab141fd10004dc698f295be3e0a4fd2d5399f8382709f7e`; separate IPS replay matched. All original `816F` terminators and native padding retained. **Text-only overlay is NOT PLAYABLE; no checksum or Vietnamese font, no emulator QA.** Integrated 048+053 still awaits accessible 043 ZIP/IPS.


**VERIFIED against user-uploaded exact clean SNES ROM, 2,097,152 B, SHA256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`: 16/16 reviewed Quiz source records match original CP932 and actual `816F` field boundaries.** The prior rejected `0x340C0` Quiz row is real: 6 native ASCII spaces at the scanner offset, JP text actually starts `0x340C6`, then eight native trailing ASCII spaces and `816F`. The corrected 053 manifest and builder protect both original padding regions byte-for-byte and replace ONLY the real 10-glyph text region. Other 15 records match original source and delimiters without padded scanner correction.

- Updated `translation/runtime/quiz_content_first_16_053.json` and `tools/build_content_first_053_quiz_16.py` to retain 16 original-ROM-safe candidates; it is not a new patch build yet.
- Full combined 048/053 ROM is **NOT BUILT**. ROM screenshot/emulator QA **NOT TESTED**. The exact checkpoint043 IPS from the prior archive has SHA256 `d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50`, but its raw bytes are not available in the working container.
- The Library metadata lists `/Dịch giả lập/Chibi_043_G0G1_176Fields_Story58_Content_First_UNTESTED.zip` (22,558 B) but Files raw materialization was refused by authorization, so **do not claim it was read or extracted**. User may attach this archived ZIP directly in the conversation for building full 043 -> 048 -> 053 from their already supplied clean ROM.
- No copyrighted ROM/font uploaded to GitHub. Keep content-first and no intermediate IPS links. After archived 043 patch is accessible, run guarded chain, validate exact 047 SHA, merge 048 and 053, then proceed with remaining Quiz/G2/G3.


## CHECKPOINT 053 — 2026-10-11: 16 CURATED QUIZ ROM-SLOT TRANSLATIONS + GUARDED BUILDER

- Authored `translation/runtime/quiz_content_first_16_053.json`: **16** Quiz source-addressed compact Vietnamese captions, including original Japanese and full canonical Vietnamese text. Covered short trivia/answers (comedy, riddles, driver, six age choices, birthday choices and more). Avoids name mutilation and preserves source-of-truth `vi_full`.
- Added `tools/build_content_first_053_quiz_16.py`, a fail-closed source-to-ROM builder requiring clean-ROM SHA, previously integrated 048 binary with explicit external expected SHA, original CP932 two-byte exact source, unchanged `816F` terminators, no previously translated 047 overlaps, NFC/old V2 font mapping and approved byte diff plus rechecked clean-based IPS. Does not commit copyrighted ROM.
- These are **source-reviewed candidates pending ROM byte verification**; no new ROM bytes actually tested, no new emulator PASS. Never count them as physically integrated in 048/053 until the strict builder runs successfully.
- Local ROM original and 043 IPS unavailable in this session; run full checkpoint049 chain to create exact 048 and determine SHA, then 053 builder. Continue large Quiz/full text/layout engine instead of tiny clipping or font microtests; no intermediate IPS links.


## CHECKPOINT 052 — 2026-10-11: QUIZ 381-ROW PHYSICAL PREFLIGHT

- Fixed actual Python syntax error in `tools/audit_quiz_source_050.py` introduced at checkpoint051 (literal `\\n` was inserted into executable source). The checker can now be parsed; no local execution has yet taken place.
- Added `tools/preflight_quiz_physical_052.py` read-only strict physical scanner for all 381 Quiz rows. It requires exact original clean ROM SHA, identical CP932 source bytes at exact offsets, even glyph byte width, immediate original `816F` terminator, and no collision with existing Vietnamese baseline; it blocks scanner layout separators, half-character aliases and already-patched 047 rows.
- Output reports original Japanese, canonical full Vietnamese, writable glyph-slot capacity only on proved safe fields, and blocking reasons. **Does NOT automatically truncate Vietnamese or produce patches.**
- Both tools committed to GitHub. Neither has been executed here: no original ROM or baseline ROM mounted. Therefore no additional Quiz fields have been integrated into ROM and no emulator PASS.
- Next: run checkers with real clean+verified 048 baseline, select natural compact translations under measured budgets, and author a single substantial guarded Quiz patch. Do not send intermediate IPS; prioritize content, font later.


## CHECKPOINT 051 — 2026-10-11: FIX QUIZ AUDIT COMPLETENESS

- Live GitHub source check exposed two files accidentally omitted by checkpoint050 triage: `quiz_batch02_part3_vi.csv` (43 rows), `quiz_batch03_part3_vi.csv` (58 rows). Original six held 280 rows; total canonical inventory **381 = 280+43+58**.
- Fixed `tools/audit_quiz_source_050.py` to scan **eight** canonical Quiz CSVs and fail closed if the row count differs from 381. This is substantive source coverage correction, **not** an integrated ROM text patch.
- In this conversation, no original ROM/043 IPS is mounted. The Quiz auditor and 048 merge still have NOT been executed locally; no emulator/runtime PASS.
- Next: run complete eight-file audit against source checkout, then build substantial Quiz ROM integration with guarded original CP932 text and relocation for long names/questions. Never shrink meaningful names to illegible abbreviations. Continue content-first and no interim download links.


## CHECKPOINT 050 — 2026-10-11: QUIZ SOURCE TRIAGE TOOL ADDED

- Confirmed accessible canonical Quiz Batch01/02/03 source CSVs, six files. Source rows already have complete Vietnamese `vi_full`, but the Japanese scanner source embeds line-layout separators and some entries start at CP932 half-glyph boundaries. Do not write these CSV scanner offsets directly into ROM.
- Added `tools/audit_quiz_source_050.py`: read-only inventory of all six CSVs; checks duplicate offsets, compares previously integrated 047 Quiz rows, marks scanner layout delimiters, leading padding and manually corrected source spans for physical-ROM verification. Generates JSON with source text/full Vietnamese/risk reasons for the next meaningful larger Quiz integration.
- The auditor has been committed but **not executed** against a local repo checkout in this turn. No new Quiz physical ROM entries or emulator PASS. Full 048 merge runner from 049 also remains unexecuted for lack of local original ROM + IPS 043.
- Next: run the auditor and inspect original ROM byte slots/control flow; author a substantial safe Quiz batch and guarded build on top of merged 048. Content first, no new font experiments or interim download links.


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
