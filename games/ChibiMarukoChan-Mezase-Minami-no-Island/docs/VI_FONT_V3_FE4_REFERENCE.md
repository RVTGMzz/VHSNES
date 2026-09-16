# Vietnamese Font V3 — FE4 Vietnamese reference transfer

Updated: 2026-09-16 +07

## Why V3 exists

Probe 008 booted and rendered Vietnamese, but the user screenshot showed the handcrafted V2 face was visually worse than V1: uneven proportions, excessive spacing feel, and unattractive letterforms. Codepage/runtime behavior itself remained healthy; the failure was typography quality.

The user supplied `Seiseno no Keifu Vietnamese(1).smc` specifically as a font reference and asked to reuse that visual language.

## Reference identity and extraction

The exact supplied reference file is guarded as:

- size: `4,194,816` bytes = 4 MiB body + 512-byte copier header
- full-file SHA-1: `2556860f8f51d0895c191a5f614c9088fc8fd98e`
- internal title: `FIREEMBLEM4`

Recovered dialogue-font body range after removing the 512-byte copier header:

```text
0x128000 .. 0x12BBFF
```

Size `0x3C00` / 15,360 bytes. It is raw SNES 2bpp data. Interpreted as a 16-tile-wide sheet, one logical source glyph occupies a 2x2 tile block / 16x16 cell. Latin/Vietnamese ink uses the left 8 pixels, producing a compact 8x16 reference face with good native Vietnamese diacritics.

Recovered core source order includes:

- `A..Z`: cells `0x00..0x19`
- `a..z`: cells `0x1A..0x33`
- Vietnamese lowercase families in `0x3A..0x7B`, including `á à ả ã ạ`, `â/ă` families, `ê`, `ô`, `ơ`, `ư`, and `ý/ỳ/ỷ/ỹ/ỵ`

The generator does not copy FE4 ROM addresses or rendering code into Chibi. It only extracts raster shapes from the user-supplied reference and converts them to Chibi's already runtime-proven 12x12 raw-1bpp glyph format.

## Chibi adaptation

Tool:

`tools/generate_vi_glyphs_v3_fe4ref.py`

Adaptation rule:

1. decode one FE4 16x16 logical cell;
2. keep its left 8x16 raster, including Vietnamese marks;
3. nearest-neighbor adapt to 10x12;
4. center it in Chibi's 12x12 cell with one pixel side margin;
5. preserve Probe-006/007 codepage architecture (`0x84` lead); only glyph art changes.

Uppercase accented Vietnamese letters are synthesized from the FE4 uppercase base body plus the corresponding recovered lowercase accent/horn/dot layer. `Đ/đ` use FE4 `D/d` bodies with a one-pixel crossbar.

The source ROM itself is never committed.

## Probe 009

Files:

- `translation/codepage/vi_codepage_v3_fe4ref.csv`
- `translation/codepage/vi_glyphs_v3_fe4ref.json`
- `tools/probe_visible_menu_009_fe4ref_font.py`

To make the typography comparison internally consistent, five letters that V2 still borrowed from Chibi's native font receive reserved custom slots only for V3:

```text
B -> 0x0958
u -> 0x0959
M -> 0x095A
o -> 0x095B
V -> 0x095C
```

That increases the custom visual count from 121 to 126 and leaves 6 of the 132 conservatively safe blank slots reserved.

Probe rows remain deliberately identical to Probe 008 so the user can compare typography directly:

```text
Âm thanh
Bói!!
Đấu đội!
Vẽ!!
Maruko?
Ổn rồi
```

Static CLEAN-ROM build checkpoint:

- codepage entries: 160
- custom visual glyphs: 126
- lead `0x84` pointer identity: PASS
- blank/reuse audit: PASS
- source identity + exact two-byte unit preservation: PASS
- diff-surface gate: PASS
- checksum: `0x04DF`
- complement: `0xFB20`
- SHA-1: `94c0c2c303dd824ee617ec765a645a4a7adefde9`
- SHA-256: `072abd670a2e0dca888391f74b3104ba853ac49ec6144373e820eb95a18a782b`

**Runtime status: PENDING screenshot.**

Do not freeze V3 typography until the user confirms the in-game screenshot is materially better than Probe 007/008.
