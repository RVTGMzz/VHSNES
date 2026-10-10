# Chibi Maruko-chan SNES — Checkpoint 028: glyph geometry + V3 medium staged, emulator NOT run

Date: 2026-10-10. Repo: `RVTGMzz/VHSNES`; branch `chibi-maruko-bootstrap-01`.

## User evidence still controls quality

**Checkpoint 025 remains a confirmed RUNTIME TYPOGRAPHY FAIL**, based on the user's real screenshot: Vietnamese glyphs are fragmented and spaced close to 13px instead of intended 9px. The 025 source-bank/WRAM-pointer gate was not proved by its microtests and it remains quarantined. Do NOT issue the 025 binary again, assume the G2 text looks acceptable, or claim the new 028 binaries passed gameplay.

## 1. 65816 font renderer — better source of actual glyph ID

A crucial correction to former checkpoint 023: **`$001FB2` is not a proved glyph ID**. Its write sites are the separate routines at file offsets `0x28026` and `0x28579`. The actual G2 parser obtains glyph ID in A from codepage mapping (`0x28407 LDA [$02],Y`), then calls `JSL $85:8E7B` (`0x28413`); the renderer starts `PHB; PHX; PHY; PHA` at `0x28E7B`, thus preserving **incoming actual glyph ID in its own hardware stack frame**. Only afterward does it read `LDA.l $001FB2` to feed its separate helper `JSL $85:8E05`.

The first 13px word table load is at `0x28E0C` inside that helper. At a nested JSL hook with PHP, the saved actual glyph is at:

- `$0A,S` if original X was 8-bit;
- `$0C,S` if original X was 16-bit.

These depths include the nested JSL return frames and original PHX/PHY/PHA. The hook checks the saved X-width flag, uses `REP #$20` before a word read, then restores P via `PLP`.

At the **second** shift-table lookup `0x290EE`, the original renderer has already converted glyph ID into a 3-byte font-page pointer in DP `$18/$19/$1A` and a 12px atlas cell position in DP `$08` (x) and `$0A` (y). This second source is independent of the source text bank DBR and of the `$1F94` parser pointer, avoiding checkpoint 025's assumed scene-bank predicate.

- Original V2 font page 08: glyph cells 58–99 -> custom 9px.
- Page 09: cells 10–99 -> custom 9px.
- Page 0A: cells 0–83 -> 9px; cells 84–99 not allocated.
- Original Japanese quotes: glyph IDs `0159` and `015A`, corresponding to page01 cell89/90 -> also 9px **in any scene that renders these glyphs**.
- Everything else -> original 13px.

**Limit:** The quote rule is glyph-wide, **not G2-scene-only**. Japanese content elsewhere that uses these exact opening/closing quotation glyphs will also receive 9px coordinates. This must be tested for regressions in normal Japanese UI/story. A final scene-scoped solution is preferable if broader text is adversely affected. Do not claim all Japanese content is pixel-identical.

## 2. Code / data checks

Read-only `tools/audit_g2_probe008_renderer_glyph_geometry_028.py` checks the actual code/signatures, font-page pointers, cell BCD table, and all 1,100 page/cell glyph IDs. Result:

- **1,100/1,100** first-vs-second-stage 9px/13px classifications match exactly.
- **218 IDs** select 9px (including original quote glyphs); **882** other valid page/cell IDs select 13px.
- All three original G2 dialogue source records at `0x181CE`, `0x18247`, `0x182C0` have 53 strict 2-byte code units, with separators at indices 16/34/52; each of the 50 other code units per record maps to glyphs covered by the 9px selector. Original bytes are unchanged.
- No new persistent WRAM flag or assumed reset logic.

Guarded, explicit opt-in `tools/build_g2_probe008_glyph_geometry9_diagnostic.py` builds an **UNTESTED diagnostic only**, never a verified ROM release:

- Requires exact 2 MiB Probe008 V2 font-only SHA256 `2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd`.
- 65816 word hook at `$85:FB80` **71 bytes**; shift hook at `$85:FD00` **120 bytes**.
- Original JSL callsites at file `0x28E0C` and `0x290EE`; 9px lookup tables `$85:FC80/$85:FCC0`. Existing Japanese 13px tables remain byte-for-byte.
- Exact staged output SHA256 `a3d2e75da5f9dac36750ef77e249fae7613ffd35f8185c50cd6f6197ca8a8688`, **258 diff bytes** vs V2 13px, checksum/complement `0xC1E2/0x3E1D`.
- G2 direct ROM dialogue 3×106 bytes, codepage, controls/separators and palette/scene unchanged.
- Full subset opcode-interpreter regression of **83,600** cases: 11 font pages ×100 cells ×19 positions ×2 X modes ×2 lookup hooks; **0 model mismatches**. It executes the generated machine-code subset, but not a real SNES emulator. Script `tools/selftest_g2_probe008_geometry9_opcode_028.py`.

## 3. Optional V3 medium glyph bitmaps staged on top of 028

A second exact-hash-guarded, opt-in script `tools/build_g2_probe008_v3_medium_geometry9_experiment.py` imports V3 proposal generator from checkpoint 027, applies only the increased-weight **178 custom physical glyphs**, preserves 32 original native page-0A glyphs, and whitelists modified font atlas regions plus checksum. This also leaves original G2 text and the renderer hooks untouched.

- Combined local **EXPERIMENTAL/UNTESTED** ROM SHA-256: `59f4c45b14a24e6cf67de1c9c7cbe1d9b862eaa2eb4c6518bbc4bcbd6dd006fb`.
- Diff vs 028 geometry-only ROM: **1,183 byte positions**.
- Checksum/complement: `0x7587 / 0x8A78`.
- V3 medium: **5,055 total bitmap ink pixels**, **210/210 full 12×12 glyphs roundtrip**, **0 glyph-pair ink collisions in 44,100 ordered pairs** at 9px.
- No source ROM or experiment ROM committed to GitHub. No real gameplay screenshots of this build exist.

### Reproduce only for controlled offline experiments

```bash
python tools/audit_g2_probe008_renderer_glyph_geometry_028.py V2_13px.sfc audit028.json
python tools/selftest_g2_probe008_geometry9_opcode_028.py V2_13px.sfc opcode028.json
python tools/build_g2_probe008_glyph_geometry9_diagnostic.py V2_13px.sfc geom028_UNTESTED.sfc geom028.json --allow-untested-diagnostic
python tools/build_g2_probe008_v3_medium_geometry9_experiment.py V2_13px.sfc geom028_UNTESTED.sfc V3_geom028_UNTESTED.sfc combined028.json --allow-untested-diagnostic
```

Do not upload ROM binaries to GitHub or distribute this as an accepted Vietnamese patch.

## 4. Remaining honest blockers and next gate

1. **No supported SNES emulator is available in the current container.** The new renderer / font remain **NOT RUNTIME TESTED**. The user's failure screenshot for checkpoint025 is not erased by the synthetic successes here.
2. Test in a debugger with live A and stack at `$85:8E0C`, DP `$18/$08/$0A` at `$85:90EE`, verify actual selected table values and correct spacing in G2.
3. Confirm combined V3 9px graphics at real in-game zoom: clear letters, upper-case A, tone marks, quotation marks, line wrapping, accented clusters, original Japanese dialogue and UI.
4. Confirm new 0x85 lead/page use does not collide with dormant Japanese game content.
5. Only with **real screenshot PASS and Japanese content smoke tests** promote a release candidate; then resume G0/title, G2/G3 graphics and remaining untranslated menu/game text.

**Status:** 028 geometry and V3 medium **STATIC PASS only**. Probe008 025 **USER RUNTIME TYPOGRAPHY FAIL**. No SNES emulator used, no release claim, no repository ROM.
