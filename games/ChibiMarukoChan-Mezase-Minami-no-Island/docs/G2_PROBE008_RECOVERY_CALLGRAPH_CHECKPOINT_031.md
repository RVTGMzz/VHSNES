# Chibi Maruko-chan SNES — checkpoint 031: exact V2 recovered, exclusive direct call chain, alias preflight

Date: 2026-10-11. Repo `RVTGMzz/VHSNES`, branch `chibi-maruko-bootstrap-01`.

## Outcome

**Recovered a verifiable clean testing baseline** without asking the user for further files, and added two independent preflight checks for the 029 quote-isolated renderer plan. No SNES emulator was installed or executable in the current container, and external package download/DNS is blocked. The **029 experimental ROM still has no real gameplay pass; 025 remains user-confirmed typography FAIL.**

## 1. Exact ROM recovery FROM user's already-tested failed 025

Actual local uploaded binary:

- Previous user-tested, FAILED 025 SHA-256 `d4bd629003812578580e7a380e791d87fdf64614441394f1261df3951b9815dc`, 2,097,152 bytes.
- Original clean ROM SHA-256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`, same length.
- Undo only two injected JSL lookups at `0x28E0C`/`0x290EE`, the four guarded staging spans, and recalculate SNES header checksum. Exactly **191 changed byte positions**, completely within the 025-known patch surface.
- Recovered ROM **exactly matches previous canonical Probe008 V2 FONT-ONLY** SHA-256 `2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd`. Header checksum/complement **0x622E/0x9DD1**.
- This is a recovery baseline, **NOT** a new runtime-good game or release candidate.
- GitHub tool: `tools/recover_g2_probe008_v2_from_failed025.py`. No binary/ROM added to GitHub.

## 2. Direct 65816 caller graph — actual clean and V2 ROM

Executed a new read-only local audit on both real ROMs:

- Exactly **one direct `JSL $85:8E7B`**, at ROM file **0x28413** (parser -> glyph renderer).
- Exactly **one direct `JSL $85:8E05`**, at **0x28E83** (renderer -> tile helper).
- No same-bank direct `JSR $8E7B` or `JSR $8E05` byte patterns in ROM bank `$85` (file `0x28000..0x2FFFF`).
- The parser executes `SEP #$20` to set A8 for a source pointer step then **`REP #$20` immediately before the `LDA [$02],Y` glyph ID load** and `JSL $85:8E7B`, with no intervening M-width change in that straight-line path.
- This supports checkpoint030's 16-bit original glyph `PHA` and the proposed `$0A,S` (X8) / `$0C,S` (X16) hook offsets.
- **7/7 deliberate instruction byte mutations rejected**.
- This is a *direct byte-signature graph*, not a complete 65816 control-flow/reachability proof. Indirect jumps and live register flags are not resolved.

Tool: `tools/audit_g2_probe008_031_direct_call_graph.py`.

## 3. G2-only quotation remap preflight — original ROM and recovered V2

New independent `tools/audit_g2_probe008_031_alias_preflight.py` checks:

- Native Japanese original code `8175/8176` maps to physical glyph IDs `0159/015A`, with nonempty 12×12 bitmaps.
- Proposed new `8574/8575` maps to **unoccupied zero** entries in the 85 lead mapping table.
- Proposed new page-0A font cells `0A54/0A55` are **physically blank** in the V2 source, while the page pointer `$A4:D000` is correct.
- The three G2 records are all **106 bytes** each, with original `816F` line controls at indexes **16/34/52** (byte offsets 32/68/104). Each has exactly one native opening and one closing Japanese quote; **six two-byte substitutions** are possible without affecting separators.
- No `8574/8575` source code pairs existed in the records before patching.
- The *entire original Story bank* file `0x18000..0x1FFFF` has **zero raw `8574/8575` byte pairs**, even though the entire 2MiB ROM has **13 / 6** respective pairs in other content. Their global runtime reachability remains unknown.
- This preflight passes on the exact original + recovered V2 ROMs; it **does not certify the 029 machine-code hook at runtime**.

Local audit report artifacts (JSON only): `Chibi_Probe008_031_direct_call_report.json`, `Chibi_Probe008_031_alias_preflight.json`.

## Reproduce with exact local originals

```bash
python tools/recover_g2_probe008_v2_from_failed025.py failed025.sfc recovered-v2.sfc recovery-report.json
python tools/audit_g2_probe008_031_direct_call_graph.py clean.sfc recovered-v2.sfc direct-call-report.json
python tools/audit_g2_probe008_031_alias_preflight.py clean.sfc recovered-v2.sfc alias-preflight-report.json
```

These are local ROM tools, not a workflow requiring ROM bytes on GitHub. Do not upload user's commercial game image or translated ROM to the repo.

## Next unresolved tasks

1. **Real SNES execution** of 029 in Snes9x/bsnes/Mesen 2/BizHawk debugger. Need M/X at actual parser and renderer, glyph A on stack, DP font page/atlas locations and both advance-table results.
2. Actual screenshot QA of V3 medium 9px glyphs, Vietnamese accents, uppercase A, opening and closing copied quote glyphs, 19-column G2 wrap, palette, no crash, normal Japanese menus and Story.
3. Verify 0x85 lead mapping changes do not damage other reachable Japanese content, then consider a release candidate. No emulator-run QA was performed here.
4. Resume G0/title, G2/G3 image strings, menus and minigames only after font rendering stability is established.

**Status:** recovered V2 exact **PASS**, 031 direct caller and alias audits **STATIC PASS**, checkpoint029 **STATIC ONLY**, checkpoint025 **REAL USER SCREENSHOT TYPOGRAPHY FAIL**, **NO new release ROM**.
