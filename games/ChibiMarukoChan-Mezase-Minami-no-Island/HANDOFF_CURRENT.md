# HANDOFF CURRENT — Chibi Maruko-chan SNES Việt hóa

Updated: 2026-09-16 +07
Branch: `chibi-maruko-bootstrap-01`
Repo: `ronvotri/Viet-Hoa-SNES`

## Current milestone

Two tracks continue in parallel:

1. meaning-first Vietnamese translation;
2. renderer/font/graphics reverse.

Probe 006 screenshot already runtime-proved the visible-menu path as:

```text
2-byte game code -> 16-bit glyph ID -> 12x12 raw 1bpp bitmap
```

The exact first line `TĐST1234` appeared in game, proving that a custom-drawn Vietnamese `Đ` can render through this path.

**Current runtime test is now Probe 007**, which installs the first corpus-derived Vietnamese codepage and a multi-glyph Vietnamese font bank. Runtime screenshot is still pending.

Do not infer that every graphics/text subsystem uses this same renderer.

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

Full reverse note: `docs/REVERSE_FONT_001.md`.

Visible-menu parser: file `0x283D8`, CPU `$85:83D8`.

Per-lead mapping pointer table: file `0x29756`, CPU `$85:9756`.

Renderer: file `0x28E7B`, CPU `$85:8E7B`.

Font page pointer table: file `0x295EE`, CPU `$85:95EE`.

Ten raw 1bpp 128x128 pages:

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

Each page contains a 10x10 logical grid of **12x12 glyph cells**.

Glyph ID format:

```text
high byte = font page 0..9
low byte  = cell index 0..99
```

## Probe history

### Probe 002 — RUNTIME FAIL

Raw 1-byte ASCII froze before the visible menu.

### Probe 003 — BOOT PASS / GLYPH IDENTITY FAIL

Full-width `ＴＥＳＴ１２３４` kept two-byte framing, but `Ｅ` rendered as zero.

### Probe 004 — RUNTIME COVERAGE MAP PASS

Unsupported full-width Latin codes were shown to map to glyph zero.

### Probe 005 — superseded

No separate runtime test needed after Probe 006 proved mapping + bitmap together.

### Probe 006 — CUSTOM GLYPH RUNTIME PASS

Tool: `tools/probe_visible_menu_006_custom_glyph.py`.

Custom slot `0x0963` received a 12x12 `Đ`, and the `Ｅ` code was remapped to that slot. User screenshot showed exactly:

```text
TĐST1234
```

Visible-menu custom glyph rendering is therefore runtime-proven.

## Vietnamese Codepage V1

Full note: `docs/VI_CODEPAGE_V1.md`.

Files:

- `translation/codepage/vi_codepage_v1.csv`
- `translation/codepage/vi_glyphs_v1.json`

Architecture:

- dedicated valid Shift-JIS lead byte: `0x84`
- clean lead pointer: CPU `$85:9A74`
- mapping table file base: `0x29A74`
- entry formula: `0x29A74 + (trail - 0x40) * 2`
- trail `0x7F` deliberately skipped

Current conservative direct-text scan has **zero decoded lead-0x84 characters**, which is why this lead is reserved for the Vietnamese codepage.

V1 inventory:

- **160 Unicode characters**
- full A-Z / a-z and digits
- corpus punctuation
- Vietnamese precomposed letters currently needed by the 1,018-row meaning layer
- `ñ` for `Señorita`
- a few extra uppercase accented letters used by Probe 007

Glyph allocation audit:

- 133 blank font cells found
- `0x022D` is blank but already referenced
- **132 conservatively safe blank cells** remain after reference audit
- V1 uses **121 custom visual glyphs**
- **11 audited blank slots remain reserved**
- Probe 006's proven `Đ` slot `0x0963` is retained

The compact glyph file stores each custom 12x12 bitmap as exactly 18 bytes / 144 bits. No external font file is needed by the build tool.

Typography is still a first functional pass and is not frozen until runtime screenshots confirm readability.

## Probe 007 — CURRENT RUNTIME TEST

Tool: `tools/probe_visible_menu_007_vi_codepage.py`.

Probe 007 starts from CLEAN ROM and installs the entire V1 mapping/glyph bank, then changes only the first six known visible menu string spans while preserving their exact two-byte unit counts.

Expected rows:

```text
ĐẦY ĐỦ!!
được!
CÓ DẤU!!
Việt
Maruko?
Ổn rồi
```

Static checkpoint PASS:

- codepage entries: 160
- custom visual glyphs: 121
- lead `0x84` pointer identity: PASS
- custom blank/reuse audit: PASS
- six source identities: PASS
- exact two-byte unit preservation: PASS
- diff-surface gate: PASS
- SNES checksum/complement: PASS
- checksum `0xB46C`
- complement `0x4B93`
- SHA-1 `9d890f1d00af6d893dcf07174ea66f8954c30382`
- SHA-256 `e3a9e1555f3bb85ac326a47bd610e6fd9cfa4e1428666fd99bc0276c1456e46a`

**Runtime status: PENDING screenshot.**

Do not call V1 runtime-proven until the user screenshot confirms the intended Vietnamese rows and shows which glyphs need typography correction.

## NEXT HIGH-VALUE WORK

If Probe 007 renders all six rows recognizably:

1. freeze V1 encoding semantics;
2. correct any ambiguous 12x12 glyph shapes revealed by screenshot, without changing code assignments unnecessarily;
3. build a guarded real Vietnamese main-menu candidate from the meaning layer;
4. begin runtime-fit work for translated direct-text banks, with source identity/control preservation;
5. continue graphics/tilemap reverse separately for `どれにする？`, Start, Password, Continue, ending family.

If Probe 007 freezes or corrupts unrelated text:

1. do not blame the bitmap layer already proven by Probe 006;
2. isolate whether lead `0x84` or a specific mapping/trail causes the failure;
3. binary-split the codepage installation while keeping exact source-unit counts.

## Frozen workflow

Use Gaia Master-style guardrails, not Gaia Master hardware assumptions.

Always separate:

- source meaning translation;
- runtime candidate/layout;
- font/codepage;
- graphics/tilemap text.

Do not call whole-game Runtime PASS from a subsystem probe. Runtime claims must state exactly what screenshot evidence proved.
