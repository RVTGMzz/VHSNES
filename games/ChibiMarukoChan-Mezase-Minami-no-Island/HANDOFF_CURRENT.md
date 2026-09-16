# HANDOFF CURRENT — Chibi Maruko-chan SNES Việt hóa

Updated: 2026-09-16 +07
Branch: `chibi-maruko-bootstrap-01`
Repo: `ronvotri/Viet-Hoa-SNES`

## Current rules

Two tracks run independently: meaning-first Vietnamese translation and renderer/font/graphics reverse. Do not block translation on font work. Do not bulk-write Vietnamese into ROM until the font/codepage path is runtime-proven.

Canonical clean ROM: size `0x200000`, SHA-1 `08a2415362f69788ec76b1a36044dc1f1a5f2ea1`, SHA-256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`, LoROM/FastROM, header `0x7FC0`, no copier header, checksum `0x1115`, complement `0xEEEA`. Never patch an unknown or already modified ROM.

Tone is cute school/family comedy, not combat RPG. Keep `vi_full` natural and fully accented. Maruo's `ズバリ` stays around `Nói thẳng ra!`; Hanawa keeps `Hey` / `baby` / `Señorita` when natural; narrator stays dry and lightly teasing. Prefer `thi`, `thi đấu`, `so tài`, `vượt qua` over unnecessarily martial wording.

## Translation progress

Detailed tracker: `translation/TRANSLATION_PROGRESS.md`.

Committed **release-intent meaning-layer rows: 1,018**.

Breakdown:

- seed: 10
- main menu: 10
- Story Batch 01: 126
- Story Batch 02: 126
- Story Batch 03: 84
- credits: 19
- rules/tutorial: 2
- Maruko Q Batch 01: 74
- Maruko Q Batch 02: 129
- Maruko Q Batch 03: 178
- Maruko Fortune Batch 01: 157
- Minigame UI Batch 01: 52
- Karaoke Batch 01: 28
- Stage-name Batch 01: 15
- Quiz misc/result UI: 8

Additional reverse/reference rows are **not** included in the 1,018 count:

- `translation/source/internal_debug_reference_vi.csv`: 10 internal QA/debug translations
- `translation/source/graphics_text_targets_vi.csv`: 5 graphics/tilemap translation targets/hypotheses

Main story direct-text arc is meaning-covered approximately `0x181CC .. 0x1DE81`.

Maruko Q coherent banks are meaning-covered through approximately `0x368D8`.

Fortune / `まるこみくじ` is meaning-covered approximately `0x2BD28 .. 0x2CB92`.

Minigame setup/rules are translated approximately `0x288C2 .. 0x28C40`.

Karaoke lyric-like bank is meaning-translated approximately `0x2B380 .. 0x2B76E`; singability/timing pass remains separate.

Stage names are translated approximately `0x2CBAD .. 0x2CD5F`.

Quiz misc/result UI is translated around `0x3153A` and `0x31C52 .. 0x31D2F`.

## Direct-text audit milestone

Audit doc: `docs/DIRECT_TEXT_COVERAGE_AUDIT_20260916.md`.

The remaining large coherent retail-facing direct-text banks currently discovered by the conservative scanner are meaning-covered. Do not treat random CP932-decodable binary islands elsewhere in the ROM as untranslated dialogue without evidence.

This is **not** a whole-game completion claim. Visible Japanese may still live in graphics/tilemaps, compressed assets, alternate renderers, or dynamic UI.

### Internal QA/debug block classified

Range approximately `0x2865E .. 0x287FC`.

Raw ROM resolves a development/test navigation block containing:

- `さくらプロへのビデオ出しは、８／３１です。皆さん、頑張りましょう！！`
- Start / Password screen description
- `今からやるよ` conversation demo description
- full-width `ＶＳ` demo description
- Maru-chan win/loss demos
- Continue screen
- Story Mode quit screen
- final-win demo
- ending

These 10 rows are translated in `internal_debug_reference_vi.csv` only for reverse-engineering. **Do not patch them into a normal release unless runtime evidence proves they are player-visible.**

The block is valuable because it reveals visual/graphics targets that are not present in the proven direct-text path.

## Graphics/tilemap translation targets

File: `translation/source/graphics_text_targets_vi.csv`.

Current targets:

- `どれにする？` → `Chọn gì đây?` — visually verified from user screenshot, render path still unknown
- `はじめから` → `Bắt đầu` — inferred from QA block
- `パスワード` → `Mật khẩu` — inferred from QA block
- `今からやるよ` → `Bắt đầu thôi!` — inferred, exact visible context must be verified
- `ＶＳ` → `VS` — inferred from QA block

## Main menu meaning layer

- `ストーリーモード` → `Chế độ Cốt truyện`
- `対戦モード` → `Thi đấu`
- `チーム対戦モード` → `Thi đấu theo đội`
- `まるこＱ` → `Maruko Q`
- `まるこペイント` → `Maruko tập vẽ`
- `まるこみくじ` → `Bói vui cùng Maruko`
- `針切カラオケ` → `Karaoke`
- `サウンド` → `Âm thanh`
- `ステレオ` → `Stereo`
- `モノラル` → `Mono`

## Renderer/font reverse

Probe 002 raw 1-byte ASCII: runtime FAIL, froze before menu.

Probe 003 full-width `ＴＥＳＴ１２３４`: boot PASS, but `Ｅ` rendered as zero-like glyph.

Probe 004 alphabet map: runtime shows many full-width Latin codes map to glyph-id zero.

Static mapping table discovered for CP932 `0x82xx`: base for `0x824F` (`０`) at file `0x29880`, entry formula `0x29880 + (trail - 0x4F) * 2`. Examples: `Ａ -> 0x0517`, `Ｅ -> 0x0000`, `Ｔ -> 0x0516`.

Probe 005 changes first menu field to `ＴＥＳＴ１２３４` and changes the `Ｅ` mapping at `0x298AA` from `0x0000` to A's glyph `0x0517`. Expected runtime line: `TAST1234`. Static gates PASS; screenshot is still pending. Do not call this mapping behavior runtime-proven until screenshot evidence confirms it.

## NEXT HIGH-VALUE WORK

1. locate/extract graphics or tilemaps for the Start / Password / Continue / ending family of screens revealed by the internal QA block;
2. locate the pink `どれにする？` render path;
3. continue static glyph-id -> bitmap/font reverse while Probe 005 runtime confirmation remains pending;
4. once font/codepage is proven, build one custom Vietnamese glyph probe (`Đ` or `ế`), then start runtime insertion.

## Frozen workflow

Use Gaia Master-style guardrails, not Gaia Master hardware assumptions. Keep source meaning, runtime candidate/layout, font/codepage, and graphics/tilemap text as separate layers. Do not call Runtime PASS without gameplay screenshot evidence.
