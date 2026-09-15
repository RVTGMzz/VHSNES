# HANDOFF CURRENT — Chibi Maruko-chan SNES Việt hóa

Updated: 2026-09-16 +07
Branch: `chibi-maruko-bootstrap-01`
Repo: `ronvotri/Viet-Hoa-SNES`

## Current rules

Two tracks run independently: meaning-first Vietnamese translation and renderer/font reverse. Do not block translation on font work. Do not bulk-write Vietnamese into ROM until the font/codepage path is runtime-proven.

Canonical clean ROM: size `0x200000`, SHA-1 `08a2415362f69788ec76b1a36044dc1f1a5f2ea1`, SHA-256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`, LoROM/FastROM, header `0x7FC0`, no copier header, checksum `0x1115`, complement `0xEEEA`. Never patch an unknown or already modified ROM.

Tone is cute school/family comedy, not combat RPG. Keep `vi_full` natural and fully accented. Maruo's `ズバリ` stays around `Nói thẳng ra!`; Hanawa keeps `Hey` / `baby` / `Señorita` when natural; narrator stays dry and lightly teasing. Prefer `thi`, `thi đấu`, `so tài`, `vượt qua` over unnecessarily martial wording.

## Translation progress

Detailed tracker: `translation/TRANSLATION_PROGRESS.md`.

Committed meaning-layer rows: **580**.

- seed: 10
- main menu: 10
- Story Batch 01: 126
- Story Batch 02: 126
- Story Batch 03: 84
- credits: 19
- rules/tutorial: 2
- Maruko Q Batch 01: 74
- Maruko Q Batch 02: 129

Main story direct-text arc is translated approximately `0x181CC .. 0x1DE81`, through the current visible ending sequence.

Maruko Q Batch 01 covers `0x34009 .. 0x34F3E`.

Maruko Q Batch 02 covers `0x34F7B .. 0x368D8` in:

- `translation/source/quiz_batch02_part1_vi.csv`
- `translation/source/quiz_batch02_part2_vi.csv`
- `translation/source/quiz_batch02_part3_vi.csv`

Batch 02 raw-ROM recovery confirmed numeric/class fields that the scanner missed or split: Maruo birthday choices `12/31`, `12/19`, `3/3` with `12/31` correct; Maruo mother ages `49`, `44`, `34` with `49` correct; Yoshiko classes `6-2`, `5-3`, `6-5` with `6-2` correct; Maruko house choices `1`, `2`, `4` floors with one-story correct.

The coherent direct quiz sequence ends at `0x368D8`; do not treat following binary-looking scanner candidates as real quiz text.

### NEXT TRANSLATION TARGET

A coherent untranslated Maruko Q block remains at approximately `0x31D47 .. 0x34008`, at least 165 scanner candidates. It covers Maruko/Momoe, Maruko's birthday and allowance, Tomozo, grandmother, Hiroshi, Sumire, older sister, Ono, Kayoko, Kenta, Sugiyama, Buutaro's sister, Nagasawa family, and more. Translate this block next in audited chunks. Recover numeric/full-width fields from raw ROM instead of guessing scanner placeholders.

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

Pink heading `どれにする？` ≈ `Chọn gì đây?`, but its text path is not yet proven.

## Renderer/font reverse

Probe 002 raw 1-byte ASCII: runtime FAIL, froze before menu.

Probe 003 full-width `ＴＥＳＴ１２３４`: boot PASS, but `Ｅ` rendered as zero-like glyph.

Probe 004 alphabet map: runtime shows many full-width Latin codes map to glyph-id zero.

Static mapping table discovered for CP932 `0x82xx`: base for `0x824F` (`０`) at file `0x29880`, entry formula `0x29880 + (trail - 0x4F) * 2`. Examples: `Ａ -> 0x0517`, `Ｅ -> 0x0000`, `Ｔ -> 0x0516`.

Probe 005 changes first menu field to `ＴＥＳＴ１２３４` and changes the `Ｅ` mapping at `0x298AA` from `0x0000` to A's glyph `0x0517`. Expected runtime line: `TAST1234`. Static gates PASS; screenshot is still pending. Do not call this mapping behavior runtime-proven until the screenshot confirms it.

If Probe 005 is confirmed, next technical task is glyph-id -> bitmap reverse, safe slot selection, then one custom Vietnamese glyph probe (`Đ` or `ế`).

## Frozen workflow

Use Gaia Master-style guardrails, not Gaia Master hardware assumptions. Keep source meaning, runtime candidate/layout, font/codepage, and graphic/tilemap text as separate layers. Do not call Runtime PASS without gameplay screenshot evidence.
