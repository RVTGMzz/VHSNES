# Chibi Maruko-chan SNES — Checkpoint 077: the final independent non-answer Quiz source

Date: 2026-10-12 · Branch `chibi-maruko-bootstrap-01` · Original user-owned Japanese ROM SHA256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`.

## Actual progress: identify and prepare the ONE separate question line

The earlier checkpoint076 had **279/381** staged canonical Quiz source rows, plus 81 full-length original-answer candidates with verified static bank06 relocation. This left **21 canonical non-answer source labels**. Comparing all eight canonical Quiz CSVs, all eight 041–061 staged manifests and the original 50×3 choice table proves the 21 are **not** 21 separate text fields:

| Unstaged non-answer Quiz source categories | IDs | What to do |
|---|---:|---|
| Physically nested inside previously staged script text | **10** | Review already-staged parent translation for semantic completeness, do not overwrite parent or double-count |
| Not safe original scanner text entrypoints | **10** | Repair/triage source and parent; do not invent standalone glyph ranges |
| **Genuine individually pointer-addressable text field** | **1** | This checkpoint prepares a full line relocation, still needs V2 font and emulator verification |

The sole remaining independent line is the question about **Maruko's daily allowance**, from the original scanner source at **`0x320E8`**, caption reference `...mỗi ngày là bao nhiêu?`. IMPORTANT: original physical record actually begins earlier at **`0x320DC`**, native control `0E 00 0F 0E`, followed by six ASCII layout spaces and **`は１日いくら？`** (27-byte record including `81 6F 00` terminator). Writing at the scanner's `0x320E8` alone would leave the beginning Japanese `は` in the game. That would be a regression.

Checkpoint059 already staged the previous two source frames at **`0x32095`**, currently rendered as **“Maru mê kem”** / **“Tiền tiêu vặt”** (native frame capacities 14 and 13). To complete the question naturally and explicitly identify the protagonist, this checkpoint prepares one *entire new follow-on native record*:

**“Mỗi ngày Maru có mấy yên?”**

This retains the source question's daily time dimension and money amount, works with the previously staged parent lines, and is contextually compatible with the original three Quiz choices **30 / 1,000,000 / 50 yên**. It uses 25 V2 glyph cells. This is an editorial **candidate pending in-game readability**, not a blindly invented shorter alias or acceptance of the whole quiz.

## Genuine original 16-bit question-pointer relocation

The original Japanese ROM's nine parallel question tables include **the continuation-pointer word at ROM `0x311AF`**, whose original bytes are `DC A0`, CPU address `$A0DC` in bank06, referring to native full record `0x320DC`. The new complete record uses exactly:

`0E 00 0F 0E` + six ASCII layout spaces + 25 project V2-encoded glyphs + `81 6F 00`

Total **63** bytes. The builder pads it to a conservative **66-byte source window**, then leaves a **two-byte untouched FF guard**. It changes only the 16-bit pointer `0x311AF` from `DC A0` to **`84 FF`** (LoROM bank06 address **`$FF84`**) and writes the new record starting at **`0x37F84`**.

This is the **first 68-byte slot immediately after** all 81 candidate answer slots introduced in checkpoint073 (`0x36A00–0x37F84` end-exclusive). It ends at `0x37FC8`; **56 bytes remain** before the bank06 boundary `0x38000`. The original Japanese question and answer bytes remain completely unchanged. The original game executable and the 81 answer pointer table entries are not modified by this additional candidate.

**Safety caveat:** The earlier checkpoint073 established the 66-byte fixed copy for *answer* records. It has **not independently established that the question-continuation renderer obeys the same exact source-width limit or correctly displays a 25-glyph translated line**. The 66B padded record is deliberately conservative, but actual game/emulator validation is still mandatory.

### Independent byte-level original-ROM reproducibility

An independent Python construction using the exact real 2MiB Japanese ROM and the project's actual V2 glyph codes (cross-checked against live GitHub mapping) added **only this ONE new continuation candidate**, without the unavailable V2 graphics/font base:

| Source-only static experiment | Exact result |
|---|---|
| Original 16-bit pointer source | `0x311AF: DC A0` |
| Trial new record | `0x37F84`, 63B actual + 3B zero padding + 2B FF guard |
| Changed original Japanese ROM bytes | **72** (including checksum) |
| Resulting clean-original IPS | **95 bytes / 3 records** |
| IPS SHA256 | `0deca543c5b7b2b8509766b66c40a0b2f759d94c01a4de83443a7fa9daa6d538` |
| Candidate original-ROM SHA256 | `209628345d7fc502dde620ea85a227bfe9ff2c9b538dd551d0a886aabe7bf1aa` |
| Recomputed standard LoROM checksum | `0xE9CA` |
| Real emulator, text width, visible question, answer correctness | **NOT TESTED** |

The exact source-only bytes/IPS were independently constructed and replayed on the real retail ROM in this session. **This does not represent a playable Vietnamese patch**, because the unmodified Japanese game has no V2 glyph font and the true combined game is still blocked on access to a historical IPS.

## Source and CI changes

- `translation/runtime/quiz_nonanswer_077_single_continuation.json` records original 059 parent context, exact original native source bytes, pointer, full Vietnamese continuation, required bank06 location, all four unsatisfied gameplay/screen proof flags.
- `tools/build_quiz_nonanswer_continuation_077.py` validates the source ROM, parent stage059 source/runtime content, all exact original-control bytes and new V2 codepage glyphs, available FF bank space, byte whitelist, LoROM checksum, IPS replay and *independent source-only SHA fingerprint*. It accepts an original SFC with optional already-built 81-answer cumulative IPS and validates all 81 bank06 answer destinations when present. It writes an IPS+JSON **only** when explicitly requested with `--allow-untested`.
- `tools/audit_quiz_nonanswers_077.py` is ROM-independent: checks exactly **10 nested + 10 unsafe + 1 independent** among the 21 labels, refuses double-counting 20 alias/unsafe records, validates new manifest and existing 059 source context.
- `tools/recover_merge_061_81_one_ips_076.py` has been extended to build **061 + all 81 answer candidates + 1 new non-answer question continuation** into ONE clean-original-ROM IPS/JSON when a valid historical 039–043 ZIP/IPS is supplied; no intermediate game ROM output.
- `.github/workflows/chibi-snes-source-qa.yml` now runs the ROM-free 077 remaining-nonanswer audit. [Source CI run 38227202937](https://github.com/RVTGMzz/VHSNES/actions/runs/38227202937) completed **SUCCESS**.

### Remaining limitations

1. The entire latest cumulative **061+81+1 IPS** is **not built**, because user-owned historical original 039–043 ZIP/IPS bytes still cannot be retrieved from Library. The latest one-archive script has source CI only, not real compilation against the complete Japanese+V2 images.
2. All **82 remaining independently addressable** Quiz sources (81 answers + this single continuation) now have **static source-byte candidates**, but **none of those new 82 is emulator-approved**. Do **NOT** change 279/381 official staged/accepted source count to 361/381 yet.
3. The other 20 canonical Quiz scanner labels are **overlapping/untrusted offsets**, not 20 distinct independently safe fields; review the already-translated parent scripts for complete meaning. They remain unselected source IDs for bookkeeping; do not count them as done without a semantic audit.
4. Four long Fortune pieces, G3 ending/results screens, full game menu/Story progression, long Quiz answer clipping, and the mixed CP932/V2 native Kanji font check still require actual integration/emulator QA.

User preference: **complete user-facing content first, font appearance polish later; avoid meaningless tiny IPS downloads.**
