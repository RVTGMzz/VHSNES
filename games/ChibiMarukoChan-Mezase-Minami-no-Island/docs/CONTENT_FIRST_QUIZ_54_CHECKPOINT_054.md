# Chibi Maruko-chan SNES — Checkpoint 054: 54 nonduplicate Quiz text records

Date: 2026-10-11. Branch: `chibi-maruko-bootstrap-01`.

## Concrete work performed

The user-supplied original 2,097,152-byte Japanese SNES ROM matched SHA256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`. We physically encoded a newly edited Vietnamese Quiz overlay into 54 original Quiz records (123 native physical line regions), keeping existing leading/trailing ASCII layout spaces and every original `81 6F` text separator untouched. A separate IPS reader applied the resulting text-only IPS to the exact clean source and reproduced the entire output ROM byte-for-byte.

This text-only experiment has no Vietnamese font or rewritten SNES checksum. It is **NOT PLAYABLE** and was not sent to the user. It proves location/layout correctness of the 54 source fields; a real integrated release must be built on a verified full 048 baseline.

| Check | Verified result |
|---|---:|
| Reviewed distinct new Quiz logical fields | **54** |
| Original physical glyph-bearing and blank segments | **123** |
| Preserved native `816F` separators | **123** |
| Approved editable text byte positions | **2,642** |
| Actual changed byte positions on original | **2,636** |
| Text-only IPS size / records | **3,279 bytes / 127** |
| Text-only IPS SHA256 | `9f5069f7a105e371a71f9cf8bf5fdd38bae099d774c184a272f9abec9c8908ad` |
| Text-only experiment output ROM SHA256 | `1eea9a31907384b42f1646d84a1c252a64c85b7adeba333c4e6b663a695008ef` |
| Actual 048 + 054 merged ROM | **NOT YET BUILT** |
| SNES emulator/gameplay test | **NOT TESTED** |

These 54 are **source-to-ROM edited caption candidates**, separate from full `vi_full` translations in canonical Quiz CSV. The captions are deliberately constrained by original SNES display cells and still require user-visible gameplay editorial review. The original Japanese layout is preserved rather than overwriting line breaks, pointer data, or names in adjacent slots.

## Major correction to earlier count

Old 053 claimed 16 additional Quiz records; cross-comparison against `translation/runtime/quiz_answers_exact_fit_041.csv` proved **15 of those 16 had already been inserted in 041**. Only Quiz `0x340C0` is genuinely new. This specific record contains 6 original ASCII indentation bytes, the actual Japanese question starting at `0x340C6`, 8 trailing native spaces, then the original `816F`. It is safely included once in this 054 manifest.

The old `tools/build_content_first_053_quiz_16.py` now refuses to execute and directs the operator to the 054 chain, avoiding double-counting and baseline collisions. Old 053 JSON is marked superseded.

Cross-check of the 54 new file offsets against published 039 menu/UI, 041 Quiz and 047 Quiz/Fortune source manifest offsets found **zero exact address collisions**. The legacy 053 manifest intersects only at the intentionally rescued `0x340C0` row.

## GitHub source and how to build later

- `translation/runtime/quiz_content_first_54_054.json`: 54 edited display candidates, original offsets and proven native glyph capacities. The full canonical Vietnamese sources remain unchanged.
- `tools/build_content_first_054_quiz_54.py`: strict clean-ROM SHA, existing V2 glyph table, original layout/frame width, saved native breaks, baseline byte guards, Unicode glyph coverage, allowed diff and clean-ROM IPS replay.
- `tools/rebuild_content_first_054_full_chain.py`: combines exact clean + exact 043 IPS through 044/045/046/047/048 and then adds the new 054 source, **without writing intermediate ROMs or requiring an archived 047 binary**.

Technical invocation, once the user-owned checkpoint043 IPS is available:

```bash
python tools/rebuild_content_first_054_full_chain.py clean-japanese.sfc exact-043-clean.ips --ips merged-054.ips --report merged-054-qa.json --allow-untested
```

The archived `Chibi_043_G0G1_176Fields_Story58_Content_First_UNTESTED.zip` is visible in Library metadata but its raw contents could not be authorized for materialization in the active runtime. The exact 043 IPS is still absent. Therefore **NO 054 integrated ROM has been constructed, checksum-verified, or run in an emulator**. Never publish the clean-ROM text-only overlay or claim the full game is finished.

Next priorities: get the exact 043 patch bytes, run guarded 054 full rebuild, follow with remaining long Quiz/character full-name layout expansion, G2 rules, G3 outcome artwork and finally one comprehensive real emulator + font QA.
