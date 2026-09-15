# HANDOFF CURRENT — Chibi Maruko-chan SNES Việt hóa

Updated: 2026-09-16 +07
Branch: `chibi-maruko-bootstrap-01`
Repo: `ronvotri/Viet-Hoa-SNES`

## Current milestone

Two tracks are active in parallel:

1. **meaning-first Vietnamese translation** is now underway;
2. **visible-menu renderer/font reverse** continues independently.

Do not block translation work on font work. Do not write bulk Vietnamese into the ROM until the font/codepage path is runtime-proven.

## Canonical clean ROM contract

- size: `0x200000` (2 MiB)
- SHA-1: `08a2415362f69788ec76b1a36044dc1f1a5f2ea1`
- SHA-256: `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`
- internal title: `RS051 CHIBIMARUKOCHAN`
- header: LoROM / FastROM at file `0x7FC0`
- no copier header on canonical file
- stored/computed checksum: `0x1115`
- complement: `0xEEEA`

Never patch an unknown or already modified ROM.

## Proven text/source facts

Direct CP932/Shift-JIS-like text exists in ROM.

Scanner: `tools/scan_sjis_candidates.py`

Reproducible candidate counts with current scanner:

- whole ROM: 2,274 candidate runs
- focused range `0x18000..0x34000`: 889 candidate runs

These are candidates with false positives, split strings, and control/layout bytes. They are NOT translation coverage.

Frequently observed around text:

`00 0E xx 0F xx ...text... 81 6F 00`

Do not assign semantics to these control/marker bytes until proven.

## Vietnamese style — frozen direction

See `translation/STYLE_GUIDE_VI.md`.

Game tone is cute school/family comedy, not combat RPG.

Use friendly competition wording such as `thi`, `thi đấu`, `so tài`, `chơi theo đội` rather than unnecessarily martial terms.

Voice anchors:

- Maruko: casual, cheeky, childlike;
- Tama-chan: gentle, earnest;
- Maruo: pompous/formal, `ズバリ` anchored around `Nói thẳng ra!`;
- Hanawa: suave/comic, keep `Hey` / `baby` when appropriate;
- narrator: dry, lightly teasing;
- family adults: warm domestic comedy.

`vi_full` is meaning-first, fully accented Vietnamese and must not be shortened just to satisfy current ROM/font limitations.

## Translation progress

See `translation/TRANSLATION_PROGRESS.md`.

Committed meaning-layer rows:

- `translation/source/seed_known_strings.csv`: 10
- `translation/source/main_menu_vi.csv`: 10
- `translation/source/story_batch01_vi.csv`: 126
- total committed meaning-layer rows: **146**

Story Batch 01 covers approximately `0x181CC .. 0x1A5CA` and includes:

- school exchange-student announcement;
- Maruko/Tama-chan reactions;
- Maruo/Hanawa banter;
- Sakura-family scene;
- early representative-selection contests and win/loss reactions.

No Batch 01 story row has been patched into the ROM yet.

Next translation region: approximately `0x1A64F` onward. Continue coherent real dialogue and skip scanner garbage rather than guessing.

## Main menu meaning layer

Preferred Vietnamese wording is now:

- `ストーリーモード` → `Chế độ Cốt truyện`
- `対戦モード` → `Thi đấu`
- `チーム対戦モード` → `Thi đấu theo đội`
- `まるこＱ` → `Maruko Q`
- `まるこペイント` → `Maruko tập vẽ`
- `まるこみくじ` → `Bói vui cùng Maruko`
- `針切カラオケ` → `Karaoke` (compact label; nuance can be revisited)
- `サウンド` → `Âm thanh`
- `ステレオ` → `Stereo`
- `モノラル` → `Mono`

The pink heading `どれにする？` is visible and means roughly `Chọn gì đây?`, but it has NOT been found as the same direct CP932 text path. Treat as graphic/tilemap/other encoding until proven.

## Probe history

### Probe 002 — RUNTIME FAIL

Raw 1-byte ASCII across visible menu fields caused freeze before the normal menu.

Conclusion: do NOT use raw 1-byte ASCII for bulk menu/text patching.

### Probe 003 — BOOT PASS / GLYPH IDENTITY FAIL

First menu field changed to CP932 full-width `ＴＥＳＴ１２３４`, preserving 8 two-byte units.

Runtime screenshot:

- boot to menu: PASS
- framing/position preserved
- intended `Ｅ` (`82 64`) rendered as a zero/circle-like glyph

Conclusion: two-byte framing works for this path, but standard CP932 glyph identity is incomplete.

### Probe 004 — RUNTIME COVERAGE MAP PASS

Observed intended A–Z/digit probe approximately as:

- `ＡＢＣＤＥＦＧＨ` → `AB000000`
- `ＩＪＫＬＭ` → `I0KLM`
- `ＮＯＰＱＲＳＴＵ` → `00PQRST0`
- `ＶＷＸＹ` → `V000`
- `Ｚ０１２３４５` → `0012345`
- `６７８９ＡＢ` → `6789AB`

Here `0` is the actual digit-zero glyph, not blank pixels.

## Major static discovery — 0x82xx codepoint -> glyph-id table

A 16-bit little-endian table has been identified in CLEAN ROM.

For CP932 `0x82xx` full-width digits/Latin/hiragana range:

- base entry for `0x824F` (`０`) at file offset `0x29880`
- formula: `entry = 0x29880 + (trail - 0x4F) * 2`

Examples:

- `０` `0x824F` -> `0x0000`
- `１..９` -> `0x0001..0x0009`
- `Ａ` -> `0x0517`
- `Ｂ` -> `0x0705`
- `Ｃ` -> `0x0000`
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
- `Ｕ` -> `0x0000`
- `Ｖ` -> `0x020C`

Because digit `０` itself maps to glyph-id `0x0000`, unsupported Latin letters mapping to `0x0000` explains the visible zero glyphs in Probe 004.

Credits string `ＴＡＲＡＫＯ` supports the theory that only actually-authored Latin letters received dedicated glyph IDs.

## Probe 005 — CURRENT RUNTIME TEST

Tool: `tools/probe_visible_menu_005_map_entry.py`

Changes from CLEAN ROM only:

1. first menu field -> full-width `ＴＥＳＴ１２３４` (same 16 bytes / 8 two-byte units)
2. mapping entry for full-width `Ｅ` at `0x298AA`: `0x0000` -> `0x0517` (glyph-id used by `Ａ`)
3. checksum/complement update

Expected first line if mapping-table hypothesis is correct:

`TAST1234`

Static gates PASS. Runtime result still pending screenshot.

Do not call this mapping architecture runtime-proven until the user supplies Probe 005 screenshot evidence.

## FE4 / other SNES Vietnamese reference lesson

A Vietnamese Fire Emblem 4 ROM and public SNES translation sources were reviewed only as architectural references.

Useful lesson: successful SNES Vietnamese patches often define a game-specific internal codepage, custom glyph/font data, and sometimes width tables/VWF rather than forcing Unicode or assuming stock Japanese encodings.

Do NOT copy FE4 HiROM offsets, code, font formats, VWF assumptions, or other game-specific architecture into Chibi without proof.

Reference note: `docs/REFERENCE_FE4_VIETNAMESE_FONT.md`.

## Next technical task after Probe 005

If `TAST1234` appears exactly as predicted:

1. freeze the discovered codepoint -> glyph-id table behavior for this renderer path;
2. reverse glyph-id -> bitmap/font asset storage;
3. identify unused or safely repurposable glyph slots;
4. create ONE custom Vietnamese glyph probe, preferably `Đ` or `ế`;
5. only after it renders correctly, define the Chibi Vietnamese codepage and begin runtime insertion.

Do not brute-force more Latin letters unless new evidence requires it.

## Frozen workflow rule

Use Gaia Master-style guardrails, not Gaia Master hardware assumptions.

Always separate:

- source meaning translation;
- runtime candidate/layout;
- font/codepage work;
- graphics/tilemap text.

Do not call Runtime PASS without gameplay screenshot evidence.
