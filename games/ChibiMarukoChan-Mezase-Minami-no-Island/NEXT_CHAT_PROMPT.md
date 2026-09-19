Tiếp tục dự án Việt hóa **Chibi Maruko-chan SNES** từ repo `RVTGMzz/VHSNES`, branch `chibi-maruko-bootstrap-01`.


## AUTHORITATIVE CURRENT CHECKPOINT

Repo: `RVTGMzz/VHSNES`  
Branch: `chibi-maruko-bootstrap-01`

Do not restart G1.

G1 **Bắt đầu / Mật khẩu** is **Runtime PASS**. Exact retail asset:

`$82:AF23 record #8 -> $97:F95E (file 0x0BF95E) -> VRAM $7800`

- JP packed `0x1B4`
- output `0x3E0`
- VI packed `0x16A`
- probe changed **360** bytes
- SHA-1 `904435c61153fd7f41649ab25e8f50318d3ec72f`
- SHA-256 `16c2975f431edc74754b8b6ad9272b78e4cc37852df653d1581094efb5d15edb`
- checksum/complement `0x28CA / 0xD735`

Read `docs/G1_LABEL_ASSET_PROOF_009.md`.

`どれにする？` remains separate.

Continue G2 only:

`今からやるよ` -> **Bắt đầu thôi!**

Current reverse chain:

`Start -> A1 -> $80:E131 -> $80:E169 -> $88:8139 -> $88:CB4E -> group 4 -> school-front scene -> continue tracing overlay`

Read `docs/G2_REVERSE_CHECKPOINT_010.md`.

Rules:

- `0x286EA` is descriptor/QA evidence only; never patch it as the retail solution.
- `$9A:CB34` is rejected.
- do not call G2 asset proof until the actual retail source is decoded and tied to the execution path.
- do not call G2 Runtime PASS until user gameplay/screenshot confirms it.

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
- `games/ChibiMarukoChan-Mezase-Minami-no-Island/docs/G0_G1_ONE_COMMAND_PIPELINE_004.md`
- `games/ChibiMarukoChan-Mezase-Minami-no-Island/docs/G2_G3_GRAPHICS_REVERSE_PIPELINE_005.md`
- `games/ChibiMarukoChan-Mezase-Minami-no-Island/docs/GRAPHICS_BUILD_036_PIPELINE_006.md`
- `games/ChibiMarukoChan-Mezase-Minami-no-Island/docs/REFERENCE_VI_ROM_TECHNIQUES_001.md`
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

## One-command runners

Once the exact clean ROM is available, run:

```bash
python tools/run_g0_title_reverse_pipeline.py clean.sfc
python tools/run_g1_graphics_reverse_pipeline.py clean.sfc
```

Inspect the generated JSON summaries and G0 candidate PNGs before any write.

The GitHub static workflow is committed but no run/status has been observed yet, so do not claim CI PASS.

## Master graphics runner

When the exact clean ROM is available, prefer:

```bash
python tools/run_all_graphics_reverse.py clean.sfc
```

This generates one master summary spanning G0 through G3.

Do not patch based on ranking alone. Promote only a candidate with both path evidence and decoded retail-asset identity.

## Build 036 path after asset proof

Once an asset span is proven:

1. G1-G3: use `prepare_graphics_patch_bundle.py`;
2. G0 custom title: use `prepare_custom_graphics_patch_bundle.py`;
3. assemble fragments with `assemble_graphics_manifest.py`;
4. build with `build_036_graphics.py`;
5. require independent verifier PASS;
6. keep Runtime status UNTESTED until Ron confirms screenshots/gameplay.

Never truncate a replacement to fit. Use the fit planner; relocate/layout-change if replacement is larger.

## Reference-ROM fallback architecture

Use the three Vietnamese reference ROMs only as technique references.

If a proven Chibi graphics replacement exceeds the original span:

1. prefer a clean relocation plan over truncation;
2. evaluate free/expanded ROM space;
3. hook/upload only with exact guarded evidence;
4. preserve original execution flow and checksum.

For G0 only, if direct title replacement remains fragile after real trace, a pre-title localization splash modeled on the reset-trampoline architecture is allowed as fallback.

## Current G1 execution proof

Story selection is now statically traced through the retail main menu into the Story entry module:

`Story index 0 -> route A0 -> $70=A0 -> $80:D328 -> $88:F5F1 -> $85:E959`

The stage-curtain background is reproduced from `$82:AF23`. The two-choice logic is proven through `$1404` / `$1406`.

Continue only inside this proven module to identify the visible source representation of:

- `どれにする？`
- `はじめから`
- `パスワード`

Do not fall back to broad direct-text or raw-shape scans.

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

## G2 TARGETED TRACER NOW COMMITTED

Use `tools/trace_g2_start_flow.py` before any new broad scan.

Command:

```bash
python tools/trace_g2_start_flow.py clean.sfc \
  --json reports/generated/g2_start_flow.json
```

CI run #39 on commit `6c7026cf4b857c24e2efbeebac544cc71e055850` passed, including `selftest_g2_start_flow.py`.

Do not convert that CI pass into an asset/runtime claim. The next evidence gate is still the real clean-ROM trace around `$88:CB4E` / school-front.
