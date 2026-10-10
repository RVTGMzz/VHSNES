# Chibi Maruko-chan SNES — Probe008 checkpoint 025: bank-switch and X-width-safe G2 9px

Date: 2026-10-10. Repo `RVTGMzz/VHSNES`, branch `chibi-maruko-bootstrap-01`.

## Correcting checkpoint 024 — real renderer changes DBR mid-glyph

**Do not use the 024 diagnostic binary** (SHA-256 `feb7215a67046128ff67113fd921b6479d956df6018a3ae4e74992d03b0c978a`). It passed isolated hook tests but that test incorrectly assumed the live data-bank register (DBR) remains `$83` at both table lookups.

Disassembly of the real font renderer establishes:

- At file `0x28E7B`, renderer starts `PHB; PHX; PHY; PHA` — it saves incoming DBR and X/Y/A.
- After the first table lookup, its `PLA` at `0x28E87` restores A.
- At file **`0x28E95`**, instruction stream **`F4 00 7F AB AB`** is `PEA $7F00; PLB; PLB`. DBR is switched to **`$7F`** before the second lookup at `0x290EE`.
- Consequently a second hook that tests the *live* DBR would reject the Vietnamese source-bank `$83` and erroneously use 13px while the word lookup uses 9px, corrupting within-glyph positioning. **That is a STATIC REJECTION of checkpoint 024's machine-code approach, despite its earlier microtests.**

## Corrected and X-width-adaptive source-bank selector

The first lookup at `0x28E0C` continues to read the live DBR before the bank switch. The second lookup at `0x290EE` instead recovers the original bank saved by the renderer's entry `PHB` on the CPU stack. It dynamically handles the original X register width:

- At byte-hook entry, `PHP; SEP #$20; LDA $01,S; AND #$10` tests the X-width flag saved in P.
- If **X is 8-bit**, original `PHX/PHY` each saved one byte: read original DBR using `LDA $07,S`.
- If **X is 16-bit**, `PHX/PHY` each saved two bytes: read original DBR using `LDA $09,S`.
- Then compare that original DBR to `$83` and compare parser's `$1F94` to the three exact G2 106-byte source ranges. This includes native `8175/8176` quotes at 9px **within** those records while original Japanese elsewhere keeps 13px.
- The hooks preserve caller flags through `PHP/PLP`; no newly reserved persistent WRAM bit or manually reset scene flag is used.
- Runtime-dependent assumption still **unverified**: at actual dialogue execution the parser must use bank `$83` and `$1F94` as its source pointer, as expected from its `LDY $1F94; LDA $0000,Y` path. Verify with a real emulator debugger.

All ROM source work builds only from the exact Probe008 V2 13px font-only baseline SHA-256 `2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd`.

## Corrected local diagnostic build (replaces 024)

- Name: **G2 source-scoped 9px with renderer stack-bank fix and adaptive X width**.
- SHA-256: **`d4bd629003812578580e7a380e791d87fdf64614441394f1261df3951b9815dc`**.
- Size `0x200000` (2 MiB), unchanged.
- Changed bytes from V2 base: **191**.
- Checksum/complement: **`0xED96 / 0x1269`**.
- Word/byte hook lengths: **57 / 67 bytes**. Both fit their reserved 128-byte stages.
- Source ranges: `$83:81CE..8238`, `$83:8247..82B1`, `$83:82C0..832A` (upper ends exclusive), each 106 bytes.
- ROM data: **all three Probe003 dialogue records unchanged**, original strict 2-byte quotes and `816F` at offsets 32/68/104 unchanged, 13px native lookup tables unchanged, D038/scene untouched.
- Static 65816 subset-interpreter test cases: **18,696 PASS**. Includes both **X8/X16 saved-bank modes** at the BYTE hook across every source byte in all 3 records, all 19 column positions, and negative bank/range boundaries.
- Independent exact machine-code verifier: **PASS**; original stack/bank-switch opcode signatures, callsites, new lookup tables, byte-whitelisted ROM diff, checksum/complement and SHA match.
- Mutation tests: **5/5 PASS** (reject deliberate corruption of text, JSL hook, injected code, 9px table and header checksum).
- Offline bitmap layout: original closing quote after `Rèn gu mỹ thuật!` is at x148 rather than x212 in the source-range-scoped 9px model. This remains **NOT an emulator screenshot**.

### Reproducible scripts already updated on the branch

```bash
python tools/build_g2_probe008_line_scoped_9px_diagnostic.py Probe008_V2_13px.sfc G2_9px_Xwidth_UNTESTED.sfc g2-build.json
python tools/verify_g2_probe008_line_scoped_9px_diagnostic.py Probe008_V2_13px.sfc G2_9px_Xwidth_UNTESTED.sfc g2-verify.json --negative-tests
```

**No ROM uploaded to GitHub.** Source tools, reports/checkpoints and non-ROM previews only.

## Status and next task

- Probe003 strict 2-byte text path: prior screenshot runtime path PASS.
- Probe008 V2 codepage/bitmaps: STATIC PASS, emulator UNTESTED.
- Checkpoint 024 first source-scoped-9px diagnostic: **SUPERSEDED / WRONG DBR ASSUMPTION** — never promote.
- Checkpoint 025 X-width-adaptive saved-bank selector: **STATIC PASS ONLY**, emulator UNTESTED, **NOT RELEASE READY**.
- Exact G2 DBR and source pointer in a real CPU trace: **UNPROVEN**.
- Safe use of new 0x85 codepage across game: **UNPROVEN**.
- Font aesthetics/wrapping/line breaks/gameplay/other Japanese modes: **NOT RUNTIME TESTED**.

Next: boot a real SNES emulator debugger; verify the bank switch during text draw, `$1F94` points into correct direct-ROM G2 records, and 9px positions are used for native quotes; verify no crashes and that other Japanese screens remain at 13px. Only then broaden line-scoped patch to additional audited Vietnamese fields, finish font QA and resume the remaining G0 title, G2/G3 graphics and minigames.

**Do not claim CI PASS**: no GitHub status checks were observed for the final branch commit at creation time. Do not claim whole-game Runtime PASS.
