# Chibi Maruko-chan SNES — Checkpoint 069: 81/81 long Quiz answers byte-encodable via hybrid CP932/V2

Date: 2026-10-12 · Branch `chibi-maruko-bootstrap-01` · Clean user-supplied original SNES ROM SHA256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`.

## Result: preserve both Nagasawa Kazuo answer choices instead of shortening

Checkpoint068 demonstrated safe **byte-level** allocation for 79/81 pending Quiz answers in a test-only 4KiB portion of the original bank06 FF area. The two still-blocked Quiz choices are:

| Offset | Original Japanese | Complete original canonical Vietnamese |
|---|---|---|
| `0x33DDF` | `永沢一雄` | `Nagasawa Kazuo (一雄)` |
| `0x33DFD` | `永沢和雄` | `Nagasawa Kazuo (和雄)` |

Simply dropping the Japanese annotations would create two indistinguishable multiple-choice answers. The original clean ROM **already contains native two-byte CP932 codes** for all three distinguishing characters: `一 = 88 EA`, `和 = 98 61`, `雄 = 97 59`. They appear in the original Quiz bank data (at least three occurrences each). For a reversible data experiment, no new custom glyph was defined: the two full Unicode strings were encoded **per character**, using Vietnamese `0x84xx` V2 codes for Latin/Vietnamese characters and unchanged original CP932 codes for the **four original Kanji occurrences**. This preserves the original difference.

**Important caution:** The earlier Vietnamese V2 font/font-table modifications might have changed access to original CP932 Japanese glyphs or rendering; we have NOT loaded a real integrated V2 ROM or checked an emulator. The mixed encoding is therefore a byte-level experiment, **not proof of readable mixed Japanese/Vietnamese text in the actual game**.

## Exact clean-ROM dry-run measured results

A fresh independent Python implementation tested all **81 pending original Quiz answer alternatives**, retaining their complete canonical `vi_full` strings from the source CSVs, their original three-choice ordering and their respective LoROM 16-bit pointer words. It allocated records of the form `0E 06 0F 12 + encoded complete answer + 81 6F 00` into a *hypothetical* allocation window `0x37000–0x37FFF` (4096 bytes). It kept all original Japanese answer texts, other script bytes and the earlier bank-end area `0x36907–0x36FFF` unchanged.

| Test-only, actual original-ROM byte-level measurement | Result |
|---|---|
| Pending full-length Quiz answer alternatives | **81** |
| Fully representable through existing V2 glyph bytes only | **79** |
| Additional alternatives using existing native CP932 Kanji | **2** |
| Unique Japanese Kanji characters retained | `一`, `和`, `雄` |
| Native Japanese CP932 glyph occurrences in two longer answers | **4** |
| Original 16-bit bank06 answer pointers experimentally changed | **81** |
| Experimental 4KiB FF region used | **2,431 B** |
| Byte placement | `0x37000–0x3797E` (exclusive end `0x3797F`) |
| Remaining unused bytes inside 4KiB trial window | **1,665 B** |
| Actual ROM byte differences, including pointers and checksum | **2,517 B** |
| Recomputed standard LoROM checksum | `0xC3BC` |
| In-memory only IPS records / size | **124 records / 3,145 bytes** |
| In-memory only IPS SHA256 | `3777df4895046d8342d421f8da5d2ccabdfd01cec7b5f8e567759ba1d4e5c213` |
| In-memory 2MiB image SHA256 | `c61471d70f0025e075d6dd94366940bc8990e1cfc910cf99f421dc15ff47f184` |
| Independent apply IPS to the exact original ROM and byte compare | **PASS** |
| SNES interpreter, font V2 mixed Japanese rendering, answer selection | **NOT TESTED** |
| Integrated into a gameplay-ready Vietnamese ROM | **NO** |
| Approved as finished localization | **NO** |

This test **does not touch the original ROM file** and creates no downloadable game ROM/IPS. The local QA is in `/mnt/data/chibi069_mixed_qa.json` for this session; the GitHub repository contains only the reproducible *source code* and documentation.

## Separate display-width hazard audit

A second original-ROM check compared **each original Japanese answer's real CP932 glyph count**, excluding native ASCII padding, to its full Vietnamese caption length. **All 81 relocated captions are longer than their original glyph cells.** Forty-three contain more than 10 glyphs, 15 contain more than 14, one contains 23. Examples: `Trường Tiểu học Shimizu` requires 23 characters versus five original glyphs; `Chiếc mặt nạ kỳ quặc` needs 20 versus four; each annotated `Nagasawa Kazuo` needs 19 versus four.

This is an explicit **screen-layout / highlight / selection risk**: proving that pointers and enough ROM bytes exist does not demonstrate that 23 glyphs can render within the original one-line Quiz choice width. The committed 069 planner now fails closed if the 81 genuine source-width increases or the longest-caption distribution changes. **Do not approve or bulk-ship 81 answers until an emulator-visible rendering and answer-navigation test is passed.**

## GitHub tools added

`tools/plan_quiz_long_answers_069_mixed.py` extends the verified 068 algorithm to include only the three whitelisted original CP932 Kanji, checking that they exist as native bytes in the retail ROM and that both full Nagasawa name alternatives remain distinguishable. It pins 81 relocated records, exact pointer changes, stored-byte bounds, unchanged original text, recomputed checksum, patch record count, and all SHA256 digests. **No binary output is emitted.** It stops on any ROM SHA mismatch or any unexpected glyph/collision.

`tools/verify_quiz_technical_069.py` is an additional one-command, fail-closed QA entrypoint for a *full local checkout* with original retail SFC. It calls the earlier read-only source/checkpoint 061/063/064/065/066/067/068/069 analyzers and checks 279 distinct staged Quiz addresses, 102 unstaged source rows, 82 standalone remaining source windows, 409 script transitions, 50 questions, 150 answer choices, 450 native pointer references, the previous single-choice byte experiment, 79 V2-only candidates, and 81 hybrid candidates with fingerprinted original-ROM replay. It emits **JSON diagnostics only** and never writes a ROM or IPS.

Run from the Chibi project root:

```bash
python tools/plan_quiz_long_answers_069_mixed.py clean.sfc --json-report quiz069_mixed.json
python tools/verify_quiz_technical_069.py clean.sfc --report quiz069_all_qa.json
```

**Verification honesty:** The 81-allocation and IPS metrics above were computed and independently replayed in this session against the actual user-provided clean Japanese ROM, using all original canonical translations and the existing V2 codepage. The newly authored **repo scripts** have been committed and source-inspected but not yet executed end to end in an authorized local full repository checkout. They must not be presented as a CI pass or emulator pass until run there.

## Remaining production blockers and next meaningful tasks

- **Checkpoint043 cumulative clean IPS still absent as raw bytes.** Its expected SHA256 is `d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50`. Only historical ZIP *metadata* was accessible in the user's Library; old materialization attempts failed. Without that historical G0/G1/V2/Story base, the real 061+ localization ROM **cannot be assembled or tested** from the current active inputs.
- **First emulator acceptance gate:** run the prior *native Japanese only* choice-relocation fixture (#067) on the user's authorized local SNES emulator. Verify that Quiz #6 displays the longer option, preserves its highlight and navigation, grading, and return flow. That test is independent of missing Vietnamese V2 font.
- **Then actual integrated V2 test:** once exact 043 base is recovered, try one full Vietnamese long choice and both mixed-encoded Kanji options in the game. Check native Kanji glyph preservation and that the two Nagasawa choices really render differently. Also test long-answer width and answer correctness throughout all 50 questions.
- **Only after emulator acceptance**, approve a bulk 81 relocation patch with clean-ROM IPS, coordinate this with the four long Fortune cases, G3 result/ending screens, and finish game-wide QA. User explicitly prioritizes **content-first, font polish last**, avoiding hundreds of micro patch downloads.

The *official source-staging progress stays 279/381 unique Quiz rows*. These 81 are **experimentally encodeable**, not gameplay-verified or accepted in the actual ROM. In particular, do not report 360/381 as finished!
