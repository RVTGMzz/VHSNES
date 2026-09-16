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

Committed meaning-layer rows: **1,018**.

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

Main story direct-text arc is translated approximately `0x181CC .. 0x1DE81`, through the current visible ending sequence.

The currently discovered coherent Maruko Q banks are translated through approximately `0x368D8`.

Maruko Fortune / `まるこみくじ` is translated approximately `0x2BD28 .. 0x2CB92`, including wish/money/romance/study fortunes, advice, lucky numbers, and lucky colors.

### Minigame UI Batch 01

File: `translation/source/minigame_ui_batch01_vi.csv`

Range approximately `0x288C2 .. 0x28C40`.

Covers ball, paint/dryer, and pool minigame rules; controls; rounds-to-win; CPU difficulty; match duration; player slots; controller type; stage selector; stage digits.

Raw ROM corrections include `１ゲームの時間`, `１本..５本`, both `１８０秒` fields, `プレイヤー１..４`, and stage digits `０..９`.

### Karaoke Batch 01

File: `translation/source/karaoke_batch01_vi.csv`

Range approximately `0x2B380 .. 0x2B76E`.

Meaning-first translation of the `針切じいさんのロケンロール` song-like text is committed. This is **not** yet a singable lyric adaptation. Rhythm, syllable count, and timing require a later dedicated pass.

Start options near `0x2B7C9` / `0x2B7EF` remain in `seed_known_strings.csv`; they were not duplicated.

### Stage-name Batch 01

File: `translation/source/stage_names_batch01_vi.csv`

Range approximately `0x2CBAD .. 0x2CD5F`.

15 stage/title strings translated, including wave/ring/park stages, paint stages at Mitsuya/festival stall/mansion/department store/school, and playful square/circle names.

Runtime layout path for these stage names is not yet audited.

### Quiz misc/result UI

File: `translation/source/quiz_ui_misc_vi.csv`

Player-facing quiz UI translated around `0x3153A` and `0x31C52 .. 0x31D2F`: dynamic question-number labels, full-clear congratulations, question count, answer count, correct-answer rate, first-try correct count, and the `Có` option paired with the existing `Không` seed.

Raw ROM confirms a trailing `回` counter after `一発で正解したのは`; the conservative scanner split before it.

No Story / Quiz / Fortune / Minigame / Karaoke / Credits batch has been bulk-patched into ROM.

### NEXT TRANSLATION TARGET

Audit direct UI/demo strings around `0x2865E .. 0x28817` next. This region contains descriptions such as start/password screen, conversation demo, win/loss demo, continue screen, story-exit screen, final victory demo, and ending. It may be a hidden debug/development index rather than normal player-facing UI, so translate only after classifying what is actually displayed at runtime.

Then continue scanning only coherent direct-text islands. Do not promote binary-looking scanner candidates into translation rows without evidence.

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
