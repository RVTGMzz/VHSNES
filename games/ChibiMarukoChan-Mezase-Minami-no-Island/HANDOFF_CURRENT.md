# HANDOFF CURRENT — Chibi Maruko-chan SNES Việt hóa

Updated: 2026-09-18 +07
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

Always derive reproducible release work from this clean-ROM contract, while current runtime continuation uses the accepted pre-GBA baseline described below.

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

### Editorial status

Tracker: `translation/EDITORIAL_PROGRESS.md`

Current explicit second-pass attention:

- karaoke singable V1: 28 existing rows;
- tone consistency pass 01: 7 existing rows;
- tone consistency pass 02: 12 existing rows;
- tone consistency pass 03: 18 existing rows;
- quiz naturalness pass 01: 15 existing rows;
- tone consistency pass 04 early story: 20 existing rows;
- total: **100 row-revisions/passes**, not new source rows.

`vi_full` remains canonical meaning. Editorial/runtime-shortened forms stay separate.

## Direct-text coverage conclusion

The currently proven large coherent CP932 direct-text banks are meaning-covered. Do not inflate untranslated counts from scanner false positives or random binary that happens to decode as Japanese.

Next translation work should come from newly located player-facing assets, editorial polish, or guarded runtime insertion, not from blindly translating scanner noise.

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

The letterforms match the reversed Chibi font artwork, but storage is not a simple direct string. Contiguous/interleaved CP932, glyph-ID, and masked tilemap hypotheses failed; prioritize tracing screen setup / VRAM asset / indirect pointer structures.

## Renderer/font proven facts

Full reverse note: `docs/REVERSE_FONT_001.md`.

- parser: file `0x283D8`, CPU `$85:83D8`
- per-lead mapping pointer table: file `0x29756`
- renderer: file `0x28E7B`, CPU `$85:8E7B`
- font page pointer table: file `0x295EE`
- 10 raw 1bpp font pages at `0x128000 .. 0x12C800`, step `0x800`
- each page: 128x128 bitmap, logical 10x10 grid of 12x12 cells
- glyph ID high byte = page 0..9; low byte = cell index 0..99

Vietnamese codepage architecture:

- dedicated lead `0x84`;
- mapping base `0x29A74`;
- 160 Unicode entries;
- conservative direct-text corpus has zero decoded lead-0x84 characters;
- committed runtime codepage: `translation/codepage/vi_codepage_v4_fe4_native.csv`.

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

Build 022 was a mistaken reconstruction that restored visible menu test strings back to Japanese. It is superseded and must not be used.

Build 023 restores the **exact pre-GBA runtime state of Probe 019**, including the Vietnamese test strings and accepted pre-GBA font/codepage state. It is byte-for-byte identical to Probe 019.

Build 023 static facts:

- output `Chibi_Maruko_Build_023_PRE_GBA_STATE_RESTORED_READY.sfc`
- checksum `0x9B04`
- complement `0x64FB`
- SHA-1 `a1cdd19934ec59cf9cc1142e69730bd27efe7820`
- SHA-256 `b6ee74bbaee07b385eca78f94e03e6cc65842ab1c88f66027f6811b67e890498`

Treat Build 023 / Probe 019 state as the temporary font/codepage runtime baseline.

## Build 024 — compact Vietnamese main menu

New runtime candidate file:

`translation/runtime/main_menu_compact_v1.csv`

Builder:

`tools/build_main_menu_compact_v1.py`

Build 024 applies ten exact-fit Vietnamese labels on top of Build 023 without changing the accepted font/codepage. Full source translations remain untouched in `translation/source/main_menu_vi.csv`.

Runtime labels:

- `ストーリーモード` -> `Truyện`
- `対戦モード` -> `Đấu`
- `チーム対戦モード` -> `Đấu đội`
- `まるこＱ` -> `M.Q`
- `まるこペイント` -> `Tập vẽ`
- `まるこみくじ` -> `Bói`
- `針切カラオケ` -> `Hát`
- `サウンド` -> `Âm`
- `ステレオ` -> `ST`
- `モノラル` -> `Mono`

These are compact fixed-field runtime labels, **not final replacements for the fuller meaning layer**. `ST` in particular is temporary until field expansion/relocation is proven.

Build 024 static facts:

- output `Chibi_Maruko_Build_024_MAIN_MENU_VI_COMPACT_READY.sfc`
- checksum `0x9969`
- complement `0x6696`
- SHA-1 `9616e9937e0cfbd3b5294bbf7beff4dd4725301a`
- SHA-256 `4dc1ca459a4c04558bc421937ee6110b286fe19a9e94956b40e797777e4d863e`
- 10/10 field-fit PASS
- overlap 0 PASS
- diff surface: only ten text spans + checksum/complement
- Runtime PASS: **NOT YET**; requires user screenshot/gameplay confirmation.

## Runtime separation

No bulk Story / Quiz / Fortune / Minigame / Karaoke / Credits translation has been inserted into ROM yet.

Keep these layers separate:

1. `vi_full` meaning source;
2. editorial overrides;
3. compact/runtime candidates;
4. pre-GBA Chibi font/codepage layer;
5. graphics/tilemap text.

## Next high-value work

1. validate Build 024 main menu when the user next tests it;
2. continue editorial passes on remaining Story/Maruko Q text;
3. design guarded direct-text insertion batches for story/dialogue while preserving control bytes;
4. trace the mode-selection screen asset for `どれにする？` and other Start/Password/Continue/Ending visual text;
5. do not resume Golden Sun donor work for Chibi unless the user explicitly asks.

## Frozen workflow

Use Gaia Master-style guardrails, not Gaia Master hardware assumptions. Preserve source identity/control bytes, dry-run before writes, validate diff surface/checksum, and never call whole-game Runtime PASS from one subsystem screenshot.
