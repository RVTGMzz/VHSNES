# Heading reverse note 002 — sparse storage audit for `どれにする？`

Updated: 2026-09-17 +07

Target remains the visible pink-banner heading on the main mode-selection screen:

`どれにする？` -> `Chọn gì đây?`

This note extends `HEADING_REVERSE_001.md` without changing any runtime claim.

## Known glyph mapping

On the exact clean ROM:

- `ど` -> glyph `0x0032`
- `れ` -> glyph `0x0055`
- `に` -> glyph `0x0034`
- `す` -> glyph `0x0022`
- `る` -> glyph `0x0054`
- `？` -> glyph `0x0150`

The banner letterforms remain visually consistent with Chibi's already-reversed 12x12 1bpp font artwork.

## New audit

Tool:

`tools/audit_heading_sparse_storage_v2.py`

Exact clean-ROM contract used:

- size `0x200000`
- SHA-1 `08a2415362f69788ec76b1a36044dc1f1a5f2ea1`

The audit searched for the six heading characters while allowing control/position bytes to be interleaved between them.

### Ordered CP932 token search

For the full six-character CP932 sequence, allowing up to the following number of bytes between adjacent characters:

`0, 1, 2, 4, 8, 12, 16, 24, 32`

Result: **0 ordered hits at every gap size**.

This makes a simple command stream that preserves the original CP932 character bytes increasingly unlikely.

### Ordered 16-bit glyph-ID search

The same ordered search was repeated with little-endian glyph IDs:

`0032 0055 0034 0022 0054 0150`

again allowing gaps up to 32 bytes.

Result: **0 ordered hits at every gap size**.

This rules against a straightforward interleaved command list that stores the already-resolved 16-bit glyph IDs in order.

### Low-byte glyph-index search

The first five hiragana all live on font page 0, so their low glyph bytes are:

`32 55 34 22 54`

Result: no ordered match with gaps `<= 8` bytes anywhere in the ROM. Wider gaps begin to produce random binary coincidences, so they are not useful evidence.

### Contiguous masked 16-bit tilemap search

The six IDs were also tested as contiguous 16-bit words while masking possible attribute bits with:

- `0x03FF`
- `0x01FF`
- `0x00FF`

Result: **0 hits** under all three masks.

This does not look like a simple SNES tilemap row containing the glyph/tile identities plus fixed high attribute bits.

### Main menu bank window audit

Within `0x28000 .. 0x2B000`, the known menu/code/data neighborhood, no 24-byte or 32-byte window contains all six low glyph bytes together.

This further reduces the likelihood of a tiny nearby glyph-placement struct.

## Updated interpretation

The strongest remaining hypotheses are now:

1. pre-rendered or separately assembled graphics/tile data that reuses the same font artwork;
2. a compressed asset;
3. a renderer command structure that stores indirect references rather than CP932 bytes or resolved glyph IDs;
4. hardcoded screen setup that builds the banner through pointers/tables outside the obvious menu text block.

The earlier hypothesis of a simple interleaved CP932/glyph-ID stream is now weak.

## Next reverse step

Do not guess a patch offset.

The next useful step is to trace the mode-selection screen setup code and identify which VRAM/tile asset or pointer is responsible for the pink banner. Once that source asset is proven, replace the banner text independently from the direct-text menu labels.

**Runtime claim: none.**
