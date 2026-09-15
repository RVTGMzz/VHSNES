# Translation progress — Chibi Maruko-chan

Updated: 2026-09-16 +07
Branch: `chibi-maruko-bootstrap-01`

## Meaning-first Vietnamese source layer

Current committed translated rows:

- `translation/source/seed_known_strings.csv`: 10 seed rows
- `translation/source/main_menu_vi.csv`: 10 visible main-menu rows
- `translation/source/story_batch01_vi.csv`: 126 story/dialogue rows
- `translation/source/story_batch02_part1_vi.csv`: 42 rows
- `translation/source/story_batch02_part2_vi.csv`: 42 rows
- `translation/source/story_batch02_part3_vi.csv`: 42 rows
- total committed meaning-layer rows: **272**

These counts are translation-source rows, NOT whole-game completion percentage. The scanner still contains false positives, split strings, count/control artifacts, and unparsed layout bytes.

## Story Batch 01

Approximate range:

`0x181CC .. 0x1A5CA`

Focus:

- exchange-student announcement at school;
- Maruko/Tama-chan reactions;
- Maruo and Hanawa character banter;
- Sakura-family evening scene;
- early representative-selection contests and win/loss reactions.

## Story Batch 02

Approximate range:

`0x1A64F .. 0x1C61C`

Committed as three 42-row source files so the batch remains easy to audit and diff.

Focus:

- later rounds of the class representative-selection games;
- Maruko becoming overconfident, losing, recovering, and joking with classmates;
- Maruo's pompous election jokes and repeated `ズバリ` lines;
- Hanawa's playful `baby` / rose / `Señorita` banter;
- Tama-chan passport gag and the quiet rivalry near the final round;
- narrator punchlines and Sakura-family dinner jokes.

Editorial choices:

- school/minigame competition uses `thi`, `thi đấu`, `so tài`, `vượt qua` instead of combat-heavy wording;
- Maruo's `ズバリ` stays anchored around `Nói thẳng ra!`;
- Hanawa keeps `Hey`, `baby`, and his slightly theatrical charm;
- narrator stays dry and lightly teasing;
- Japanese wordplay is adapted for readable Vietnamese when a literal rendering would kill the joke;
- scanner fragments such as `P/Q/R` before `人/回` are NOT treated as proven text semantics. Split rows are translated conservatively from story context and marked for runtime/source-structure review.

Tone rules remain frozen in `translation/STYLE_GUIDE_VI.md`: cute school/family comedy, not an RPG battle script.

## Runtime separation

No story Batch 01 or Batch 02 row has been written into the ROM yet.

`vi_full` remains fully accented, meaning-first Vietnamese and must not be shortened to fit the current font or byte budget.

Font/codepage reverse remains a separate track. Probe 005 is still the mapping-table runtime proof and requires screenshot evidence before that architecture is frozen.

Do not derive final runtime-fit text from `vi_full` until the Vietnamese glyph/codepage path is proven.

## Next translation batch

Continue from approximately `0x1C661` onward, prioritizing coherent dialogue and skipping scanner garbage rather than guessing it.
