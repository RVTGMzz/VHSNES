# Chibi Maruko-chan SNES — Checkpoint 068: byte-exact 79-choice full Vietnamese relocation dry run

Date: 2026-10-12 · Branch: `chibi-maruko-bootstrap-01`.

## Material result: all 81 pending original Quiz options evaluated

Using the exact user-owned 2,097,152-byte Japanese ROM, SHA256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`, and all eight canonical Quiz CSV files on GitHub, reviewed the **81 actual answer choices** not currently covered by stages 041–061 (the nine-pointer-table inventory comes from checkpoint 066).

The full canonical Vietnamese strings for **79 of those 81** can be represented entirely using the existing project's `0x84xx` V2 codepage **without changing the font mapping or shortening the strings**. Two alternate Japanese proper-name spellings remain beyond the Vietnamese font codepage:

- `0x33DDF` — **Nagasawa Kazuo (一雄)**; unsupported `一` and `雄`.
- `0x33DFD` — **Nagasawa Kazuo (和雄)**; unsupported `和` and `雄`.

These characters distinguish otherwise identically romanized choices. **Do not collapse both to “Nagasawa Kazuo”** or swap them for an ambiguous A/B suffix. Preserve original Japanese annotations and explicitly defer these two to hybrid original-Japanese font support or another accurately distinguishable localization.

The actual 79 compatible canonical Vietnamese answers include full names **Hanawa Kazuhiko**, **Rolls-Royce**, **Mercedes-Benz**, **Sakura Ichiro**, **Fujiki Minoru**, full item descriptions such as **Vàng bạc ngọc trai**, and the previously impossible **Xe đạp**. There was **no compression or invented shortening**.

## 79-choice relocation test on the exact original ROM (in memory ONLY)

Checkpoint 066 established three parallel 50-word LoROM question-choice pointer tables with real one-to-one refs: Choice 1 at `0x31217`, choice 2 at `0x3127F`, choice 3 at `0x312E7`. For every pending candidate, matched its original Japanese script source address to the correct 16-bit pointer and kept the original source text bytes intact. Converted each full NFC Vietnamese answer with the existing V2 `0x84xx` mapping, stored as `0E 06 0F 12` + encoded answer + `81 6F 00`, and repointed exactly **79 two-byte addresses** into a *trial-only*, contiguous allocation beginning at `0x37000`, with two-byte alignment.

| Real original-ROM byte-level dry-run | Result |
|---|---:|
| Originally unprepared Quiz answer choices | **81** |
| Full Vietnamese alternatives representable with existing V2 map | **79** |
| Distinct non-encodable Japanese-kanji answer alternatives | **2** |
| Repointed original 16-bit bank06 choice words | **79** |
| Experimental bank06 `FF` space used | **2,339 bytes / 4,096 bytes** |
| Candidate storage span | `0x37000–0x37922` |
| Experimental bank space still empty | **1,757 bytes** |
| Physical changed ROM bytes incl. pointers/checksum | **2,422** |
| Original Japanese choice text and native script data at old offsets | **UNCHANGED** |
| SNES checksum recomputed | `0xF8B6` |
| In-memory source-only IPS size | **3,030 bytes / 120 records** |
| In-memory IPS SHA256 | `1e0552688e1b06271fa9d8597d049eb66787697c6d4412ba9178bf696bf229df` |
| In-memory resulting 2MiB ROM SHA256 | `cc730fa76611155c203ac1fa9175b7a749290b1d5c05bac4a01d0dcd4d6ad087` |
| Independently apply source-only IPS back to exact clean SFC, compare byte for byte | **PASS** |
| Vietnamese V2 font present in clean Japanese ROM | **NO** |
| SNES emulator rendering, correct-answer mapping or gameplay QA | **NOT TESTED** |
| 79 choice translations approved for production or counted as Quiz progress | **NO** |

Both original ROM and independently decoded/replayed in-memory patch remained exactly 2,097,152 bytes. No original Japanese answer slot, game-opcode delimiter, formerly approved text location, other pointer table, or executable code byte was changed by this isolated original-ROM experiment; pointer words, candidate `FF` bytes, and the four SNES checksum bytes were the only whitelisted edits.

The 5,881-byte original Quiz bank-end `FF` run spans `0x36907–0x37FFF`. This test intentionally uses only the final **4 KiB at `0x37000–0x37FFF`**, leaving all bytes `0x36907–0x36FFF` in their original state. Being all `FF` still does **not** prove the game never needs that bank space, and the extra glyphs may overflow the Quiz highlight/render bounds. All placement remains experimental.

The source-only Japanese ROM **cannot display newly encoded `0x84xx` Vietnamese glyphs**: the game's earlier V2 custom font is not part of the original ROM. Therefore the preview is **NOT a playable Vietnamese patch**, even though the source/IPS geometry and checksum pass. Do not upload or distribute the preview ROM or IPS.

## Reproducible source code and acceptance gates

Committed `tools/plan_quiz_long_answers_068.py`, which calls the original clean-ROM Quiz atlas (`tools/build_quiz_answer_atlas_065.py`) and nine-array pointer audit (`tools/audit_quiz_pointer_tables_066.py`). It reads existing canonical source and codepage files, excludes all previously staged 69 answer alternatives, allocates exact full Vietnamese for the 79 codepage-supported remaining choices, guards the original 150 pointers, records both disambiguation-blocked names and the 79 exact placements, recomputes the SNES checksum, checks a whitelist of modified bytes, reconstructs a full clean-ROM IPS in memory, and pins physical SHA fingerprints. It writes **JSON QA only** and cannot emit a ROM or IPS output file.

In the repository's game directory:

```bash
python tools/build_quiz_answer_atlas_065.py clean.sfc --report quiz065.json
python tools/audit_quiz_pointer_tables_066.py clean.sfc --report quiz066.json
python tools/plan_quiz_long_answers_068.py clean.sfc --json-report quiz068_proposal.json
```

**Validation status:** The packing/hash results above were actually reproduced by an independent local Python run with the user-provided original ROM and 81 full canonical Vietnamese answer strings retrieved from GitHub, preserving existing V2 mappings. The committed full-repository tool has **not** yet run end to end inside a complete repository checkout; if its strict guards flag inconsistency, repair and rerun before treating it as CI-validated.

**Do not update official Quiz completion metrics** from this research: existing source coverage is still **279/381** prepared, not 358/381. The production integrated stage061 ROM is still blocked by the unavailable old checkpoint043 clean-source IPS, expected SHA256 `d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50`. No real in-game proof has been performed.

### Next meaningful gates

1. Test a relocated **original native-Japanese** choice in the SNES emulator to establish that bank06 `0x37000` pointers are followed correctly, that all question options remain navigable, and that answer correctness logic does not depend on original text offsets. The existing separate checkpoint067 single-choice Japanese proof provides a minimal fixture.
2. Reacquire the exact 043 IPS raw bytes (Library metadata is insufficient) and rebuild 061 integrated Vietnamese font/title UI, then repeat one real relocated *Vietnamese* answer in the emulator, checking rendered width, selection highlight, and answer grading.
3. Only after these tests approve bulk 79 relocation; retain proper-name disambiguation for the two Japanese Kanji variants, four long Fortune entries, G3 screens, and final font/graphics QA.

**Content first, font polish last; no repeated unplayable micro patches.**
