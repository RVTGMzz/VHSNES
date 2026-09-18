# HANDOFF CURRENT — Chibi Maruko-chan SNES Việt hóa

Updated: 2026-09-18 +07  
Branch: `chibi-maruko-bootstrap-01`  
Repo: `ronvotri/Viet-Hoa-SNES`

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
- small added credit: **Việt hóa bởi VôtriValley**

Preserve the original publisher/production copyright artwork. The VôtriValley line is an additional localization credit, not a replacement copyright.

See `docs/GRAPHICS_G0_TITLE_SCREEN_PLAN.md`.

Actual title asset path is still **UNPROVEN**; no ROM write or Runtime PASS claim yet.

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
