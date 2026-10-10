# Chibi Maruko-chan SNES — Probe 008 checkpoint 023: parser reachability + selective 9px diagnosis

Date: 2026-10-10. Repository `RVTGMzz/VHSNES`, branch `chibi-maruko-bootstrap-01`.

## Outcome

**Probe008 V2 13px font-only remains the safest static baseline.** This round audited the *actual LoROM lookup chain* for 212 codepoints and made a selective 9px machine-code experiment. The selective experiment **passes byte/static checks but FAILS mixed-line typography** because native Japanese quotation glyphs remain at 13px while adjacent Vietnamese glyphs use 9px. **No Probe008 runtime or release PASS.**

## 1. Codepage -> renderer pointer chain, actual patched ROM

Validated against exact clean ROM SHA-256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`, exact Probe003 SHA-256 `5208bec10147f478cc17955c4f262a5cde08e5b85708caa2717370f6835fbacd`, and exact Probe008 V2 13px font-only SHA-256 `2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd`.

Trace applied to every actual code unit:

`lead 0x84/0x85 -> 0x29756 table -> 16-bit glyph ID -> relocated font-page pointer at 0x2F800 -> LoROM bank/address -> raw 12x12 1bpp bitmap`.

- All **212/212** codepoints resolve to exact expected bitmap bytes; **zero** data/pointer mismatches.
- Physical glyphs: **210** (two aliases among 212 codepoints).
- Page `$A4:D000` (new page 0x0A): **84 lookups**.
- Page `$A5:C000`: **44**; page `$A5:C800`: **84**.
- Both patched overlapping renderer pointer reads `0x28EA8` and `0x28EAE` are preserved.
- `0x8175` and `0x8176` still map to original Japanese quote glyph IDs **0x0159 and 0x015A**, respectively.
- Native 0x85 lead **safety remains UNPROVEN**. Raw scan of files `0x18000..0x283D8` contains 32 consecutive byte pairs of `85 40..73`, mostly opcode/data adjacency, e.g. at `0x18332` is a non-dialogue table. A byte scan does NOT prove those pairs are ever rendered as Japanese text or are safe to reassign.

Reproducible tool: `tools/verify_g2_probe008_codepage_pointer_chain.py`.

## 2. Selective 9px native-safe *diagnostic*, not release

Added `tools/build_g2_probe008_selective_9px_diagnostic.py` on exact Probe008 V2 font-only SHA above. Rather than modifying global 13px tables, this installs two guarded 65816 `JSL` dispatchers:

- word-offset lookup at file `0x28E0C` -> `$85:FB80` (41-byte stub),
- shift lookup at `0x290EE` -> `$85:FC00` (49-byte stub),
- new 9px tables at `$85:FC80` and `$85:FCC0`,
- narrow glyph ranges: `0x083A..0x0863`, `0x090A..0x0963`, `0x0A00..0x0A53`.

Existing 13px tables at `0x29670` and `0x29696` remain **byte-identical**. G2 direct-text fields, separator offsets 32/68/104, scene, font-page pointers and D038 remain unchanged.

Local **diagnostic-only** binary was built:

- SHA-256 `dffdec30af4c3ef4d02c58414a25fa8312dcffdd168691ed4add755de1582328`;
- **157 changed bytes** compared with Probe008 V2 font-only;
- SNES checksum/complement **0xF9AF / 0x0650**;
- full 65816 *subset micro-interpreter* tests: **4,028 Vietnamese lookup cases** (212 codepoints × 19 indices) at 9px, and **190 non-Vietnamese controls** at 13px, all STATIC PASS;
- independent verifier checked exact patch opcode bytes, unchanged 13px ROM table, preserved G2 text and font-page pointers, diff whitelist, checksum, output SHA.

Reproducible tools:
- `tools/build_g2_probe008_selective_9px_diagnostic.py`
- `tools/verify_g2_probe008_selective_9px_diagnostic.py`

### Typography BLOCKER — confirmed 64px misplaced trailing Japanese quote

G2 line three includes `Rèn gu mỹ thuật!` (**16 Vietnamese characters**) immediately followed by original `0x8176` (Japanese closing quote, glyph **0x015A**), which **does not fall in the Vietnamese-only glyph ranges**.

- Fully compact 9px closing quote X: `4 + 9*16 = 148`.
- Per-glyph selective approach closing quote X: `4 + 13*16 = 212`.
- **64px excess gap**. This is a concrete layout defect, not a hypothetical overlap.

An offline PNG from ROM bitmap glyphs compares 13px / per-glyph selective 9px / global 9px. It is retained locally; it is **not an emulator screenshot** and not committed as a commercial ROM asset.

**Do not release the selective probe.** Next iteration needs *line-aware or scene-aware spacing*, so quote glyphs in a Vietnamese text line also follow 9px without altering ordinary Japanese text elsewhere. Preserve original quote/separator code units instead of rewriting them into arbitrary characters.

## 3. Status and next practical steps

| Topic | Status |
| --- | --- |
| Probe003 strict two-byte flow | Prior user runtime path PASS; exact binary rebuilt |
| Probe008 V2 bitmap capacity and 212 mapping chain | STATIC PASS |
| 13px actual game renderer pitch | STATIC PASS |
| Global 9px diagnostic | STATIC PASS only; may affect Japanese UI |
| Selective 9px diagnostic | STATIC code verification PASS, offline mixed-line LAYOUT FAIL |
| Safe 0x85 reallocation under all game data paths | UNPROVEN |
| Font page 0x0A in actual SNES emulator | NOT TESTED |
| Probe008 font/runtime acceptance | NO |
| Remaining title, menus and graphics | Not resumed yet; see HANDOFF_CURRENT |

No SNES emulator is installed or accessible in the runtime used for this probe. **Do not claim runtime PASS, emulator screenshots or complete-game Việt hóa.** No ROM, ROM patch binary or game executable was uploaded to GitHub.

To reproduce with legally supplied *local* ROM binaries:

```bash
python tools/verify_g2_probe008_codepage_pointer_chain.py clean.sfc Probe003.sfc Probe008_V2_13px.sfc pointer-chain-audit.json
python tools/build_g2_probe008_selective_9px_diagnostic.py Probe008_V2_13px.sfc selective9_UNTESTED.sfc selective9-build-report.json
python tools/verify_g2_probe008_selective_9px_diagnostic.py Probe008_V2_13px.sfc selective9_UNTESTED.sfc selective9-independent-report.json
```

**Next task:** investigate reliable per-line/per-scene width flag or a bounded screen-specific layout change that includes original quote IDs, with state/reset semantics and preserved Japanese UI. Do not promote global 9px or per-glyph selective 9px merely because checksum/bitmap tests pass. Run a real emulator as soon as one is available, then revisit G0/G2/G3 graphics and remaining content.
