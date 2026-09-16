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

Committed meaning-layer rows: **758**.

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

Main story direct-text arc is translated approximately `0x181CC .. 0x1DE81`, through the current visible ending sequence.

### Maruko Q coverage

- Batch 03 covers the earlier bank `0x31D47 .. 0x33F98`, with its last explanation continuing into the already translated `0x34009` row.
- Batch 01 covers `0x34009 .. 0x34F3E`.
- Batch 02 covers `0x34F7B .. 0x368D8`.

Batch 03 files:

- `translation/source/quiz_batch03_part1_vi.csv`
- `translation/source/quiz_batch03_part2_vi.csv`
- `translation/source/quiz_batch03_part3_vi.csv`

Raw-ROM recovery in Batch 03 corrected scanner omissions/splits instead of guessing. Proven fields include Maruko grade 3 / blood type A / age 9; birthday choices `5/8`, `4/23`, `10/1`; allowance choices `30`, `1,000,000`, `50` yen; Tomozou `76`; Hiroshi `40`; Sumire `40`; older sister grade 6; Ono's 3rd-semester transfer; class `3-4`; full-width `B` in `B級男子トリオ`; and the full `かもめ第３小学校` choice.

No Story / Quiz / Credits batch has been bulk-patched into ROM.

### NEXT TRANSLATION TARGET

The currently discovered coherent Maruko Q banks are now translated through `0x368D8`.

Move next to other coherent direct-text subsystems, auditing each separately:

1. fortune / `まるこみくじ` message bank around `0x2C000`;
2. karaoke / song-like text around `0x2B000`;
3. remaining menu/tutorial strings around `0x2865E .. 0x289xx`.

Do not interpret binary-looking scanner candidates in unrelated regions as real text without evidence.

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

Probe 005 changes first menu field to `ＴＥＳＴ１２３４` and changes the `Ｅ` mapping at `0x298AA` from `0x0000` to A's glyph `0x0517`. Expected runtime line: `TAST1234`. Static gates PASS; screenshot is still pending. Do not call this mapping behavior runtime-proven until screenshot evidence confirms it.

If Probe 005 is confirmed, next technical task is glyph-id -> bitmap reverse, safe slot selection, then one custom Vietnamese glyph probe (`Đ` or `ế`).

## Frozen workflow

Use Gaia Master-style guardrails, not Gaia Master hardware assumptions. Keep source meaning, runtime candidate/layout, font/codepage, and graphic/tilemap text as separate layers. Do not call Runtime PASS without gameplay screenshot evidence.
