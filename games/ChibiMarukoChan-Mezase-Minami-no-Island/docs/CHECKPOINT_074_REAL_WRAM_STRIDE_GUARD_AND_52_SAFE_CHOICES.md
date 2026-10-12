# Chibi Maruko-chan SNES — Checkpoint 074: WRAM copy overlap and real 52-answer safe subset

Date: 2026-10-12 · Branch `chibi-maruko-bootstrap-01`.

## CRITICAL CORRECTION to checkpoint 073

Checkpoint073 correctly established that the original Quiz bank06 machine-code routine reads **33 16-bit words (66 bytes)** from each answer pointer, and that all **81 full Vietnamese source strings** fit within nonoverlapping original ROM storage windows of 68 bytes. **That was not enough to show the SNES could copy or render those answers correctly.**

The actual original 65c816 code at `0x30730`, `0x307AA`, `0x3081B` invokes the copier with destination register X equal to **`0x0000`, `0x0020` and `0x0040`** respectively. The native copier's absolute-long write instruction `9F 00 80 7E` writes 66 bytes to WRAM `$7E8000 + X` for each choice. **The source-copy windows in ROM may be separated, but the destination buffers in RAM start only 32 bytes apart.**

When the second choice is loaded, it overwrites offsets 32–65 of the first choice. When the third is loaded, it overwrites offsets 32–65 of the second. This is safe for *original short Japanese options*, but not for all full Vietnamese alternatives. The original code was checked against the actual user-provided Japanese 2MiB SFC SHA256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`.

### Verified count of newly discovered runtime hazards

| Original answer candidates not in stages 041–061 | Count |
|---|---:|
| Full canonical Vietnamese choices planned in 073 | **81** |
| Choices whose complete native record (4-byte prefix + 2 bytes/character + 3-byte terminator) needs **over 32 bytes** | **29** |
| Among those, choices #1 or #2 **overwritten by the next 66-byte copy** | **18** |
| Choices #3 longer than 32 bytes (not overwritten by the next choice, but still a render/memory-layout risk) | **11** |
| **Full-label source records at most 32 bytes, avoiding this specific overwrite** | **52** |

The longest canonical record requires 53 bytes. In an independent *in-memory source-ROM simulation*, all 81 full alternatives were temporarily packed into fixed, nonoverlapping original bank06 source cells and the actual three successive 66-byte-to-WRAM copies were simulated for each affected question. **Exactly 18 choices #1/#2 lost bytes of their full records** after the next answer was copied; 29 choices have no complete terminator within the original 32-byte slot. These counts agree with the ROM-independent canonical source planner.

This means the old tightly packed 069 proposal and the blanket 81-slot 073 proposal must **NOT** be approved as finished, playable choices. They remain useful ROM-space evidence only. The fix for the remaining 29 choices will probably require a carefully justified **WRAM buffer-layout or game-engine change**, not more storage in the ROM bank. Actual emulator testing is mandatory before approving any change to execution code or text renderer.

## Actual work: an independent 52-answer safe-subset clean-ROM patch experiment

New `tools/build_quiz_relocated_81_074.py` is a deliberately guarded builder that **excludes all 29 choices with records longer than 32 bytes**, using the canonical source and source-byte safety checks from checkpoint073 and the new WRAM risk audit `tools/audit_quiz_wram_stride_074.py`.

For each of the **52 full Vietnamese alternatives** with 32-byte-or-shorter native records, the builder:

- Validates original Japanese source, its exact 16-bit LoROM choice pointer and the previous baseline (clean original or independently verified cumulative checkpoint061) still contain the original bytes.
- Uses full, naturally localized canonical Vietnamese from `translation/source` with the existing V2 `0x84xx` font codepage (no truncation, renaming or fake synonyms).
- Assigns a separate fixed **68-byte source slot** from the reserved checkpoint073 address plan. It keeps the original order and original per-choice slot index, leaving all 29 deferred slots untouched and available for a future engine-aware implementation.
- Writes the full record plus `00` padding to cover all **66 bytes** copied by the original CPU routine, preserves two `FF` guard bytes in each cell, and updates only the exact original 16-bit answer pointer.
- Recomputes SNES checksum; checks every changed byte against an explicit pointer/66-byte storage/checksum whitelist; creates an IPS relative to the *original Japanese source* and independently replays the IPS in memory to verify every target byte.
- **Does not** claim that the clean Japanese ROM contains Vietnamese V2 glyphs or that any label was emulator tested. The full cumulative checkpoint061 V2 baseline still requires original 039–043 IPS/ZIP bytes, and there is no real visual test here.

Independent Python on the exact original Japanese source ROM reproduced the following isolated 52-choice **clean-Japanese-base byte experiment**:

| Static validation | Result |
|---|---|
| Full canonical Vietnamese choices selected | **52** |
| Full choices deferred for WRAM / UI-layout repair | **29** |
| Original Japanese choice text unchanged | **PASS** |
| Changed original-ROM bytes, including pointers/checksum | **3,539** |
| Source-only clean-ROM IPS bytes / records | **3,982 bytes / 87 records** |
| IPS SHA256 | `17b9d03fd42a732d6f0348816c540ca06e21175cde588fc25b0d60d62bfd6446` |
| Candidate original-ROM image SHA256 | `5f640db8539312bf3ac01f25daff80357e4ecddffb66b7d86dcbbbb722648b10` |
| SNES checksum | `0xB592` |
| Independent apply-IPS-back-to-source exact byte replay | **PASS** |
| Vietnamese font in untouched Japanese original ROM | **NO** |
| Actual SNES game/menu/emulator acceptance | **NOT TESTED** |

The earlier 81-choice all-at-once original-ROM byte prototype (IPS SHA `58f284de922c3e44d2616c0de73918f6a2a86ee552c19cdc4e2cc51643f5f109`) was **explicitly superseded** as a production strategy: 18 answer copies would overwrite their own text in the original WRAM layout, even though the IPS byte replay succeeded. Do not distribute it or use it to inflate translation-progress counts.

The 52-choice experimental code has been committed; the static SHA fingerprints above were computed independently with original source bytes and cross-checked against the canonical Vietnamese strings/codepage fetched from GitHub. The full newly committed builder has **not yet been exercised end-to-end in an authenticated local clone with the complete canonical source files**, so source-only hashes must not be described as GitHub runtime/ROM integration QA until that succeeds.

## Verified automated checks

- `tools/audit_quiz_wram_stride_074.py` reads all canonical Quiz sources (no copyrighted ROM required), asserts **29** choices require >32 bytes, **18** choice #1/#2 overwrite hazards, **11** longer choice #3 risks, and fails closed if those numbers change.
- This new WRAM risk audit is now part of `.github/workflows/chibi-snes-source-qa.yml`, alongside the existing 381/279 source coverage audit and the 81-original-source-bank 66-byte window planner. These tests prevent a future automated assistant from wrongly concluding that fitting strings into bank06 makes all 81 safe for SNES use.
- Real GitHub Actions `Chibi SNES source localization checks` run [38205855597](https://github.com/RVTGMzz/VHSNES/actions/runs/38205855597) completed **SUCCESS** with the new guard.

## How to reproduce source-only research

Once the project checkout and original user-owned retail SFC are available:

```bash
python tools/audit_quiz_wram_stride_074.py --original-rom clean.sfc --report wram074.json
python tools/build_quiz_relocated_81_074.py clean.sfc --ips 52_QUIZ_TEST_ONLY.ips --report qa074.json --allow-untested
```

The builder also accepts a separately confirmed cumulative 061 clean-ROM IPS and matching QA JSON (`--baseline-ips`, `--baseline-qa-json`), but this has NOT been tested because the historical 039–043 binary source is unavailable. Do **not** share a source-only V2-text patch as a playable Japanese ROM mod; without real Vietnamese font it will render invalid glyphs.

## What remains

The original official staging count is still **279/381 distinct Quiz source entries**; 52 additional **full-source-byte patch candidates** have now been independently generated in memory but are not integrated into a working Vietnamese-font ROM or approved by an emulator. The remaining **29 long choices** require WRAM/text-renderer engineering; another 21 canonical Quiz source rows are not answer options and need separate semantic integration work. Four long Fortune cases and G3 result/ending screen graphics also remain. User preference: **content first, final font polish last**, but preserve correctness and avoid meaningless mini-IPS downloads.

The most valuable next reverse-engineering step is to trace the native WRAM `$7E8000/$7E8020/$7E8040` renderer calls and their text destination limits, then prototype a verified larger WRAM stride without corrupting other game state. Do **not** assume changing the 16-bit pointer addresses alone solves this.
