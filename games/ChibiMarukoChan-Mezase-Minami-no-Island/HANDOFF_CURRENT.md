# HANDOFF CURRENT — Chibi Maruko-chan SNES Việt hóa

Updated: 2026-09-16 +07
Branch: `chibi-maruko-bootstrap-01`
Repo: `ronvotri/Viet-Hoa-SNES`

## Current milestone

Two tracks continue in parallel:

1. meaning-first Vietnamese translation;
2. renderer/font/graphics reverse.

**Major new runtime proof:** Probe 006 screenshot shows exact `TĐST1234` on the visible main menu. The visible menu path is now runtime-proven as:

```text
2-byte game code -> 16-bit glyph ID -> 12x12 raw 1bpp bitmap
```

This proves a custom-drawn Vietnamese glyph can render in game.

Do not infer that every graphics/text system uses this same renderer.

## Canonical clean ROM contract

- size `0x200000` / 2 MiB
- SHA-1 `08a2415362f69788ec76b1a36044dc1f1a5f2ea1`
- SHA-256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`
- internal title `RS051 CHIBIMARUKOCHAN`
- LoROM / FastROM
- internal header file `0x7FC0`
- no copier header
- clean checksum `0x1115`, complement `0xEEEA`

Never patch an unknown or already modified ROM.

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

Additional reverse/reference rows excluded from that count:

- `translation/source/internal_debug_reference_vi.csv`: 10 internal QA/debug rows
- `translation/source/graphics_text_targets_vi.csv`: graphics/tilemap targets/hypotheses

Meaning coverage reached:

- main direct-text story: approx `0x181CC .. 0x1DE81`
- Maruko Q coherent banks: through approx `0x368D8`
- Fortune / `まるこみくじ`: approx `0x2BD28 .. 0x2CB92`
- minigame setup/rules: approx `0x288C2 .. 0x28C40`
- karaoke lyric-like bank: approx `0x2B380 .. 0x2B76E`
- stage names: approx `0x2CBAD .. 0x2CD5F`
- quiz misc/result UI: around `0x3153A` and `0x31C52 .. 0x31D2F`

Tone is cute school/family comedy, not combat RPG. Keep `vi_full` natural and fully accented. Prefer `thi`, `thi đấu`, `so tài`, `vượt qua`; Maruo `ズバリ` stays around `Nói thẳng ra!`; Hanawa retains `Hey` / `baby` / `Señorita` when natural; narrator stays dry and lightly teasing.

No bulk Story / Quiz / Fortune / Minigame / Karaoke / Credits translation has been patched into ROM yet.

## Direct-text audit

Audit doc: `docs/DIRECT_TEXT_COVERAGE_AUDIT_20260916.md`.

The large coherent retail-facing direct-text banks currently discovered by the conservative scanner are meaning-covered. Do not inflate untranslated counts with random CP932-decodable binary islands.

This is NOT a whole-game completion claim. Visible Japanese may still be graphics/tilemaps, compressed assets, alternate renderers, or dynamic UI.

## Internal QA/debug block

Range approx `0x2865E .. 0x287FC` is development/test navigation material, not normal retail dialogue. It reveals Start / Password / VS / win-loss demo / Continue / Story quit / final-win / ending screens. Keep those rows as reverse references only unless runtime evidence proves they are retail-visible.

## Graphics/tilemap targets

`translation/source/graphics_text_targets_vi.csv` currently includes:

- `どれにする？` -> `Chọn gì đây?` — visually verified, render path unknown
- `はじめから` -> `Bắt đầu` — inferred from QA block
- `パスワード` -> `Mật khẩu` — inferred
- `今からやるよ` -> `Bắt đầu thôi!` — inferred, exact context pending
- `ＶＳ` -> `VS` — inferred

Do not patch these until their actual render/assets are located.

## Main menu meaning layer

Preferred wording:

- `ストーリーモード` -> `Chế độ Cốt truyện`
- `対戦モード` -> `Thi đấu`
- `チーム対戦モード` -> `Thi đấu theo đội`
- `まるこＱ` -> `Maruko Q`
- `まるこペイント` -> `Maruko tập vẽ`
- `まるこみくじ` -> `Bói vui cùng Maruko`
- `針切カラオケ` -> `Karaoke`
- `サウンド` -> `Âm thanh`
- `ステレオ` -> `Stereo`
- `モノラル` -> `Mono`

## Renderer/font reverse — proven facts

Full technical note: `docs/REVERSE_FONT_001.md`.

### Parser / mapping

Visible-menu parser: file `0x283D8`, CPU `$85:83D8`.

Per-lead mapping pointer table: CPU `$85:9756`, file `0x29756`.

For lead byte `0x82`, table resolves to CPU `$85:9862`, file `0x29862`.

For full-width digit/Latin range beginning at `0x824F`:

```text
entry = 0x29880 + (trail - 0x4F) * 2
```

Examples:

- `０ -> 0x0000`
- `１..９ -> 0x0001..0x0009`
- `Ａ -> 0x0517`
- `Ｅ -> 0x0000`
- `Ｔ -> 0x0516`

Probe 004 runtime showed many unsupported full-width Latin letters map to glyph zero.

### Font bitmap

Renderer: CPU `$85:8E7B`, file `0x28E7B`.

Font page pointer table: CPU `$85:95EE`, file `0x295EE`.

Ten pages at file:

```text
0x128000
0x128800
0x129000
0x129800
0x12A000
0x12A800
0x12B000
0x12B800
0x12C000
0x12C800
```

Each page = raw **1bpp 128x128 bitmap**, `0x800` bytes, containing a 10x10 logical grid of **12x12 glyph cells**.

Glyph ID:

```text
high byte = page 0..9
low byte  = cell index 0..99
```

## Probe history

### Probe 002 — RUNTIME FAIL

Raw 1-byte ASCII across visible-menu fields froze before the menu. Do not use raw ASCII bulk patching.

### Probe 003 — BOOT PASS / GLYPH IDENTITY FAIL

Full-width `ＴＥＳＴ１２３４` preserved 2-byte framing and booted, but `Ｅ` rendered as zero/circle.

### Probe 004 — RUNTIME COVERAGE MAP PASS

Alphabet/digit map showed unsupported Latin codes become the actual zero glyph.

### Probe 005 — superseded by Probe 006

Probe 005 intended to remap `Ｅ` to A glyph and expect `TAST1234`. It is no longer necessary as a separate user test because Probe 006 proved the mapping layer and bitmap layer together.

### Probe 006 — CUSTOM GLYPH RUNTIME PASS

Tool: `tools/probe_visible_menu_006_custom_glyph.py`.

Static build from CLEAN ROM:

- source field preserved at 8 two-byte units
- `Ｅ` mapping redirected to glyph ID `0x0963`
- glyph `0x0963` was a conservatively audited blank slot
- a custom 12x12 uppercase Vietnamese `Đ` bitmap was written there
- checksum/complement rebuilt

Expected first line: `TĐST1234`.

User screenshot on 2026-09-16 shows exactly **`TĐST1234`** and normal menu rendering.

Therefore for this path:

```text
2-byte game code -> glyph ID -> custom 12x12 1bpp Vietnamese glyph
```

is **RUNTIME PASS**.

This is not yet a full Vietnamese font PASS or whole-game runtime PASS.

## NEXT HIGH-VALUE WORK

1. run a stronger global collision/reference audit before allocating dozens of glyph slots;
2. freeze a Chibi-specific Vietnamese codepage using safe 2-byte codes + safe 12x12 glyph cells;
3. generate the first real Vietnamese glyph set (`Đ/đ`, `Ă/ă`, `Â/â`, `Ê/ê`, `Ô/ô`, `Ơ/ơ`, `Ư/ư`, tone-marked vowels actually needed by source text);
4. build one multi-glyph real Vietnamese phrase probe on the visible menu;
5. only after screenshot proof, begin guarded runtime insertion of translated UI/text;
6. separately continue graphics/tilemap reverse for `どれにする？`, Start, Password, Continue, ending family.

## Frozen workflow

Use Gaia Master-style guardrails, not Gaia Master hardware assumptions.

Always separate:

- source meaning translation;
- runtime candidate/layout;
- font/codepage;
- graphics/tilemap text.

Do not call whole-game Runtime PASS from a subsystem probe. Runtime claims must state exactly what screenshot evidence proved.
