# Chibi Maruko-chan SNES — Checkpoint 029: isolate Vietnamese G2 quotation glyphs

Date: 2026-10-10. Repo `RVTGMzz/VHSNES`, branch `chibi-maruko-bootstrap-01`.

## Why 028 cannot be shipped as-is

Checkpoint 028 selects 9px for glyph IDs `0x0159` (original Japanese opening quote `8175`) and `0x015A` (closing quote `8176`) everywhere, not just Vietnamese G2. A raw scan of the **clean** 2MiB game ROM finds:

| Native code pair | Raw occurrences total | Outside the 3 G2 test fields |
| --- | ---: | ---: |
| `8175` | 124 | 121 |
| `8176` | 126 | 123 |

These are raw bytes, not all necessarily reachable or rendered text; the numbers nevertheless demonstrate a serious risk if native quotation marks are shortened globally. **Do not promote checkpoint 028's hook to release.**

## 029 solution — two duplicated quote glyphs exclusive to three G2 fields

Builds on exact **028 V3 medium + 9px geometry** ROM SHA-256 `59f4c45b14a24e6cf67de1c9c7cbe1d9b862eaa2eb4c6518bbc4bcbd6dd006fb`. Both original Japanese glyphs stay as-is and return to **13px** in the font renderer.

- Duplicates bitmap `0x0159` → `0x0A54` and `0x015A` → `0x0A55`. The destination cells were the first two of 16 unallocated cells in the extra 0x0A font page `$A4:D000`. Copies checked bit-for-bit, original Japanese cells unchanged.
- Extends staged **lead `0x85` mapping** with two allocated codes `8574 → 0A54` and `8575 → 0A55`. Their corresponding entries at ROM `0x2FA68..0x2FA6B` were `00 00` and must be checked vacant. The use of this lead outside G2 is **still not globally proven safe**.
- Changes exactly **six G2 quotation code-pairs**: 3 openings `8175 → 8574` and 3 closings `8176 → 8575`. This is an intentional **byte change to the original quoted text data**, unlike the earlier "Probe003 text entirely byte-frozen" diagnostics. However, each field stays **106 bytes**, each token stays **strict two bytes**, and every `816F` line delimiter remains untouched at offsets **32/68/104**. The visible quotation glyphs remain pixel-identical to the original Japanese glyphs.
- **No other dialogue words, padding bytes, scene controls, D038, palette, native 13px lookup tables, codepage assignments, font page pointers, or two original Japanese quote codes are modified.**
- Font selector now uses 9px for 0x083A..0863, 0x090A..0963, 0x0A00..0A55. Does **not** include native glyph IDs 0x0159/0x015A. Byte/word selector stubs generated from actual glyph/atlas geometry and both restore the original 13px table for Japanese quote IDs.
- Because the original source bytes change, a tester comparing exact Probe003 checksum/source-payload SHA must exempt only these six 2-byte quote-code substitutions. The previous strict "all 3 records identical" invariant is now **relaxed narrowly and explicitly**. All control byte preservation remains mandatory.

## Offline output — static QA only

Local 029 ROM (NOT on GitHub):

- **SHA-256:** `a23304cedff0eac959a6455d90b866c49543ca381425b089771b65da264e928e`
- Changed bytes vs exact 028 combined: **180**.
- SNES checksum/complement: **`0x9309 / 0x6CF6`**.
- Word hook size: **61** bytes; shift hook size: **86** bytes. Previously 71/120.
- Two new 9px-only quote font cells: `0A54/0A55`; two extra codepage bytestrings `8574/8575`.
- New string framing: exactly 6 intentional 2-byte quote replacements, 3×106B fields, separators retained at 32/68/104.
- Original Japanese `8175/8176` still render to glyph IDs `0159/015A` and are routed to **13px** in both hooks.
- All 150 G2 drawable two-byte tokens across 3 records route to 9px; separators excluded.
- 029 machine-code subset test: **83,600 test cases PASS** (11 pages×100 valid slots×19 horizontal positions×2 X-register widths×2 font stages), including 13px for original native quotes and 9px for new duplicates.
- Output ROM guards: exact SHA identity, original 028 hook bytes, staging footprint, vacant lead slots and font slots, two-bitmaps roundtrip, allowed-byte whitelist, checksum, no native glyph modification.
- **Real SNES emulator/runtime:** NOT TESTED. This does not prove the 9px renderer works in game; checkpoint 025 still has the user's confirmed runtime typography FAIL.

## GitHub tools

- `tools/build_g2_probe008_029_isolated_quotes_diagnostic.py`: standalone opt-in gated builder, exact binary input/output hash, no commercial ROM embedded; uses prior 028 code.
- `tools/selftest_g2_probe008_029_isolated_quotes_opcode.py`: independently executes 83,600 65816 subset tests on generated code and checks six G2 quote substitutions.
- The same script can only be run with exact user-owned ROM bytes. Do not commit ROM binaries, commercial font bitmaps or the user's private screenshot.

```bash
python tools/build_g2_probe008_029_isolated_quotes_diagnostic.py \
    028_V3_COMBINED_LOCAL.sfc 029_G2_QUOTES_UNTESTED.sfc 029-build-report.json \
    --allow-untested-diagnostic
python tools/selftest_g2_probe008_029_isolated_quotes_opcode.py \
    028_V3_COMBINED_LOCAL.sfc 029-opcode-report.json
```

## Risk and next action

**Do not send a new "fixed ROM" as an accepted candidate.** The runtime selection/stack/DP assumptions at the original $85:8E0C and $85:90EE still require a real SNES debugger. This runtime has **no SNES emulator available**, and external download attempts are blocked by DNS resolution, so actual emulator certification cannot be performed here.

Before release: obtain an emulator CPU trace at both lookup hooks, validate 029 9px, inspect tone/accent readability and word wraps, check Japanese menus/stories (especially punctuation) and ensure no codepage lead `0x85` collision. If a runtime test fails, roll back and diagnose, not blindly increment versions.

**Status:** 029 STATIC PASS, REAL GAMEPLAY UNTESTED, **NOT RELEASE READY**; 025 remains runtime FAIL. Finish G0/title, G2/G3/minigames only after resolving the font blocker.
