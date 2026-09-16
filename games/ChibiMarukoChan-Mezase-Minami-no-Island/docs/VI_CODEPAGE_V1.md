# Vietnamese Codepage V1 — Chibi Maruko-chan SNES

Updated: 2026-09-16 +07

This file records the first corpus-derived Vietnamese codepage for the runtime-proven visible text renderer.

## Architecture

Probe 006 established:

```text
2-byte game code -> 16-bit glyph ID -> 12x12 raw 1bpp bitmap
```

V1 reserves Shift-JIS lead byte `0x84` for Vietnamese because the current conservative direct-text scan contains zero decoded `0x84` lead characters.

For lead `0x84`:

- pointer-table entry: file `0x2975E`
- clean pointer: CPU `$85:9A74`
- mapping table file base: `0x29A74`
- entry: `0x29A74 + (trail - 0x40) * 2`
- trail `0x7F` skipped

This is Chibi-specific.

## Inventory

- `translation/codepage/vi_codepage_v1.csv`
- `translation/codepage/vi_glyphs_v1.json`
- 160 Unicode input characters
- full A-Z / a-z, digits and required punctuation
- Vietnamese precomposed characters required by the current 1,018-row meaning layer
- `ñ` for `Señorita`
- 121 custom visual glyphs
- Probe 006 `Đ` slot `0x0963` retained

Static slot audit found 132 conservatively safe blank cells after excluding an already-referenced blank; V1 consumes 121 custom visual slots, leaving 11 reserved.

## Probe 007 result

Tool: `tools/probe_visible_menu_007_vi_codepage.py`.

Expected rows:

```text
ĐẦY ĐỦ!!
được!
CÓ DẤU!!
Việt
Maruko?
Ổn rồi
```

Static build checkpoint:

- codepage entries: 160
- custom visual glyphs: 121
- lead pointer identity: PASS
- custom blank/reuse audit: PASS
- six source identities: PASS
- exact two-byte unit preservation: PASS
- diff-surface gate: PASS
- checksum `0xB46C`, complement `0x4B93`
- SHA-1 `9d890f1d00af6d893dcf07174ea66f8954c30382`
- SHA-256 `e3a9e1555f3bb85ac326a47bd610e6fd9cfa4e1428666fd99bc0276c1456e46a`

User screenshot on 2026-09-16 showed the intended six rows recognizably and the game remained stable. Therefore:

- dedicated `0x84xx` Vietnamese codepage runtime semantics: **PASS**;
- multi-glyph custom bank path: **PASS**;
- V1 typography/readability: **NEEDS REVISION**.

The screenshot showed weak or ambiguous accents and inconsistent stroke shapes, so `vi_glyphs_v1.json` is not release typography.

## Superseded typography

V1 encoding assignments stay useful and are carried forward. Font artwork is superseded by Font V2:

- `docs/VI_FONT_V2.md`
- `translation/codepage/vi_codepage_v2.csv`
- `translation/codepage/vi_glyphs_v2.json`
- `tools/generate_vi_glyphs_v2.py`
- `tools/probe_visible_menu_008_font_v2.py`

Do not reinterpret Probe 007 as whole-game Runtime PASS. It proves this direct-text renderer/codepage path only.