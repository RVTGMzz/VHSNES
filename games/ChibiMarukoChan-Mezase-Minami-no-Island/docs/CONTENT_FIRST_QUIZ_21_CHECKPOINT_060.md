# Chibi Maruko-chan SNES — Checkpoint 060: 21 Quiz fields + duplicate audit

Date: 2026-10-11. Branch: `chibi-maruko-bootstrap-01`.

## Critical 059 correction — DO NOT count three earlier answers twice

An all-stage offset audit discovered that three checkpoint059 birthday answers at `0x31F75`, `0x31F84`, and `0x31F95` were **already integrated in checkpoint047**. The old 059 count of 37 and cumulative Quiz count of 244 were overstated. The current 059 manifest excludes those three; **059 now contains 34 unique records, not 37**. The unchanged filename `quiz_content_first_37_059.json` is a historical filename, not the current record count.

We reconstructed the original 059 byte overlay on the user's actual original SNES ROM, reproduced its *old published IPS SHA exactly*, then removed the three duplicate fields and remeasured the precise resulting data:

| Corrected 059 metric | Result |
|---|---:|
| Distinct new Quiz records | **34** |
| Original physical line windows / `816F` controls | **73 / 73** |
| Editable two-byte-glyph source bytes | **1,544** |
| Actually changed source bytes | **1,541** |
| Original-Japanese ROM test IPS | **1,914 B / 73 records** |
| Corrected 059 test IPS SHA256 | `d383a705336236b3ff2c992ab3ce28c4605d1a5afd809bb8f8eb630035802a81` |
| Corrected 059 test image SHA256 | `7a6c5cb411738706b019ea4b320e20d4bb131888ba2acdf3bd3aae3fdd3be0c2` |

Both `translation/runtime/quiz_content_first_37_059.json` and `tools/build_content_first_059_quiz_37.py` were updated, and the latter explicitly fails if any of those three earlier 047 addresses reappear in 059.

## Checkpoint 060 new, clean-ROM-confirmed content

Added **21** genuinely new contextual Quiz source entries across seven canonical Quiz CSV files. These include Hanawa's full given name Kazuhiko in continuous dialogue, Maruo's glasses, Migiwa's crush on Hanawa and Mark, Maruko's farewell to Pusadi, Nagayama as a caring older brother, Hanawa's Rolls-Royce, plus concise but recognizable options **Ono**, **Jump**, **Idol** and **Sáo**.

The original complete Japanese `source_jp_scanner` and full canonical Vietnamese `vi_full` are preserved in the manifest alongside shortened approved display variants. Long character names which do not fit remain deferred, not replaced with inaccurate abbreviations. The new 060 manifest was checked against **all 241 unique earlier staged Quiz offsets** before being committed.

The actual user-provided clean 2,097,152-byte Japanese SNES ROM matched SHA256
`e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`.
We encoded 21 vetted fields using the existing V2 `84xx` Unicode table *without modifying the font*, respected the 43 original text rows and ASCII indentation, preserved the original `81 6F` delimiters, and independently decoded and applied the IPS back to the entire clean original ROM.

| Checkpoint 060 source-only QA | Measured |
|---|---:|
| New distinct Quiz source fields | **21** |
| Original physical text rows | **43** |
| Original `816F` controls unchanged | **43** |
| Writable text bytes | **816** |
| Text bytes actually changed | **815** |
| Clean-ROM test IPS size/records | **1,038 B / 43** |
| Source-only IPS SHA256 | `f03313fd1d822c2b3c49b46c3bec520313f3ae3d5b8c62db6d177206238a5822` |
| Source-only ROM overlay SHA256 | `8eb2b3ea0aedafd744039d4b05f2a647d0c4a239e778ef4c604305c2b033fbe9` |
| Independently replayed IPS against actual clean SFC | **PASS** |
| Full 059+060 combined ROM | **NOT BUILT** |
| Real emulator, visual or gameplay QA | **NOT TESTED** |

**Do not release the isolated text-only source overlay:** The Japanese clean ROM lacks the existing V2 Vietnamese font and graphics/title changes, and it has no regenerated SNES checksum. This overlay merely verifies the original binary source text slots.

## Committed tools and follow-up

- `translation/runtime/quiz_content_first_21_060.json` — 21 new runtime translations, canonical Japanese and full Vietnamese references, exact source slot widths and verified fingerprint.
- `tools/build_content_first_060_quiz_21.py` — source/fingerprint validation, prevention of previously modified source regions, glyph coverage, exact `816F`/padding guard, SNES checksum calculation and final clean-ROM IPS replay.
- `tools/rebuild_content_first_060_full_chain.py` — guarded in-memory rebuild from the exact 043 baseline to 060.
- `tools/audit_quiz_unique_060.py` — automated fail-closed audit of 381 canonical source offsets and the individual staged counts 21+15+54+50+67+34+21. These newly committed 060 Python tools have **not** been run against the unavailable fully integrated 059 ROM; the distinct-offset count was cross-checked through connected source manifests, and source bytes were separately tested locally on the actual ROM.

**Corrected conditional Quiz progress: 262/381 distinct staged source targets, 119 remaining.** This is not the share of strings confirmed in playable Vietnamese; the full composite ROM is not available for testing.

The missing historical `checkpoint043.ips` raw bytes are still the hard dependency to build the composite 060 patch: expected original Japanese clean-source IPS SHA256
`d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50`.
The historical 043 ZIP exists as Library metadata only and could not be materialized. Do not claim it was read. The user-provided clean Japanese SFC **is** available and verified.

After 043 IPS becomes readable, from game project root:

```bash
python tools/audit_quiz_unique_060.py
python tools/rebuild_content_first_060_full_chain.py clean.sfc checkpoint043.ips --ips final060.ips --report final060_qa.json --allow-untested
```

Future content work: **119 remaining Quiz entries**, many of which are full names or answer choices requiring safe text-area expansion rather than mangling; the last four Fortune long fields; G3 result/ending graphics; finally actual SNES emulator screen/gameplay QA and then typography.
