# G2 Probe 005 Clean Dialogue Font Checkpoint 016

Updated: 2026-09-23 +07

## Probe 004 runtime result

User screenshot result:

**Typography remains unacceptable.**

The one-sided thickening experiment produces blocky, merged letterforms and is rejected.

Therefore:

- Probe 004 scene/text path: inherited from Probe 003 and still reaches the dialogue
- Probe 004 typography: **RUNTIME FAIL**
- do not continue dilation/thickening experiments

## Direction change

Probe 005 abandons V5-thin-derived morphology.

The text path remains the already-proven Probe 003 strict 2-byte path.

Probe 005 replaces only the visible dialogue glyph bitmaps with a newly rasterized 12x12 set designed for readability:

- consistent body weight;
- fixed 12x12 cells;
- clear Vietnamese accents;
- explicit distinct bitmaps for tone-mark variants;
- no one-sided dilation;
- no V5 thin source;
- no Probe 009 stretched/heavy source.

The source font file is not stored or committed. Only the resulting 1bpp 12x12 bitmap JSON is committed.

## Consistency fix

To avoid mixing SNES-native Latin shapes with the new dialogue face, Probe 005 temporarily remaps these codepage entries to clean blank custom slots:

- `!`
- `L`
- `y`
- `R`
- `T`

All other needed dialogue glyphs use their existing Probe-003 custom slots.

This diagnostic remap is scoped to the Probe 005 runtime test and is not yet a whole-game font/codepage freeze.

## Files

Added:

- `translation/codepage/g2_probe005_dialogue_glyphs.json`
- `tools/build_g2_probe_005_clean_dialogue_font.py`
- `tools/selftest_g2_probe_005_dialogue_font.py`

## Local artifact

`Chibi_Maruko_G2_DIRECT_TEXT_PROBE_005_CLEAN_DIALOGUE_FONT.sfc`

Built directly on the verified Probe 003 ROM.

Static facts:

- glyphs: **32**
- font diff bytes vs Probe 003: **471**
- mapping diff bytes vs Probe 003: **10**
- total diff bytes vs Probe 003: **485**
- SHA-1: `36c2aff02d471e6d49bab48c783c1179eb0e91f4`
- SHA-256: `c98934c7233f032a2dd6b369f8b7858042aed606bb1dfe69301be55d3b9b1940`
- checksum/complement: `0x68E4 / 0x971B`

Diff surface is limited to:

- 32 dialogue glyph cells;
- five 0x84 codepage mapping overrides;
- SNES checksum/complement.

No direct-text payload bytes are changed relative to Probe 003.

No D038 / scene / palette / controller bytes are changed.

## Claims

- Probe 003 strict text path: **RUNTIME PATH PASS**
- Probe 004 typography: **RUNTIME FAIL**
- Probe 005 static build: **PASS / READY FOR TEST**
- Probe 005 typography: **RETEST REQUIRED**
- whole G2 Runtime PASS: **NO**

If Probe 005 is readable, freeze this as the dialogue-font direction before expanding it beyond the 32 tested glyphs.
