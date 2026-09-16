# Translation progress — Chibi Maruko-chan

Updated: 2026-09-16 +07
Branch: `chibi-maruko-bootstrap-01`

## Meaning-first Vietnamese source layer

Current committed translated rows:

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
- **total committed meaning-layer rows: 1,010**

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

Translated:

- ball-throwing rules and controls;
- paint/dryer rules and controls;
- pool/pushing rules and controls;
- rounds-to-win setting;
- CPU difficulty;
- game duration;
- player 1–4 assignment/status;
- controller type (`Pad`, mouse, Super Scope);
- stage selector and stage numbers `0..9`.

Raw-ROM recovery fixed fields the scanner missed or started inside:

- `１ゲームの時間` at `0x28AC4`;
- `１本..５本` at `0x28AD6..0x28AF6`;
- both `１８０秒` occurrences at `0x28B1C` and `0x28B34`;
- `プレイヤー１..４`;
- stage digits `０..９` at `0x28C0A..0x28C40`.

UI fragments that form a two-line Japanese label are localized as a Vietnamese pair rather than forced word-for-word. Examples: `ボールを` / `なげる` becomes `Ném` / `bóng`, and `コンピュータの` / `つよさ` becomes `Độ khó của` / `máy tính`.

## Karaoke — Batch 01

File: `translation/source/karaoke_batch01_vi.csv`

Range approximately `0x2B380 .. 0x2B76E`.

The song-like text for `針切じいさんのロケンロール` has a meaning-first Vietnamese translation. The current source layer preserves playful wording and jokes, but it is **not yet a singable lyric pass**. Rhythm, syllable count, and timing must be audited separately before runtime insertion.

The existing start options near `0x2B7C9` / `0x2B7EF` remain represented by `seed_known_strings.csv` and were not duplicated in the karaoke batch.

## Stage-name Batch 01

File: `translation/source/stage_names_batch01_vi.csv`

Range approximately `0x2CBAD .. 0x2CD5F`.

Translated 15 stage/title strings, including `Coi chừng sóng!`, `Vòng tròn bật nảy`, several paint stages (`tiệm Mitsuya`, `quầy hội chợ`, `dinh thự`, `trung tâm bách hóa`, `trường học`), and playful square/circle names such as `Quảng trường trơn tuột` and `Quảng trường quay tít`.

These are meaning-first names; runtime layout path is not yet audited.

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

## Next translation work

Strong next target: audit the remaining direct UI/demo strings around `0x2865E .. 0x28817` and keep only strings that are actually player-facing or useful runtime labels. This region contains demo/start/password/continue/ending descriptions and may include debug/development text, so do **not** assume all of it belongs in the final player translation.

After that, scan remaining coherent direct-text islands before touching binary-looking candidates. Karaoke also needs a separate singability pass later, after font/layout behavior is understood.
