# Golden Sun (VH) donor-font note 001

Updated: 2026-09-17 +07

Purpose: use the user-supplied `Golden Sun (VH).gba` only as a **glyph-shape donor** for Chibi Maruko-chan. Do not transplant GBA renderer/code/encoding assumptions into SNES.

## Correctly decoded Golden Sun font record

Observed font base in the supplied GBA ROM:

- file offset approximately `0x32224`
- one record per character: 32 bytes
- first 2 bytes: width/metric
- remaining 30 bytes: 15 scanlines
- each scanline is one little-endian **16-bit 1bpp row mask**

Important correction: an earlier preview incorrectly treated the two bytes of each scanline as two planes and ORed them together. That folded right-side pixels into the left side and created fake black squares, malformed `Ư/ư`, and other apparent glyph corruption. Those preview artifacts were extraction bugs, not evidence that the donor font itself was broken.

## Probe 020 donor slots

For the first Chibi A/B probe, the following Golden Sun donor slots are used:

- `Â` -> `0xC6`
- `Ư` -> `0xF4`
- `ớ` -> `0xA6`
- `Đ` -> `0xFF`
- `ấ` -> `0x85`
- `đ` -> `0xBA`
- `ộ` -> `0xA3`
- `ẽ` -> `0x8C`
- `ỏ` -> `0x9B`
- `é` -> `0x8A`
- `Ổ` -> `0xE6`
- `ồ` -> `0x9F`

Plain ASCII donor glyphs are read from their ASCII code positions.

## SNES transplant rule

Golden Sun donor glyphs are not copied as raw GBA bytes. They are decoded to a clean 1bpp silhouette and placed into Chibi's already-proven 12x12 glyph cells.

Chibi architecture remains unchanged:

`0x84xx Vietnamese code -> 16-bit Chibi glyph ID -> 12x12 raw 1bpp bitmap`

The first donor probe modifies only glyph cells already used by the existing Vietnamese codepage and the six visible menu test fields. It does not redesign the parser, codepage architecture, or renderer.

## Probe 020 test rows

The visible menu fields are repurposed to show:

1. `Âm thanh`
2. `Ước!!`
3. `Đấu đội!`
4. `Vẽ!!`
5. `Hỏi nhé`
6. `Ổn rồi`

This intentionally exercises circumflex, horn, acute, hook, tilde, under-dot, uppercase/lowercase, and `Đ/đ` in one screenshot.

## Runtime status

Static build only. **No Runtime PASS** until the user boots the ROM and provides screenshot evidence.

Tool: `tools/probe_visible_menu_020_golden_sun_donor.py`
