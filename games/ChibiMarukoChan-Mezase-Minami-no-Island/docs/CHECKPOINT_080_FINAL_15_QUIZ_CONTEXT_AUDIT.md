# Chibi Maruko-chan SNES — Checkpoint 080: Japanese-source QA of last 15 Quiz scanner aliases

Date: 2026-10-13 · Branch `chibi-maruko-bootstrap-01`.

## Scope and actual content changes

Checkpoint079 had 15 original scanner aliases left requiring **source-versus-translated-parent semantic QA**. These are not 15 distinct new writable native script fields; all currently have staged parent regions. Rather than inflating the source count or attempting unsafe in-place edits at scanner starts, this checkpoint compared the original game text, native physical line sizes and real nine-table 16-bit Quiz field pointers to historical staged Vietnamese captions.

**Three factual/phrasing problems were confirmed and edited** using a new **post-079 guarded overlay**. The old stage054/058 manifests and their exact historical clean-ROM IPS SHA anchors remain untouched:

| Original native Quiz record, true pointer word | Parent source/stage | Before | Corrected Vietnamese | Native physical capacities |
|---|---|---|---|---|
| `0x32C05`, `0x313BD:05 AC`, explanation part 2 (slot 3) | `0x32C09`, stage058; source alias `0x32C15` | `Sang đợt ba` / `đi Tokyo` / `rồi!` | **`Học kỳ 3`** / `đi Tokyo` / `rồi!` | **13 / 8 / 6** |
| `0x330E5`, `0x3114F:E5 B0`, question main (slot 4) | `0x330E9`, stage058; source alias `0x33119` | `Hamaji cùng` / `Buutaro hạng B` | **`Bộ ba hạng B`** / **`Hamaji Buutaro`** | **13 / 14** |
| `0x353D2`, `0x313A7:D2 D3`, explanation part 1 (slot 44) | `0x353D6`, stage054; alias `0x353F3` | `Mẹ Maruo 49` / `rất thương con` / `thế mà bị chê` | `Mẹ Maruo 49` / **`rất hiền lành`** / `thế mà bị chê` | **14 / 14 / 13** |

The Japanese CP932 glyphs and actual 16-bit LoROM pointer bytes of all three complete native records were independently checked in the user's original unheadered 2MiB Japanese SFC, SHA256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`. There is **no change to the original CPU execution, pointer tables, text control delimiters, widths or user ROM file**. The patch candidate updates only **four existing translated caption lines**, preserving all exact original glyph capacities and using characters in the existing V2 font codepage. The corrected B-trio wording works with the separately staged follow-up `Ai còn lại?`.

The Tokyo line still has to be tested with surrounding explanation frames to verify style and pacing; the Maruo line deliberately translates `とてもやさしい` as kind/gentle rather than claiming a specific mother-son sentiment.

## Remaining twelve scanner IDs, not twelve new native strings

`translation/runtime/quiz_remaining_fact_qa_080.json` documents each original scanner alias, staged parent, stage and the exact **key fact already present in the previous translation**. The new source-only CI audit validates all parent captions instead of just asserting that their bytes overlap:

| Disposition | Count | Details |
|---|---:|---|
| Significant subfact already present in earlier parent translated lines | **11** | Maruko grade 3, blood type A and lazy, Sakura Sumire age 40, sister grade 6, class 3-4, Hanawa's mother 29 and distant work, Hideji 68, Maruo Dec 31 birth and Sueo naming, Ono/Sugiyama win at Namiki, single-floor house |
| Known narrative clue still omitted from currently available original line capacity | **1** | `0x31F33`: original says **Maruko is turning nine**. Staged question correctly retains her Taurus zodiac and asks for birthdate, but not nine years old. Two physical native lines allow only **13 + 13 V2 glyph cells**. Do not truncate a name or force artificial shorthand solely to call it complete. |
| Independent new Quiz native text records introduced in 080 | **0** | All corrections are in previously staged original text fields. |

The above confirms each specific key fact, **not exhaustive sentence-level completeness for every earlier parent**. The age-nine clue remains a known unaddressed nuance until longer-text rendering/rewrapping can be safely approved.

## Source code / combined build integration

- `translation/runtime/quiz_parent_semantic_restore_080.json`: verified original parent records, pointer-word addresses, CP932 source, old stage strings, corrected Vietnamese text and true eight native 2-byte glyph spans.
- `tools/build_quiz_parent_semantic_restore_080.py`: fail-closed source manifest/stage hash lineage and V2 codepage audit. Actual ROM-dependent build validates clean original SHA, genuine native pointers, original Japanese glyph bytes, **the full real stage061 V2 font pointer**, exact original baseline V2 caption bytes from old 054/058 sources and required actual glyph lookups before writing the four changed lines. Preserves untouched layout, native control and ROM outside reviewed glyphs + checksum; emits only clean-original-relative cumulative IPS + JSON with exact replay validation. **Not yet run with the inaccessible historical V2 base.**
- `translation/runtime/quiz_remaining_fact_qa_080.json`: source-aware inventory of last 12 historical Quiz scanner aliases, including the explicitly unaddressed nine-year-old clue.
- `tools/recover_merge_061_81_one_ips_076.py`: one historical user-owned 039–043 ZIP/IPS → guarded cumulative 061 V2 base → 81 answer candidates → 077 continuation → 078 explanations → 079 corrections → **080 corrections** → ONE original-SFC-relative IPS and QA report, no commercial game ROM output.
- `.github/workflows/chibi-snes-source-qa.yml`: executes 080 ROM-free stage/source correctness audit, protected old field length and QA inventory. One initial workflow failed due a literal `0x` versus `0X` address-string comparison; fixed by integer parsing. A second attempt added the 12-parent ledger and initially omitted stages 057/059 in the source-only ledger lookup; fixed by importing these two old manifests. Always check latest current-head CI rather than claiming those historical failing runs passed.

## Release reality

The **historical staged Quiz source count stays 279/381**. In addition, 81 original Quiz answer candidates + three original separate non-answer field candidates (077/078) have static source-byte proposals, and checkpoint079/080 repair some already-staged narration facts. **No integrated Vietnamese-font game build, SNES emulator pass or proof that every user-facing label is Vietnamese has occurred.**

The only way to run the current guarded composite production-candidate source path is to recover one original **user-owned checkpoint039–043 ZIP/IPS**. All previously visible Library items remain only metadata, their archive bytes inaccessible. Do not claim that a passing code/ROM-source checksum solves the original UI width/font/grading issues. Further work: age-nine clue, Fortune's four long passages, G3 win/lose/result and title/Story, and direct SNES visual QA. No separate experimental IPS download is needed for this checkpoint.
