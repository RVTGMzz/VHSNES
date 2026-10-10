# Chibi Maruko-chan SNES — Checkpoint 027: safe medium-weight font prototype + renderer callflow re-audit

Date: 2026-10-10. Repo: `RVTGMzz/VHSNES`; branch: `chibi-maruko-bootstrap-01`.

## Context: the user screenshot FAILURE of Probe008 025 remains authoritative

- Checkpoint 025 ROM (`d4bd629003812578580e7a380e791d87fdf64614441394f1261df3951b9815dc`) shows **unacceptably scattered/thin Vietnamese strokes with excessive spacing** in a **real user screenshot**.
- The prior screenshot-width heuristic (~13px, not intended 9px) suggests the original 13px table is still used. It does **not** prove which CPU predicate failed.
- Do **not** revive or send the 025 ROM. The original 025 builder is quarantined. **Checkpoint 026 failure is not superseded.**
- No emulator was installed in this execution environment; no new runtime claim is possible. A current screenshot, not a synthetic CPU microtest, decides real font acceptability.

## 1. Inspecting actual ROM renderer flow

Read exact source ROMs and the 65816 instruction spans:

- G2 parser source `$85:8340` reads `$1F94` then `LDA $0000,Y`; precise live source bank/offset is **still unknown**.
- Char parser routes through `$85:83D8`, then draws at `$85:8E7B` (`0x28E7B`) using the glyph ID in `$1FB2`, column `$1F9A` and row `$1F9C`.
- Word pixel-offset table load at `0x28E0C` is actually inside the helper `$85:8E05`, which the renderer calls. The bit-shift load at `0x290EE` runs later after a data-bank switch.
- The parser's line column counter increments at `0x2841A`, and it wraps after 19 columns. This counter path is distinct from the font pixels' physical pitch; shortening a bitmap width without changing the table positions cannot solve huge gaps.
- The 025 byte hook condition depends on a **saved data bank on the actual 65816 stack**. Prior subset-interpreter tests are insufficient to establish that the saved bank and `$1F94` in a real scene select the expected 9px table.

**Open issue:** observe DBR / `$1F94` / stack-derived bank in an emulator debugger at `$85:8E0C` and `$85:90EE`, identify where fallback happened, then build a *minimal* patch that handles original Japanese closing quote `8176` without global regression. Do not pretend static evidence resolves this.

## 2. Font V3 experimental redesign — NO ROM patch

Built several **offline bitmap-only** font comparisons using all 210 physical glyphs from the actual Probe008 V2 font ROM. Five known G2 dialogue samples:

- `Nói thẳng nhé!`
- `Du học chớ ngại!`
- `Luyện phản xạ!`
- `Tập khỏi rơi!`
- `Rèn gu mỹ thuật!`

Compared V2 at 13px (what screenshot most resembles), V2 at 9px, V3 medium weight at 9px, V3 dense at 9px. Generated local PNG `Chibi_Probe008_V3_Font_Weight_Prototype_027.png` with **four complete unclipped panels** in a 2x2 layout. It is **NOT** a screenshot from emulator.

Pure data generator added:
`tools/propose_g2_probe008_v3_medium_font.py`

The generator:
- accepts ONLY the exact Probe008 V2 font-only ROM SHA256 `2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd`;
- checks all **212** codepoint bitmaps resolve identically to `translation/codepage/g2_probe008_complete_candidate_v2.json`;
- preserves **all 32 originally-native glyph cells** relocated to page 0x0A, unchanged byte-for-byte, and keeps all original code assignments;
- strengthens body pixels **only** (y≥4; adds a right-side pixel for x≤8) on **178 custom glyphs** (180 codepoint aliases); accents y=0..3 are not widened;
- proposes a V3 bitmap JSON and a QA JSON; no ROM modified or produced, no font pointer/lead/scene change.
- independently tested custom-only subset locally: 178 physical glyphs changed, **5,055** total ink pixels vs V2 3,651, zero overlaps among **210×210 = 44,100 ordered glyph pairs at 9px**.
- Current preview follows the same native-protected policy as the proposed V3 medium JSON: 32 native glyphs unchanged and 5,055 total ink pixels.

The exact native-protected V3 medium preview has 5,055 pixels, while the native-protected V3 dense option has 6,174 ink pixels. The all-glyph version was only an early prototype and is no longer the pictured artifact. V3 medium is a working candidate, not approved.

### Reproduce data-only proposal

```bash
python tools/propose_g2_probe008_v3_medium_font.py \
  Probe008_V2_FONT_ONLY.sfc \
  translation/codepage/g2_probe008_v3_medium_candidate_LOCAL.json \
  docs/g2_probe008_v3_medium_local_qa.json
```

Outputs are text/JSON only. Never commit a commercial ROM. Source script can be peer-reviewed and re-run on a legally available ROM.

## 3. Next required gates

1. Validate font data script, compare representative Vietnamese pairs and UI punctuation at 9px, especially stacked hỏi/ngã, upper-case A, and hỏi/ngã combinations.
2. Resolve actual **live font-table selection**; the most important outstanding bug is still the **13px-like in-game output**. Do not assume 025's bank-source checks are correct.
3. Only after trace + source-specific safe patch should V3 medium be integrated into an **explicit experimental ROM**, strictly whitelisted to the allocated custom glyph bitmaps plus checksum.
4. Test in emulator or via user screenshot with a specific regression matrix (five sample lines, Japanese UI, line wrapping, punctuation, crash, title/menus). No Runtime PASS for V3 yet.
5. Continue G0/title, G2/G3 graphics and remaining untranslated scenes after font gate.

**Current status:** V3 medium design `STATIC BITMAP PAIR TEST PASS`; original 025 gameplay `FAIL`; new V3 gameplay `NOT TESTED`; no new ROM sent to user. No CI status checks should be claimed without verifying them.
