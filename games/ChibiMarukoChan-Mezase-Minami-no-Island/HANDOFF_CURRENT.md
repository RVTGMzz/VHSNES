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

Probe 006 proved one custom `Đ`; Probe 007 proved the dedicated Vietnamese `0x84xx` codepage and multi-glyph bank; Probe 008 and 009 were typography failures; Probe 010 finally produced a clearly readable FE4-native-width face, but the user asked for thinner/lighter strokes.

**Current runtime test: Probe 011 FE4 Native Thin V5.**

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

No bulk Story / Quiz / Fortune / Minigame / Karaoke / Credits translation has been patched into ROM yet.

## Graphics/tilemap track remains separate

Known targets include:

- `どれにする？` -> `Chọn gì đây?` — visually verified, render path unknown
- `はじめから` -> `Bắt đầu`
- `パスワード` -> `Mật khẩu`
- `今からやるよ` -> `Bắt đầu thôi!`
- `ＶＳ` -> `VS`

Do not assume these use the direct-text renderer.

## Renderer/font proven facts

Full reverse note: `docs/REVERSE_FONT_001.md`.

- parser: file `0x283D8`, CPU `$85:83D8`
- per-lead mapping pointer table: file `0x29756`
- renderer: file `0x28E7B`, CPU `$85:8E7B`
- font page pointer table: file `0x295EE`
- 10 raw 1bpp font pages at `0x128000 .. 0x12C800`, step `0x800`
- each page: 128x128 bitmap, logical 10x10 grid of 12x12 cells
- glyph ID high byte = page 0..9; low byte = cell index 0..99

## Vietnamese codepage architecture

Frozen semantic architecture through V5:

- dedicated Shift-JIS lead: `0x84`
- lead pointer resolves to CPU `$85:9A74`
- mapping file base: `0x29A74`
- entry formula: `0x29A74 + (trail - 0x40) * 2`
- trail `0x7F` skipped
- 160 Unicode codepage entries
- current conservative direct-text corpus has zero decoded lead-0x84 characters

## Probe history

### Probe 002 — RUNTIME FAIL
Raw 1-byte ASCII froze before the menu.

### Probe 003 — BOOT PASS / GLYPH IDENTITY FAIL
Two-byte framing booted, but unsupported CP932 Latin mapped incorrectly.

### Probe 004 — RUNTIME COVERAGE MAP PASS
Many unsupported full-width Latin codes collapsed to glyph zero.

### Probe 006 — CUSTOM GLYPH RUNTIME PASS
Custom `Đ` at glyph `0x0963`; screenshot showed exact `TĐST1234`.

### Probe 007 — CODEPAGE PASS / TYPOGRAPHY FAIL
Dedicated `0x84xx` Vietnamese codepage and multi-glyph bank worked, but marks/strokes were weak and inconsistent.

### Probe 008 — BOOT/ENCODING PASS / TYPOGRAPHY FAIL
Handcrafted V2 face rendered correctly but user judged it uglier and too awkward.

### Probe 009 — BOOT/ENCODING PASS / TYPOGRAPHY FAIL
FE4 raster was stretched 8->10 and resampled 16->12, making it heavy/muddy. Do not reuse this scaling strategy.

### Probe 010 — READABILITY PASS / WEIGHT TOO BOLD

Probe 010 preserved FE4 native 8-pixel width, centered it in Chibi 12x12, and cropped vertically without interpolation. User screenshot showed all six intended rows clearly and judged it acceptable, but requested a lighter/thinner weight.

Expected/observed board:

```text
Âm thanh
Bói!!
Đấu đội!
Vẽ!!
Maruko?
Ổn rồi
```

This proves V4's native-width raster strategy is the best typography baseline so far. It is not frozen as release font because stroke weight is still too bold for user preference.

## Font V5 — FE4 Native Thin

Doc: `docs/VI_FONT_V5_FE4_THIN.md`.

Files:

- reuses `translation/codepage/vi_codepage_v3_fe4ref.csv` unchanged
- `translation/codepage/vi_glyphs_v5_fe4_thin.json`
- `tools/generate_vi_glyphs_v5_fe4_thin.py`
- `tools/probe_visible_menu_011_fe4_thin.py`

V5 keeps Probe 010's native-width FE4 transfer, then applies one conservative Zhang-Suen thinning iteration to letter bodies. Accent/horn/circumflex rows `0..4` and below-dot row `11` are restored from the pre-thinned raster to avoid repeating V1's faint-mark problem.

No code assignments or renderer logic change.

## Probe 011 — CURRENT RUNTIME TEST

Same six rows as Probe 010 for direct A/B comparison:

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
- lead pointer identity: PASS
- blank/reuse audit: PASS
- source identity + exact units: PASS
- diff-surface gate: PASS
- checksum `0x38C2`
- complement `0xC73D`
- SHA-1 `45d06514306cd6d1a0cf0c65c6339527944199d4`
- SHA-256 `11b1b8c824be60dcdad8d9f287e916a245fe5edc42cdbb33855c02f25bf8f9bd`

**Runtime status: PENDING screenshot.**

Do not call Font V5 runtime/release PASS until screenshot evidence confirms it is thinner than Probe 010 while keeping Vietnamese marks readable.

## Next high-value work

If Probe 011 is visually approved:

1. freeze V5 font/codepage for this direct-text renderer;
2. build a real compact Vietnamese main-menu candidate;
3. solve field-length/advance constraints for labels such as `Cốt truyện` / `Thi đấu` without blind truncation;
4. start guarded runtime insertion of translated direct-text batches;
5. continue graphics/tilemap reverse separately for the pink heading and Start/Password/Continue/ending family.

If Probe 011 becomes too thin or loses character identity, revert to Probe 010 raster and do targeted per-glyph shaving rather than another global thinning pass.

## Frozen workflow

Use Gaia Master-style guardrails, not Gaia Master hardware assumptions. Always build from CLEAN ROM. Keep source meaning, runtime candidate/layout, font/codepage, and graphics/tilemap as separate layers. Preserve source identity/control bytes, dry-run before write, validate diff surface/checksum, and state runtime claims narrowly.
