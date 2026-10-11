# Chibi Maruko-chan SNES — Checkpoint 061 and experimental layout probe 062

Date: 2026-10-11. Branch: `chibi-maruko-bootstrap-01`.

## New real original-ROM text QA: 17 Quiz fields

The user's **exact 2,097,152-byte clean Japanese SNES ROM** was read and matched SHA256
`e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`.

Checkpoint 061 initially contained 19 compact answer candidates. Editorial review found two that compromised meaning:

- `0x36579`: `Rolls` omitted the `-Royce` portion of the proper name **Rolls-Royce**.
- `0x32108`: `1tr` for **1,000,000 yen** is ambiguous without a unit and may misleadingly suggest Vietnamese đồng.

Both were **removed** from approved 061 data and must receive a display-expansion strategy instead. The historical filename `quiz_content_first_19_061.json` is retained; **its content now has exactly 17 distinct records**. There is no longer any "19 new" progress claim.

On the exact actual clean-ROM source, regenerated a 17-record Vietnamese source-only overlay with the existing V2 `84xx` codepage, confirmed all bytes outside original text remain untouched, and replayed the IPS. It is **not** a playable localization (no integrated custom font or checksum).

| Verified static-source metric | Corrected 061 |
|---|---:|
| Distinct edited Quiz records | **17** |
| Original `816F` delimiter locations preserved | **17** |
| Original writable text region bytes | **182** |
| Changed source-text bytes | **180** |
| Test-only IPS | **283 bytes / 19 records** |
| Test-only IPS SHA256 | `89ba15c82f8b66b74bd0055ec5255ec3e512bca08d0a842d46ddbe4c63a08de6` |
| Source-only overlay ROM SHA256 | `50181b14eedf96845f9428a2809536e891829a6455e7afe51f2e1ee85d3cfb5f` |
| Full actual 060 -> 061 ROM | **NOT BUILT** |
| SNES gameplay/font acceptance | **NOT TESTED** |

New source-backed integration code:
- `translation/runtime/quiz_content_first_19_061.json`: 17 real candidates, canonical Japanese/full Vietnamese kept per record
- `tools/build_content_first_061_quiz_17.py`: guarded full-060 -> 061, original ROM/hash/layout, live V2 font pointer, output checksum, exact source-overlay signature, no `Rolls`/`1tr` regressions
- `tools/rebuild_content_first_061_full_chain.py`: in-memory clean Japanese + 043 IPS through 061, final IPS and report only
- `tools/audit_quiz_unique_061.py`: stage-specific duplicate detection against 381 original Quiz CSV records; revised counts **21 + 15 + 54 + 50 + 67 + 34 + 21 + 17 = 279 distinct**; **102 remain**. The older 053 15 duplicates and 059 three duplicates are not counted.

**Important:** The new full-integrated-061 builder is committed but **has not been executed on a verified real full-060 ROM** because the historical checkpoint043 clean-ROM IPS raw bytes are still unavailable. The user's clean SFC is available and used for isolated byte QA; do not claim runtime success.

## 062: a six-answer padding-expansion experiment, NOT counted as integrated

Analyzed native single-byte `0x20` padding **between original Japanese text and immutable `0x816F` text terminators**. Six Quiz answer alternatives have physically reusable padding, allowing a source-only byte experiment without moving any later script bytes.

| Clean ROM offset | Proposed label | Original glyphs | Native trailing ASCII bytes | Bytes reassigned |
|---|---|---:|---:|---:|
| `0x338D8` | Tokuda Ryoji | 4 | 16 | 16 |
| `0x338F7` | Tokugawa | 4 | 8 | 8 |
| `0x33AC5` | Shimizu | 5 | 6 | 4 |
| `0x33C27` | Tomiko | 5 | 6 | 2 |
| `0x33C3E` | Hanako | 4 | 8 | 4 |
| `0x33C55` | Toshie | 5 | 6 | 2 |

The complete canonical originals are unchanged: **Tokugawa Ieyasu**, **Shimizu Elementary School**, **Tomita Tomiko**, **Buu Hanako**, **Yoshiyama Toshie**, etc. The above are **short on-screen candidates only**, not a claim of full name fidelity or display acceptance.

Real-Japanese-ROM source-byte checks succeeded for these six experiment windows:

| Unapproved 062 static probe | Result |
|---|---:|
| Original candidate sources | **6** |
| Original text-plus-padding writable bytes | **104** |
| Actually changed source bytes | **90** |
| Original `816F` controls preserved | **6** |
| Test-only IPS bytes/records | **128 / 6** |
| Test-only IPS SHA256 | `74cc6dd983753e9370228092b404549891ca6e273e32dbd9e59887c284aed5cd` |
| Text-only source overlay SHA256 | `2d0df00692276b4256c888aa71aaf4290a7f449c5bb57a41b90d382271487d96` |
| In-emulator text width, menu selection, rendering, wrapping | **NOT TESTED** |

The native scanner offset `0x33B8D` **failed control-boundary parsing** (it points into an intermediate script fragment), so it was rejected, not written. The six valid records remain **explicitly unapproved**, because consuming original ASCII layout spaces changes the number of displayed glyphs. The source-only IPS passes byte fidelity but says nothing about whether rendered text runs outside its selection highlight.

Repo source:
- `translation/runtime/quiz_padding_expansion_PROBE_062.json`: six exact byte scopes, original glyph capacities, consumed and retained padding, immutable delimiters, explicit `approved_for_integration:false`
- `tools/probe_quiz_padding_062.py`: safely reproduces six source-only experiments on an exact clean Japanese SFC and emits a QA report **without outputting a ROM or IPS file**

**062 contributes zero additional completed Quiz records.** These are renderer-research candidates, pending actual combined ROM and emulator screenshot/interaction QA.

## Blockers and next work

The earlier exact checkpoint043 clean Japanese IPS expected SHA256
`d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50`
is present only as old Library ZIP metadata and cannot currently be read into the runtime. Thus **no full 061/062 playable game** has been rebuilt. The source-only physical overlays must never be distributed as a complete game patch.

On availability of exact 043 IPS, from the game project directory:

```bash
python tools/audit_quiz_unique_061.py
python tools/rebuild_content_first_061_full_chain.py clean.sfc checkpoint043.ips --ips combined061.ips --report qa061.json --allow-untested
python tools/probe_quiz_padding_062.py clean.sfc
```

Next: inspect and safely translate the remaining **102** originally inventoried Quiz source offsets. Many are full names and answer choices that exceed original display width. Resolve them by proven safe relocation or emulator-verified layout, not artificial nonsense abbreviations. Four original Fortune display cases remain, as well as G3 results and a complete emulator/visual QA pass. User requested content first, font last, no unsolicited micro-patch downloads.
