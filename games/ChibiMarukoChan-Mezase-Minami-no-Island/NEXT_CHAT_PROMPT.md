Tiếp tục dự án Việt hóa **Chibi Maruko-chan SNES** từ repo `ronvotri/Viet-Hoa-SNES`, branch `chibi-maruko-bootstrap-01`.

Đọc trước:

- `games/ChibiMarukoChan-Mezase-Minami-no-Island/HANDOFF_CURRENT.md`
- `games/ChibiMarukoChan-Mezase-Minami-no-Island/docs/RUNTIME_BUILD_035_CHECKPOINT.md`
- `games/ChibiMarukoChan-Mezase-Minami-no-Island/docs/GRAPHICS_TILEMAP_PASS_001_AUDIT.md`
- `games/ChibiMarukoChan-Mezase-Minami-no-Island/docs/HEADING_REVERSE_001.md`
- `games/ChibiMarukoChan-Mezase-Minami-no-Island/docs/HEADING_REVERSE_002.md`
- `games/ChibiMarukoChan-Mezase-Minami-no-Island/docs/G1_RENDER_PATH_TRACE_003.md`
- `games/ChibiMarukoChan-Mezase-Minami-no-Island/docs/G1_SHAPE_PROBE_004.md`
- `games/ChibiMarukoChan-Mezase-Minami-no-Island/docs/GRAPHICS_G0_TITLE_SCREEN_PLAN.md`
- `games/ChibiMarukoChan-Mezase-Minami-no-Island/docs/G0_BOOT_TITLE_TRACE_001.md`
- `games/ChibiMarukoChan-Mezase-Minami-no-Island/docs/G0_DMA_SOURCE_TRACE_002.md`
- `games/ChibiMarukoChan-Mezase-Minami-no-Island/docs/G0_WRAM_STAGING_TRACE_003.md`
- `games/ChibiMarukoChan-Mezase-Minami-no-Island/docs/GRAPHICS_ASSET_RENDER_PROBE_001.md`
- `games/ChibiMarukoChan-Mezase-Minami-no-Island/docs/UI_LOCALIZATION_COVERAGE_001.md`

Canonical clean ROM SHA1: `08a2415362f69788ec76b1a36044dc1f1a5f2ea1`.

## Current checkpoint

Latest large direct-text candidate is **Build 035**:

`Chibi_Maruko_Build_035_QUIZ01_CREDITS_PASS_READY.sfc`

Static identity:

- checksum `0x6547`
- complement `0x9AB8`
- SHA-1 `054380f9b452f245471e6309eb33c7486d581462`
- SHA-256 `f8fb662a9e1b8fc5a5ff689f690ceaf332055ed86983e52b476a78852e4fd58d`
- runtime status: **UNTESTED**

Do not commit ROMs to GitHub.

Build 035 already carries the large direct-text runtime chain: compact menu, 328 Story fields, Minigame UI/rules, Fortune, large Quiz/Maruko Q insertion, stage labels, karaoke direct candidates, credits labels, story hotfixes, and current font/codepage fixes.

Meaning-first layer remains **1,018 release-intent rows**. Keep `vi_full` canonical; compact runtime text is separate.

## Font status

Do not restart font reverse.

The Golden Sun GBA donor experiment was rejected for Chibi.

Build 034 statically repaired issues reported after Build 033:

- T too thick;
- V thin;
- A/K/L thin;
- e thin/floating;
- g unclear/clipped;
- circumflex wrong orientation;
- dot-below disappearing.

These fixes are inherited by Build 035 but are **not yet runtime-release PASS**.

## Added Graphics Batch G0 — title / intro

The user wants the first title screen localized as well.

Frozen presentation:

- `ちびまる子ちゃん めざせ！南のアイランド！！` -> **Chibi Maruko-chan: Tiến tới đảo phương Nam!!**
- add small credit: **Việt hóa bởi VôtriValley**
- preserve original publisher/copyright attribution.

Reverse the actual title-screen graphics path before writing; do not assume the 12x12 direct-text renderer.

## Frozen UI wording before graphics insertion

Read:

- `translation/editorial/ui_choice_flow_pass02.csv`
- `translation/runtime/graphics_ui_labels_v1.csv`

Do not re-decide these labels unless new screen evidence changes the context.

Notably:

- `コンティニュー` -> **Tiếp tục**
- `やめる` -> **Thoát**
- `勝ち / 敗けた` -> **Thắng / Thua**
- `はい / いいえ` -> **Có / Không**

## Canonical UI wording authority

Read `translation/UI_GLOSSARY_VI.md` before changing any menu/setup/result wording.

Also read:

- `translation/editorial/ui_auxiliary_pass03.csv`
- `translation/runtime/ui_auxiliary_compact_v2.csv`

The UI glossary is now the preferred language authority for all proven player-facing UI. Only change it when new screen evidence proves a context mismatch.

## G0 title reverse first

Before G1, run `tools/trace_g0_title_boot.py` on the exact clean ROM.

Prioritize a boot-near routine only when it shows coherent:

- BG mode/tilemap/tile-data setup;
- VRAM address/data setup;
- DMA channel configuration;
- MDMA trigger.

Then prove the DMA source pointer and decode the source graphics before any title write.

Do not patch a high-scoring routine by score alone.

## Candidate asset visual proof

After a G0/G1 source pointer is proven, use `tools/render_snes_graphics_probe.py` to render:

- a 2bpp/4bpp contact sheet; or
- the candidate graphics through its raw 16-bit tilemap.

Use visual reproduction as confirmation, not as a substitute for pointer/DMA proof.

## G0 DMA source pipeline

After `trace_g0_title_boot.py`, run:

1. `reconstruct_dma_sources.py`;
2. `correlate_g0_dma_sources.py`;
3. render only the best ROM-backed tile-aligned candidates with `render_snes_graphics_probe.py`.

A candidate is not proven until decoded output reproduces the retail title and the boot/title setup reaches that transfer.

If DMA source points to WRAM or candidate ROM tiles do not reproduce the title, trace the decompressor/staging path next.

## WRAM fallback

If reconstructed G0 DMA source is `$7E/$7F`, run `trace_wram_staging_candidates.py`.

Do not resume blind ROM scanning. Prove:

`title setup -> staging/decompressor -> WRAM -> VRAM DMA -> visible title`

## Main task now: graphics/tilemap reverse

The remaining visible Japanese in screenshots is no longer a normal direct-text problem.

Important: the CP932 block around `0x286B4..0x287FC` only contains **internal screen/demo descriptors**, not the retail visible assets. Do not patch those descriptors and claim the graphics are translated.

Start with **Graphics Batch G1**:

1. `どれにする？` -> **Chọn gì đây?**
2. `はじめから` -> **Bắt đầu**
3. `パスワード` -> **Mật khẩu**

Then G2:

- `今からやるよ` -> **Bắt đầu thôi!**
- VS/rule graphics:
  - `ルールをせつめいするよ` -> **Luật chơi**
  - `２本先取だよ` -> **Thắng 2**
  - `ゲームの時間は勝つまでだよ` -> **Đến khi thắng**

Then G3:

- `勝ち` -> **Thắng**
- lose result -> **Thua**
- Continue -> **Tiếp tục**
- quit-story -> **Hủy / Thoát** after exact context check
- ending/chapter/large title cards

For G1, determine whether the actual visible asset uses raw 2bpp/4bpp tiles, tilemap composition, compressed graphics, or another renderer. Do not guess offsets.

A second read-only layer now also exists:

- `tools/scan_g1_shape_fingerprints.py`
- `tools/correlate_g1_evidence.py`

Run these after the render tracer. The shape scanner searches visual fingerprints for all three G1 targets under raw 1bpp and SNES 2bpp/4bpp hypotheses; the correlator ranks clusters that are also reached by candidate pointer tables. Do not treat a shape hit alone as a patch offset.

A read-only tracer now exists at:

`tools/trace_g1_render_path.py`

It must be run on the exact clean ROM before making a G1 write. Use its xrefs, proven renderer calls, bank-`$85` VRAM/DMA sites, and pointer runs to establish a real screen-setup -> source-asset path. In the checkpoint that added this tool, the clean ROM/Build 035 binary was not available in the active runtime, so **no G1 asset offset has been proven yet** and **no G1 ROM patch exists yet**.

The pink `どれにする？` heading has already failed simple CP932/glyph-ID/interleaved/tilemap sequence searches. Continue from the existing reverse docs instead of restarting.

## Workflow guardrails

- exact clean-ROM identity;
- preserve source identity before writes;
- separate direct text, compact runtime text, font/codepage, and graphics/tilemap layers;
- dry-run/diff-surface/checksum gates;
- no broad scanner-noise translation;
- no Runtime PASS without screenshot/gameplay evidence;
- user prefers **fewer, larger tests**, so use one high-information probe or one coherent graphics batch where technically safe.

Continue directly with the graphics/tilemap investigation and update `HANDOFF_CURRENT.md` when a new asset path or build checkpoint is proven.
