# HANDOFF CURRENT — Chibi Maruko-chan SNES Việt hóa

Updated: 2026-09-17 +07
Branch: `chibi-maruko-bootstrap-01`
Repo: `ronvotri/Viet-Hoa-SNES`

## Current milestone

Continue the **translation/content track** using the pre-GBA Chibi Vietnamese font/codepage layer. The experimental Golden Sun GBA donor font has been rejected by the user for this game and must not be used in future Chibi builds unless the user explicitly reopens that experiment.

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

File:

`translation/source/karaoke_batch01_singable_v1_vi.csv`

This is a second-pass lyric draft for all 28 karaoke rows. It keeps `vi_full` intact and adds `vi_singable_v1` with shorter, more rhythmic Vietnamese phrasing.

Important:

- this does not increase the 1,018 unique source-row count;
- it is not yet timing-validated or syllable-fit proven;
- do not patch it into ROM until the karaoke timing/layout path is audited.

### Editorial status

Tracker:

`translation/EDITORIAL_PROGRESS.md`

Current explicit second-pass attention:

- karaoke singable V1: 28 existing rows;
- tone consistency pass 01: 7 existing rows;
- tone consistency pass 02: 12 existing rows;
- tone consistency pass 03: 18 existing rows;
- quiz naturalness pass 01: 15 existing rows;
- total: **80 row-revisions/passes**, not new source rows.

## Direct-text coverage conclusion

The currently proven large coherent CP932 direct-text banks are meaning-covered. Do not inflate untranslated counts from scanner false positives or random binary that happens to decode as Japanese.

Next translation work should come from newly located player-facing assets or from editorial passes such as quiz/story naturalness and karaoke timing/singability, not from blindly translating scanner noise.

## Graphics/tilemap track remains separate

Known visual-text targets include:

- `どれにする？` -> `Chọn gì đây?` — visually verified main-menu banner;
- `はじめから` -> `Bắt đầu`;
- `パスワード` -> `Mật khẩu`;
- `今からやるよ` -> `Bắt đầu thôi!` pending exact context;
- `ＶＳ` -> `VS`;
- `コンティニュー` -> `Tiếp tục`;
- `エンディング` -> `Kết thúc`.

Start / Password / Continue / ending family must be located in their actual graphics/tilemap/render paths before insertion.

### `どれにする？` reverse status

Docs:

- `docs/HEADING_REVERSE_001.md`
- `docs/HEADING_REVERSE_002.md`

Tools:

- `tools/audit_heading_dorenisuru.py`
- `tools/audit_heading_sparse_storage_v2.py`

Proven glyph mapping:

- `ど` -> `0x0032`
- `れ` -> `0x0055`
- `に` -> `0x0034`
- `す` -> `0x0022`
- `る` -> `0x0054`
- `？` -> `0x0150`

The letterforms visually match the already-reversed Chibi font artwork, but storage is not a simple direct string. Simple contiguous/interleaved CP932, glyph-ID, and masked tilemap hypotheses have all failed; prioritize tracing screen setup / VRAM asset / indirect pointer structures.

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

## Font baseline status

Key runtime evidence:

- Probe 006: custom `Đ` runtime PASS (`TĐST1234`).
- Probe 007: Vietnamese `0x84xx` multi-glyph codepage PASS, typography weak.
- Probe 008/009: typography FAIL.
- Probe 010: best overall readable FE4/native-width baseline.
- Probe 011..018: thinning/accent experiments rejected as inconsistent or uglier.
- Probe 019: Probe 010 baseline plus targeted lowercase `đ` fix; user then said the font was good enough temporarily and asked to continue translation.
- Probe 020/021: experimental Golden Sun GBA donor font. User rejected this donor on 2026-09-17: **do not use it for Chibi**.

### Canonical pre-GBA runtime state

**Correction:** Build 022 was a mistaken reconstruction. It restored the visible menu probe strings back to clean Japanese, which the user did not ask for. Build 022 is superseded and must not be used as the working baseline.

Build 023 restores the **exact pre-GBA runtime state of Probe 019**, including its Vietnamese test strings and the accepted pre-GBA font/codepage state. It is byte-for-byte identical to Probe 019.

Static facts for Build 023:

- output name: `Chibi_Maruko_Build_023_PRE_GBA_STATE_RESTORED_READY.sfc`
- exact match to Probe 019: PASS
- checksum `0x9B04`
- complement `0x64FB`
- SHA-1 `a1cdd19934ec59cf9cc1142e69730bd27efe7820`
- SHA-256 `b6ee74bbaee07b385eca78f94e03e6cc65842ab1c88f66027f6811b67e890498`

Treat **Build 023 / Probe 019 state** as the temporary working runtime baseline. The Golden Sun donor changes are discarded. Do not silently restore translated/test-visible text back to Japanese when reverting font experiments.

## Runtime separation

No bulk Story / Quiz / Fortune / Minigame / Karaoke / Credits translation has been inserted into ROM yet.

Keep these layers separate:

1. `vi_full` meaning source;
2. optional editorial/runtime candidates;
3. pre-GBA Chibi font/codepage layer;
4. graphics/tilemap text.

## Next high-value work

1. continue editorial translation passes where wording is still stiff, especially remaining Maruko Q banks and Story early batches;
2. trace the mode-selection screen setup to locate the actual source asset for `どれにする？`;
3. locate Start / Password / Continue / ending visual text paths;
4. build guarded small runtime insertion batches from the 1,018-row meaning layer on top of the **Build 023 / Probe 019 pre-GBA state**;
5. do not resume Golden Sun donor work for Chibi unless the user explicitly asks.

## Frozen workflow

Use Gaia Master-style guardrails, not Gaia Master hardware assumptions. Preserve source identity/control bytes, dry-run before writes, validate diff surface/checksum, and never call whole-game Runtime PASS from one subsystem screenshot.
