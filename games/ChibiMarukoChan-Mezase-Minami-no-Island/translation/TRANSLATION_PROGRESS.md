# Translation progress — Chibi Maruko-chan

Updated: 2026-09-18 +07  
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

- `translation/source/internal_debug_reference_vi.csv`: internal QA/debug reference, excluded from the 1,018 release-intent count
- `translation/source/graphics_text_targets_vi.csv`: visual-text targets for graphics/tilemap work, not direct-text rows

These counts are source-translation rows, **not whole-game completion percentage**.

`vi_full` remains the canonical meaning-first translation. Runtime compact strings are allowed to shorten for fixed fields but must not replace `vi_full`.

## Main story

The coherent direct-text story arc is meaning-covered through the currently discovered ending sequence.

Tone remains frozen in `translation/STYLE_GUIDE_VI.md`: cute school/family comedy, not combat RPG.

The large runtime Story chain inserted **328** discovered direct Story fields by Build 027.

See `docs/RUNTIME_STORY_BUILD_027.md`.

## Maruko Q / Quiz

The large coherent quiz banks are meaning-covered through the currently discovered direct-text end.

Build 035 added another **65** Quiz/direct runtime entries in the remaining discovered Batch01 region around `0x34009..0x34F3E`.

The current runtime chain also carries the earlier large Quiz insertions.

## Maruko Fortune

Range approximately `0x2BD28 .. 0x2CB92`.

Files:

- `translation/source/fortune_batch01_part1_vi.csv`
- `translation/source/fortune_batch01_part2_vi.csv`
- `translation/source/fortune_batch01_part3_vi.csv`

Meaning coverage includes wish, money, romance, study, general advice, lucky items, lucky numbers, and lucky colors.

The current runtime chain carries compact Fortune insertion.

## Minigame UI

File: `translation/source/minigame_ui_batch01_vi.csv`

Meaning coverage includes:

- ball-throwing rules/controls;
- paint/dryer rules/controls;
- pool/pushing rules/controls;
- rounds;
- CPU difficulty;
- game duration;
- player slots/status;
- controller type;
- stage selector/digits.

The current runtime chain carries a direct-text Minigame/UI pass. Large Japanese title/rule graphics remain a separate graphics track.

## Karaoke

Files:

- `translation/source/karaoke_batch01_vi.csv`
- `translation/source/karaoke_batch01_singable_v1_vi.csv`

The 28-row singable V1 draft remains a second-pass runtime-oriented draft and does not replace `vi_full`.

## Stage names / Credits / Quiz UI

Meaning-covered source files include:

- `translation/source/stage_names_batch01_vi.csv`
- `translation/source/quiz_ui_misc_vi.csv`
- `translation/source/credits_vi.csv`

Build 035 adds **22 compact Credits role-token patches** on top of the prior runtime chain.

## Current direct-text runtime checkpoint

Latest large candidate:

`Chibi_Maruko_Build_035_QUIZ01_CREDITS_PASS_READY.sfc`

Static facts:

- base: Build 034
- new Quiz/direct entries: **65**
- new Credits role-token patches: **22**
- changed bytes vs Build034: **3129**
- checksum `0x6547`
- complement `0x9AB8`
- SHA-1 `054380f9b452f245471e6309eb33c7486d581462`
- SHA-256 `f8fb662a9e1b8fc5a5ff689f690ceaf332055ed86983e52b476a78852e4fd58d`
- runtime status: **UNTESTED**

See `docs/RUNTIME_BUILD_035_CHECKPOINT.md`.

## Font/codepage status

The current architecture is the proven dedicated `0x84xx` Vietnamese codepage mapped to 12x12 raw 1bpp glyphs.

The Golden Sun GBA donor-font experiment was rejected for Chibi and is not part of the current plan.

User runtime screenshots after Build 033 identified several typography defects. Build 034 applied targeted static fixes for T/V/A/K/L/e/g, circumflex orientation, and dot-below visibility. Those changes are inherited by Build 035, but the font is **not yet release-runtime PASS**.

Do not reopen broad font reverse unless new runtime evidence requires it.

## Direct-text remaining audit

After Build 035, a whole-ROM scanner audit found only 13 unchanged kana-rich candidates.

They are not established ordinary player-facing direct text:

- internal review/debug screen descriptors;
- likely effect/debug data;
- likely binary false positives.

Therefore broad direct-text scanning is no longer the current priority.

## Graphics / tilemap translation targets — CURRENT PRIORITY

See:

- `translation/source/graphics_text_targets_vi.csv`
- `docs/GRAPHICS_TILEMAP_PASS_001_AUDIT.md`
- `docs/HEADING_REVERSE_001.md`
- `docs/HEADING_REVERSE_002.md`

### Batch G1

- `どれにする？` -> **Chọn gì đây?**
- `はじめから` -> **Bắt đầu**
- `パスワード` -> **Mật khẩu**

### Batch G2

- `今からやるよ` -> **Bắt đầu thôi!**
- visible VS/rule graphics:
  - `ルールをせつめいするよ` -> **Luật chơi**
  - `２本先取だよ` -> **Thắng 2**
  - `ゲームの時間は勝つまでだよ` -> **Đến khi thắng**

### Batch G3

- `勝ち` -> **Thắng**
- lose-result graphic -> **Thua**
- Continue -> **Tiếp tục**
- quit story -> **Hủy / Thoát** after exact context confirmation
- ending/chapter/large title cards

The descriptor block at approximately `0x286B4..0x287FC` names these screens but is **not the actual visible retail asset**.

Do not patch the descriptor text and claim the graphic is translated.

## Editorial / runtime rules

- keep `vi_full` fully accented and meaning-first;
- keep compact runtime candidates separate;
- preserve the school/family-comedy tone;
- preserve source identity/control bytes;
- do not translate scanner noise to inflate progress;
- graphics/tilemap is a separate layer from direct text;
- no Runtime PASS without user screenshot/gameplay evidence;
- user prefers fewer, larger tests.

## Next work

1. reverse actual Graphics Batch G1 asset paths;
2. determine raw tiles vs tilemap vs compressed graphics vs alternate renderer;
3. make one high-information graphics probe or one coherent graphics batch on top of Build 035;
4. then proceed to G2 and G3;
5. update `HANDOFF_CURRENT.md` whenever a new asset path/build checkpoint is proven.
