# Chibi Maruko-chan — Probe008 checkpoint 030: original CPU stack + codepage alias audit

Date: 2026-10-11. Repository `RVTGMzz/VHSNES`, branch `chibi-maruko-bootstrap-01`.

## Prior state

- Checkpoint 025: **user screenshot confirms RUNTIME TYPOGRAPHY FAIL**; never reship.
- Checkpoint 029: V3 medium + geometry-based 9px and two duplicated G2-specific quotation glyphs `0A54/0A55`, mappings `8574/8575`; original Japanese quotes `8175/8176` remain 13px in both hooks. **Static PASS; emulator/runtime NOT TESTED.**
- This checkpoint is strictly **READ-ONLY original-ROM evidence**, not a new release or diagnostic ROM.

## New direct evidence from exact clean ROM

Used exact, headerless 2 MiB ROM SHA-256:

`e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`

Tool `tools/audit_g2_probe008_030_renderer_stack_contract.py` checks **nine actual instruction anchors** without relying on checkpoint025's misidentified source-bank gate:

1. Parser lead dispatch, the glyph lookup `LDA [$02],Y`, and call `JSL $85:8E7B`.
2. Renderer `PHB; PHX; PHY; PHA` at `0x28E7B`, saving the actual glyph ID passed in **A**.
3. Helper `PHX; PHY` at `0x28E05`, and the word-offset lookup `0x28E0C`.
4. The renderer's DBR switch, `PEA $7F00; PLB; PLB`.
5. Original font page-pointer assembly at `0x28E9A`, atlas X at `0x28EB4`, atlas Y at `0x28EC2`.
6. Shift lookup at `0x290EE`, original 13px tables, and original 100-cell BCD position lookup.

Symbolically tracks the original 65816 *real instruction order*, including nested 3-byte JSL return frames and X-width-dependent PHX/PHY saves:

| Original X width | Actual glyph low-byte offset from hook SP | high byte |
|---|---:|---:|
| 8-bit | `$0A,S` | `$0B,S` |
| 16-bit | `$0C,S` | `$0D,S` |

This independently confirms the stack displacements used by checkpoint029's first hook, **conditional on original renderer PHA saving a 16-bit accumulator**; this condition still needs real CPU debugger confirmation. The test is not full 65816 execution.

All **9 direct instruction anchors PASS** on the exact clean ROM. Nine separate intentional one-byte instruction corruptions are rejected by the structural checker. The original ROM was not written or repacked.

### Original Japanese quote glyphs — actual ROM bitmap

The untouched original glyphs are physically narrow:

| Native quote glyph ID | Font page / cell | Ink pixel count | Ink X extent inside 12px cell |
|---|---|---:|---|
| `0159` | page 1, cell 89 | 11 | 6–9 |
| `015A` | page 1, cell 90 | 11 | 1–4 |

This supports glyph-copy fidelity for G2 aliases `0A54/0A55`; it is **not proof of their visual position in game**.

### New lead `85` alias raw collision inventory

In the **clean** 2 MiB ROM:

| Proposed G2-only code | Raw matching byte pairs across ROM | Raw matches inside text bank file 0x18000–0x1FFFF |
|---|---:|---:|
| `8574` | 13 | 0 |
| `8575` | 6 | 0 |

This confirms the aliases have **no raw occurrences in the entire original G2/Story text bank** (not just the three replacement fields). However raw matches in other banks may be graphics, machine code or game data; **a zero in one bank does not prove globally safe codepage reallocation or parser reachability**. Keep runtime/native Japanese checks as a blocking requirement.

## Reproduction

```bash
python tools/audit_g2_probe008_030_renderer_stack_contract.py \
    "Chibi Maruko-chan - Mezase! Minami no Island!! (Japan).sfc" \
    probe008-checkpoint030-original-stack-audit.json --negative-tests
```

Locally generated report (not a ROM): `Chibi_Probe008_030_stack_contract_report.json`.

## Critical remaining work

- **No available SNES emulator** in this container; Snes9x/bsnes/RetroArch absent and outbound DNS resolving to fetch dependencies is unavailable. No real 029 execution or screenshot was produced.
- Real SNES debugger must confirm M/X mode and actual A saved by renderer PHA at `$85:8E7B`, hook word at `$85:8E0C`, and atlas registers + selected shift table at `$85:90EE`. Observe live glyph IDs `0A54/0A55`, original Japanese `0159/015A`, and other Vietnamese glyphs.
- Font V3 legibility, tone marks, line breaks, quote placement, native Japanese UI/story, and codepage lead `0x85` safety must be checked **in game**.
- Only promote a release when a gameplay screenshot and Japanese-mode smoke tests pass; do not send the user a string of untested ROM revisions. Continue G0/title, G2/G3 graphics, menus and minigames after font gate.

**Status 030:** read-only original-ROM code-stack audit **PASS**, checkpoint029 static build **PASS**, checkpoint025 user visual **FAIL**, full runtime **NOT TESTED**. No commercial ROM committed to GitHub, and CI was not claimed.
