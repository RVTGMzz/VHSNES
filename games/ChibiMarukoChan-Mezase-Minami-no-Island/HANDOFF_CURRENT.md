# HANDOFF CURRENT — Chibi Maruko-chan SNES Việt hóa

Updated: 2026-09-17 +07
Branch: `chibi-maruko-bootstrap-01`
Repo: `ronvotri/Viet-Hoa-SNES`

## Current milestone

The project is now continuing the **translation/content track**. Font work is temporarily paused at the user's request so translation can keep moving.

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

Always build from this exact clean ROM.

## Translation progress

Committed player-facing / release-intent meaning layer remains **1,018 source rows**. Detailed tracker: `translation/TRANSLATION_PROGRESS.md`.

Covered coherent direct-text banks include:

- main story through the currently discovered ending sequence;
- credits and tutorial/rule text;
- Maruko Q quiz banks;
- Maruko Fortune / `まるこみくじ`;
- minigame setup/rules/UI;
- karaoke meaning-first lyrics;
- stage names;
- quiz misc/result UI;
- known seed strings and main menu meanings.

Tone stays cute school/family comedy. Do not rewrite competition language into combat/RPG language.

### Karaoke singable pass V1

New file:

`translation/source/karaoke_batch01_singable_v1_vi.csv`

This is a **second-pass lyric draft** for all 28 karaoke rows. It keeps `vi_full` intact and adds `vi_singable_v1` with shorter, more rhythmic Vietnamese phrasing.

Important:

- this does **not** increase the 1,018 unique source-row count;
- it is not yet timing-validated or syllable-fit proven;
- do not patch it into ROM until the karaoke timing/layout path is audited.

## Direct-text coverage conclusion

The currently proven large coherent CP932 direct-text banks are meaning-covered. Do not inflate untranslated counts from scanner false positives or random binary that happens to decode as Japanese.

Next translation work should come from newly located player-facing assets or from editorial passes such as karaoke timing/singability, not from blindly translating scanner noise.

## Graphics/tilemap track remains separate

Known visual-text targets include:

- `どれにする？` -> `Chọn gì đây?` — visually verified main-menu banner;
- `はじめから` -> `Bắt đầu`;
- `パスワード` -> `Mật khẩu`;
- `今からやるよ` -> `Bắt đầu thôi!` pending exact context;
- `ＶＳ` -> `VS`.

Start / Password / Continue / ending family must be located in their actual graphics/tilemap/render paths before insertion.

## Renderer/font proven facts

Full reverse note: `docs/REVERSE_FONT_001.md`.

- parser: file `0x283D8`, CPU `$85:83D8`
- per-lead mapping pointer table: file `0x29756`
- renderer: file `0x28E7B`, CPU `$85:8E7B`
- font page pointer table: file `0x295EE`
- 10 raw 1bpp font pages at `0x128000 .. 0x12C800`, step `0x800`
- each page: 128x128 bitmap, logical 10x10 grid of 12x12 cells
- glyph ID high byte = page 0..9; low byte = cell index 0..99

Vietnamese codepage architecture remains:

- dedicated lead `0x84`;
- mapping base `0x29A74`;
- 160 Unicode entries;
- conservative direct-text corpus has zero decoded lead-0x84 characters.

## Font probe status

Key runtime evidence:

- Probe 006: custom `Đ` runtime PASS (`TĐST1234`).
- Probe 007: Vietnamese `0x84xx` multi-glyph codepage PASS, typography weak.
- Probe 008/009: typography FAIL.
- Probe 010: best overall readable baseline so far, FE4 native-width raster transfer.
- Probe 011..018: various thinning/accent experiments were rejected by user as inconsistent or uglier.
- Probe 019: returned to Probe 010 baseline and changed only lowercase `đ`; no final font freeze was declared.

**User decision on 2026-09-17:** font is "tạm thời xong" so pause font iteration and resume translation.

Therefore:

- treat Probe 010 as the visual baseline to return to later;
- treat Probe 019 only as a temporary targeted `đ` experiment;
- do not call the font release-quality PASS;
- do not resume typography work unless translation/runtime needs it or the user asks.

## Runtime separation

No bulk Story / Quiz / Fortune / Minigame / Karaoke / Credits translation has been inserted into ROM yet.

Keep these layers separate:

1. `vi_full` meaning source;
2. optional editorial/runtime candidates;
3. font/codepage;
4. graphics/tilemap text.

## Next high-value work

1. continue editorial translation work where meaningful, especially karaoke timing/singability;
2. locate player-facing graphics/tilemap strings and translate them when their source assets are proven;
3. later build guarded small runtime insertion batches from the 1,018-row meaning layer;
4. return to font typography only after content/layout needs are clearer.

## Frozen workflow

Use Gaia Master-style guardrails, not Gaia Master hardware assumptions. Preserve source identity/control bytes, dry-run before writes, validate diff surface/checksum, and never call whole-game Runtime PASS from one subsystem screenshot.
