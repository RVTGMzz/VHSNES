# Probe 008 — checkpoint 021: V2 font coverage and renderer proof

Date 2026-10-10. Repo `RVTGMzz/VHSNES`, branch `chibi-maruko-bootstrap-01`.

## Done and COMMITTED in this session

1. **Actual renderer spacing proved**, not assumed: 13 px advance (19 entries in `0x29670` and `0x29696` match `4+13*i`). Read `docs/G2_PROBE008_RENDERER_SPACING_PROOF_020.md`.
2. Offline *current V1 bitmap* spacing comparisons 13/12/9px generated. Five sample lines have zero literal overlapping ink pixels at 9px, but this is not a guarantee of runtime wrapping. Preview in `docs/previews/probe008-spacing/spacing_13_12_9.svg`. The user also has a local PNG copy.
3. Tool `tools/probe008_spacing_evidence.py` added. It enforces the source ROM SHA-256 and only allows an optional global 9px **DIAGNOSTIC** write from exact Probe003 (never a final game build). Expected writes: two positioning tables and four checksum header bytes. No new ROM has been built or emulated in this session.
4. Audited all **126 distinct custom glyph IDs** reserved by the 128 custom entries on the clean ROM: 0 bitmap pixels and 0 references in the audit mapping region for every ID. These are existing **RESERVED** slots, not 126 unclaimed spare glyph slots. The old "6 new slots" preflight was a fresh-only count.
5. One potential **additional font page** is feasible by size without increasing the ROM: `0x125000..0x1257FF` is `FF`, as is `0x2F800..0x2FBFF`; 11th glyph page at file `0x125000` / SNES `$A4:D000`, table relocation `$85:F800`, new codepage map `$85:FA00`. Verified the original ten 3-byte page pointers and the sole `BF EE 95 85` consumer at file `0x28EA8`, plus `0x0F` glyph-page nibble mask. This is **capacity/byte-level feasibility, NOT ownership/reachability proof or runtime PASS**.
6. Added `tools/audit_g2_probe008_font_expansion.py` to enforce above checks on exact clean ROM.
7. Created V2 generator `tools/repair_g2_probe008_full_font.py` and committed generated `translation/codepage/g2_probe008_complete_candidate_v2.json`: **212 Unicode entries**, consisting of original 160 plus **49 previously missing uppercase** and **3 missing lowercase** (`ằ/ẵ/ỵ`). **210 unique 12x12 bitmaps**. Extra 52 two-byte units are PROPOSED `0x8540..0x8573`. All original 160 code units remain unchanged.
8. V2 fixes accented uppercase `A` by explicit body rows retaining horizontal crossbar; stacked hỏi/ngã tones are centered over breve/circumflex instead of x=7 side-shifting. Generator and generated data passed structural code/unit/bitmaps, accented-A-crossbar and stacked-mark geometry assertions in the construction pass. **Visual typography and emulator still UNTESTED.**
9. V1 vs V2 defect comparison at `docs/previews/probe008-spacing/glyphs_v1_v2_accent_fix.svg`.
10. Python CP932 decoding test: **zero valid `0x85xx` pairs** for trails 0x40..0xFC, and native lead 0x85 already aliases the 0x84 glyph map. This is supportive but **not a proof that this particular game never uses proprietary 0x85xx data**.

## Key guardrails

- Do NOT modify or commit a commercial ROM; never interpret source `FF` as definitive unreferenced storage.
- Keep source-clean hash and reconstructed Probe003 hash contract.
- `0x85` runtime lead reassignment and page0x0A access remain **UNVERIFIED**; audit usage/indirect reachability before a font build.
- **Global 9px patch affects Japanese native text as well as Vietnamese.** Keep the 13px tables in a release build until a Vietnamese-only, state-aware spacing implementation is designed and tested. A global 9px version is diagnostic only.
- Existing `0x84E1..0x84FC` are not automatically free to overwrite (there is native mapping data and adjacent pointer tables).
- Probe003 strict two-byte text, `8175/8176` quotes, `816F` separators at byte offsets 32/68/104, D038 and palette/scene/controller code are FROZEN.
- A font data file and a PNG/SVG preview are not a running game. No new runtime PASS, no claim of a finished Probe008.

## To resume

First run the read-only scripts on the canonical clean ROM, generate V2 previews, inspect the 0x85 lead's game-proprietary uses, and prove bank85/page0x0A relocation against actual references. Then create a guarded ROM build on exactly verified Probe003 with independent checksum and diff-surface checks, followed by **emulator** testing and user screenshot. Only then continue other remaining game localization tasks in `HANDOFF_CURRENT.md`.

Commands (use files already in repo; ROM only locally):

```bash
python tools/probe008_spacing_evidence.py CLEAN.sfc --preview spacing-comparison.png --report spacing-report.json
python tools/audit_g2_probe008_font_expansion.py CLEAN.sfc expansion-preflight.json
python tools/repair_g2_probe008_full_font.py
```

Expected next-step statuses: **ROM build not performed, runtime UNTESTED, font release FAIL/PENDING**.


## 2026-10-10 continuation: exact Probe003 rebuilt + dual pointer fix

The supplied clean ROM was independently used to reconstruct the exact strict-framing Probe003, using 33 runtime codepoints / thin V5 glyphs from the frozen builder. **Hash matched both existing checkpoint digests**:

- SHA-1: `d0f7969aea3cad0a167dca3889ee9960be6415e0`
- SHA-256: `5208bec10147f478cc17955c4f262a5cde08e5b85708caa2717370f6835fbacd`
- 621 changed bytes vs clean, checksum/complement `0x4FE8/0xB017`.
- Separators exactly 32/68/104, strict two-byte payloads. Source/derived ROMs are kept **local**, never committed.

**Renderer-critical relocation correction:** `$85:8EA8` (`BF EE 95 85`) accesses the low-word page-pointer address, **AND** `$85:8EAE` (`BF EF 95 85`) reads the overlapping pointer bank byte. On page-table relocation both opcodes must be repointed (`BF 00 F8 85` **and** `BF 01 F8 85`); relocating only the first would use the wrong bank for page 0x0A. The guarded builder now patches both.

New tools committed:

- `tools/build_g2_probe008_v2_font_only.py` — exact clean + exact Probe003 inputs, install all 212 mapped glyphs through existing 126 reserved custom cells and expanded page 0x0A, 52-codepoint separate 0x85 map, 13px unchanged, checksum and diff whitelist. **FONT-ONLY EXPERIMENT — NOT FOR PUBLIC RELEASE**.
- `tools/verify_g2_probe008_v2_font_only.py` — independent checksum, both pointer-opcode fixups, bitmap roundtrip, 210 physical glyphs, all 212 mapped Unicode characters, exact original Probe003 payloads, scope verification, unchanged 13px tables.

Usage on a local machine with all binary inputs:
```bash
python tools/build_g2_probe008_v2_font_only.py clean.sfc Probe003.sfc Probe008_V2_FONT_ONLY_UNTESTED.sfc probe008-build.json
python tools/verify_g2_probe008_v2_font_only.py clean.sfc Probe003.sfc Probe008_V2_FONT_ONLY_UNTESTED.sfc probe008-verify.json
```

**Important:** builder and independent verifier added to repo, but full candidate V2 ROM has **not been built/emulated in this turn**, and scripts have not yet passed a real end-to-end local run. No new ROM runtime PASS, CI PASS or font release PASS is claimed. Next action is run both tools with supplied baseline in an environment containing the full repo, inspect font images, prove 0x85 native-safety and page0x0A renderer access, then emulator test. The actual 9px layout remains unimplemented in release version.
