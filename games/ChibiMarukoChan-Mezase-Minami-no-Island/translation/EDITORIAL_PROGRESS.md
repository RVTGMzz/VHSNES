# Editorial progress — Chibi Maruko-chan

Updated: 2026-09-18 +07
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
- Hanawa keeps `Hey`, `baby`, `señorita` while sounding playful rather than battle-heavy;
- Maruo keeps his formal `Nói thẳng ra!!` personality, but surrounding Vietnamese is less stiff;
- narrator wording stays dry and lightly teasing.

## Tone consistency pass 03

File: `translation/editorial/tone_consistency_pass03.csv`

18 Story Batch 03 rows received a focused character-voice pass. Main changes:

- Maruo remains formal and self-important without sounding like translated legal prose;
- Maruko and classmates use more natural kid-to-kid Vietnamese such as `hên xui`, `mất mặt`, and `không có cửa` where the Japanese register supports it;
- removed combat-like phrasing such as `trụ tới đây` in favor of neutral competition wording;
- Hanawa's rich-kid flourish stays intact (`Hey`, `baby`, `papa`, `señorita`) while the Vietnamese flows more naturally;
- Tomozou/family dialogue is kept warm and domestic rather than heroic;
- the ending-island sequence now sounds more playful and conversational;
- `寂しかった` was corrected from a stronger inferred `nhớ` to the source-faithful `buồn vì vắng bạn` sense;
- the foreign-speaker study call no longer invents an age hierarchy (`các em` -> `các bạn`).

## Quiz naturalness pass 01

File: `translation/editorial/quiz_naturalness_pass01.csv`

15 Maruko Q rows were polished for smoother Vietnamese while preserving question/answer facts.

Highlights:

- split several Japanese-style chained clauses into natural Vietnamese question lead-ins;
- restored explicit subjects where Vietnamese otherwise sounded clipped;
- kept the narrator's teasing tone in lines about birthdays, pocket money, Tomozou, and Hiroshi;
- retained `kamishibai` context as a street `gánh kể chuyện tranh` rather than replacing it with a modern medium;
- preserved joke uncertainty such as `...chắc vậy?` instead of turning it into a factual statement;
- no answer choice or factual quiz content was changed.

## Tone consistency pass 04 — early story

File: `translation/editorial/tone_consistency_pass04_story_early.csv`

20 Story Batch 01 rows were polished. Focus:

- smoother child-to-child dialogue around the exchange-student announcement;
- less Japanese-style nominal phrasing in Maruko's daydream scenes;
- Hanawa remains suave without sounding translated literally;
- family dialogue is warmer and more conversational;
- Maruo's `Nói thẳng ra!!` stays intact but the surrounding Vietnamese is less stiff;
- narrator punchlines remain dry and lightly teasing.

## Tone consistency pass 05 — Story Batch 02

File: `translation/editorial/tone_consistency_pass05_story_mid.csv`

32 Story Batch 02 rows were polished without changing contest outcomes or story facts. Focus:

- Maruko sounds more casual and cheeky instead of translated/literary;
- Tama-chan's supportive lines flow more naturally;
- Hanawa keeps his theatrical `baby` / romantic persona without sounding combative;
- Maruo stays pompous and formal, with `ズバリ` consistently carried by `Nói thẳng ra`;
- narrator jokes are drier and less literal;
- restored the direct `生きてるかいがない` / `いきてるかい…` callback that the earlier Vietnamese had softened too much;
- contest language stays playful rather than RPG/battle-heavy.

## Fortune naturalness pass 01

File: `translation/editorial/fortune_naturalness_pass01.csv`

24 Maruko Fortune rows were refined for short, playful fortune-cookie Vietnamese. Main corrections:

- restored `カン` as **trực giác** instead of generic `đầu óc` / `đoán mò`;
- removed added meaning such as `đặc biệt`, `chiêu`, and `thật kỹ` where the Japanese did not assert it;
- made money-fortune lines punchier while preserving their meaning;
- retained the intentionally odd/comic fortune tone in lines such as looking down while walking;
- tightened warnings and lucky-day lines into natural spoken Vietnamese.

## Quiz naturalness pass 02

File: `translation/editorial/quiz_naturalness_pass02.csv`

36 Maruko Q Batch 02 rows were revised. This pass includes both naturalness work and source-faithfulness corrections.

Notable corrections:

- `心にうたれ` is restored as **cảm động** rather than the earlier inferred **áy náy**;
- `しるよしもない` restores the missing meaning that Yoshiko-san had **no way of knowing** what happened to the guppies;
- `だがし屋` is corrected from the unnatural **tiệm quà vặt** to a **tiệm bánh kẹo** context;
- `みぎまき` is kept as **xoáy sang phải** rather than over-specifying a clock direction;
- several fragmentary Japanese-style question leads were reworked into natural Vietnamese while preserving answer facts;
- Migiwa/Midori/Yamane/Nagayama character-description jokes now retain their intended contrast and teasing tone.

## UI / game-choice naturalness pass 01

File: `translation/editorial/ui_menu_naturalness_pass01.csv`

31 existing UI/menu/stage rows were refined for clearer game-language Vietnamese.

Highlights:

- difficulty is standardized as **Dễ / Vừa / Khó**;
- `体当り` becomes the concise control label **Húc**;
- CPU/player slot states are simplified to **Chơi / CPU / Nghỉ** where appropriate;
- quiz statistics become shorter labels such as **Lượt trả lời**, **Tỷ lệ đúng**, **Đúng ngay lần đầu**;
- `クイズを続けますか？` is tightened to **Tiếp tục câu đố?**;
- several stage-selection names were polished to read like game stages rather than literal Japanese compounds;
- menu `ストーリーモード` is normalized to **Cốt truyện**, while runtime may remain even shorter where fixed fields demand it.

## UI choice-flow pass 02

File: `translation/editorial/ui_choice_flow_pass02.csv`

A unified glossary now freezes the Vietnamese wording for the recurring game-flow choices and states.

Key choices:

- **Bắt đầu**
- **Mật khẩu**
- **Tiếp tục**
- **Thoát**
- **Có / Không**
- **Dễ / Vừa / Khó**
- **Chơi / CPU / Nghỉ**
- **Thắng / Thua**
- **Kết thúc**

Important context resolution:

- `やめる` is now fixed as **Thoát** because the internal descriptor explicitly identifies the Story Mode quit screen.

The glossary also keeps evidence/status separate so descriptor-only labels are not mistaken for verified retail graphics.

## Current editorial total

- unique source rows translated: **1,018**
- karaoke singable V1: **28 existing rows** with second-pass lyric drafts
- tone consistency pass 01: **7 existing rows** refined
- tone consistency pass 02: **12 existing rows** refined
- tone consistency pass 03: **18 existing rows** refined
- quiz naturalness pass 01: **15 existing rows** refined
- tone consistency pass 04: **20 existing rows** refined
- tone consistency pass 05: **32 existing rows** refined
- Fortune naturalness pass 01: **24 existing rows** refined
- Quiz naturalness pass 02: **36 existing rows** refined
- UI / game-choice naturalness pass 01: **31 existing rows** refined
- total explicit second-pass editorial row revisions so far: **223 passes/row-revisions** (not unique-source additions)

## Rule

`vi_full` remains the source-of-truth meaning layer. Editorial CSVs are review/override proposals until merged back into canonical source CSVs. Do not silently replace meaning with runtime-shortened text. Runtime/layout candidates stay separate.
