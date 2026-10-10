# Probe 008 — font and spacing checkpoint, 2026-10-10

## User direction

The user finds the text too widely spaced. Preserve thin, legible letterforms and investigate a smaller advance, initially 9 pixels, before widening the glyph bodies further. **9 px is a proposed experiment, not an implemented or verified renderer patch.** The user requests saving all current work to RVTGMzz/VHSNES now to conserve weekly usage and resume later.

## Verified source and baseline

User supplied `Chibi Maruko-chan - Mezase! Minami no Island!! (Japan).sfc`.

- Clean SHA-256: `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956` — exact contract match.
- Rebuilt Probe 003 using the existing strict two-byte builder.
- Probe 003 SHA-1: `d0f7969aea3cad0a167dca3889ee9960be6415e0`.
- Probe 003 SHA-256: `5208bec10147f478cc17955c4f262a5cde08e5b85708caa2717370f6835fbacd` — exact checkpoint match.
- No new emulator test was performed. Uploaded source was not modified. ROMs are not committed.

## Current font findings

The custom candidate contains 163 mapped entries / 161 unique bitmaps. This is not full Vietnamese coverage: 49 Vietnamese uppercase characters are missing.

Confirmed bug: accented uppercase A loses its crossbar because the five-row compaction takes source rows 0,1,3,5,6 and omits row 4. Replace that generic compaction with explicit accented-capital bodies.

Visual issues remain: stacked hoi/nga on a-breve/a-circumflex/e-circumflex/o-circumflex drift right; preview spacing looks excessive. Preview scripts assume a fixed 12 px advance; this is NOT a measurement of runtime cursor advance. Verify actual renderer behavior before changing machine code. Current font is not release-ready.

## Actual ROM preflight

`plan_g2_probe008_font.py` was run against the verified reconstructed Probe 003.

- Entry count: 163.
- Unique bitmaps: 161.
- Fresh blank unreferenced candidate slots: **6**.
- Capacity check: **FAIL** for the fresh-slot-only strategy.
- The scan deliberately excludes ALL slots listed in the existing codepage, including custom slots. Six is therefore not a claim that the game has only six reusable slots in total.
- Next investigate safely reusable custom slots or a verified font-page expansion.
- Proposed additional codes for `ằ/ẵ/ỵ` still require mapping-table capacity proof.
- Do not overwrite native Japanese cells or expand mappings without verifying boundaries.

## Next work, in order

1. Inspect the renderer at file `0x28E7B` / CPU `$85:8E7B` and its callers to measure cursor advance and line layout. Do not assume bitmap width equals advance.
2. Make an offline 12 px versus 9 px comparison with the same glyphs. Check horn, stacked tones, `M/W/m/ư`, adjacent marks, spaces, wrapping and quotes. A preview is not runtime evidence.
3. Fix accented A crossbars and stacked tone placement; keep complete family shapes coherent. Fill missing uppercase only with a validated codepage/slot plan.
4. Audit custom-slot reuse or font storage expansion before building Probe 008.
5. Preserve Probe 003 strict 2-byte framing, separator offsets 32/68/104, D038, palette, scene and controller behavior.
6. Verify ROM diff and checksum independently, then test in an emulator. No runtime PASS before observed evidence.

## Existing work

- `tools/generate_g2_probe008_font.py` and `tools/preview_g2_probe008_font.py`: first candidate.
- `tools/customize_g2_probe008_font.py`: wider custom candidate and comparison images.
- `tools/plan_g2_probe008_font.py`: read-only slot planning, never creates a patched ROM.
- `tools/selftest_g2_probe008_preflight.py`: local regression checks PASS.
- `tools/selftest_g2_conversation_direct_probe_003.py`: local strict-framing checks PASS.
- `docs/previews/probe008-custom/`: comparison and atlases.

Earlier GitHub push attempts were blocked by automatic approval review. On 2026-10-10 the user explicitly requested updating this repository. This checkpoint supersedes earlier claims that the input ROM is unavailable. Probe 008 has NOT been built, and spacing has NOT been patched.
