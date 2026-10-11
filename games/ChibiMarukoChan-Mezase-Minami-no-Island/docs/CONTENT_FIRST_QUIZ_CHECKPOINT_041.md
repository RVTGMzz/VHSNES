# Checkpoint 041 — 21 more Quiz answers integrated into Chibi Maruko-chan SNES ROM

Date: 2026-10-11. Branch: `chibi-maruko-bootstrap-01`. **User priority: complete content/graphics first; address font only later.**

## Concrete game data progress

An experiment based on the actual ROM generated in checkpoint040 adds **21 new Vietnamese Quiz multiple-choice fields** into **their original player-facing CP932 string positions**. Not merely a CSV review: exact Japanese bytes in the clean ROM, old field glyph-unit sizes, existing `816F` record terminators and existing V2 `0x84xx` character lookup were checked before each write.

| New Quiz fields | Count |
|---|---:|
| Short answer types, including `Hài` / `Đố` / `Tài xế` | 3 |
| Ages, e.g. `２９才 → 29` | 9 |
| Birthdates, e.g. `１２月３１日 → 31/12` | 3 |
| Grade/class, e.g. `６年２組 → 6-2` | 3 |
| Floors in multiple-choice options, e.g. `１かい → T1` | 3 |
| **Total fields written** | **21** |

These are compact **choice-label** variants only; the full `vi_full` strings are unchanged. 21/21 source identities (`file_offset`, Japanese original, full Vietnamese translation) cross-checked live from five canonical Quiz source CSVs. **Two scanner-derived question fragments were deliberately rejected** because their claimed Japanese text did NOT match the raw ROM byte window at that offset; we did not overwrite them. Character names that would lose identity when shortened were also skipped.

New canonical runtime candidates:

`translation/runtime/quiz_answers_exact_fit_041.csv`

Reproducible guarded builder:

`tools/build_content_first_041_quiz.py`

Uses clean Japanese ROM + **exact checkpoint040 clean-ROM IPS**, source Quiz CSVs, and the existing V2 codepage mapping. Checks all UTF-8 NFC compact strings, source Japanese, `816F`, character capacity, same original bytes in 040, mapped glyph existence, one-file-offset uniqueness, binary change whitelist and deterministic ROM/IPS hashes. Requires explicit `--allow-untested`; does not modify dialogue font or source `vi_full`.

## Exact build and static QA

| Field | Value |
|---|---|
| Original clean 2MiB Japanese SHA256 | `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956` |
| Input 040 IPS SHA256 | `2bfdcc64973bc31ce268fa7e68a6118808c633b10d1437b7f811ac290616e580` |
| 040 base ROM SHA256 | `d892c51576c103f5881f1481c65fd2746635d222b1d387f9666cd7f44b1da3ac` |
| **041 updated ROM SHA256** | **`56c36cbc8e477d262216d3aa0f06909e09b9929ba0f6f544dccbaa3671bf48fb`** |
| **041 clean-ROM IPS SHA256** | **`2117bc6e165f2c86263e74a637b6961a13f79257fccd9f02152a769fe1deb962`** |
| New fields | 21 Quiz answer rows |
| Existing fields preserved | 38 UI + 33 Fortune = 71 |
| **Current cumulative direct text fields in this experiment** | **92** |
| Original G0/G1 artwork | Preserved; startup title and exact credit **Việt hóa bởi Votri Valley** |
| Changes vs 040 ROM | **132 bytes total**, only approved 21 fields and cartridge checksum |
| Clean-ROM IPS | **22,100 bytes / 756 records** |
| Independent IPS replay | **PASS; full output byte-for-byte equal** |
| New SNES header checksum / complement | `0x327D / 0xCD82` |
| SNES emulator actual gameplay | **NOT TESTED** |
| Complete main Story/Quiz/Fortune language | **NOT YET** |

Local user-facing patch-only package:

`Chibi_041_G0G1_92UIFortuneQuiz_Content_First_UNTESTED.zip`

The ZIP contains only the IPS, Vietnamese instructions and static reports; it **does not contain a commercial ROM or font files**. Patch is for the exact clean original Japanese ROM, NOT for stacking on top of 039/040 IPS or historical direct-text Build035.

## Build command

From a full GitHub checkout:

```bash
cd games/ChibiMarukoChan-Mezase-Minami-no-Island
python tools/build_content_first_041_quiz.py \
  original-japanese.sfc checkpoint040-clean-rom.ips \
  --ips checkpoint041-clean-rom.ips \
  --report checkpoint041.json --allow-untested
```

The exact original and patch SHA256 are enforced. Output ROM is optional and must not be committed.

**QA honesty:** the physical original clean ROM and actual 040/041 ROMs were inspected locally, a separate locally constructed script encoded 21 exact candidates from the GitHub source and produced the reported hashes, and an independently implemented IPS decoder replayed the new 041 IPS exactly. The **newly committed GitHub builder script was not executed in GitHub CI**, and no game runtime has been checked.

## Why Story is still pending

The canonical Story/Quiz content already includes many natural full-length Vietnamese translations, but dialogue boxes include embedded source formatting, delimiters, multi-line segments, and codepoint budgets. Most complete Vietnamese lines exceed a single Japanese field's glyph count; previous compact-runtime 027 direct-text builder was not preserved as a reproducible ROM pipeline in this branch and the direct-text Build035 ROM binary is unavailable.

**Do not replace storylines with unnatural one-word fragments to inflate progress.** Next work must reconstruct the Story 328-field segment-aware wrapping/insertion pipeline from the exact existing runtime CSVs and CP932 original ROM, with independently verified frame limits and original control bytes. Then integrate it into 041 safely, keeping G0/G1, Quiz and Fortune intact. More text content and G3 actual results remain pending. Font remains frozen per the user.

**Status: 21 additional physical Quiz fields patched; 92 current direct-text fields total; static verification PASS; emulator UNTESTED; not full Vietnamese game.**
