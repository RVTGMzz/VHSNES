# Chibi Maruko-chan SNES — Checkpoint 057: +50 Quiz physical text records

Date: 2026-10-11. Branch: `chibi-maruko-bootstrap-01`.

## Substantive content change (not another font experiment)

Edited four additional lines for natural context (Maruko/Midori relation, Yoshikawa's impact, sister's calm demeanor and Mitsuya's role); re-checked all original fields, the 105 line markers and byte-exact IPS replay. The final verified IPS/ROM source fingerprints are listed below.

Added **50 new, nonduplicated Quiz narrative/question/answer fields** from
`translation/source/quiz_batch02_part2_vi.csv` and
`translation/source/quiz_batch02_part3_vi.csv`. These are the Yoshikawa Midori,
Yamada/April Fool, Yamane/Michiru, Yoshiko, Nagayama/Koharu, Ono/Sugiyama,
Fujiki/skating, Maruko's family/house, Hanawa's chauffeur and Maruko's sister/
favorite candy store vignettes. The original complete source `vi_full` remains
untouched. The new fixed-size `vi_runtime_lines` are edited display variants
(not a claim that all full narrative fits in the original cells).

Selections deliberately **exclude full character-name answer choices** that
cannot remain recognizable in the original 2–5-cell SNES text slots.
Avoid meaningless abbreviations: do not shorten `Hanawa Kazuhiko`,
`Fujiki Minoru`, `Rolls-Royce`, `Ribon`, etc. into unrecognizable names to
artificially raise a percentage. Those require future safe dialog relocation
or glyph/layout expansion. The untouched four Fortune exceptions likewise
stay deferred, rather than changing colors `Vàng` and `Trắng` into the
wrong meanings.

## Exact physical QA with user-supplied clean SNES ROM

The actual user-provided `Chibi Maruko-chan - Mezase! Minami no Island!!
(Japan)(1).sfc` was used; original file size 2,097,152 B and SHA256
`e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`.

Parsed original CP932 two-byte characters, native single-byte ASCII padding,
`81 6F` row/page delimiters and raw script stop opcodes. Encoded each
approved Vietnamese source character through the **existing V2 `84xx` map**.
No Japanese source font assets were modified; full source `vi_full` remains in
the canonical CSVs.

| Independent physical source check | Measured result |
|---|---:|
| New logical Quiz records | **50** |
| Distinct original physical text frames | **105** |
| Original `816F` line controls preserved | **105** |
| Writable source text byte positions | **2,106** |
| Physically changed source text bytes | **2,106** |
| Text-only QA IPS size / records | **2,614 B / 100** |
| QA-only IPS SHA256 | `73829cb20f1b182142e428ba55366227417258d8e87f9e7da6de4fa1d093b749` |
| Original-ROM QA text overlay SHA256 | `525575f7d178d3a2df4d616934484b8e5ae4a15db60c264c607db5fd3f1c4b98` |
| Apply IPS to original, compare every byte | **PASS** |
| Original Japanese source ROM SHA pinned | **PASS** |
| SNES emulator screenshot or gameplay QA | **NOT TESTED** |
| Full 056 + 057 combined ROM actually built | **NO** |

This **clean-ROM source-only overlay is NOT PLAYABLE**: the original ROM does not
have the existing Vietnamese V2 font, graphics/title alterations or SNES
checksum regeneration. Don't distribute a text-only partial IPS to the user.

## Build implementation tested

`tools/build_content_first_057_quiz_50.py` checks exact Japanese source SHA,
existing V2 codepage pointer/table, capacity/Unicode NFC, immutable original
padding, 105 exact original delimiters, all approved physical byte addresses,
non-overlap with the 056 baseline, regenerated checksum and
independent final clean-ROM IPS replay. Every record offset is anchored in a
canonical `quiz_batch02_part2_vi.csv` or `quiz_batch02_part3_vi.csv` source row
containing Japanese scanner source and full Vietnamese text.

Besides byte-level QA on the actual original ROM, **the 057 merge builder's
algorithm was run successfully with a SYNTHETIC font-enabled baseline**:
an in-memory copy of the clean original was modified solely for test-fixture
V2 pointer/glyph table entries. Its 50 records/105 controls, IPS replay and
checksum generation passed. This synthetic result **does not** establish
compatibility with the missing original integrated 056 binary, does not
verify the original Vietnamese font's appearance and must not be presented as
a playable game.

Repo files:
- `translation/runtime/quiz_content_first_50_057.json` — 50 edited displays
- `tools/build_content_first_057_quiz_50.py` — byte-guarded 056 -> 057
- `tools/rebuild_content_first_057_full_chain.py` — in-memory rebuild chain
- `docs/CONTENT_FIRST_QUIZ_50_CHECKPOINT_057.md` — this report

After access to the old **043 clean-ROM IPS** (SHA256
`d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50`),
an exact 057 patch could be rebuilt from the user's actual clean ROM:

```bash
python tools/rebuild_content_first_057_full_chain.py clean.sfc checkpoint043.ips --ips combined057.ips --report qa057.json --allow-untested
```

**Known blocker:** The historical 043 ZIP appears in Library metadata, but
the active runtime has no authorized raw-byte materialization path for it.
Do not claim the combined ROM or gameplay exists. Do not store copyrighted
SNES game ROM or font files on GitHub.

After this patch is actually integrated and reviewed, inspect the remaining
Quiz narrative and the larger-name/layout cases, the 4 Fortune cases, G3
end/result graphics and then font/emulator screenshots.
