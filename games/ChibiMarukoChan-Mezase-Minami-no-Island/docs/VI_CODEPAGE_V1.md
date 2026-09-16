# Vietnamese Codepage V1 — Chibi Maruko-chan SNES

Updated: 2026-09-16 +07

This file defines the first corpus-derived Vietnamese codepage for the runtime-proven visible text renderer.

## Proven base architecture

Probe 006 screenshot proved:

```text
2-byte game code -> 16-bit glyph ID -> 12x12 raw 1bpp bitmap
```

The parser uses a per-lead mapping table. V1 reserves Shift-JIS lead byte `0x84` for Vietnamese because the current conservative direct-text scan contains **zero decoded 0x84 lead characters**.

For lead `0x84`:

- pointer-table entry: file `0x2975E`
- clean pointer value: CPU `$85:9A74`
- mapping table file base: `0x29A74`
- entry formula: `0x29A74 + (trail - 0x40) * 2`
- trail `0x7F` is deliberately skipped

This is a Chibi-specific codepage. Do not generalize it to other SNES games.

## Inventory

Files:

- `translation/codepage/vi_codepage_v1.csv`
- `translation/codepage/vi_glyphs_v1.json`

V1 currently defines:

- **160 Unicode input characters**
- digits and full A-Z / a-z coverage
- punctuation currently needed by the translated corpus
- all Vietnamese precomposed characters already used by the 1,018-row meaning layer
- several extra uppercase Vietnamese characters needed by Probe 007
- `ñ` for Hanawa's `Señorita`

The codepage maps some characters to native game glyphs and allocates new raster glyphs only when needed.

## Glyph-slot audit

All ten font pages were decoded as 10x10 grids of 12x12 cells.

Static clean-ROM audit found:

- 133 blank cells total
- glyph `0x022D` is blank but already referenced, so it is not a new allocation candidate
- **132 blank cells** pass the conservative nearby mapping/reuse scan
- V1 uses **121 custom visual glyphs**
- **11 audited blank slots remain reserved** for future additions

Probe 006's runtime-proven `Đ` slot is retained:

```text
Đ -> glyph ID 0x0963
```

Curly left/right double quotes share the straight double-quote bitmap to save slots.

## Glyph-art status

`vi_glyphs_v1.json` contains packed 12x12 1bpp bitmaps, 18 bytes per custom visual glyph. No external font file is required by the build tool.

The V1 raster is a functional first typography pass. Runtime readability must be judged from gameplay screenshots before typography is frozen for release.

## Probe 007

Tool:

`tools/probe_visible_menu_007_vi_codepage.py`

Probe 007 installs the complete V1 mapping/glyph bank from a CLEAN ROM and replaces only the first six known visible menu fields, preserving the exact two-byte unit count of every source field.

Expected rows:

```text
ĐẦY ĐỦ!!
được!
CÓ DẤU!!
Việt
Maruko?
Ổn rồi
```

The probe intentionally mixes:

- upper/lower case;
- `Đ/đ`;
- tone-marked vowels;
- `Ư/ư` and `ợ`;
- punctuation;
- native and newly allocated glyphs.

Static build checkpoint:

- codepage entries: 160
- custom visual glyphs: 121
- lead `0x84` pointer identity: PASS
- custom blank/reuse audit: PASS
- six source identities: PASS
- exact two-byte unit preservation: PASS
- diff-surface gate: PASS
- checksum/complement: PASS
- output checksum: `0xB46C`
- complement: `0x4B93`
- SHA-1: `9d890f1d00af6d893dcf07174ea66f8954c30382`
- SHA-256: `e3a9e1555f3bb85ac326a47bd610e6fd9cfa4e1428666fd99bc0276c1456e46a`

**Runtime status: pending screenshot.**

Do not call the whole Vietnamese codepage runtime-proven until Probe 007 is visually checked. Probe 006 proves one custom glyph and the renderer path, not the whole 160-character bank.

## After Probe 007

If all six rows render correctly enough to identify the intended Vietnamese text:

1. freeze V1 encoding semantics;
2. make typography corrections only where the screenshot shows ambiguous glyphs;
3. build a guarded real-menu Vietnamese candidate;
4. begin runtime-fit work for translated direct-text banks;
5. keep graphics/tilemap text such as `どれにする？` on its separate reverse track.
