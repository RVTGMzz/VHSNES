# Chibi Maruko-chan SNES — Checkpoint 042: First 26 REAL Story text fields integrated

Date: 2026-10-11. Repo `RVTGMzz/VHSNES`, branch `chibi-maruko-bootstrap-01`.

## User's standing priority

**Complete game text, dialogue, menus and graphics first; font/renderer work later.** The user also dislikes numerous tiny diagnostics and unnaturally chopped-up dialogue. This checkpoint edits real retail SNES ROM text and maintains complete, natural Vietnamese source meanings for any content requiring larger future boxes.

## Actual work completed

Starting from the **exact checkpoint041 clean-ROM IPS**, 26 vetted dialogue/narrator source records from the beginning of Story Batch01 were physically rewritten in the SNES ROM.

- **26 first-arc player-facing Story entries** newly encoded as Vietnamese, in **41 original physical text segments**.
- The canonical complete `vi_full` translations in `translation/source/story_batch01_vi.csv` were NOT shortened or overwritten. The new `translation/runtime/story_batch01_safe_segments_042.json` holds separate **edited compact runtime lines** and copies their exact canonical `vi_full_reference` to detect future source/meaning drift.
- Proven speaker/voice-sensitive examples: `Cô có tin vui!`, `Tớ cũng muốn đi!`, `Tama-chan thi?`, `Ơ... tớ thì...`, `Ta-Tama-chan...`, `Tớ nói gì đâu...`. Narrative comments remain distinguishable from personal dialogue, and Hanawa's recurring “Baby” remains recognizable.
- Conservatively use original Story text windows only, rather than trimming full text mechanically or creating random Japanese-scanner source rows. Two-word/day-specific framing remains in larger canonical translations where an 8×8/2-byte source field cannot fit it.
- One apparently easy `0x18408` source record was **excluded** because its raw first byte is ASCII `0x50` (`P`) inside dynamic script text, NOT a proven replaceable normal CP932 glyph. An early-artifact `印`-prefixed field was also excluded. These controls/metadata need a separate guarded treatment before re-insertion.
- Other long Story lines still remain Japanese in the binary, even where their FULL `vi_full` source translation is already present. No false whole-game progress percentage should be stated.

## Original game text segmentation and safety

Real original ROM sample:

At file `0x1852C`, the Japanese text has **two distinct glyph spans** separated by `81 6F`:

`はやいはなしが  タダで` / `がいこくに 行けるってことだね`

New compact Vietnamese in exactly those spans:

`Được đi xa` / `miễn phí còn gì!`

The builder understands:
- **`81 6F`** as the original line break, and **`81 A5`** as a page/speech marker.
- Other raw low-byte story engine opcodes (`0x00`, `0x0E`, `0x0F`, `0x08`, `0x12`, `0x14` etc.) are not writable dialogue pixels.
- Original field regions can have single-byte ASCII `20` padding among double-byte Japanese characters; new Vietnamese maps via existing `0x84xx` V2 table and pads to the exact old byte limit, leaving odd trailing byte untouched.
- Original control-byte locations are physically preserved, not regenerated from a CSV.
- The code refuses unknown ASCII/control tokens, source changed by prior patch, codepoints without valid V2 mapping, line-by-line overflows, overlapping fields, or output hash drift.

### Static validation performed from the actual ROM and independent IPS decoder

| Check | Result |
|---|---|
| Exact 2MiB original Japanese SHA256 | `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956` |
| Exact checkpoint041 baseline SHA256 | `56c36cbc8e477d262216d3aa0f06909e09b9929ba0f6f544dccbaa3671bf48fb` |
| **New 042 experimental ROM SHA256** | **`901744ff2edb6bbf667e225e68478009f426a4d1358c1c35ccb34cdc29254691`** |
| **New clean-ROM IPS SHA256** | **`3e3c3de245a9a0a6648b2e62eff44a72093ef1e2e9cfcb1cf013ff6c4cbb5035`** |
| New physical Story text records | **26** |
| Distinct physical text spans | **41** |
| Explicit `816F` / `81A5` Story break markers within those rows | **40 preserved** |
| Entire Story bank positions of both marker pairs | **Unchanged** |
| Existing checkpoint041 UI/Fortune/Quiz fields | **92 preserved** |
| **Total direct-text source records physically patched in this experimental build** | **118** |
| Existing G0/G1 graphics + Votri Valley title credit | **Preserved** |
| Existing V2 glyph/codepage ROM bytes | **Unmodified** |
| Actual changed bytes vs 041 ROM | **794**, only 26 approved text regions + cartridge checksum |
| Checksum / complement | `0x3988 / 0xC677` |
| IPS size / records | **23,105 bytes / 799 records** |
| Independently reapply IPS on exact clean ROM | **PASS, exact final 042 ROM SHA256** |
| SNES emulator and user screenshot | **NOT TESTED** |
| Full game Story/Quiz/Fortune completion | **NOT COMPLETE** |

The local read-only checker `Chibi_042_Independent_Static_QA.json` independently reconstructed **both** ROM 041 and ROM 042 from their clean-based IPS patches, compared all 2MiB bytes, confirmed no changes before/after the Story data region except checksum, compared entire bank `816F` and `81A5` positions, and checked checksum math. It is NOT a CPU/PPU runtime test.

## GitHub reproducibility

- `translation/runtime/story_batch01_safe_segments_042.json` — 26 runtime dialogue/narrator candidates; canonical `vi_full` and expected physical source line capacities.
- `tools/build_content_first_042_story_safe_segments.py` — reads the *existing* source Story CSV and codepage CSV directly, validates the exact 041 clean-based IPS and ROM SHA256, inserts only source spans, fails on any control-byte movement and verifies exact resulting 042 ROM and IPS hashes.

Rebuild in a full repository checkout:

```bash
cd games/ChibiMarukoChan-Mezase-Minami-no-Island
python tools/build_content_first_042_story_safe_segments.py \
  exact_clean_japanese.sfc exact_041_clean_rom.ips \
  --ips checkpoint042_clean_rom.ips --report checkpoint042.json --allow-untested
```

The physical ROM, font files and emulator screenshots are not committed to GitHub. The new script is source-reviewed and locally equivalent binary construction was verified from the physical ROM, but **the committed script has not been run by GitHub CI**, so do NOT claim CI PASS.

Local patch-only package: `Chibi_042_G0G1_118Fields_Story26_Content_First_UNTESTED.zip` (IPS, Vietnamese README and two JSON reports, no ROM).

## Scope and next meaningful steps

The prior historical Build027 claimed **328 original Story fields** patched through Batch03, but neither its runtime candidate table nor its executable build source survived in the repository. Checkpoint042 recovers the first **26** safe Story text fields reproducibly; it is not the whole 328 and should not be represented as such.

1. Continue Story Batch01 + Batch02/03 **segment-aware text assembly** with natural Vietnamese, consistent speaker voice and controls. The next payoff is to restore tens/hundreds more with reliable existing script layout.
2. For long rows unable to fit, research proven executable Story data-pointer/record relocation or larger dialogue layout before writing, **never overwrite next script or truncate meaning without editorial approval**.
3. Add missing G2 rules (`0x1E325` fixed source bug) and five exact-fit-excluded UI labels only when safe, then G3 actual result graphics once linked to real screen code.
4. Produce **one large eventual emulator test**, not dozens of tiny builds. V2 glyph font was reused but previously user-reported ugly/incorrect typography is unresolved; **font remains deferred** as requested.

**Status: 26 actual Story records integrated and independently verified at binary level; full Story and gameplay QA pending.**
