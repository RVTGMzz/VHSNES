# Chibi Maruko SNES — G2 Probe008 checkpoint 022: LOCAL STATIC BUILD PASS

**Date:** 2026-10-10. **Branch:** `chibi-maruko-bootstrap-01`.
**State:** font-only V2 ROM **BUILT LOCALLY / STATIC PASS**; separate global 9px diagnostic ROM **BUILT LOCALLY / STATIC PASS**; both **RUNTIME UNTESTED**, **NOT RELEASE-READY**. **NEVER COMMIT ROMs**.

## Actual input and exact Probe003 reconstruction

A freshly supplied clean source ROM, 2MiB, SHA-256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`, was rebuilt using the frozen strict-two-byte Probe003 payloads and original thin V5 bitmap codepoints. Rebuilt Probe003 matches checkpoint **exactly**:

- SHA-1 `d0f7969aea3cad0a167dca3889ee9960be6415e0`
- SHA-256 `5208bec10147f478cc17955c4f262a5cde08e5b85708caa2717370f6835fbacd`
- 621 changed bytes vs clean, checksum `0x4FE8`, complement `0xB017`.
- All 3 payloads retain `816F` at 32 / 68 / 104, NUL, strict two-byte units, D038 unchanged.

## Probe008 V2 font-only — local static build result

Exact Probe003 plus `translation/codepage/g2_probe008_complete_candidate_v2.json` (212 codepoints / 210 unique font bitmaps). Created only a local experimental ROM.

- **SHA-1:** `1e21c6ecac3333cd7c1ccb9ca52e5fa37381c76e`
- **SHA-256:** `2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd`
- Size: **2,097,152 bytes**, unchanged.
- **4,034 changed bytes** versus exact Probe003.
- SNES checksum **0x622E**, complement **0x9DD1**.
- **212 mapped Unicode characters / 210 physical font cells**. All codepoint-to-glyph mappings and every 12x12 bitmap read back from ROM correctly.
- Existing 126 unique custom slots were clean and unused in original mapping; retained for custom characters. 32 native-row copies + 52 extra letters occupy **84 of 100** cells of the additional page 0x0A at ROM file `0x125000`.
- Reused original 10 page pointers unmodified; appended new page `$A4:D000` in relocated pointer table `$85:F800`.
- **CRITICAL VERIFIED CORRECTION:** renderer has TWO consecutive page pointer fetch instructions, **0x28EA8** (`BF EE 95 85`) and **0x28EAE** (`BF EF 95 85`); both changed to `BF 00 F8 85` and `BF 01 F8 85`. An earlier script version incorrectly used offset `0x28EAD`; **fixed before successful build**.
- `0x85` lead mapping for new 52 codes uses staged `$85:FA00`; existing 160 code units are not renumbered.
- Original 13px renderer tables untouched, all three dialogue fields byte-identical with Probe003, edit footprint explicitly whitelisted, checksum verified independently.
- Independent local negative tests rejected corruption of a font pixel, bank-pointer operand, dialogue payload, and checksum: **4/4 expected failures**.

## Offline spacing — exhaustive pairwise geometric check

Each of the 212 mapped 12x12 bitmaps was compared against each other **ordered** neighbor: **44,944 pairs per pitch**.

| Advance | Ordered pairs with touching/overlapping ink |
| --- | ---: |
| 13px (current renderer) | 0 |
| 12px | 0 |
| 10px | 0 |
| **9px (requested)** | **0** |
| 8px | 0 |
| 7px negative-control | **769** |

**This is an offline bitmap collision check, not proof of SNES renderer/scene/palette/wrapping behavior or aesthetic approval.** Script: `tools/selftest_probe008_pitch_collisions.py`.

Generated a local PNG comparing the **glyph pixels read back from the patched font ROM** at 13px and 9px across five dialogue examples, and a complete 212-entry glyph atlas. They are offline images, **not emulator screenshots**. Existing SVG previews are committed to `docs/previews/probe008-spacing/`.

## Probe008 V2 font plus GLOBAL 9px — local diagnostic-only build

This is **not the release approach**: both renderer lookup tables are global and also govern remaining native Japanese; a 9px edit needs language-aware gating before promotion.

- V2 13px base SHA-256 `2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd`.
- 9px diagnostic SHA-1 `6b45fd17ed8315c48bedf14eda512a7044d9c45d`.
- 9px diagnostic SHA-256 `7b982dbbcd683fa981b2a20da10850d61b6f34fd9f25970baa5f32dab75440f8`.
- Change surface vs V2 13px: **35 different bytes** in two positioning tables plus checksum, despite 57 candidate table bytes; unchanged positions do not count as diffs.
- Checksum **0x60CE**, complement **0x9F31**.
- Strict Probe003 scene fields unchanged, **runtime UNTESTED**.
- `tools/probe008_spacing_evidence.py` now permits a diagnostic 9px patch from EITHER the exact Probe003 SHA256 OR exact above V2 font-only SHA256.

## Reproduce and finish validation

```bash
python tools/repair_g2_probe008_full_font.py
python tools/audit_g2_probe008_font_expansion.py CLEAN.sfc expansion-report.json
python tools/build_g2_probe008_v2_font_only.py CLEAN.sfc PROBE003.sfc PROBE008_V2_13PX_UNTESTED.sfc build-report.json
python tools/verify_g2_probe008_v2_font_only.py CLEAN.sfc PROBE003.sfc PROBE008_V2_13PX_UNTESTED.sfc verify-report.json
python tools/selftest_probe008_pitch_collisions.py
python tools/probe008_spacing_evidence.py PROBE008_V2_13PX_UNTESTED.sfc --diagnostic-9px PROBE008_V2_GLOBAL_9PX_DIAG_UNTESTED.sfc
```

**Blocked before release:** no SNES emulator is installed/accessible in the current execution environment; neither candidate has been emulated. No photo/screenshot-based typography approval for final V2. 0x85 proprietary control usage and page0x0A execution (not merely static pointer plausibility) remain unproven. Global 9px may break native Japanese UI; design and verify selective Vietnamese-only advance. Use emulator tests on story-start dialogues, remaining native UI, questions/wrapping, tones, horns, punctuation, controls and other modes. Never claim final game completed or `RUNTIME PASS` solely from hash/static pass.

No ROM is included in the GitHub repository. All reports, builders, validators, codepage data and SVG previews remain on the branch.
