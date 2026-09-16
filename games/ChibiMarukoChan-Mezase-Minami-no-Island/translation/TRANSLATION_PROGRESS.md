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
- Maruko Q Batch 03: 178 rows across `quiz_batch03_part1_vi.csv`, `quiz_batch03_part2_vi.csv`, `quiz_batch03_part3_vi.csv`
- **total committed meaning-layer rows: 758**

These counts are source-translation rows, NOT whole-game completion percentage. Scanner output still contains false positives, split strings, control/layout data, and numeric/count artifacts.

## Main story

The coherent direct-text story arc is translated approximately from `0x181CC .. 0x1DE81`, through the currently discovered visible ending sequence.

Tone remains frozen in `translation/STYLE_GUIDE_VI.md`: cute school/family comedy, not combat RPG.

## Maruko Q — Batch 01

Approximate range: `0x34009 .. 0x34F3E`.

Covers Noguchi, Hanawa, Hamaji, Hideji, Buutaro, Fujiki, Pusadi, and related trivia. Raw-ROM recovery restored scanner-missed numeric choices such as Hanawa's mother age, Hamaji's 100-yen choice, and Hideji's age.

## Maruko Q — Batch 02

Approximate range: `0x34F7B .. 0x368D8`.

Covers Fuyuta, Maruo, Migiwa, Midori, Yamada, Yamane, Yoshiko, Nagayama, Ono/Sugiyama, Hiroshi's brother, Fujiki, the Sakura house, Hideji, Maruko's sister, and Mitsuya shop trivia.

Raw-ROM recovery confirmed:

- Maruo birthday: `12/31`;
- Maruo's mother: `49` years old;
- Yoshiko: class `6-2`;
- Sakura house: one story.

## Maruko Q — Batch 03

Approximate range: `0x31D47 .. 0x33F98`, with the explanation continuing into the already translated Batch 01 at `0x34009`.

Files:

- `translation/source/quiz_batch03_part1_vi.csv`
- `translation/source/quiz_batch03_part2_vi.csv`
- `translation/source/quiz_batch03_part3_vi.csv`

Focus:

- Maruko / Momoe-chan gift trivia;
- Maruko birthday, age, blood type, and allowance;
- Tomozou, grandmother, Hiroshi, Sumire, and Maruko's older sister;
- Ono, Kayoko, Hasegawa Kenta, Sugiyama, Sekiguchi;
- Tama-chan, teacher Togawa, Toku-chan, Toshiko;
- Buutaro's younger sister and Nagasawa's family.

Raw-ROM recovery was used instead of guessing scanner placeholders. Newly recovered/corrected fields include:

- Maruko: grade 3, blood type A, age 9;
- birthday choices: `5/8`, `4/23`, `10/1`;
- allowance choices: `30`, `1,000,000`, `50` yen;
- Tomozou choices: `76`, `67`, `82`, with explanation confirming `76`;
- Hiroshi choices: `40`, `45`, `36`, with explanation confirming `40`;
- Sumire: `40` years old;
- older sister: grade 6;
- Ono transfers in the 3rd semester;
- Maruko/Sugiyama class: `3-4`;
- `B級男子トリオ` restored as the `B-class boys trio` wording;
- Toshiko/Maruko/Tama school question restores full-width `3` and `Kamome No. 3 Elementary` choice;
- their grade restores to grade 3.

## Editorial rules

- `vi_full` stays fully accented and meaning-first;
- do not shorten source translation to current ROM/font limits;
- school/minigame competition uses `thi`, `thi đấu`, `so tài`, `vượt qua` rather than combat-heavy language;
- Maruo's `ズバリ` stays around `Nói thẳng ra!`;
- Hanawa keeps `Hey`, `baby`, `Señorita` where natural;
- narrator stays dry and lightly teasing;
- suspicious scanner fragments are verified against raw ROM before translation.

## Runtime separation

No bulk Story / Quiz / Credits translation has been patched into ROM yet.

Font/codepage reverse remains separate. Probe 005 is still the current mapping-table runtime proof and requires screenshot evidence before freezing that architecture.

## Next translation work

The large coherent Maruko Q banks now cover the discovered quiz text through `0x368D8`.

Next meaning-first target should move to other coherent direct-text systems rather than binary-looking scanner noise. Strong candidates are:

- fortune / `まるこみくじ` message bank around `0x2C000`;
- karaoke / song-like text around `0x2B000`;
- remaining menu/tutorial strings around `0x2865E .. 0x289xx`.

Audit each subsystem separately because menu, fortune text, karaoke lyrics/phrases, and graphics may use different runtime/layout paths.
