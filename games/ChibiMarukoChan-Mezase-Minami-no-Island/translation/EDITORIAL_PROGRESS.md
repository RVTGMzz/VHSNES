# Editorial progress — Chibi Maruko-chan

Updated: 2026-09-17 +07
Branch: `chibi-maruko-bootstrap-01`

The meaning-first source layer remains **1,018 unique player-facing rows**. Editorial passes do not increase this count because they refine existing translated rows rather than add new Japanese source strings.

## Tone consistency pass 01

File: `translation/editorial/tone_consistency_pass01.csv`

7 rows revised toward a softer school/family/minigame tone. Main changes:

- `người chiến thắng` -> more conversational `mình thắng rồi` where appropriate;
- `chiến thắng` -> `thắng` / `mừng ... thắng` in casual cheering;
- `phân thắng bại` -> `so tài` for school-age rivalry;
- `đánh bại` -> `xử lý được` for mischievous-kid context;
- preserve the original outcome meaning without turning the game into combat/RPG prose.

## Tone consistency pass 02

File: `translation/editorial/tone_consistency_pass02.csv`

12 more rows polished. Highlights:

- `Mạnh ghê` -> `Giỏi ghê` in friendly minigame cheering;
- `sức mạnh bộc phát lúc nguy cấp` -> `sức trâu` for the comic `バカぢから` punchline;
- Hanawa keeps `Hey`, `lady`, `señorita` while sounding playful rather than battle-heavy;
- Maruo keeps his formal `Nói thẳng ra!!` personality, but surrounding Vietnamese is less stiff;
- narrator wording stays dry and lightly teasing.

## Current editorial total

- unique source rows translated: **1,018**
- karaoke singable V1: **28 existing rows** with second-pass lyric drafts
- tone consistency pass 01: **7 existing rows** refined
- tone consistency pass 02: **12 existing rows** refined
- total existing rows with explicit second-pass editorial attention so far: **47 passes/row-revisions** (not unique-source additions)

## Rule

`vi_full` remains the source-of-truth meaning layer. Editorial CSVs are review/override proposals until merged back into canonical source CSVs. Do not silently replace meaning with runtime-shortened text. Runtime/layout candidates stay separate.
