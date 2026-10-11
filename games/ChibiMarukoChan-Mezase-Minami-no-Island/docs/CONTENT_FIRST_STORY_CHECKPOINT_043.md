# Chibi Maruko-chan SNES — Checkpoint 043: 58 more real Story dialogue records

Date: 2026-10-11. Branch `chibi-maruko-bootstrap-01` in `RVTGMzz/VHSNES`.

## Significant content-first milestone

The user instructed: **complete Vietnamese story/menu/game graphics first; font/renderer later**. This checkpoint builds a **new actual SNES clean-ROM-based IPS** by adding **58 new edited Story Batch01 dialogue/narrator records** to the existing checkpoint042 integrated ROM. It is not another font diagnostic or a mere language-planning report.

- **58 additional Story records**, with **170 physical glyph segments**.
- **167 original source `81 6F` / `81 A5` line/page control markers preserved** within these records.
- **All** `816F/81A5` marker positions across the source Story bank `0x18000..0x1DFFF` remain byte-identical to checkpoint042.
- 26 earlier Story records from 042 remain intact. Therefore **84 Story Batch01 text records physically Vietnamese in the current experiment**, out of its 123 canonical `story_batch01_vi.csv` rows; **39 still not patched**. Historical broader Story Batch02/03 content remains pending in this reconstructed pipeline; never describe 84 as all Story.
- Prior 38 UI +33 Fortune +21 Quiz remain intact, giving **176 actual direct-text fields** in the experimental build, plus the separate translated G0/G1 artwork (first-boot `Chibi Maruko-chan` / `Tiến tới đảo phương Nam!!` / `Việt hóa bởi Votri Valley`, mode choice, `Bắt đầu`, `Mật khẩu`).

The added dialogue covers class discussions about the school exchange, the exaggerated excitement about going overseas for free, Tamae/Maruko tension, Maruo's self-important contest rhetoric, Hanawa's characteristic “Baby”, the family jokes and the early match wins/losses. This runtime wording was manually edited **per scene and per original display segment**; complete `vi_full` original Vietnamese translations were **NOT** replaced, clipped or overwritten in the canonical source.

Examples of connected dialogue fragments (each separated physically into its original line windows):

- `Maru-chan, cậu / qua đó để / học mà`
- `Nói thẳng ra! / Đại diện lớp phải / là tôi đó!`
- `Tama-chan, tớ xin / lỗi. Cậu ổn chứ?`
- `Baby, tớ yếu lòng / trước các quý cô / như cậu mà.`
- `Sakura hạ Maruo / và Hanawa`

The source includes some one-character blank segments in its original script; these were padded with the existing V2 `8440` space character, not used to overwrite adjacent control bytes. The final/longer canonical narrative text stays in `translation/source/` to be handled by a future safe layout-expansion path. We do **not** claim that all runtime shortened dialogue is as rich as full-width translation; player review remains necessary.

## Precise technical scope

| Field | Result |
|---|---|
| Exact clean 2MiB Japanese SHA256 | `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956` |
| Original 042 ROM SHA256 | `901744ff2edb6bbf667e225e68478009f426a4d1358c1c35ccb34cdc29254691` |
| Exact clean-ROM 042 IPS SHA256 | `3e3c3de245a9a0a6648b2e62eff44a72093ef1e2e9cfcb1cf013ff6c4cbb5035` |
| **New 043 ROM SHA256** | **`45ffca7db5db83bc2734e885ee90c77f33746e2c4a54d1c99f1502f3e992a6ae`** |
| **New clean-ROM 043 IPS SHA256** | **`d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50`** |
| Additional Story records | **58** |
| Additional physical segments | **170** |
| Original line/page markers inside those records | **167 preserved** |
| Writable original Story text bytes covered | **4,148** |
| Actual ROM changed-byte positions vs 042 | **4,144** (within those fields + checksum only) |
| Exact clean-ROM IPS size | **28,135 bytes / 977 records** |
| SNES checksum / complement | `0xE83A / 0x17C5` |
| Independent IPS replay onto CLEAN ROM | **PASS, exact target 043 SHA256** |
| Original Story bank `816F`/`81A5` marker positions | **UNCHANGED** |
| Font/glyphs/renderer modified | **NO** |
| Existing G0/G1 pixels + previous 118 direct fields | **UNCHANGED** |
| SNES emulator gameplay/screenshot QA | **NOT TESTED** |
| Finished whole-game Vietnamese release | **NO** |

All glyphs were mapped into the existing 0x84 two-byte V2 codepage, with no glyph bitmap changes. The base 042 ROM's original Story source bytes were required to match clean Japanese ROM at every new target offset; no already-patched field was re-edited. Odd-byte spans, unsupported controls/codepoints, per-segment overflows, crossing into original line markers, and overlapping replacement spans were rejected. The old extra source offset beginning at an ASCII/variable marker was not forced into the patch.

## Reproducible source now on GitHub

- `translation/runtime/story_batch01_safe_segments_043.json`: all 58 manually selected Story runtime line sequences, exact source offsets and **per-segment capacity counts**, plus exact `vi_full_reference` from canonical Story CSV. Status is **static editorial candidate**, not user-accepted runtime presentation.
- `tools/build_content_first_043_story_58.py`: starts from exact clean Japanese ROM + exact 042 IPS; uses original ROM script layout and repo's V2 Unicode table, validates every original field and the prior 042 non-overlap set, all original marker bytes and the whole bank's marker positions, source `vi_full` identity, final ROM/IPS hashes and checksum. Explicit `--allow-untested` required.
- `docs/CONTENT_FIRST_STORY_CHECKPOINT_043.md`: this document.

Rebuild from a full checkout:

```bash
cd games/ChibiMarukoChan-Mezase-Minami-no-Island
python tools/build_content_first_043_story_58.py \
  original-japanese.sfc checkpoint042-clean-rom.ips \
  --ips checkpoint043-clean-rom.ips \
  --report checkpoint043.json --allow-untested
```

The exact new ROM/IPS was physically constructed and verified against the actual original ROM using an independent local Python implementation; 58/58 physical source layouts and bytes were checked. The committed GitHub builder was derived from the previously published 042 build tool; **it was not separately run by GitHub CI** (no configured status checks), so do not claim CI PASS or SNES runtime PASS.

Local shareable **patch-only** archive, NOT a game ROM:

`Chibi_043_G0G1_176Fields_Story58_Content_First_UNTESTED.zip`

It contains the 043 clean-ROM IPS, independent static QA JSON, list of the 58 new Vietnamese dialogue segments and instructions. Do not apply this IPS on top of already modified ROMs: it is solely for the exact CLEAN Japanese cartridge dump.

## Continue next, content first

1. **Remaining 39 of 123 Batch01 Story records:** prioritize multi-window natural complete replies where physically safe; particularly long speeches, the exchange announcement and Tamae/Maruko narrative require a real larger-field text/layout plan, not stilted one-word compression.
2. Reconstruct **Batch02 and Batch03** from canonical meaning CSVs using actual CP932 script spans, not scanner-only artifact offsets. Audit total original 328 Story records from old Build027 separately from current physically inserted 84.
3. Next milestone must meaningfully improve long-text presentation or large multi-scene coverage, not return to 025–031 font patches. Source code and patches must remain GitHub-reproducible.
4. Add G2 rule text and exact remaining UI, then trace executed G3 result screens before editing. One larger future emulator QA, no micro-test barrage.

**Checkpoint043 status: 58 new real text insertions + full exact IPS static QA PASS; Story incomplete, no in-game runtime acceptance, font work deferred.**
