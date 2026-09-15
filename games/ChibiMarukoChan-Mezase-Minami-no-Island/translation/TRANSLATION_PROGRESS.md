# Translation progress — Chibi Maruko-chan

Updated: 2026-09-16 +07
Branch: `chibi-maruko-bootstrap-01`

## Meaning-first Vietnamese source layer

Current committed translated rows:

- `translation/source/seed_known_strings.csv`: 10 seed rows
- `translation/source/main_menu_vi.csv`: 10 visible main-menu rows
- `translation/source/story_batch01_vi.csv`: 126 story/dialogue rows
- total committed meaning-layer rows: **146**

These counts are translation-source rows, NOT whole-game completion percentage. The scanner still contains false positives, split strings, and unparsed control/layout bytes.

## Story Batch 01

Range covered approximately:

`0x181CC .. 0x1A5CA`

Focus:

- exchange-student announcement at school;
- Maruko/Tama-chan reactions;
- Maruo and Hanawa character banter;
- Sakura-family evening scene;
- early representative-selection contests and win/loss reactions.

Tone rules are frozen in `translation/STYLE_GUIDE_VI.md`.

Important editorial choices:

- school/minigame competition uses `thi`, `thi đấu`, `so tài` rather than combat-heavy wording;
- Maruo's `ズバリ` is anchored around `Nói thẳng ra!`;
- Hanawa keeps his playful `Hey` / `baby` persona;
- narrator stays dry and lightly teasing;
- `vi_full` keeps natural Vietnamese with full diacritics and is not shortened for current ROM limits.

## Runtime separation

No story Batch 01 row has been written into the ROM yet.

Font/codepage reverse remains a separate task. Probe 005 is still the current mapping-table runtime proof and requires screenshot evidence before freezing that architecture.

Do not derive runtime-fit text from `vi_full` until the Vietnamese glyph/codepage path is proven.

## Next translation batch

Continue from approximately `0x1A64F` onward, prioritizing coherent real dialogue and skipping scanner garbage/control artifacts rather than guessing them.
