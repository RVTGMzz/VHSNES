# HANDOFF CURRENT — Chibi Maruko-chan SNES Việt hóa

Updated: 2026-09-16 +07
Branch: `chibi-maruko-bootstrap-01`
Repo: `ronvotri/Viet-Hoa-SNES`

## Current milestone

Two tracks continue in parallel:

1. meaning-first Vietnamese translation;
2. renderer/font/graphics reverse.

Visible-menu architecture is now runtime-proven as:

```text
2-byte game code -> 16-bit glyph ID -> 12x12 raw 1bpp bitmap
```

Probe 006 showed exact `TĐST1234`, proving one custom Vietnamese `Đ` glyph. Probe 007 then proved that the dedicated Vietnamese `0x84xx` codepage and a large multi-glyph custom bank boot and render through the same path.

**Probe 007 classification:**

- Vietnamese codepage / multi-glyph runtime semantics: **PASS**;
- font typography/readability: **NEEDS REVISION**.

User screenshot on 2026-09-16 showed all six intended rows recognizable, but many accents were too faint or visually unstable. Do not freeze V1 glyph artwork.

**Current runtime test: Probe 008 Font V2.**

## Canonical clean ROM contract

- size `0x200000` / 2 MiB
- SHA-1 `08a2415362f69788ec76b1a36044dc1f1a5f2ea1`
- SHA-256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`
- internal title `RS051 CHIBIMARUKOCHAN`
- LoROM / FastROM
- header file `0x7FC0`
- no copier header
- clean checksum `0x1115`, complement `0xEEEA`

Never patch an unknown or already modified ROM.

## Translation progress

Committed release-intent meaning-layer rows: **1,018**. Detailed tracker: `translation/TRANSLATION_PROGRESS.md`.

Meaning coverage includes the currently discovered coherent direct-text story, Maruko Q banks, fortune bank, minigame setup/rules, karaoke meaning pass, stage names, credits, and quiz misc/result UI. This is not a whole-game completion claim. Visible Japanese may still be graphics/tilemaps, compressed assets, alternate renderers, or dynamic UI.

Tone is cute school/family comedy, not combat RPG. Keep `vi_full` natural and fully accented.

## Graphics/tilemap targets remain separate

`translation/source/graphics_text_targets_vi.csv` includes targets such as:

- `どれにする？` -> `Chọn gì đây?` — visually verified, render path unknown
- `はじめから` -> `Bắt đầu`
- `パスワード` -> `Mật khẩu`
- `今からやるよ` -> `Bắt đầu thôi!`
- `ＶＳ` -> `VS`

Do not assume these use the proven direct-text renderer.

## Renderer/font proven facts

Full reverse note: `docs/REVERSE_FONT_001.md`.

- parser: file `0x283D8`, CPU `$85:83D8`
- per-lead mapping pointer table: file `0x29756`
- renderer: file `0x28E7B`, CPU `$85:8E7B`
- font page pointer table: file `0x295EE`
- 10 font pages at `0x128000 .. 0x12C800`, step `0x800`
- each page: raw 1bpp 128x128 bitmap
- each page: 10x10 logical grid of 12x12 cells
- glyph ID high byte = page 0..9; low byte = cell index 0..99

## Vietnamese codepage architecture

V1/V2 preserve the same code assignments:

- dedicated Shift-JIS lead: `0x84`
- lead pointer resolves to CPU `$85:9A74`
- mapping file base: `0x29A74`
- entry formula: `0x29A74 + (trail - 0x40) * 2`
- trail `0x7F` skipped
- 160 Unicode codepage entries
- 121 custom visual glyphs
- Probe 006 slot `0x0963` retained for `Đ`

The current conservative extracted direct-text corpus has zero decoded lead-0x84 characters, so this lead remains reserved for Vietnamese.

## Probe history

### Probe 002 — RUNTIME FAIL
Raw 1-byte ASCII froze before the menu.

### Probe 003 — BOOT PASS / GLYPH IDENTITY FAIL
Same-size two-byte full-width text booted, but unsupported Latin glyphs mapped incorrectly.

### Probe 004 — RUNTIME COVERAGE MAP PASS
Many unsupported full-width Latin codes rendered glyph zero.

### Probe 006 — CUSTOM GLYPH RUNTIME PASS
Custom `Đ` at glyph `0x0963`; screenshot showed exact `TĐST1234`.

### Probe 007 — CODEPAGE PASS / TYPOGRAPHY NEEDS REVISION

Files:

- `translation/codepage/vi_codepage_v1.csv`
- `translation/codepage/vi_glyphs_v1.json`
- `tools/probe_visible_menu_007_vi_codepage.py`

Screenshot showed the intended rows recognizably:

```text
ĐẦY ĐỦ!!
được!
CÓ DẤU!!
Việt
Maruko?
Ổn rồi
```

but accents and stroke consistency were not release-quality. Encoding semantics are usable; V1 bitmap artwork is not frozen.

## Font V2

Docs: `docs/VI_FONT_V2.md`.

Files:

- `translation/codepage/vi_codepage_v2.csv`
- `translation/codepage/vi_glyphs_v2.json`
- `tools/generate_vi_glyphs_v2.py`
- `tools/probe_visible_menu_008_font_v2.py`

V2 keeps all proven code assignments and redraws the custom bitmap bank with a deterministic retro-pixel style. Tone marks are thicker and positioned deliberately for 12x12 readability. The exact Probe 006 `Đ` bitmap remains unchanged.

## Probe 008 — CURRENT RUNTIME TEST

Probe 008 uses six already-visible menu fields purely as a typography board, with exact two-byte unit preservation:

```text
Âm thanh
Bói!!
Đấu đội!
Vẽ!!
Maruko?
Ổn rồi
```

This tests `Â`, `ó`, `Đ`, `ấ`, `đ`, `ộ`, `ẽ`, `Ổ`, `ồ` and common lowercase Latin. These are not yet final menu labels.

Static CLEAN-ROM build PASS:

- codepage entries: 160
- custom visual glyphs: 121
- lead pointer identity: PASS
- blank/reuse audit: PASS
- six source identities: PASS
- exact two-byte unit fit: PASS
- diff-surface gate: PASS
- checksum `0x8DFC`
- complement `0x7203`
- SHA-1 `605240bb3ca81883e6c4f06e76c642ad84be59a1`
- SHA-256 `7b9a447d7d3c19631699cfa9daa17124c08998f68878730ba89d5ee4fc6e31b5`

**Runtime status: PENDING user screenshot.**

Do not call Font V2 Runtime PASS until screenshot evidence confirms readability.

## After Probe 008

If V2 is readable:

1. freeze the V2 bitmap style/codepage for the direct-text renderer;
2. build a real compact Vietnamese menu candidate;
3. address fixed-field limits separately for longer labels such as `Cốt truyện` and `Thi đấu` via relocation/layout proof rather than truncating meaning blindly;
4. begin guarded insertion of translated direct-text batches;
5. continue graphics/tilemap reverse for the pink heading and Start/Password/Continue/ending family.

If some V2 accents remain ambiguous, revise only the affected glyph bitmaps and keep code assignments stable.

## Frozen workflow

Use Gaia Master-style guardrails, not Gaia Master hardware assumptions. Keep source meaning, runtime candidate/layout, font/codepage, and graphics/tilemap as separate layers. Every runtime claim must state exactly what screenshot evidence proved.