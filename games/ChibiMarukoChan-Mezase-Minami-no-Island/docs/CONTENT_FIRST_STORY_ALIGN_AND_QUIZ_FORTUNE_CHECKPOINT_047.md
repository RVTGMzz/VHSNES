# Chibi Maruko-chan SNES — Checkpoint 047: Story source coverage repair + Quiz/Fortune in-ROM content

Date 2026-10-11 · `RVTGMzz/VHSNES` · branch `chibi-maruko-bootstrap-01`.

## User instruction

User has repeatedly complained about month-long SNES localization, micro-checkpointing and unrequested IPS downloads. Prioritize **substantial content-first progress**, keep the old font unchanged until content is done, update GitHub reproducibly and **do not send intermediate IPS/ZIP links**.

## Why 23 Story rows seemed missing

The seven canonical Story source CSVs contain **336** entries. Previous experimental checkpoint045 had identified **313** as translated in the physical ROM, but the 23 residual entries were **not 23 independent dialogue windows**. Inspecting original raw CP932 characters established:

- **8 scanner offsets cut into the second byte of a two-byte fullwidth Japanese number**. The apparent Latin `P/Q/R/O` from the earlier scanner was **the trailing byte** of `１/２/３/０` (e.g. original bytes `82 51` for `２`, and source scanner falsely starting at its trailing byte `0x51`). These are **NOT runtime placeholders**.
- Four misleading scanner offsets were already translated as a subspan of a previously patched parent: `0x18408 → 0x183A7`, `0x189EE → 0x189B3`, `0x1A1B0 → 0x1A18F`, `0x1B159 → 0x1B13C`.
- Four others become covered once the **proper entire parent physical record** is translated, not a byte-fragment: `0x1B245 → 0x1B23A`, `0x1B34D → 0x1B33A`, `0x1B535 → 0x1B51E`, `0x1B631 → 0x1B620`.
- The three old tutorial rows at `0x181CC`, `0x18245`, `0x182BE` were already present in the experimental ROM and are counted **once**, not rewritten.
- **15 actual new distinct physical Story records** needed Vietnamese insertion, including special prefix cases. Some original records begin `E6 F3`, `88 F3`, `FA F3`, or `92 F3`. Their engine role is not confirmed, so the **original two-byte prefix was preserved unchanged**; only the original two-byte glyph slots after it were replaced. No claim that such prefixes are definitively non-rendering technical metadata.

### Checkpoint046 physical ROM result

15 real newly patched Story records, 31 native text segments, 30 original `816F/81A5` dialogue line/page markers physically preserved, zero changes elsewhere except header checksum. Guarded original bytes: **616 editable two-byte glyph bytes**; **620 changed ROM byte positions** including checksum. The source manifests include exact original Japanese file offsets, native starts, canonical `vi_full`, separate runtime wording, special prefix hex and physical field capacities.

| Exact artifact | SHA256 / value |
|---|---|
| Input checkpoint045 experimental ROM | `7ddf449c2266838c3d55415f14aeee34fc21334c1ed0a490590647eb75e047b5` |
| **Checkpoint046 ROM** | **`c10c0f444a97d6bea7f8f669d67bb6c0c5b6889b654d99d6e6dfa25e3d061624`** |
| **Checkpoint046 clean-ROM IPS** | **`11abac1b8e0f48e6580822bcdcd3b1b3568ae08676020b86c819ae641f53367d`** |
| IPS length and records | **44,450 bytes / 1,599** |
| Cartridge checksum/complement | `F71E / 08E1` |
| In-game emulator or screenshots | **NOT TESTED** |

**Exact source coverage re-audit performed via live GitHub:** all seven Story source CSVs (126+42+42+42+42+21+21 = **336** source rows) were cross-compared with ALL prior runtime manifests 042/043/044/045, new 046 physical entries, the 8 scanner aliases and the 3 previously localized tutorial entries. **All 336/336 source row IDs are accounted for; 0 missing and 0 extraneous.** This is a **source-to-ROM field mapping result only**, not proof the player can see/read correct Vietnamese in-game.

Distinct tracked original physical Story text records = prior **310** (26+58+87+139) + new **15** + earlier **3 tutorial records** = **328** physical records represented by 336 canonical CSV scan rows. Still possible there are additional visible strings outside these seven tables.

## Checkpoint047: 30 more actual Quiz + Fortune text replacements

After rebuilding the checkpoint046 original ROM, another **30 fixed-width source entries** were encoded into real ROM bytes:

| Domain | Newly patched | Content |
|---|---:|---|
| Quiz | **15** | Numeric age answers, grade/class identifiers (e.g. `3-4`), exact birthdates (e.g. `23/4`) and price choices |
| Fortune | **15** | 10 digits as lucky numbers, 3 multi-million amounts and 2 short fortune tips (`Gọi thử!`, `Văn hên!`) |
| **Total** | **30** | Original two-byte CP932 source, glyph limit, original `816F` terminator verified for each |

The compact quiz choices preserve the numeric value; units are supplied by the corresponding question context. No character names were mangled or cut merely to fill a count. Existing canonical `vi_full` text was **not edited**. All new font characters use existing V2 `0x84xx` codepage; glyph bitmaps were not changed.

| Exact artifact | SHA256 / value |
|---|---|
| **Final checkpoint047 ROM** | **`1f6430064b70671a4f3ba94f0fd256764db54690950519c22d9e03ec74230dd9`** |
| **Final original-clean ROM IPS** | **`725ca433dfeb919bd19bde6903a1e2e7d95cde1889980677863724007090cd6c`** |
| IPS length and records | **44,980 bytes / 1,671** |
| Relative bytes changed vs 046 | 174 byte positions, confined to 222 writable source glyph bytes + checksum |
| New SNES checksum/complement | **EB53 / 14AC** |
| Clean-ROM IPS replay using separate decoder | **PASS** (2,097,152 bytes equal, correct SHA) |
| Actual SNES emulator game QA | **NOT TESTED** |

**Cumulative experimental content physically integrated:** 38 old UI fields + **48** Fortune (33+15) + **36** Quiz choices (21+15) + **328** distinct Story physical records = **450** direct translated text windows, separate from G0/G1 on-ROM graphics (first-boot title, `Việt hóa bởi Votri Valley` credit, mode heading and Start/Password). This does **NOT** mean the game is completely Vietnamese: around 381 canonical Quiz source rows and 157 Fortune source rows exist, and most non-Story dialogue/question content has not been built into this experimental ROM.

## GitHub source-of-truth and reproduction

- `translation/runtime/story_special_cp932_alignment_046.json` — 15 new native Story text records, protected `xx F3` prefixes, 8 repaired Japanese-digit scanner aliases, unchanged canonical full Vietnamese.
- `tools/build_content_first_046_story_special.py` — deterministic exact clean+045 IPS binary builder, source identity/cp932 offset checks, immutable script code and page/line markers, exact 046 output SHA/IPS guard.
- `translation/runtime/quiz_fortune_exactfit_047.json` — 30 further Quiz/Fortune natural compact variants and exact original/source-file anchors.
- `tools/build_content_first_047_quiz_fortune_30.py` — deterministic exact clean+046 IPS binary builder, original CP932 2-byte source/delimiter/codepage guards, output hash and IPS replay.
- `docs/CONTENT_FIRST_STORY_ALIGN_AND_QUIZ_FORTUNE_CHECKPOINT_047.md` — this document.

Local ROM/IPS output is **experimental and kept out of GitHub**; the repository contains reproducible source and noncopyrighted metadata. Source-committed tools were not run in GitHub CI (no status checks configured), while equivalent local binary patching and independent IPS replay did pass static tests.

## Next priorities

1. **Quiz and Fortune broad remaining content:** the biggest outstanding percentage now. Restore more of their source CSVs into the actual ROM using verified original text record control lengths, not broken abbreviations or character-name truncations. Need real field expansion/relocation for long questions and choices.
2. G2 tutorial rules: real direct CP932 text at `0x1E307/0x1E325/0x1E339`, corrected half-glyph source; not yet in integrated ROM. Need size/wrap-safe representation without dropping essential rule logic.
3. G3 win/lose/results screens: rendered asset/callback still untraced; do not overwrite internal QA descriptors as player-facing visuals.
4. Full completeness sweep, one sizable emulator test after content integration, then font/visual quality work. Previous user-reported font deformity remains unresolved.

**No intermediary IPS download links to the user.** Continue pushing meaningful game data and tools. Distinguish original byte-level validation from runtime gameplay QA.
