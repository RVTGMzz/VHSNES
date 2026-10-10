# Chibi Maruko-chan SNES — Probe008 checkpoint 024: G2-source-scoped 9px

Date: 2026-10-10. Repository `RVTGMzz/VHSNES`, branch `chibi-maruko-bootstrap-01`.

## Main change — avoids the 64px Japanese closing-quote defect

Checkpoint 023's **glyph-ID-selective** 9px approach fails because original Japanese closing quote `0x8176` is placed using the native 13px table after 16 Vietnamese glyphs, leaving a **64px gap**. Do not release that probe.

Checkpoint 024 replaces that idea with a **stateless source-bank-and-record-range selector**. It inspects the data-bank register (DBR) and the parser's existing source pointer `$001F94`. When the CPU is rendering from bank `$83` and the source pointer falls within **one of the three exact 106-byte G2 records**, the ENTIRE text run receives a 9px advance, including native `0x8175/0x8176` opening/closing quotes, spaces and punctuation. Otherwise, the original 13px positioning tables remain in use.

Source file spans (bank `$83`, upper end exclusive):

- `$83:81CE..$83:8238` (file `0x181CE..0x18238`);
- `$83:8247..$83:82B1` (file `0x18247..0x182B1`);
- `$83:82C0..$83:832A` (file `0x182C0..0x1832A`).

This is source-record scoped, not automatic universal Vietnamese line detection. It does **not** cover other menus, stories or scenes yet.

### Static renderer evidence

- Parser reads source position `$1F94` using `LDY $1F94; LDA $0000,Y` at file `0x28340`.
- Renderer receives per-character column `$1F9A` and row `$1F9C` (file `0x28409`).
- Word-advance consumer: `0x28E0C` (original `BF 70 96 85`).
- Shift consumer: `0x290EE` (original `BF 96 96 85`).
- The injected routines use `PHP/PLP` to restore processor width/flags and `PHB/PLA` to read the DBR without modifying its value. No new or assumed-free WRAM byte is reserved, so no latch reset is necessary.
- The original 13px tables at `0x29670/0x29696` are **unaltered**.

**Crucial unresolved runtime dependency:** the parser must actually keep DBR=`$83` and `$1F94` as the source offset while drawing these direct-ROM G2 records. Static parser instructions are consistent with this, but there has been **no emulator CPU trace to prove register values**. If the bank differs at runtime, the selector deliberately falls back to 13px. Do NOT claim rendered 9px gameplay until that is checked.

## Local build results — verified against exact ROM hashes

Input: **Probe008 V2 font-only 13px** SHA-256 `2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd`.

Output: **Probe008 V2 G2-line-scoped-9px diagnostic**:

- SHA-256: `feb7215a67046128ff67113fd921b6479d956df6018a3ae4e74992d03b0c978a`
- Original ROM size: `0x200000` (2 MiB).
- Changed bytes vs exact V2: **181**.
- SNES checksum/complement: **`0xF4D6 / 0x0B29`**.
- 65816 word/shift hook stubs: **57 bytes each**, installed at `$85:FB80`/`$85:FC00`.
- Separate 9px lookup tables: `$85:FC80`/`$85:FCC0`.
- Entire original 13px lookup tables: byte-for-byte preserved.
- All three G2 `106-byte` text records: byte-for-byte preserved; original separators `816F` remain at `32/68/104`, quotes `8175/8176`, and D038/scene/font-page-pointer code untouched.
- 65816 instruction-subset micro-interpreter tests: **12,464 PASS**, covering every source byte of the three records at each of 19 glyph indexes and both lookup modes, plus foreign-bank/field-boundary tests.
- Independent byte-level verifier: **PASS** (exact 65816 machine-code bytes, source-path anchors, original lookup tables, diff-surface whitelist, checksum and output SHA-256).
- **5/5 negative corruption tests PASS**: deliberate modifications of a text source byte, JSL callsite, injected code, new lookup table, and checksum were rejected.
- Offline glyph preview from the patched ROM places closing quote at **x=148px** rather than selective glyph-mode x=212px. This is a **layout model result only**, NOT an emulator screenshot.

Tools committed:

- `tools/build_g2_probe008_line_scoped_9px_diagnostic.py`
- `tools/verify_g2_probe008_line_scoped_9px_diagnostic.py`

Reproduce (with exact local source ROM, not committed to GitHub):

```bash
python tools/build_g2_probe008_line_scoped_9px_diagnostic.py Probe008_V2_13px.sfc G2_line9_UNTESTED.sfc g2-line9-build.json
python tools/verify_g2_probe008_line_scoped_9px_diagnostic.py Probe008_V2_13px.sfc G2_line9_UNTESTED.sfc g2-line9-verify.json --negative-tests
```

## Correct status; next work

| Workstream | Status |
| --- | --- |
| Exact Probe003 strict 2-byte path | Earlier user runtime path PASS; exact rebuild verified |
| Probe008 V2 complete 212-entry font | Static bitmap / mapping PASS, emulator UNTESTED |
| G2 scoped 9px and original Japanese quotes | Source-range microhook STATIC PASS |
| Native 13px untouched outside G2 | STATIC PASS under tested bank/pointer conditions |
| G2 source pointer/DBR live CPU values | **UNVERIFIED — EMULATOR DEBUGGER REQUIRED** |
| Expanded 0x85 codepage use by other game scripts | Still not exhaustively proven safe |
| Probe008 typography and full-game Runtime PASS | **NO** |

There is **no supported SNES emulator** installed in this execution environment, so no real runtime test occurred. Do not ship the new ROM as completed, or claim screenshots are emulator output. Only tools, documentation and non-ROM previews may go into GitHub; all commercial ROM binaries remain local. Next verify DBR + `$1F94` live during G2 scene, check quote/line wrapping and game UI, then expand pitch selection only with corresponding source evidence. Return to remaining G0/title, G2/G3 graphics and untranslated visible screens after font acceptance.
