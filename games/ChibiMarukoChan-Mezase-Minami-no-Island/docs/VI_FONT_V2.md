# Vietnamese Font V2 — Chibi Maruko-chan SNES

Updated: 2026-09-16 +07

## Why V2 exists

Probe 007 runtime proved that the dedicated Vietnamese two-byte codepage (`0x84xx`) is accepted by the visible-menu renderer and that many custom glyph slots render. However, the screenshot showed inconsistent typography: several tone marks were too small or weak, some accented forms lost visual distinction, and the custom lowercase/uppercase set did not feel uniform.

Therefore Probe 007 is classified narrowly as:

- codepage / multi-glyph runtime path: PASS;
- font-quality/readability: NEEDS REVISION.

## V2 design

V2 preserves the already-proven architecture and code assignments. It changes only the custom bitmap artwork.

- cell: 12x12 raw 1bpp
- dedicated code lead: `0x84`
- codepage entries: 160
- custom visual glyphs: 121
- native glyph mappings are retained where they were already suitable
- uppercase `Đ` keeps the exact Probe 006 runtime-proven bitmap
- other custom glyphs use a deterministic handcrafted retro-pixel base
- tone marks are deliberately thicker than V1 to survive emulator scaling
- circumflex/breve occupy rows 2-3
- tone marks occupy rows 0-2
- underdot occupies row 11
- horn is drawn as a visible right-side hook

Generator: `tools/generate_vi_glyphs_v2.py`

Generated assets:

- `translation/codepage/vi_codepage_v2.csv`
- `translation/codepage/vi_glyphs_v2.json`

## Probe 008

Tool: `tools/probe_visible_menu_008_font_v2.py`

Built only from the canonical clean ROM. It preserves exact two-byte unit counts and uses six already-visible menu fields as a typography board:

- `Âm thanh`
- `Bói!!`
- `Đấu đội!`
- `Vẽ!!`
- `Maruko?`
- `Ổn rồi`

These phrases intentionally exercise `Â`, `ó`, `Đ`, `ấ`, `đ`, `ộ`, `ẽ`, `Ổ`, `ồ` plus common lowercase Latin.

Probe 008 does **not** claim final menu wording or final layout. It is a font-quality probe. Final menu strings such as `Cốt truyện` and `Thi đấu` exceed some original fixed fields and may need a later relocation/layout solution.

Do not call V2 font-quality Runtime PASS until a gameplay screenshot verifies readability.
