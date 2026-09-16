# HANDOFF CURRENT — Chibi Maruko-chan SNES Việt hóa

Updated: 2026-09-16 +07
Branch: `chibi-maruko-bootstrap-01`
Repo: `ronvotri/Viet-Hoa-SNES`

## Current milestone

Two tracks continue in parallel:

1. meaning-first Vietnamese translation;
2. renderer/font/graphics reverse.

Visible-menu architecture is runtime-proven as:

```text
2-byte game code -> 16-bit glyph ID -> 12x12 raw 1bpp bitmap
```

Probe 006 showed exact `TĐST1234`, proving one custom Vietnamese `Đ`. Probe 007 proved the dedicated Vietnamese `0x84xx` codepage and a large multi-glyph bank render in game, but its typography was weak. Probe 008 booted and rendered the intended Vietnamese rows, but the handcrafted V2 font looked visibly worse than V1.

**Current runtime test: Probe 009 FE4-reference Font V3.**

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

Meaning coverage includes the currently discovered coherent direct-text story, Maruko Q, fortune, minigame setup/rules, karaoke meaning pass, stage names, credits, and quiz misc/result UI. This is not a whole-game completion claim. Visible Japanese may still be graphics/tilemaps, compressed assets, alternate renderers, or dynamic UI.

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

V1/V2/V3 preserve the same proven text encoding architecture:

- dedicated Shift-JIS lead: `0x84`
- lead pointer resolves to CPU `$85:9A74`
- mapping file base: `0x29A74`
- entry formula: `0x29A74 + (trail - 0x40) * 2`
- trail `0x7F` skipped
- 160 Unicode codepage entries
- current conservative extracted direct-text corpus has zero decoded lead-0x84 characters

## Probe history

### Probe 002 — RUNTIME FAIL
Raw 1-byte ASCII froze before the menu.

### Probe 003 — BOOT PASS / GLYPH IDENTITY FAIL
Same-size two-byte full-width text booted, but unsupported Latin glyphs mapped incorrectly.

### Probe 004 — RUNTIME COVERAGE MAP PASS
Many unsupported full-width Latin codes rendered glyph zero.

### Probe 006 — CUSTOM GLYPH RUNTIME PASS
Custom `Đ` at glyph `0x0963`; screenshot showed exact `TĐST1234`.

### Probe 007 — CODEPAGE PASS / TYPOGRAPHY FAIL
Dedicated `0x84xx` Vietnamese codepage and multi-glyph bank worked at runtime. Screenshot showed intended rows recognizably, but accents/strokes were too weak or inconsistent for release.

### Probe 008 — BOOT/ENCODING PASS / TYPOGRAPHY FAIL

V2 kept the same code assignments and replaced bitmap art with a handcrafted deterministic pixel face.

User screenshot on 2026-09-16 showed:

```text
Âm thanh
Bói!!
Đấu đội!
Vẽ!!
Maruko?
Ổn rồi
```

The game booted and text remained recognizable, so codepage/runtime behavior was healthy. However, user judged V2 visually worse than the previous font, with awkward proportions and spacing. **Do not freeze V2 typography.**

## FE4 Vietnamese reference font extraction

Doc: `docs/VI_FONT_V3_FE4_REFERENCE.md`.

The user supplied `Seiseno no Keifu Vietnamese(1).smc` as a visual font reference.

Exact supplied reference identity:

- total size `4,194,816` bytes = 4 MiB body + 512-byte copier header
- full SHA-1 `2556860f8f51d0895c191a5f614c9088fc8fd98e`
- internal title `FIREEMBLEM4`

Recovered dialogue-font range from the headerless body:

```text
0x128000 .. 0x12BBFF
```

Size `0x3C00` bytes, raw SNES 2bpp. It decodes as 240 logical 16x16 cells (2x2 8x8 tiles per cell), with Latin/Vietnamese ink in the left 8 pixels. The reference contains a compact 8x16 Latin/Vietnamese face with native tone-marked lowercase glyph families.

Recovered source ordering includes:

- `A..Z` = cells `0x00..0x19`
- `a..z` = cells `0x1A..0x33`
- Vietnamese lowercase accented families roughly `0x3A..0x7B`

Important: **only raster shapes are transferred.** FE4 addresses, renderer, codepage, width rules, and engine assumptions are not copied into Chibi.

## Font V3 — FE4-reference transfer

Files:

- `translation/codepage/vi_codepage_v3_fe4ref.csv`
- `translation/codepage/vi_glyphs_v3_fe4ref.json`
- `tools/generate_vi_glyphs_v3_fe4ref.py`
- `tools/probe_visible_menu_009_fe4ref_font.py`
- `docs/VI_FONT_V3_FE4_REFERENCE.md`

Adaptation:

```text
FE4 8x16 raster shape -> nearest-neighbor 10x12 -> centered in Chibi 12x12 cell
```

V3 keeps the `0x84xx` encoding semantics. Five previously native letters needed by the typography board receive safe custom slots so the comparison is visually consistent:

```text
B -> 0x0958
u -> 0x0959
M -> 0x095A
o -> 0x095B
V -> 0x095C
```

V3 uses 126 custom visual glyphs, leaving 6 conservatively safe blank slots reserved.

## Probe 009 — CURRENT RUNTIME TEST

Probe rows are deliberately identical to Probe 008 for direct visual comparison:

```text
Âm thanh
Bói!!
Đấu đội!
Vẽ!!
Maruko?
Ổn rồi
```

Static CLEAN-ROM build PASS:

- codepage entries: 160
- custom visual glyphs: 126
- lead `0x84` pointer identity: PASS
- blank/reuse audit: PASS
- six source identities: PASS
- exact two-byte unit fit: PASS
- diff-surface gate: PASS
- checksum `0x04DF`
- complement `0xFB20`
- SHA-1 `94c0c2c303dd824ee617ec765a645a4a7adefde9`
- SHA-256 `072abd670a2e0dca888391f74b3104ba853ac49ec6144373e820eb95a18a782b`

**Runtime status: PENDING user screenshot.**

Do not call V3 typography Runtime PASS until the screenshot shows it is materially better than Probe 007/008.

## After Probe 009

If V3 looks good:

1. freeze the FE4-derived raster face for the direct-text renderer;
2. build a real compact Vietnamese main-menu candidate;
3. separately solve field-length/spacing constraints rather than truncating meaning blindly;
4. begin guarded insertion of translated direct-text batches;
5. consider width/advance work only if fixed-width spacing remains objectionable;
6. continue graphics/tilemap reverse for the pink heading and Start/Password/Continue/ending family.

If V3 still looks poor, do not keep redrawing blindly. Audit the Chibi renderer's character advance/spacing behavior and consider a width/advance layer inspired by reference projects, but prove it on Chibi before adopting it.

## Frozen workflow

Use Gaia Master-style guardrails, not Gaia Master hardware assumptions. Keep source meaning, runtime candidate/layout, font/codepage, and graphics/tilemap as separate layers. Every runtime claim must state exactly what screenshot evidence proved.