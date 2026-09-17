# Translation progress — Chibi Maruko-chan

Updated: 2026-09-18 +07
Branch: `chibi-maruko-bootstrap-01`

## Meaning-first Vietnamese source layer

Current committed **player-facing / release-intent** translated rows:

- `translation/source/seed_known_strings.csv`: 10
- `translation/source/main_menu_vi.csv`: 10
- Story Batch 01: 126
- Story Batch 02: 126
- Story Batch 03: 84
- `translation/source/credits_vi.csv`: 19
- `translation/source/rules_tutorial_vi.csv`: 2
- Maruko Q Batch 01: 74
- Maruko Q Batch 02: 129
- Maruko Q Batch 03: 178
- Maruko Fortune / `まるこみくじ` Batch 01: 157
- Minigame UI Batch 01: 52
- Karaoke Batch 01: 28
- Stage-name Batch 01: 15
- Quiz misc/result UI: 8
- **total release-intent meaning rows: 1,018**

Additional reverse/reference material:

- `translation/source/internal_debug_reference_vi.csv`: 10 translated internal QA/debug rows, **excluded from the 1,018 release-intent count**
- `translation/source/graphics_text_targets_vi.csv`: visual-text targets/hypotheses for later graphics/tilemap work, not direct-text rows

These counts are source-translation rows, NOT whole-game completion percentage. Scanner output still contains false positives, split strings, control/layout data, and numeric/count artifacts.

## Main story

The coherent direct-text story arc is translated approximately from `0x181CC .. 0x1DE81`, through the currently discovered visible ending sequence.

Tone remains frozen in `translation/STYLE_GUIDE_VI.md`: cute school/family comedy, not combat RPG.

Editorial polish has now explicitly reviewed 100 row-revisions/passes across story, quiz, and karaoke. See `translation/EDITORIAL_PROGRESS.md`.

## Maruko Q

The large coherent quiz banks are translated through the currently discovered direct-text end at approximately `0x368D8`.

- Batch 03: `0x31D47 .. 0x33F98`
- Batch 01: `0x34009 .. 0x34F3E`
- Batch 02: `0x34F7B .. 0x368D8`

Raw-ROM recovery is required whenever the conservative scanner starts inside a full-width digit/Latin character or omits a short numeric field.

## Maruko Fortune / `まるこみくじ` — Batch 01

Range approximately `0x2BD28 .. 0x2CB92`.

Files:

- `translation/source/fortune_batch01_part1_vi.csv`
- `translation/source/fortune_batch01_part2_vi.csv`
- `translation/source/fortune_batch01_part3_vi.csv`

Translated headings, wish/money/romance/study fortunes, general advice, lucky items, lucky numbers, and lucky colors.

## Minigame UI — Batch 01

File: `translation/source/minigame_ui_batch01_vi.csv`

Range approximately `0x288C2 .. 0x28C40`.

Translated ball-throwing, paint/dryer, and pool/pushing rules; controls; rounds-to-win; CPU difficulty; game duration; player 1–4 assignment/status; controller type; stage selector; stage digits `0..9`.

## Karaoke — Batch 01

Files:

- `translation/source/karaoke_batch01_vi.csv`
- `translation/source/karaoke_batch01_singable_v1_vi.csv`

The karaoke text has a meaning-first Vietnamese translation plus a complete 28-row singable V1 draft. Singable V1 remains timing/layout-unproven and does not replace `vi_full`.

## Stage-name Batch 01

File: `translation/source/stage_names_batch01_vi.csv`

Translated 15 stage/title strings. Runtime layout path is not yet audited.

## Quiz misc/result UI

File: `translation/source/quiz_ui_misc_vi.csv`

Translated dynamic `Câu số` labels, full-clear congratulations, question count, answer count, correct-answer rate, first-try correct count, and the `Có` choice paired with the existing `Không` seed.

## Graphics / tilemap translation targets

File: `translation/source/graphics_text_targets_vi.csv`.

Known targets include:

- visible pink heading `どれにする？` → `Chọn gì đây?`;
- `はじめから` → `Bắt đầu`;
- `パスワード` → `Mật khẩu`;
- `今からやるよ` → `Bắt đầu thôi!` pending exact on-screen context;
- `ＶＳ` → `VS`;
- `コンティニュー` → `Tiếp tục`;
- `エンディング` → `Kết thúc`.

`どれにする？` is visually verified but its asset/storage path is still unresolved. Simple CP932/glyph-ID/interleaved/tilemap searches did not find an exact storage sequence.

## Editorial rules

- `vi_full` stays fully accented and meaning-first;
- do not shorten source translation to current ROM/font limits;
- school/minigame competition uses `thi`, `thi đấu`, `so tài`, `vượt qua` rather than combat-heavy language;
- Maruo's `ズバリ` stays around `Nói thẳng ra!`;
- Hanawa keeps `Hey`, `baby`, `señorita` where natural;
- narrator stays dry and lightly teasing;
- suspicious scanner fragments are verified against raw ROM before translation.

## Runtime status

The pre-GBA Vietnamese font/codepage baseline remains Build 023 / Probe 019 state. The Golden Sun GBA donor experiment was rejected for Chibi and is not part of current runtime work.

### Build 024 — compact Vietnamese main menu

Runtime candidates: `translation/runtime/main_menu_compact_v1.csv`

Builder: `tools/build_main_menu_compact_v1.py`

Ten direct mode-selection menu fields now have guarded exact-fit Vietnamese runtime labels on top of Build 023:

- `Truyện`
- `Đấu`
- `Đấu đội`
- `M.Q`
- `Tập vẽ`
- `Bói`
- `Hát`
- `Âm`
- `ST`
- `Mono`

The fuller meanings remain in `translation/source/main_menu_vi.csv`. These compact forms are fixed-field runtime candidates, not a rewrite of `vi_full`.

Build 024 static facts:

- SHA-1 `9616e9937e0cfbd3b5294bbf7beff4dd4725301a`
- SHA-256 `4dc1ca459a4c04558bc421937ee6110b286fe19a9e94956b40e797777e4d863e`
- checksum `0x9969`, complement `0x6696`
- 10/10 field-fit PASS
- diff surface limited to ten menu text spans plus checksum/complement
- Runtime PASS: **not yet**, pending user gameplay/screenshot confirmation.

No bulk Story / Quiz / Fortune / Minigame / Karaoke / Credits runtime insertion has been declared yet. Those require guarded control-byte-aware insertion batches.

## Next translation / runtime work

The currently proven large coherent direct-text banks are meaning-covered. Do **not** inflate the untranslated count using binary-looking CP932 false positives.

Next high-value work:

1. validate Build 024 mode-selection menu when convenient;
2. build the first guarded story/dialogue insertion batch while preserving control bytes;
3. continue editorial naturalness passes on remaining story/quiz text;
4. trace `どれにする？` plus Start / Password / Continue / ending graphics paths;
5. later audit karaoke timing/singability in runtime.
