# Chibi Maruko-chan SNES — Checkpoint 045: 139 Story Batch02/03 lines inserted

Date 2026-10-11. Repo `RVTGMzz/VHSNES`, branch `chibi-maruko-bootstrap-01`.

## Larger content milestone, not more font experiments

User's standing requirements: **finish actual game content first; repair fonts after content; stop sending one-off IPS downloads for every iteration**. This checkpoint inserts **139 NEW full-screen/dialogue Story records** into the existing checkpoint044 clean-ROM-derived experimental build, including the **final island and farewell scenes**, and stores reproducible Vietnamese candidates and the build script on GitHub.

| Story group | Added in 045 | In experimental 045 ROM | Canonical row total |
|---|---:|---:|---:|
| Batch01 | 0 | **120** (117 tracked + 3 older tutorial fields) | 126 |
| Batch02 | **58** | **112** (54 from 044 + 58 new) | 126 |
| Batch03 | **81** | **81** | 84 |
| **Story overall** | **139** | **313** | **336** |

**23 Story records remain** (six Batch01, fourteen Batch02, three Batch03). These are NOT claimed translated in the ROM. Several were split across variable controls `50/51/52`; others begin with suspicious special glyph IDs, e.g. **`0x1A916` begins `88 F3`**. This was originally included in the draft but **removed from the final binary and GitHub manifest**. Similar suspicious starters `FA F3`, `92 F3` and `88 F3` are explicitly forbidden by the 045 builder. Do NOT patch technical/scanner artifacts as visible Japanese text.

**Cumulative source-record bookkeeping:** 402 tracked direct-text fields = 38 menu/VS/quiz UI + 33 Fortune + 21 Quiz + 310 tracked Story (84 in 042–043, +33/+54 in 044, +58/+81 in 045). Three older in-ROM localized Story tutorial fields are known separately, giving 405 direct field locations with Vietnamese bytes at the static ROM level (no double counting). Translated graphics G0/G1 (start title, exact `Việt hóa bởi Votri Valley`, selection/Start/Password) are separate from this count. Not all 1,018+ translation source rows are yet inserted.

## Editorial handling

Manually edited physical line slots were used, **not** an automatic first-N-character truncation. The full natural Vietnamese meaning remains unchanged in canonical `translation/source/story_batch02*.csv` and `story_batch03*.csv`; separate in-game compact candidates and exact offset/source anchor live in `translation/runtime/story_batch02_03_content_first_045.json`.

The new batch spans story outcomes, class voting aftermath, school friends, Tama-chan, Hanawa's `Baby` jokes, Maruo's `Nói thẳng ra!` characteristic, Maruko's family and grandfather, the school exchange, and the ending at the island. Text labels were checked against the existing `0x84` two-byte Vietnamese codepage and original Story script segmentation.

This is a fixed-width experimental translation; some compact phrases lose detail from the full Vietnamese source, and they **still require a real in-game editorial/legibility pass** before claiming natural 100% presentation. Long or dynamic dialogue needs safe expansion, NOT further destructive shortening.

## Binary static verification (actual physical source ROM)

The underlying clean Japanese ROM is **2,097,152 bytes**, SHA256:

`e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`

Input checkpoint044 ROM SHA:

`2312b9ba52c0cf6ac491e71117d5c537ad7dc61828dc9e87d838826e5165f322`

**Final checkpoint045 experimental ROM SHA:**

`7ddf449c2266838c3d55415f14aeee34fc21334c1ed0a490590647eb75e047b5`

**Final clean-Japanese-ROM-based IPS SHA:**

`685d7e9f0146950ca030fd8469f57313a0b368be98e0a9c95999bda48cb65379`

| Static QA item | Verified result |
|---|---|
| Additional Story records physically written | **139** |
| B02 / B03 new rows | **58 / 81** |
| Original physical glyph segments | **368** |
| Original `816F/81A5` line/page markers in edited records | **367 preserved** |
| All original Story bank `816F/81A5` positions | **UNCHANGED** |
| Whitelisted original writable glyph bytes | **7,918** |
| Byte positions changed vs checkpoint044 | **7,915**, contained in approved glyph regions + SNES checksum |
| Original script stop opcodes (e.g. `00/11/12/13/14/15/16`) | **UNCHANGED** |
| Existing codepage/font and G0/G1 artwork | **UNCHANGED** |
| SNES checksum / complement | `E4C1 / 1B3E` |
| Clean-ROM IPS size/records | **43,679 bytes / 1,568 records** |
| Independent 2MiB clean-ROM IPS replay | **PASS, exactly the target ROM SHA256** |
| Actual SNES runtime/emulator screenshots | **NOT TESTED** |
| Whole-game player-facing translation | **NOT FINISHED** |

Local experimental files were generated and hash-verified, **not** committed as a copyrighted ROM. The user has expressly asked **not to receive more piecemeal IPS links**.

## Reproducible GitHub source

- `translation/runtime/story_batch02_03_content_first_045.json`: all 139 verified source offsets, original Japanese scanner reference, canonical full Vietnamese meaning reference, scene/batch, and manually edited physical text line variants.
- `tools/build_content_first_045_story_139.py`: exact SHA input/output guards, canonical CSV identity, physical native 4bpp-game text frame sizes, unchanged special script opcodes and original line/page marker offsets, two-byte V2 glyph encoding with untouched font, source overlap fail-closed, static clean-ROM IPS replay and final checksum. Explicit `--allow-untested` required.
- The earlier draft tool named `tools/build_content_first_045_story_140.py` was removed from GitHub because it could rewrite suspicious metadata offset `1A916`; only the validated 139 script is active.

Rebuild from a full repository checkout with the exact clean ROM and exact checkpoint044 CLEAN-based IPS (not historical Build035 or an already patched ROM):

```bash
python tools/build_content_first_045_story_139.py clean-jp.sfc checkpoint044-clean-rom.ips \
  --ips checkpoint045-clean-rom.ips --report checkpoint045-qa.json --allow-untested
```

The physical original-ROM test and independent IPS comparison ran locally. The committed new GitHub builder itself has **not been run in a GitHub CI job**, and **no emulator gameplay QA** has been performed. Do not claim these were done.

## What's next

1. **Resolve 23 remaining Story records**, especially dynamic `Q/R/P` script variables and `88 F3` technical markers, by tracing live CPU text renderer/operand semantics rather than overwriting source bytes. Confirm consistent narrative and dialogue without clipping.
2. Cover remaining Quiz, Fortune, G2 actual rules, G3 result graphics, descriptions/tutorials, music/karaoke and Credits in a larger content pass; many canonical source translations are still not active in 045 ROM.
3. **Reconstruct all assets and text in one large integrated candidate and run real SNES emulator QA**, including earlier reported poor V2 font appearance. User said font later: do not begin 65816 font microtests now.
4. Continue publishing code and checkpoint on GitHub, **NOT** repeated interim patch download links. Preserve exact startup credit `Việt hóa bởi Votri Valley`.

**Status:** 139 new Story ROM insertions; Story static coverage 313/336; precise checksum/diff/IPS PASS; final gameplay and text completeness NOT YET VERIFIED.
