# HANDOFF CURRENT — Chibi Maruko-chan SNES Việt hóa

Updated: 2026-09-18 +07
Branch: `chibi-maruko-bootstrap-01`
Repo: `ronvotri/Viet-Hoa-SNES`

## Current milestone

The project is now on a **large runtime insertion checkpoint** using the accepted pre-GBA Chibi Vietnamese font/codepage layer.

The Golden Sun GBA donor-font experiment was rejected by the user for Chibi and must not be reused unless explicitly reopened.

Visible-menu architecture remains runtime-proven as:

```text
2-byte game code -> 16-bit glyph ID -> 12x12 raw 1bpp bitmap
```

Do not restart font reverse from scratch.

## Canonical clean ROM contract

- size `0x200000` / 2 MiB
- SHA-1 `08a2415362f69788ec76b1a36044dc1f1a5f2ea1`
- SHA-256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`
- internal title `RS051 CHIBIMARUKOCHAN`
- LoROM / FastROM
- header file `0x7FC0`
- no copier header
- clean checksum `0x1115`, complement `0xEEEA`

Always derive reproducible release work from this clean-ROM contract.

## Translation source status

Committed player-facing / release-intent meaning layer remains **1,018 source rows**. Detailed tracker: `translation/TRANSLATION_PROGRESS.md`.

Covered meaning banks include:

- main story through the discovered ending sequence;
- credits and tutorial/rules;
- Maruko Q quiz banks;
- Maruko Fortune / `まるこみくじ`;
- minigame setup/rules/UI;
- karaoke meaning-first lyrics;
- stage names;
- quiz misc/result UI;
- known seed strings and main-menu meanings.

Tone stays cute school/family comedy. `vi_full` remains canonical meaning; compact runtime forms are a separate layer.

## Font/codepage baseline

Proven reverse facts: `docs/REVERSE_FONT_001.md`.

- parser: file `0x283D8`, CPU `$85:83D8`
- per-lead mapping pointer table: file `0x29756`
- renderer: file `0x28E7B`, CPU `$85:8E7B`
- font page pointer table: file `0x295EE`
- 10 raw 1bpp font pages at `0x128000 .. 0x12C800`, step `0x800`
- each page: 128x128 bitmap, logical 10x10 grid of 12x12 cells
- glyph ID high byte = page 0..9; low byte = cell index 0..99

Vietnamese codepage:

- dedicated lead `0x84`;
- mapping base `0x29A74`;
- 160 Unicode entries;
- committed runtime codepage: `translation/codepage/vi_codepage_v4_fe4_native.csv`.

Font runtime history:

- Probe 006: custom `Đ` PASS.
- Probe 007: multi-glyph Vietnamese codepage PASS, typography weak.
- Probe 010: best overall FE4/native-width baseline.
- Probe 019: Probe 010 + targeted lowercase `đ` fix; user accepted it temporarily and asked to continue translation.
- Probe 020/021: Golden Sun donor experiment rejected for Chibi.

Build 023 is byte-for-byte the accepted pre-GBA Probe 019 runtime state and remains the font/codepage baseline.

## Build 024 — compact Vietnamese main menu

Build 024 applies ten fixed-field Vietnamese labels on top of Build 023 while keeping full translations intact in `translation/source/main_menu_vi.csv`.

Runtime labels include `Truyện`, `Đấu`, `Đấu đội`, `M.Q`, `Tập vẽ`, `Bói`, `Hát`, `Âm`, `ST`, `Mono`.

Static facts:

- checksum `0x9969`
- complement `0x6696`
- SHA-1 `9616e9937e0cfbd3b5294bbf7beff4dd4725301a`
- SHA-256 `4dc1ca459a4c04558bc421937ee6110b286fe19a9e94956b40e797777e4d863e`

Runtime PASS was not yet separately declared for Build 024.

## Build 027 — BIG Story runtime checkpoint

Full note: `docs/RUNTIME_STORY_BUILD_027.md`.

The user explicitly requested one large test after inserting as much translated Story content as possible.

Build chain:

- Build 025: Story Batch 01 compact runtime text, 123 non-overlapping fields.
- Build 026: Story Batch 02 compact runtime text, 121 fields.
- Build 027: Story Batch 03 through the discovered ending sequence, 84 fields.

Cumulative Story runtime fields inserted: **328**.

Insertion guardrails:

- source bytes verified against the exact clean ROM before every Story write;
- preserve known script separator/control-like pairs `81 6F` and `81 A5`;
- preserve low control bytes following each player-text region;
- no pointer relocation or field expansion claimed;
- Vietnamese is wrapped into the existing fixed byte budget through the proven `0x84xx` codepage;
- overlap rejected;
- diff surface restricted to target text spans + checksum/complement.

Build 027 artifact:

`Chibi_Maruko_Build_027_STORY_COMPLETE_READY.sfc`

Static facts:

- cumulative Story runtime fields: **328**
- checksum `0x87CF`
- complement `0x7830`
- SHA-1 `9a9280d27c9e96df972e0b21f8b806bf19ef52f7`
- SHA-256 `ed815e70f1956d37e9fe3023bb651378874de32ebfbbd8544cbc087860f17b04`
- Batch03 source identity 84/84 PASS
- overlap 0 PASS
- diff surface PASS

**Runtime status: UNTESTED. Do not call Runtime PASS yet.**

Next user test should boot Build 027, enter `Truyện`, verify the first classroom dialogue renders/advances, then continue through several scene/minigame transitions if practical. If something breaks, record the earliest broken line/freeze and isolate from there instead of restarting font work.

## Graphics/tilemap track remains separate

Known visual targets include:

- `どれにする？` -> `Chọn gì đây?`
- `はじめから` -> `Bắt đầu`
- `パスワード` -> `Mật khẩu`
- `今からやるよ` -> `Bắt đầu thôi!`
- `ＶＳ` -> `VS`
- `コンティニュー` -> `Tiếp tục`
- `エンディング` -> `Kết thúc`

The pink `どれにする？` banner is not a simple contiguous CP932/glyph-ID string. See `docs/HEADING_REVERSE_001.md` and `docs/HEADING_REVERSE_002.md`. Do not guess offsets.

## Next high-value work after Build 027 test

If Build 027 Story runtime is good:

1. keep Build 027 as the new runtime insertion baseline;
2. apply the same guarded fixed-field method to Quiz / Fortune / Minigame / Karaoke / Credits where practical;
3. continue tracing visual/tilemap text such as the pink banner and Start/Password/Continue/Ending family;
4. keep `vi_full` separate from compact runtime forms;
5. do not resume Golden Sun donor work for Chibi.

If Build 027 fails, isolate the earliest failing Story field first.

## Frozen workflow

Use Gaia Master-style guardrails, not Gaia Master hardware assumptions. Preserve source identity and control bytes, validate diff surface/checksum, and never call whole-game Runtime PASS from one subsystem screenshot.
