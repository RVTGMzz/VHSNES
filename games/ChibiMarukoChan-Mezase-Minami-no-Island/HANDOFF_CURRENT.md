# HANDOFF CURRENT — Chibi Maruko-chan SNES Việt hóa

Updated: 2026-09-16 +07
Branch: `chibi-maruko-bootstrap-01`
Repo: `ronvotri/Viet-Hoa-SNES`

## Current milestone

Two tracks run in parallel:

1. **meaning-first Vietnamese translation**;
2. **visible-menu renderer/font reverse**.

Do not block translation work on font work. Do not bulk-write Vietnamese into ROM until the font/codepage path is runtime-proven.

## Canonical clean ROM contract

- size: `0x200000` (2 MiB)
- SHA-1: `08a2415362f69788ec76b1a36044dc1f1a5f2ea1`
- SHA-256: `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`
- internal title: `RS051 CHIBIMARUKOCHAN`
- LoROM / FastROM header at file `0x7FC0`
- no copier header on canonical ROM
- stored/computed checksum: `0x1115`
- complement: `0xEEEA`

Never patch an unknown or already modified ROM.

## Proven source facts

Direct CP932/Shift-JIS-like text exists in ROM.

Scanner: `tools/scan_sjis_candidates.py`

Current scanner counts:

- whole ROM: 2,274 candidate runs
- focused `0x18000..0x34000`: 889 candidate runs

These are scanner candidates, NOT translation coverage. They include false positives, split strings, control/layout bytes, and unresolved count markers.

Frequently observed around text:

`00 0E xx 0F xx ...text... 81 6F 00`

Do not assign semantics to these control bytes without proof.

## Vietnamese style — frozen

See `translation/STYLE_GUIDE_VI.md`.

Tone is cute school/family comedy, not combat RPG.

Voice anchors:

- Maruko: casual, cheeky, childlike;
- Tama-chan: gentle, earnest;
- Maruo: pompous/formal; `ズバリ` → anchor around `Nói thẳng ra!`;
- Hanawa: theatrical/comic; retain `Hey`, `baby`, `Señorita` when natural;
- narrator: dry and lightly teasing;
- Sakura family: warm domestic comedy.

Competition wording should favor `thi`, `thi đấu`, `so tài`, `vượt qua`, `chơi theo đội` rather than martial language.

`vi_full` is the source of truth and stays fully accented/natural. Never shorten it merely to satisfy the current ROM/font.

## Translation progress

Detailed tracker: `translation/TRANSLATION_PROGRESS.md`.

Committed meaning-layer rows:

- seed known strings: 10
- visible main menu: 10
- Story Batch 01: 126
- Story Batch 02: 126, stored as 3 x 42-row audit-friendly files
- **total: 272 rows**

### Story Batch 01

Range approximately `0x181CC .. 0x1A5CA`.

Covers school exchange announcement, Maruko/Tama reactions, Maruo/Hanawa banter, Sakura-family scenes, and early representative-selection games.

### Story Batch 02

Range approximately `0x1A64F .. 0x1C61C`.

Files:

- `translation/source/story_batch02_part1_vi.csv`
- `translation/source/story_batch02_part2_vi.csv`
- `translation/source/story_batch02_part3_vi.csv`

Covers later selection rounds, Maruko's win/loss comedy, Maruo election jokes, Hanawa rose/`baby` banter, Tama passport gag, final-round rivalry, narrator punchlines, and family dinner jokes.

Scanner fragments such as `P/Q/R` before `人/回` are NOT treated as proven literals. They are translated conservatively from surrounding context and remain marked for source/runtime review.

No Batch 01/02 dialogue has been patched into ROM.

**Next translation region:** approximately `0x1C661` onward.

## Main menu meaning layer

Preferred wording:

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

Pink heading `どれにする？` ≈ `Chọn gì đây?`, but it is not proven to use the same direct text path. Treat as graphic/tilemap/other encoding until proven.

## Renderer/font reverse status

### Probe 002 — RUNTIME FAIL

Raw 1-byte ASCII across visible menu fields froze before the normal menu. Do not use raw ASCII bulk patching.

### Probe 003 — BOOT PASS / GLYPH IDENTITY FAIL

Full-width CP932 `ＴＥＳＴ１２３４` preserved 2-byte framing and booted, but intended `Ｅ` displayed as zero/circle.

### Probe 004 — RUNTIME COVERAGE MAP PASS

Many full-width Latin codepoints are structurally accepted but map to glyph-id zero. Missing letters therefore display as the actual digit-zero glyph rather than blank.

## Major static discovery — 0x82xx codepoint -> glyph-id table

A 16-bit little-endian mapping table exists in clean ROM.

For the CP932 `0x82xx` range:

- base entry for `0x824F` (`０`) at file offset `0x29880`
- `entry = 0x29880 + (trail - 0x4F) * 2`

Examples:

- `０` -> `0x0000`
- `１..９` -> `0x0001..0x0009`
- `Ａ` -> `0x0517`
- `Ｂ` -> `0x0705`
- `Ｅ` -> `0x0000`
- `Ｉ` -> `0x074B`
- `Ｋ` -> `0x0519`
- `Ｌ` -> `0x074C`
- `Ｍ` -> `0x0814`
- `Ｏ` -> `0x051A`
- `Ｐ` -> `0x0815`
- `Ｑ` -> `0x0216`
- `Ｒ` -> `0x0518`
- `Ｓ` -> `0x020D`
- `Ｔ` -> `0x0516`
- `Ｖ` -> `0x020C`

The credits string `ＴＡＲＡＫＯ` supports the theory that only authored Latin letters received dedicated glyph IDs.

## Probe 005 — CURRENT RUNTIME TEST

Tool: `tools/probe_visible_menu_005_map_entry.py`

Changes only:

1. first menu field → `ＴＥＳＴ１２３４`, same 8 two-byte units;
2. mapping entry for full-width `Ｅ` at `0x298AA`: `0x0000` → `0x0517` (A glyph);
3. checksum/complement.

Expected visible first line if mapping-table hypothesis is correct:

`TAST1234`

Static gates PASS. Runtime screenshot still pending.

If it appears exactly as predicted:

1. freeze codepoint → glyph-id behavior for this renderer path;
2. reverse glyph-id → bitmap/font storage;
3. identify safe unused/repurposable glyph slots;
4. make ONE Vietnamese glyph probe, preferably `Đ` or `ế`;
5. then define the Chibi Vietnamese codepage.

## Reference lesson from Vietnamese FE4 / other SNES work

Useful architectural lesson only: successful SNES translations often use a game-specific internal codepage, custom glyph/font data, and optionally width tables/VWF.

Do NOT copy FE4 HiROM offsets, font format, hooks, VWF logic, or any other game-specific assumption into Chibi without proof.

Reference note: `docs/REFERENCE_FE4_VIETNAMESE_FONT.md`.

## Frozen workflow rule

Use Gaia Master-style guardrails, not Gaia Master hardware assumptions.

Always separate:

- source meaning translation;
- runtime candidate/layout;
- font/codepage work;
- graphics/tilemap text.

Do not call Runtime PASS without gameplay screenshot evidence.
