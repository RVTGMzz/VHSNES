# Heading reverse note 001 — `どれにする？`

Updated: 2026-09-17 +07

Visible target: pink-banner heading on the main mode-selection screen.

Vietnamese meaning target remains:

`どれにする？` -> `Chọn gì đây?`

## Proven mapping facts

Using the already-proven Chibi font mapping tables on the exact clean ROM, the six characters resolve to:

- `ど` CP932 `82 C7` -> glyph `0x0032`
- `れ` CP932 `82 EA` -> glyph `0x0055`
- `に` CP932 `82 C9` -> glyph `0x0034`
- `す` CP932 `82 B7` -> glyph `0x0022`
- `る` CP932 `82 E9` -> glyph `0x0054`
- `？` CP932 `81 48` -> glyph `0x0150`

Reconstructing those glyphs from Chibi's known 12x12 1bpp font pages produces the same basic hiragana/question-mark letterforms seen in the banner. This is **strong visual evidence that the banner face derives from the same glyph artwork**, but it does not yet prove the same direct-text renderer is used.

## Storage searches

Tool: `tools/audit_heading_dorenisuru.py`

Searched the exact clean ROM for the heading as:

1. contiguous raw CP932 bytes;
2. contiguous little-endian 16-bit glyph IDs;
3. contiguous big-endian 16-bit glyph IDs;
4. contiguous low-byte glyph indices for the first five page-0 hiragana glyphs.

All four simple storage hypotheses return **0 exact hits**.

Therefore the visible heading is **not stored as an obvious contiguous string under those representations**.

## Current interpretation

Most likely remaining possibilities include:

- a pre-rendered/tilemap graphics asset built from the same font face;
- a command stream with control/position bytes interleaved between glyph references;
- a compressed graphics/text asset;
- hardcoded drawing logic or a separate layout structure.

Do not patch guessed offsets.

## Next step

Trace the mode-selection screen's draw/setup code around the known menu block and/or locate the rendered banner tile data, then prove the source asset before replacing `どれにする？` with `Chọn gì đây?`.

**Runtime claim: none.**
