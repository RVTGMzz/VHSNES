# Translation progress — Chibi Maruko-chan

Updated: 2026-09-16 +07
Branch: `chibi-maruko-bootstrap-01`

## Meaning-first Vietnamese source layer

Current committed translated rows:

- `translation/source/seed_known_strings.csv`: 10
- `translation/source/main_menu_vi.csv`: 10
- `translation/source/story_batch01_vi.csv`: 126
- `translation/source/story_batch02_part1_vi.csv`: 42
- `translation/source/story_batch02_part2_vi.csv`: 42
- `translation/source/story_batch02_part3_vi.csv`: 42
- Story Batch 03: 84 rows across `story_batch03_part1_vi.csv`, `story_batch03_part2a_vi.csv`, `story_batch03_part2b_vi.csv`
- `translation/source/credits_vi.csv`: 19
- `translation/source/rules_tutorial_vi.csv`: 2
- Maruko Q Batch 01: 74 rows across `quiz_batch01_part1_vi.csv`, `quiz_batch01_part2_vi.csv`
- **total committed meaning-layer rows: 451**

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

Continue Maruko Q from approximately `0x34F7B` onward. The quiz database remains coherent well past `0x368D8`, so translate it in audited batches while separately flagging scanner-missed numeric/control fields for raw-ROM recovery.
