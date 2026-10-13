# Chibi Maruko-chan SNES — Checkpoint 079: Recover 3 missing facts in previously translated Quiz narration

Date: 2026-10-13 · Branch `chibi-maruko-bootstrap-01`.

## Why this is a content-editing checkpoint, not another repointing experiment

Checkpoint078 recovered two missed native Quiz explanation fields. The **18 other canonical scanner offsets** (10 nested + eight still unsafe as standalone starts) were carried forward for a *semantic review*, not a blanket "done".

This checkpoint re-read the actual Japanese original user-owned 2MiB retail ROM, SHA256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`, and compared full native CP932 text under the genuine nine Quiz pointer-table references with the Vietnamese staged 057/058/059 captions. **Three real translation omissions** were found. These are *already-staged fields whose earlier compressed line translations omitted facts*, so they must **not** be counted as three new original source IDs or repaired by rewriting old SHA-pinned stage manifests.

## Three restored narrative facts

| Real original Quiz script and pointer | Japanese fact missing in previous VN lines | Previous VN | Corrected proposed VN (original line capacities) |
|---|---|---|---|
| `0x3271A`, pointer `0x31399`, staged `0x3271E` at 059 | Father Hiroshi is **40** and likes **fishing** and singer **Misora Hibari**; old VN forgot his age | `Bố mê câu cá` / `và Misora nữa` | `Bố mê câu cá` (12/13) / `40. Mê Misora` (13/13) |
| `0x3296D`, pointer `0x31171`, staged `0x32971` at 058 | The older sister is in **sixth grade** and is a **Saijo Hideki fan**; old VN omitted the celebrity | `Chị của Maruko` / `học lớp 6 rồi` | `Chị lớp 6 mê` (12/14) / `Saijo Hideki` (12/14) |
| `0x35D78`, pointer `0x313AD`, staged `0x35D7C` at 057 | Yoshiko is specifically in **class 6-2**, attends class with Maruko's elder sister, and **likes Koyama**; old VN lost class number and her crush | `Yoshiko học` / `chung khối với` / `chị Maruko` | `Yoshiko 6-2` (11/13) / `cùng lớp chị` (12/14) / `mê Koyama` (9/14) |

These are deliberately compact quiz caption lines, constrained by the SNES original *physical glyph-cell width*. The complete proper name **Saijo Hideki** and **Koyama** remain intact. The original text also describes the sister's cool personality and calls the singer **Misora Hibari**; those details are acknowledged in editorial context but were not all squeezed into the 13/14-cell displayed caption slots. Do not claim a complete lossless rendition of every Japanese word until an emulator-supported wider-text solution is verified.

The exact original byte positions of the seven nonblank Japanese glyph spans were read from the user-owned SFC and checked in this session:

`0x3272A` (13), `0x3274C` (13), `0x32977` (14), `0x3299B` (14), `0x35D84` (13), `0x35DA6` (14), `0x35DCA` (14).

All seven original CP932 spans matched the expected Japanese glyph strings, including names, year 6-2 and age 40. No game control codes, bank pointers, text window sizes or emulator behavior were guessed.

## Actual committed implementation

- `translation/runtime/quiz_parent_semantic_restore_079.json` contains the **three original whole-record anchors, actual LoROM pointer-word offsets, stage057/058/059 old lines, seven exact glyph-slot ROM offsets and widths, Japanese originals and newly edited Vietnamese lines**.
- `tools/build_quiz_parent_semantic_restore_079.py` is a **post-stage061 exact-V2-font-only corrective overlay**. It does not alter the historical 057/058/059 source-manifest files or their pinned original-ROM IPS digests. It checks the original ROM SHA and exact original Japanese glyph spans/pointer table values, verifies all existing *Vietnamese old captions* match the actual previously staged font-V2 bytes at the physical addresses, verifies the font pointer at `0x2975E == 0x9A74`, verifies required V2 glyph lookups are present, and writes only 7 reviewed glyph spans + standard LoROM checksum. It refuses unknown source overwrites, unsupported glyphs, width overflow, wrong baseline, wrong original ROM or IPS replay mismatch. It generates a clean-original-ROM-relative cumulative IPS and audit report **only when the actual old 039–043 V2 historical archive is available to rebuild the merged 061 baseline**.
- `tools/selftest_quiz_parent_semantics_079.py` runs without any ROM: checks actual historical 057/058/059 manifests for the old text, each original Japanese slot, all new V2 encoded characters and widths, 18 scanner-offset review inventory and non-release QA flags.
- `tools/recover_merge_061_81_one_ips_076.py` now inserts checkpoint079 **after** 061 base recovery, full 81 Quiz choices (075), one 077 question continuation and two original 078 missing explanations — thus users will eventually need **one historic 039–043 ZIP/IPS and get one cumulative patch**, not serial incompatible mini-patches.
- Real GitHub Actions `Chibi SNES source localization checks` [run 38340814478](https://github.com/RVTGMzz/VHSNES/actions/runs/38340814478) completed **SUCCESS** with 079's ROM-free semantic/cell audit and previous CI suite. This **does not** mean an SNES emulator test or a finished integrated ROM.

## Remaining 18 original scanner aliases: actual editorial classification

The 18 IDs are **not 18 independent executable text records**. Three have received newly authored semantic content corrections in 079: `0x3275E`, `0x3299F`, `0x35DB3`. The remaining 15 still need context-oriented verification of their staged parent scenes or original scanner boundaries:

- Nested: `0x31E50`, `0x31E7B`, `0x31F33`, `0x32874`, `0x32A96`, `0x32C15`, `0x33050`, `0x33119` (eight).
- Other unsafe scanner aliases: `0x34403`, `0x34A99`, `0x352AC`, `0x352C2`, `0x353F3`, `0x361A4`, `0x364B1` (seven).

Original-source physical text and nearby translated parents were looked at in this session to prioritize actual missing details; this does **not** establish that every remaining scene preserves every narrative detail. Future source QA should prefer checking and re-anchoring genuine native fields, not treating overlapping scanner offsets as separate game strings.

## Correct overall progress and next priorities

**Official prepared/staged Quiz scanner IDs remain 279/381.** This checkpoint restores missing facts in three already-staged parent fields; it does not add three separate approved fields. The previously identified **81 full answer candidates + three real non-answer field candidates** are still source-byte proposals, not emulator-accepted. There are no restored, loadable historical 039–043 IPS/ZIP bytes in this session and no verified rendered Vietnamese game build; the unmodified Japanese SFC contains no V2 Vietnamese glyph map. Do not distribute this stage as a standalone playable IPS.

Most valuable next user-facing step is still **recover just one user-owned original historical 039–043 archive**, build the combined IPS and do actual gameplay QA: quiz option widths, correct answers, long mixed Kanji/Vietnamese labels, story progression, Fortune's four overlong fields, G3 result/ending screens and title credit. User prefers content completeness before final font aesthetics, but all diacritics must render correctly.
