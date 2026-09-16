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
- Maruko Fortune / `まるこみくじ` Batch 01: 157 rows across `fortune_batch01_part1_vi.csv`, `fortune_batch01_part2_vi.csv`, `fortune_batch01_part3_vi.csv`
- **total committed meaning-layer rows: 915**

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

Range: approximately `0x2BD28 .. 0x2CB92`.

Files:

- `translation/source/fortune_batch01_part1_vi.csv`
- `translation/source/fortune_batch01_part2_vi.csv`
- `translation/source/fortune_batch01_part3_vi.csv`

Translated systems:

- headings: `Điều ước`, `Tài lộc`, `Tình duyên`, `Học hành`, `Lời trời mách`, `Con số may mắn`, `Màu may mắn`;
- wish fortunes;
- money fortunes;
- romance fortunes;
- study fortunes;
- general advice / lucky-item messages;
- lucky-number fields;
- lucky-color list.

Tone is intentionally light, school-age, and playful rather than mystical/formal. Examples include `Coi chừng tiêu hoang`, `Chỉ có lúc này thôi, tỏ tình đi!`, `Trước hết ôn bài đã`, and the deliberately deadpan `Xin hãy... từ bỏ tất cả`.

Raw-ROM recovery corrected scanner omissions/splits:

- `４人集めてみて` begins with full-width `４`; the scanner started one byte late and displayed `S人...`;
- lucky digits `０..９` were recovered directly from raw ROM;
- large lucky-number strings recovered directly: `１６，７７７，２１６`, `１，０００，０００`, `１３０，０００，０００`.

## Editorial rules

- `vi_full` stays fully accented and meaning-first;
- do not shorten source translation to current ROM/font limits;
- school/minigame competition uses `thi`, `thi đấu`, `so tài`, `vượt qua` rather than combat-heavy language;
- Maruo's `ズバリ` stays around `Nói thẳng ra!`;
- Hanawa keeps `Hey`, `baby`, `Señorita` where natural;
- narrator stays dry and lightly teasing;
- suspicious scanner fragments are verified against raw ROM before translation.

## Runtime separation

No bulk Story / Quiz / Fortune / Credits translation has been patched into ROM yet.

Font/codepage reverse remains separate. Probe 005 is still the current mapping-table runtime proof and requires screenshot evidence before freezing that architecture.

## Next translation work

Strong next player-facing direct-text target: minigame rules/config around `0x288C2 .. 0x28BFF`.

This region includes:

- ball-throwing rules;
- paint/dryer rules;
- pool/pushing rules;
- controls;
- rounds-to-win settings;
- CPU strength;
- match duration;
- player/controller assignment;
- stage selection.

Recover short full-width numeric fields directly from raw ROM where the scanner omits them, such as `１ゲームの時間`, `１本..５本`, and `１８０秒`.
