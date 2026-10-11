# Chibi Maruko-chan SNES — Checkpoint 059: 37 more Quiz records

Date: 2026-10-11. Branch: `chibi-maruko-bootstrap-01`.

## What actually changed

Translated another **37 distinct Quiz answer, question and narrator source fields** in `translation/source/quiz_batch03_part1_vi.csv`, concerning Momoe-chan, Maruko's birthday and pocket money, Grandpa Tomozou, food and grandmother's bicycle, father Hiroshi and Sumire's lost ring. All **canonical full Vietnamese** and original scanner Japanese remain untouched. New short text shown by the current fixed-width engine is recorded independently in `translation/runtime/quiz_content_first_37_059.json`.

Examples:
- `Cung Kim Ngưu / Sinh hôm nào?`; answers `8/5`, `23/4`, `1/10`
- `Maruko ghét / natto,cà chua / hành lá!` (keeps the correct foods rather than omitting "chua")
- `Ông hiểu Maru / nhất nhà / thơ haiku`
- `Bà âm thầm / mà biết đạp xe / Maru đã hay`
- `Maruko làm mất / nhẫn của mẹ`; answer `Opal`

Some standalone answer choices are **intentionally deferred** because existing source slots cannot represent the exact full Vietnamese meaning, including `Xe đạp` (6 glyphs / 5-cell slot), `Hành lá` (7 / 2), `Nepal` (5 / 4), and one million yen. Merging scanner fragments that overlap already selected text (`0x31E50` vs `0x31E04`, `0x31F33` vs `0x31F23`, `0x3275E` vs `0x3271E`) was prohibited, and the source entry at `0x32874` was excluded because its underlying text extends into previously selected 058 region `0x3288E`. Those source records are not falsely counted as newly patched.

## Actual clean-ROM physical source QA (NOT a playable build)

Ran the in-memory overlay and standalone IPS replay on the user's **exact, 2,097,152-byte Japanese retail SNES ROM**, SHA256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`. Physical scans decoded original CP932 two-byte characters and spaces, located original text break `81 6F`, kept all script-stop bytes and indentation untouched, and replaced approved text bytes only with existing V2 `0x84xx` Unicode mappings.

| QA evidence | Verified |
|---|---:|
| Newly selected logical Quiz fields | **37** |
| Original line windows / native `816F` markers | **76 / 76** |
| Approved two-byte text area | **1,572 B** |
| Actually modified text bytes | **1,568 B** |
| Text-only experimental IPS | **1,961 B / 77 records** |
| Text-only IPS SHA256 | `15e12c50f501f6455c4b31dc837231ca23dbccdfe94bd07ef5a4d4384f844856` |
| Experimental clean-source image SHA256 | `3dcdaca24ed47d92c7f11d8851fcf1c3516a41412f224a123fb3fe4234e51aaf` |
| Independently decode/reapply IPS to full clean ROM | **PASS: exact 2 MiB match** |
| Combined verified 058 -> 059 ROM | **NOT BUILT** |
| Actual emulator / visual QA | **NOT TESTED** |

**The source-only IPS is not distributed and is NOT a playable localization.** The clean ROM does not contain the existing Vietnamese font, G0/G1 pictures or integrated checksum; the proof is solely of exact, approved source text replacement. The user's preference is to finish all text before font tuning and avoid endless minor patch downloads.

## Implementation

- `translation/runtime/quiz_content_first_37_059.json` — 37 individually approved offsets with original scanner Japanese, unchanged full Vietnamese reference, compact runtime wording and verified per-row glyph capacity
- `tools/build_content_first_059_quiz_37.py` — guarded 058 -> 059 binary text merge, exact clean-ROM 059 overlay hashes, pointer V2, native segmentation and source width, source CSV match, output checksum and IPS replay
- `tools/rebuild_content_first_059_full_chain.py` — exact clean Japanese + trusted checkpoint 043 IPS -> 044..048 -> 054..059, keeping intermediary ROMs in memory

Combined output still depends on historical clean-ROM **043 IPS** expected SHA256 `d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50`. That file exists only as archived ZIP **metadata** in the Library; earlier raw-byte extraction requests were denied, and neither a 043 IPS nor original graphical/font layer is available to this build session. Do **not** claim a full integrated ROM/gameplay pass.

When the exact 043 IPS is provided as a readable conversation attachment:
```bash
python tools/rebuild_content_first_059_full_chain.py clean.sfc exact_043.ips --ips full059.ips --report full059_qa.json --allow-untested
```

## Accurate cumulative figures

**Conditional Quiz source coverage**: 041 21 + 047 15 + 054 54 + 057 50 + 058 67 + 059 37 = **244 distinct physical-source targets from 381 canonical entries**. **137 are not yet selected** for safe integrated text replacement. This is preparation/source-byte verification, *not* evidence that 244 strings are playable in a combined Vietnamese ROM. Obsolete 053's 15 duplicated rows have been excluded from the total.

Other remaining work: four physically too-small Fortune source fields, other Quiz long names and questions, G3 results and eventual one comprehensive real SNES emulator test and font/layout review.
