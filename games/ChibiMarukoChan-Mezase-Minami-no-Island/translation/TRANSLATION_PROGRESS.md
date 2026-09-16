# Translation progress — Chibi Maruko-chan

Updated: 2026-09-16 +07
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
- `translation/source/graphics_text_targets_vi.csv`: 5 visual-text targets/hypotheses for later graphics/tilemap work, not direct-text rows

These counts are source-translation rows, NOT whole-game completion percentage. Scanner output still contains false positives, split strings, control/layout data, and numeric/count artifacts.

## Main story

The coherent direct-text story arc is translated approximately from `0x181CC .. 0x1DE81`, through the currently discovered visible ending sequence.

Tone remains frozen in `translation/STYLE_GUIDE_VI.md`: cute school/family comedy, not combat RPG.

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

Raw-ROM recovery corrected scanner omissions including full-width `４` in `４人集めてみて`, digits `０..９`, and large lucky-number fields such as `１６，７７７，２１６`, `１，０００，０００`, and `１３０，０００，０００`.

## Minigame UI — Batch 01

File: `translation/source/minigame_ui_batch01_vi.csv`

Range approximately `0x288C2 .. 0x28C40`.

Translated ball-throwing, paint/dryer, and pool/pushing rules; controls; rounds-to-win; CPU difficulty; game duration; player 1–4 assignment/status; controller type; stage selector; stage digits `0..9`.

Raw-ROM recovery fixed `１ゲームの時間`, `１本..５本`, both `１８０秒` fields, `プレイヤー１..４`, and stage digits that the scanner missed or entered mid-character.

## Karaoke — Batch 01

File: `translation/source/karaoke_batch01_vi.csv`

Range approximately `0x2B380 .. 0x2B76E`.

The `針切じいさんのロケンロール` song-like text now has a meaning-first Vietnamese translation. It is **not yet a singable lyric pass**. Rhythm, syllable count, and timing must be audited separately before runtime insertion.

The existing start options near `0x2B7C9` / `0x2B7EF` remain in `seed_known_strings.csv` and were not duplicated.

## Stage-name Batch 01

File: `translation/source/stage_names_batch01_vi.csv`

Range approximately `0x2CBAD .. 0x2CD5F`.

Translated 15 stage/title strings. These are meaning-first names; runtime layout path is not yet audited.

## Quiz misc/result UI

File: `translation/source/quiz_ui_misc_vi.csv`

Translated player-facing quiz UI around `0x3153A` and `0x31C52 .. 0x31D2F`: dynamic `Câu số` labels, full-clear congratulations, number of questions, answer count, correct-answer rate, first-try correct count, and the `Có` choice paired with the existing `Không` seed.

## Internal QA / debug block audit

Range approximately `0x2865E .. 0x287FC`.

File: `translation/source/internal_debug_reference_vi.csv`.

Raw ROM resolves this block as a development/test navigation section rather than normal retail dialogue. It includes:

- Sakura Production video submission deadline `８／３１`;
- Start / Password screen description;
- `今からやるよ` conversation demo description;
- full-width `ＶＳ` demo description;
- Maru-chan win / loss demos;
- Continue screen;
- Story Mode quit screen;
- final-win demo;
- ending.

These 10 rows are translated only as reverse-engineering references and are deliberately **excluded** from the release-intent count. Do not patch them into a normal release unless runtime evidence proves they are player-visible.

Full audit: `docs/DIRECT_TEXT_COVERAGE_AUDIT_20260916.md`.

## Graphics / tilemap translation targets

File: `translation/source/graphics_text_targets_vi.csv`.

Current targets:

- visible pink heading `どれにする？` → `Chọn gì đây?`;
- `はじめから` → `Bắt đầu`;
- `パスワード` → `Mật khẩu`;
- `今からやるよ` → `Bắt đầu thôi!` pending exact on-screen context;
- `ＶＳ` → `VS`.

Only `どれにする？` is visually verified from the user screenshot. The other four are inferred from the internal QA block and must be located in their actual render path before insertion.

## Editorial rules

- `vi_full` stays fully accented and meaning-first;
- do not shorten source translation to current ROM/font limits;
- school/minigame competition uses `thi`, `thi đấu`, `so tài`, `vượt qua` rather than combat-heavy language;
- Maruo's `ズバリ` stays around `Nói thẳng ra!`;
- Hanawa keeps `Hey`, `baby`, `Señorita` where natural;
- narrator stays dry and lightly teasing;
- suspicious scanner fragments are verified against raw ROM before translation.

## Runtime separation

No bulk Story / Quiz / Fortune / Minigame / Karaoke / Credits translation has been patched into ROM yet.

Font/codepage reverse remains separate. Probe 005 is still the current mapping-table runtime proof and requires screenshot evidence before freezing that architecture.

## Next translation / reverse work

The currently proven large coherent direct-text banks are now meaning-covered. Do **not** inflate the untranslated count using binary-looking CP932 false positives.

Next high-value work:

1. locate and extract graphics/tilemap text for the Start / Password / Continue / ending family of screens hinted by the debug block;
2. locate the pink `どれにする？` heading render path;
3. continue font/codepage reverse so full Vietnamese can be inserted safely;
4. later perform a karaoke singability/timing pass after font/layout behavior is known.
