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

Committed meaning-layer rows: **915**.

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
- Maruko Fortune / `まるこみくじ` Batch 01: 157

Main story direct-text arc is translated approximately `0x181CC .. 0x1DE81`, through the current visible ending sequence.

### Maruko Q coverage

The currently discovered coherent direct quiz banks are translated through approximately `0x368D8`.

Raw-ROM recovery is mandatory when the conservative scanner starts inside a full-width digit/Latin character or omits a short field.

### Maruko Fortune / `まるこみくじ` Batch 01

Range approximately `0x2BD28 .. 0x2CB92`.

Files:

- `translation/source/fortune_batch01_part1_vi.csv`
- `translation/source/fortune_batch01_part2_vi.csv`
- `translation/source/fortune_batch01_part3_vi.csv`

Translated: headings, wish fortunes, money fortunes, romance fortunes, study fortunes, general advice, lucky items, lucky numbers, and lucky colors.

Raw-ROM recovery corrected important scanner misses:

- `４人集めてみて` was mis-scanned as `S人集めてみて`; raw ROM proves full-width `４`;
- digits `０..９` are direct short fields omitted by the scanner;
- large lucky-number fields recovered directly: `１６，７７７，２１６`, `１，０００，０００`, `１３０，０００，０００`.

No Story / Quiz / Fortune / Credits batch has been bulk-patched into ROM.

### NEXT TRANSLATION TARGET

Translate the coherent player-facing minigame rules/config region around `0x288C2 .. 0x28BFF` next.

It includes ball-throwing rules, paint/dryer rules, pool/pushing rules, controls, rounds-to-win, CPU strength, game time, player/controller assignment, and stage selection.

Raw ROM already shows short fields that the scanner partially misses, including `１ゲームの時間`, `１本..５本`, and `１８０秒`. Recover these directly instead of guessing.

After that, audit karaoke/song-like text around `0x2B000` separately because it may have different layout/runtime behavior.

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
