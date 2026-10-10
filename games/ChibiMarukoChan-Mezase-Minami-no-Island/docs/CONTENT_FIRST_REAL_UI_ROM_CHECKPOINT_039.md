# Chibi Maruko-chan SNES — Checkpoint 039: graphics G0/G1 + 38 direct Vietnamese UI fields in one ROM candidate

Date: 2026-10-11. Repository: `RVTGMzz/VHSNES`, branch `chibi-maruko-bootstrap-01`.

## User priority remains: CONTENT FIRST, FONT LATER

After checkpoint038 discovered the exact historical direct-text **Build035** binary was unavailable, this checkpoint **did not stop** at another font or G3 scanner report. It created a **new, actual patched SNES ROM candidate** by combining three already verified clean-ROM-derived layers:

1. The original 2MiB Japanese ROM (exact SHA256 below).
2. The already-existing **Probe008 V2 FONT ONLY** ROM (recovered exactly in checkpoint031), including 0x84 codepage and existing glyphs. **Its bitmap, layout and renderer were NOT modified in this checkpoint.** This does not constitute font-runtime acceptance.
3. The existing **GRAPHICS checkpoint036** ROM containing actual on-ROM Vietnamese G0 startup title and credit and G1 main-mode/Story graphics.

Then **38 additional direct-text UI fields** were rewritten, using only the exact-fit Vietnamese candidates already in `translation/runtime/`, without changing the original Japanese control bytes.

### Actual in-ROM Vietnamese content added in 039

| Category | Fields actually patched |
|---|---:|
| Main menu mode/sound labels | **10** |
| VS/minigame/Quiz direct UI labels | **28** |
| **Total newly patched direct UI source fields** | **38** |

Examples: `Truyện`, `Đấu`, `Đấu đội`, `M.Q`, `Tập vẽ`, `Bói`, `Hát`, `Âm`; match setup `Ván?`, `Độ khó`, `Mỗi ván`, `Dễ`, `Vừa`, `Khó`, player states `P1`–`P4`, and Quiz `Bấm START`, `Tiếp tục?`, `Có`. Source translations `vi_full` were **not truncated or edited**: these are separate compact runtime candidates with strict field sizes. One entry `SS` is the game's `Super Scope` accessory shorthand, not an untranslated Japanese label.

**Five more direct UI entries deliberately remain in Japanese** because `runtime_needs_expansion` in the existing source, and no natural, accepted exact-fit Vietnamese version exists:
`0x28B28` `Đến khi thắng`, `0x28B40` same, `0x28BC6` `Không kết nối`, `0x28BDE` `Chuột`, and `0x31D3A` `Không`. **Do not force awkward broken abbreviations into these.** They need asset layout/field expansion later.

## Verified binary contract

| Property | Value |
|---|---|
| Exact clean Japanese ROM SHA256 | `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956` |
| Exact already-existing V2 font-only SHA256 | `2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd` |
| Exact graphics036 SHA256 | `2c8beee73e985c9a2690cc36ace335f05115c1a3e81b369e09d0cfb132117090` |
| **New combined experimental 039 ROM SHA256** | **`a1f4459942e3a757cc314d12c959168046b4a6dd66018d55b014c70d052e98ce`** |
| New direct UI fields applied | **38** |
| V2 and graphics036 changed-byte overlaps excluding header | **0** |
| Source Japanese byte identity | **38/38 PASS** |
| Original field sizes | **38/38 unchanged** |
| Original `816F` delimiters and any intervening ASCII/full-width spaces | **38/38 preserved** |
| Existing V2 0x84 codepage glyph lookup | **all generated codepoint pairs validated** |
| Existing G0/G1 compiled graphic resource byte spans | **identical to checkpoint036** |
| ROM byte changes vs original Japanese ROM | **17,752** |
| SNES checksum / complement | **`0x7485 / 0x8B7A`** |
| Combined clean-ROM IPS patch | **21,130 bytes / 674 IPS records** |
| Independent IPS replay on exact clean Japanese ROM | **PASS, byte-for-byte exact new output SHA** |
| Actual SNES emulator / gameplay | **NOT TESTED** |
| Full game Story/Quiz/Fortune Vietnamese | **NOT IN THIS ROM** |

Three controls deserve explicit QA:

1. Direct strings use **two-byte** V2 codepage `0x84xx` only. Every destination field is encoded to its original number of 2-byte glyph units with `8440` spaces as padding. Original Japanese CP932 bytes are checked exactly.
2. Some UI records have extra single-byte spaces or full-width `8140` between the field and `816F`. The builder preserves those **original control/layout suffix bytes**, rather than mistakenly identifying them as a new writable field.
3. The new output is pinned to its independently produced SHA256 and IPS record count. If source GitHub CSVs, font/table mapping, graphics or Japanese ROM differ, fail closed instead of silently generating unreviewed data.

Local verified IPS-only artifact (NO commercial ROM inside): `Chibi_039_G0G1_38UI_Content_First_UNTESTED.zip`. Contains IPS, a Vietnamese README, builder report and independent verifier report. **Do not require user to test yet**; this is not a full-language release.

## Committed reproducible builder

`tools/build_content_first_g0g1_v2_38_ui_039.py`

It reads the repo's original source-of-truth files:

- `translation/runtime/main_menu_compact_v1.csv` — ten exact-fit entries.
- `translation/runtime/ui_choices_compact_v1.csv` — 28 exact-fit entries; exclude five marked `runtime_needs_expansion`.
- `translation/codepage/vi_codepage_v4_fe4_native.csv` — all Unicode-to-actual-V2 0x84 pairs.

The independent **local equivalent** of this builder was executed against exact physical ROM binaries and 38 locally reconstructed CSV fixture rows representing the published candidate values; it rebuilt the identical output hash `a1f445994...`, checksum and IPS. **The newly committed GitHub tool itself was not run in CI**, and the GitHub repo's latest commit has no configured status checks. Do not claim GitHub CI PASS or full-repo checkout was exercised.

Usage in a full checkout:

```bash
cd games/ChibiMarukoChan-Mezase-Minami-no-Island
python tools/build_content_first_g0g1_v2_38_ui_039.py \
  clean.sfc recovered-v2-font-only.sfc exact-graphics036.sfc \
  g0g1-v2-38ui-UNTESTED.sfc \
  --ips g0g1-v2-38ui-UNTESTED.ips \
  --report g0g1-v2-38ui-static.json --allow-untested
```

For all inputs use exact SHA256 above. Neither ROMs nor TTF/font files are on GitHub.

## What is STILL NOT done

- **Historical direct-text Build035 was NOT recovered.** Thus most Story, Quiz, Fortune, Karaoke, Credits and other full-language source work is still **absent from this newly built candidate**, although the meaning-first CSVs exist (1,018 regular rows + three G2 demos).
- Checkpoint032's 216 final editorial `vi_full` revisions are source changes and still require inclusion in a true direct-text runtime builder.
- G2 corrected source offset `0x1E325` and rules are **not yet integrated into this ROM**. G3 actual Win/Lose/Continue/Ending display assets are **not proven** and remain on the queue.
- Probe008 V2 typography previously gave poor visual results in a different renderer diagnostic. Reusing its existing font bytes is NOT equivalent to fixing font spacing or real-screen legibility. User asked font AFTER content progress.
- No SNES emulator runtime or screenshots; no release-ready claim.

**Next work should be high-impact:** reconstruct a reproducible larger direct-text Story/Quiz/Fortune builder from canonical source CSVs without needing lost Build035, or recover the exact binary if the user supplies it; verify actual G3 retail result content, preserve G0/G1 assets and choose one future comprehensive user test. Avoid serial font-only checkpoints.
