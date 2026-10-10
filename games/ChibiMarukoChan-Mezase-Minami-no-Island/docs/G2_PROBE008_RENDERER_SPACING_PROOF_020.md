# Probe 008 — renderer pitch proof and safe expansion plan (checkpoint 020)

Date: 2026-10-10. Branch: `chibi-maruko-bootstrap-01`.

## ROM evidence (verified from uploaded CLEAN ROM)

- 2 MiB ROM SHA-256: `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`.
- The previous 12-pixel pitch was **only the offline preview assumption**.
- Renderer X placement comes from **two actual lookup tables**:
  - file `0x29670`: 19 little-endian tile offsets, with values `16 * floor((4 + 13*i)/8)`.
  - file `0x29696`: 19 bit shifts, with values `(4 + 13*i) % 8`.
- All 19 entries in BOTH tables match the formula exactly: the real advance is **13 pixels**.
- Actual consumers at file `0x28E0C` (`BF 70 96 85`) and `0x290EE` (`BF 96 96 85`).
- `tools/probe008_spacing_evidence.py` independently enforces ROM identity and verifies both tables before rendering an offline 13/12/9 comparison.
- Current custom round bitmap comparison with lines `Nói thẳng nhé!`, `Du học chớ ngại!`, `Rèn gu mỹ thuật!`, `M W mư ơ ớ ả ẳ ỹ`, `ƯỚI?`: **0 pixel-ink collisions** at all three pitch settings in this offline model. Font beauty, 9px WRAM/VRAM compositor behavior and full-game runtime are **NOT** confirmed.
- A 9px replacement of both tables is mechanically feasible; the guarded command `--diagnostic-9px` only accepts exact Probe003, checks whitelisted bytes and recomputes checksum. **Global 9px would also change remaining Japanese glyphs**, so this is a diagnostic, NOT a release patch. A Vietnamese-only switch or complete original-language asset audit is required before promotion.

## Additional storage findings — feasibility only

The existing 160-row `0x84` codepage has 32 *native* font entries and 128 custom entries. The fuller font needs **49 missing uppercase letters** plus 3 missing lowercase (`ằ/ẵ/ỵ`): 52 new codepoints. Native copies plus new glyphs would require up to **84** glyph cells in a new page, within one 100-cell 12x12 page if all are unique.

Potential ROM locations read-only verified (contents only, not reachability or ownership):

- raw 0x800-byte page at `0x125000..0x1257FF` currently all `FF`, LoROM pointer `$A4:D000`.
- bank 85 staging at `0x2F800..0x2FBFF` currently all `FF`.
- native font pointer table at `0x295EE`: 10 three-byte page pointers; one usage `BF EE 95 85` at `0x28EA8`, high-page lookup supports low four bits of glyph ID, but **page 0x0A has NOT been executed**.
- lead `0x85` pointer-table entry at `0x29760` currently aliases `0x84` (`0x9A74`). A separate table at `$85:FA00` is a *candidate* route for the 52 extra two-byte codes; **0x85 native-text use has NOT been ruled out**.
- Existing `0x84E1..` entries must NOT be blindly extended: they contain nonzero pre-existing mappings, and at `0x29BE8` the next native map starts. Do not overwrite them.
- Possible one-page route: relocate 10 page pointers to `$85:F800`, append `$A4:D000` for page 0x0A, and repoint *only* the proven `BF EE 95 85` reference. This is an **unproven allocation plan**; don't claim a runnable Probe008 from it.

## Font defects still pending

- Accented capital A crossbar disappears because current five-row compression skips row 4. Use an explicit 5-row capital A retaining the crossbar, and add regression fixtures before installing.
- Lower and uppercase stacked hỏi/ngã need centered tone above circumflex/breve, with dedicated non-overlapping vertical rows.
- 49 missing capitals require safe new lead and glyph page proof, not overwriting Japanese glyphs.

## Reproduce

```sh
python tools/probe008_spacing_evidence.py CLEAN.sfc --preview docs/previews/probe008-spacing/side-by-side.png --report probe008-spacing-report.json
# Optional DIAGNOSTIC ONLY, exact Probe003 input; NOT a release patch:
python tools/probe008_spacing_evidence.py Probe003.sfc --diagnostic-9px Probe008_SPACING_ONLY_UNTESTED.sfc
```

No ROM was committed. No new emulator run was performed. Final bitmap build, independent changed-byte verifier and runtime typography test remain pending. Keep Probe003 strict 2-byte payloads, separators `32/68/104`, D038 and scene logic untouched.
