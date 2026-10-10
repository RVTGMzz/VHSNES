# Translation progress — Chibi Maruko-chan

## LATEST — 2026-10-11 CHECKPOINT 037: G2 RULE DATA CORRECTION

**User priority remains: finish text/graphics content first, font later.** G2 rule-board source is now classified more accurately: 3 originally Japanese lines `ルールをせつめいするよ`, `２本先取だよ`, `ゲームの時間は勝つまでだよ` have **real coherent direct CP932 source bytes** in bank83 at offsets 0x1E307/0x1E325/0x1E339, not necessarily separate graphics that must be redrawn. Exact menu rendering path still needs tracing.

**One real source-integrity error FIXED:** canonical `translation/source/rules_tutorial_vi.csv` record moved from `0x1E326` (second byte of full-width SJIS digit ２) to correct `0x1E325`. Natural Vietnamese wording revised to `Ai thắng 2 ván trước sẽ thắng / Chơi đến khi phân thắng bại`; bullet structure semantically retained. The 0x1E323/0x1E337 original full-width bullet bytes and 3 paragraph delimiters were independently verified intact in clean ROM.

**35 already-translated minigame/VS direct UI fields** were checked against exact raw CP932 source offsets 0x288C2..0x28BFF (fullwidth rounds, difficulty, timer, player slots, controller and stage). This confirms existing semantic source inventory; it adds **zero** new Japanese meaning rows. The audit deliberately rejects the old wrong 0x1E326 offset. See `docs/G2_RULE_TEXT_ACTUAL_ROM_SOURCE_CHECKPOINT_037.md` and `tools/audit_g2_rules_direct_sources_037.py`.

A read-only scout decoded 42 nearby candidate resources for G2 and 52 distinct 4bpp sprite source/destination entries from the package catalog for G3. **No G3 result asset was proven or changed**, and there is **NO new ROM patch** this checkpoint. Graphics-only 036 remains static UNTESTED and not merged into historical Vietnamese direct-text Build035. Need G3 result callback proof and safe combined build. Font remains deferred.


## LATEST GRAPHICS — CHECKPOINT 036 (2026-10-11)

One additional **actually modified retail graphic label**: the main-mode header “どれにする？” → “Chọn gì” / “đây?” (display reading **Chọn gì đây?**). Original asset found in package $82:A213 index6 (main mode init ROM 0x20047), source $98:F06F / file0xC706F, 8192B=256 4bpp sprite tiles. Actual ROM graphic replacement keeps first **192 native icon/menu-label tiles** identical and rewrites only last 64 heading tiles. Compressed stream **3485→2428 bytes**, same original slot, no relocation.

Merged with G0 startup three-line title and G1 Story Start/Password sprite. Three graphics targets now patched in actual art assets (G0 title + credit, G1 two buttons + main-menu heading): current graphics-only combined clean-ROM experiment SHA256 **2c8beee73e985c9a2690cc36ace335f05115c1a3e81b369e09d0cfb132117090**. IPS 14,452B/263 records, replay exact. Main-menu sprite referenced by 13 UI scripts: requires real emulator smoke tests before acceptance.

**Important:** graphic-only experiment still does NOT contain prior Story/Quiz/Fortune direct-text Vietnamese meaning layer. Actual SNES runtime NOT TESTED; no assertion of whole-game completion. Full font path deferred per user request. Next: G2 VS/rules graphics and G3 result/ending screens, then exact-verified merge with canonical language build.


## LATEST RETAIL GRAPHICS — 2026-10-11 CHECKPOINT 035

**Two more genuine Japanese graphics labels were replaced in a SNES experiment**, not just translated in a CSV: G1 Story `はじめから → Bắt đầu` and `パスワード → Mật khẩu`. Their exact original sprite resource is `$97:F95E`, file `0xBF95E`, loaded by G1 resource package `$82:AF23` to VRAM word `0x7800`; 31 tiles ×32B = 992B, **436B original compressed slot**, now **331B**. Blank separator and original icon tiles are preserved. See `docs/G1_START_PASSWORD_ACTUAL_ROM_PATCH_CHECKPOINT_035.md`.

Checkpoint034 title graphics `Chibi Maruko-chan / Tiến tới đảo phương Nam!! / Việt hóa bởi Votri Valley` and two G1 new Vietnamese graphic labels are **now combined** as a clean-ROM-only experimental IPS: 10,880B /225 records, joint SHA256 `77a207589857d2886059057151eaf3d47530032b726744fe739e991ff81a5b80`; clean-ROM IPS reapply PASS, **zero G0/G1 byte collisions except checksum**. Original Japanese Story/Quiz/Fortune text still exists in this graphics-only build; no full Vietnamese merge, emulator gameplay test or final font acceptance has happened.

**G1 heading `どれにする？` still pending**. G2 rules and G3 results/ending still pending graphics insertion. Do not confuse this with the 216 source-language editorial changes from 032: these are two real **retail graphics** labels patched, not new meaning-source discoveries. User priority remains translation/content/graphics first, font later.


## LATEST GRAPHICS CONTENT — 2026-10-11 CHECKPOINT 034

G0 **actual first-boot title graphics asset FOUND and replaced in an experimental ROM**, not just a suggested Japanese→Vietnamese wording. Original title BG package `$82:A087`, map at ROM `0xF1F00`, graphics at `0xF6456`; offline render visually identifies the original logo. Approved pixels now contain `Chibi Maruko-chan` / `Tiến tới đảo phương Nam!!` / `Việt hóa bởi Votri Valley`, and have been round-tripped from the patched graphics ROM. **166 new title tiles, 583 non-title shared tiles preserved, four background maps identical, OBJ sprites untouched.** See `docs/G0_ACTUAL_TITLE_ASSET_REPACK_CHECKPOINT_034.md`.

The clean-ROM G0 title-only experiment SHA256 is `012cdfb87eae1b7c5a9feada4e1c322541e3c91ba45ba0b857e08a2465f47ce0`, with verified IPS patch available locally. This title-only ROM **does not contain the main Story/Quiz/Fortune Vietnamese work** (Build035 not merged) and **has not run in an SNES emulator**; title graphics runtime PASS must not be claimed. G1 Start/Password and G2/G3 retail screen graphics still need asset proof and real integration. Font stays deferred.


## CURRENT CONTENT-FIRST CHECKPOINT 032 — 2026-10-11

**User priority: finish translating the game content first; font/renderer work later.** See `docs/CONTENT_FIRST_CANONICAL_MERGE_CHECKPOINT_032.md`.

- Historical source-language tally: **1,018 ordinary player-facing meaning rows**, plus **3 G2 demo rows**, giving **1,021 tracked release-intent source records** including demo. Neither total is a whole-game completion percentage.
- **220** editorial revision events from **10** review CSVs were reconciled into the actual canonical `translation/source/*.csv` `vi_full` cells.
- They represent **216 distinct source offsets** across **20 source CSV files**, with **4 later-pass supersessions**.
- **209 revision operations changed Vietnamese `vi_full` strings**, **11 already matched**. No new Japanese source rows were invented or added.
- After applying final revision precedence, current GitHub branch source vs final editorial audit: **216/216 exact matches, zero unresolved conflicts** (Story 85, Quiz 54, Fortune 24, UI 53). Source Japanese, offsets, technical fields and controls were preserved.
- Earlier editorial notes saying auxiliary UI pass03 had 24 rows were off by one: the checked-in CSV has **25** rows.
- New tool: `tools/audit_g2_editorial_canonical_032.py`. This checks semantic source consistency; it is not a ROM/font runtime test.
- **Font work frozen** at historical 031 until text/graphics content is handled. Old 025 user screenshot is still a typography FAIL; candidate 029 static-only. No new runtime PASS claimed.
- Next translation/content tasks: graphics-language integration G0 title, G1 Start/Password, G2 rules, G3 results/ending; prove actual visible graphics assets before patching. Audit new Japanese lines only when clearly user-facing, never from raw scanner noise.

The later headings in this tracker document earlier historical work; this checkpoint 032 status supersedes their old claims about editorial CSVs being merely unmerged proposals.


Updated: 2026-09-20 +07  
Branch: `chibi-maruko-bootstrap-01`

## Meaning-first Vietnamese source layer

Current committed **player-facing / release-intent** translated rows:

- `translation/source/seed_known_strings.csv`: 10
- `translation/source/main_menu_vi.csv`: 10
- Story Batch 01: 126
- Story Batch 02: 126
- Story Batch 03: 84
- `translation/source/credits_vi.csv`: 19
- `translation/source/rules_tutorial_vi.csv`: 2
- Maruko Q Batch 01: 74
- Maruko Q Batch 02: 129
- Maruko Q Batch 03: 178
- Maruko Fortune / `まるこみくじ` Batch 01: 157
- Minigame UI Batch 01: 52
- Karaoke Batch 01: 28
- Stage-name Batch 01: 15
- Quiz misc/result UI: 8
- G2 conversation demo direct text: 3
- **total release-intent meaning rows: 1,021**

Additional reverse/reference material:

- `translation/source/internal_debug_reference_vi.csv`: internal QA/debug reference, excluded from the 1,021 release-intent count
- `translation/source/graphics_text_targets_vi.csv`: visual-text targets for graphics/tilemap work, not direct-text rows

These counts are source-translation rows, **not whole-game completion percentage**.

`vi_full` remains the canonical meaning-first translation. Runtime compact strings are allowed to shorten for fixed fields but must not replace `vi_full`.

## Main story

The coherent direct-text story arc is meaning-covered through the currently discovered ending sequence.

Tone remains frozen in `translation/STYLE_GUIDE_VI.md`: cute school/family comedy, not combat RPG.

The large runtime Story chain inserted **328** discovered direct Story fields by Build 027.

See `docs/RUNTIME_STORY_BUILD_027.md`.

## Maruko Q / Quiz

The large coherent quiz banks are meaning-covered through the currently discovered direct-text end.

Build 035 added another **65** Quiz/direct runtime entries in the remaining discovered Batch01 region around `0x34009..0x34F3E`.

The current runtime chain also carries the earlier large Quiz insertions.

## Maruko Fortune

Range approximately `0x2BD28 .. 0x2CB92`.

Files:

- `translation/source/fortune_batch01_part1_vi.csv`
- `translation/source/fortune_batch01_part2_vi.csv`
- `translation/source/fortune_batch01_part3_vi.csv`

Meaning coverage includes wish, money, romance, study, general advice, lucky items, lucky numbers, and lucky colors.

The current runtime chain carries compact Fortune insertion.

## Minigame UI

File: `translation/source/minigame_ui_batch01_vi.csv`

Meaning coverage includes:

- ball-throwing rules/controls;
- paint/dryer rules/controls;
- pool/pushing rules/controls;
- rounds;
- CPU difficulty;
- game duration;
- player slots/status;
- controller type;
- stage selector/digits.

The current runtime chain carries a direct-text Minigame/UI pass. Large Japanese title/rule graphics remain a separate graphics track.

## Karaoke

Files:

- `translation/source/karaoke_batch01_vi.csv`
- `translation/source/karaoke_batch01_singable_v1_vi.csv`

The 28-row singable V1 draft remains a second-pass runtime-oriented draft and does not replace `vi_full`.

## Stage names / Credits / Quiz UI

Meaning-covered source files include:

- `translation/source/stage_names_batch01_vi.csv`
- `translation/source/quiz_ui_misc_vi.csv`
- `translation/source/credits_vi.csv`

Build 035 adds **22 compact Credits role-token patches** on top of the prior runtime chain.

## Current direct-text runtime checkpoint

Latest large candidate:

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

## Font/codepage status

The current architecture is the proven dedicated `0x84xx` Vietnamese codepage mapped to 12x12 raw 1bpp glyphs.

The Golden Sun GBA donor-font experiment was rejected for Chibi and is not part of the current plan.

User runtime screenshots after Build 033 identified several typography defects. Build 034 applied targeted static fixes for T/V/A/K/L/e/g, circumflex orientation, and dot-below visibility. Those changes are inherited by Build 035, but the font is **not yet release-runtime PASS**.

Do not reopen broad font reverse unless new runtime evidence requires it.

## Direct-text remaining audit

After Build 035, a whole-ROM scanner audit found only 13 unchanged kana-rich candidates.

They are not established ordinary player-facing direct text:

- internal review/debug screen descriptors;
- likely effect/debug data;
- likely binary false positives.

Therefore broad direct-text scanning is no longer the current priority.

## Graphics / tilemap translation targets — CURRENT PRIORITY

### Batch G0 — title / intro

- `ちびまる子ちゃん めざせ！南のアイランド！！` -> **Chibi Maruko-chan: Tiến tới đảo phương Nam!!**
- additional localization credit -> **Việt hóa bởi Votri Valley**
- preserve original copyright/publisher attribution
- actual title-screen asset path still requires reverse



See:

- `translation/source/graphics_text_targets_vi.csv`
- `docs/GRAPHICS_TILEMAP_PASS_001_AUDIT.md`
- `docs/HEADING_REVERSE_001.md`
- `docs/HEADING_REVERSE_002.md`

### Batch G1

- `どれにする？` -> **Chọn gì đây?**
- `はじめから` -> **Bắt đầu**
- `パスワード` -> **Mật khẩu**

### Batch G2

- `今からやるよ` -> **Bắt đầu thôi!**
- visible VS/rule graphics:
  - `ルールをせつめいするよ` -> **Luật chơi**
  - `２本先取だよ` -> **Thắng 2**
  - `ゲームの時間は勝つまでだよ` -> **Đến khi thắng**

### Batch G3

- `勝ち` -> **Thắng**
- lose-result graphic -> **Thua**
- Continue -> **Tiếp tục**
- quit story -> **Hủy / Thoát** after exact context confirmation
- ending/chapter/large title cards

The descriptor block at approximately `0x286B4..0x287FC` names these screens but is **not the actual visible retail asset**.

Do not patch the descriptor text and claim the graphic is translated.

## Latest editorial translation pass

The release-intent source count remains **1,018** because no new player-facing Japanese source rows were proven.

New second-pass work:

- `translation/editorial/tone_consistency_pass05_story_mid.csv`: **32** Story Batch 02 revisions;
- `translation/editorial/fortune_naturalness_pass01.csv`: **24** Fortune revisions;
- `translation/editorial/quiz_naturalness_pass02.csv`: **36** Maruko Q Batch 02 revisions.

The latest Quiz pass also corrects several source-faithfulness issues, including `心にうたれ`, `しるよしもない`, and `だがし屋`.

These are editorial improvements to already-proven source rows, not new source-row discoveries. See `translation/EDITORIAL_PROGRESS.md`.

## UI / game-choice pass

The game-choice/setup layer now has a dedicated polish + compact-runtime pass.

Files:

- `translation/editorial/ui_menu_naturalness_pass01.csv`: **31** existing rows refined;
- `translation/runtime/ui_choices_compact_v1.csv`: compact fixed-field candidates and explicit expansion-required fields.

Key UI conventions are now:

- **Dễ / Vừa / Khó**
- **Chơi / CPU / Nghỉ**
- **Màn**
- **Bấm START**
- **Tiếp tục câu đố?** / runtime **Tiếp tục?**
- **Có / Không** in the meaning layer; `Không` is not shortened to informal `Ko` merely to fit.

Release-intent source-row count remains **1,018**.

## Unified game-flow UI wording

Added:

- `translation/editorial/ui_choice_flow_pass02.csv`
- `translation/runtime/graphics_ui_labels_v1.csv`

The recurring UI vocabulary is now frozen around:

**Bắt đầu / Mật khẩu / Tiếp tục / Thoát / Có / Không / Dễ / Vừa / Khó / Chơi / CPU / Nghỉ / Thắng / Thua / Kết thúc**

`やめる` is resolved to **Thoát** for the Story Mode quit context.

This does not create a new runtime build and does not change the **1,018** proven release-intent source-row count.

## Auxiliary UI pass

Added:

- `translation/editorial/ui_auxiliary_pass03.csv`: **24** existing UI rows refined;
- `translation/runtime/ui_auxiliary_compact_v2.csv`: compact runtime candidates for karaoke start, quiz results, and minigame controls;
- `translation/UI_GLOSSARY_VI.md`: canonical UI wording authority.

Current canonical UI language now covers the main menu, game-flow choices, match setup, difficulty, controllers, minigame controls, quiz results, karaoke start options, result labels, and title/intro wording.

Release-intent source-row count remains **1,018**.

## Editorial / runtime rules

- keep `vi_full` fully accented and meaning-first;
- keep compact runtime candidates separate;
- preserve the school/family-comedy tone;
- preserve source identity/control bytes;
- do not translate scanner noise to inflate progress;
- graphics/tilemap is a separate layer from direct text;
- no Runtime PASS without user screenshot/gameplay evidence;
- user prefers fewer, larger tests.

## Next work

1. reverse actual Graphics Batch G1 asset paths;
2. determine raw tiles vs tilemap vs compressed graphics vs alternate renderer;
3. make one high-information graphics probe or one coherent graphics batch on top of Build 035;
4. then proceed to G2 and G3;
5. update `HANDOFF_CURRENT.md` whenever a new asset path/build checkpoint is proven.
