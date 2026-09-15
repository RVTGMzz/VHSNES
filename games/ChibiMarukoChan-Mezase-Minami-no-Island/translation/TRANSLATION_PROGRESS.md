# Translation progress — Chibi Maruko-chan

Updated: 2026-09-16 +07
Branch: `chibi-maruko-bootstrap-01`

## Meaning-first Vietnamese source layer

Current committed translated rows:

- `translation/source/seed_known_strings.csv`: 10
- `translation/source/main_menu_vi.csv`: 10
- `translation/source/story_batch01_vi.csv`: 126
- Story Batch 02: 126 rows across `story_batch02_part1_vi.csv`, `story_batch02_part2_vi.csv`, `story_batch02_part3_vi.csv`
- Story Batch 03: 84 rows across `story_batch03_part1_vi.csv`, `story_batch03_part2a_vi.csv`, `story_batch03_part2b_vi.csv`
- `translation/source/credits_vi.csv`: 19
- `translation/source/rules_tutorial_vi.csv`: 2
- Maruko Q Batch 01: 74 rows across `quiz_batch01_part1_vi.csv`, `quiz_batch01_part2_vi.csv`
- Maruko Q Batch 02: 129 rows across `quiz_batch02_part1_vi.csv`, `quiz_batch02_part2_vi.csv`, `quiz_batch02_part3_vi.csv`
- **total committed meaning-layer rows: 580**

These counts are source-translation rows, NOT whole-game completion percentage. Scanner output still contains false positives, split strings, control/layout data, and numeric/count artifacts.

## Story Batch 01

Approximate range: `0x181CC .. 0x1A5CA`

Covers the school exchange-student announcement, Maruko/Tama-chan reactions, Maruo/Hanawa banter, Sakura-family scenes, and early representative-selection games.

## Story Batch 02

Approximate range: `0x1A64F .. 0x1C61C`

Covers later selection rounds, Maruko's win/loss comedy, Maruo election jokes, Hanawa's `baby` / rose banter, Tama-chan passport gag, final-round rivalry, narrator punchlines, and family dinner jokes.

## Story Batch 03

Approximate range: `0x1C661 .. 0x1DE81`

The currently discovered direct-text story arc reaches the ending scene in this range:

- final representative-selection scenes;
- Noguchi / Nagasawa / Tomozou comedy;
- Maruko wins and the Sakura family reacts;
- Tomozou mistakes the southern island for Antarctica;
- Maruko arrives on the island;
- classmates unexpectedly arrive too;
- exchange students are called back to study;
- final Maruko/Pusadi beat and `わたしって…` ending line.

This does **not** mean the whole game is translated. It means the coherent main-story text in the current direct-CP932 scan has been translated through its visible ending.

## Credits and rule text

`credits_vi.csv` translates credit roles while preserving personal names. `rules_tutorial_vi.csv` contains the directly verified rule text around `0x1E2FF`:

- `ルールをせつめいするよ` → `Giải thích luật chơi nhé!`
- `２本先取だよ` → `Ai thắng trước 2 ván là thắng`
- `ゲームの時間は勝つまでだよ` → `Chơi cho tới khi phân thắng bại nhé`

The full-width `２` was recovered from raw ROM bytes rather than guessed from the scanner.

## Maruko Q — Batch 01

Range approximately `0x34009 .. 0x34F3E`.

Focus:

- Noguchi and her love of comedy;
- Hanawa's full name, mother, and expensive sushi shop;
- Hamaji rumors and Momoe concert-ticket gag;
- Hideji's age;
- Buutaro's baseball dream;
- Fujiki's full name;
- Pusadi's farewell gift.

Numeric answer rows skipped by the conservative scanner were recovered directly from raw ROM where proven, including:

- Hanawa's mother answer choices: 29 / 40 / 32;
- Hamaji exchange choice: 100 yen;
- Hideji answer choices: 68 / 70 / 78;
- explanatory text confirms Hanawa's mother = 29 and Hideji = 68.

## Maruko Q — Batch 02

Range approximately `0x34F7B .. 0x368D8`.

Committed as three 43-row files for audit-friendly diffs:

- `translation/source/quiz_batch02_part1_vi.csv`
- `translation/source/quiz_batch02_part2_vi.csv`
- `translation/source/quiz_batch02_part3_vi.csv`

Focus:

- Fuyuta and her crush on Ono;
- Maruo's birthday, mother, and spiral glasses;
- Migiwa / Mark / Hanawa comedy;
- Midori and Fujiki;
- Yamada's April Fools episode;
- Yamane's idol fandom;
- Yoshiko's school class and guppy story;
- Nagayama and his younger sister Koharu;
- Ono/Sugiyama and Namiki Park;
- Hiroshi's older brother Ichiro;
- Fujiki's skating skill;
- Maruko's one-story house;
- Hideji's Rolls-Royce;
- Maruko's sister reading Ribon;
- Mitsuya candy shop.

Raw-ROM recovery was used instead of guessing scanner fragments. Newly recovered answer rows include:

- Maruo birthday choices: `12/31`, `12/19`, `3/3`; explanation confirms `12/31`;
- Maruo mother age choices: `49`, `44`, `34`; explanation confirms `49`;
- Yoshiko class choices: `6-2`, `5-3`, `6-5`; explanation confirms `6-2`;
- Maruko house choices recovered as `1`, `2`, `4` floors; explanation confirms one-story.

The current direct quiz sequence ends at `0x368D8`. Immediately after that, the conservative scanner does not show a coherent continuation; do not invent one from binary false positives.

## Important remaining quiz bank discovered earlier in ROM

A separate coherent Maruko Q block remains untranslated at approximately `0x31D47 .. 0x34008`.

It contains at least 165 scanner candidates covering questions about:

- Maruko / Momoe-chan;
- Maruko's birthday and allowance;
- Tomozo, grandmother, Hiroshi, Sumire, and Maruko's older sister;
- Ono, Kayoko, Kenta, Sugiyama;
- Buutaro's sister and Nagasawa's family;
- additional classmates and family trivia.

This should be the next meaning-first translation target. As before, numeric/full-width answer fields must be recovered from raw ROM when the scanner begins inside multibyte characters.

## Editorial rules

Tone remains frozen in `translation/STYLE_GUIDE_VI.md`: cute school/family comedy, not combat RPG.

- competitions use `thi`, `thi đấu`, `so tài`, `vượt qua`;
- Maruo's `ズバリ` stays around `Nói thẳng ra!`;
- Hanawa retains `Hey`, `baby`, `Señorita` where natural;
- narrator stays dry and lightly teasing;
- Japanese wordplay is adapted only when literal Vietnamese would kill the joke;
- unresolved scanner fragments are never silently guessed.

`vi_full` remains fully accented meaning-first Vietnamese and is not shortened for current ROM/font limits.

## Runtime separation

No bulk Story / Quiz / Credits translation has been patched into ROM yet.

Font/codepage reverse remains separate. Probe 005 is still the current mapping-table runtime proof and requires screenshot evidence before freezing that architecture.

## Next translation work

Translate the earlier coherent Maruko Q block from approximately `0x31D47 .. 0x34008`, in audited batches, with raw-ROM recovery for scanner-missed numeric/count fields.
