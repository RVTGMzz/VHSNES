# Chibi Maruko-chan — Checkpoint 048: 103 more Fortune records (content-first, safe merge pending)

Date: 2026-10-11. Repo `RVTGMzz/VHSNES`, branch `chibi-maruko-bootstrap-01`.

## Why this round matters

The user expressly wants **substantial game-content localization** rather than SNES font experiments, repeated tiny checkpoints or unsolicited IPS download links. The most significant remaining text corpus is Quiz and Fortune. This round reviewed **103 additional canonical Fortune source entries** and verified the resulting **actual SNES ROM glyph replacement bytes** against the original Japanese cartridge and an existing verified checkpoint043 base. These are NOT merely new translations on paper.

Fortune subtopics covered: wished-for outcomes, money and thrift, romance, school subjects, luck in games/contests, self-care, cardinal directions, lucky items, and colors. Each original `vi_full` meaning was retained exactly in its canonical CSV. The editable in-game compact variants in `translation/runtime/fortune_content_first_103_048.json` are separate reviewed display strings, authored within the original physical two-byte glyph capacity; they were not produced by blindly truncating the Vietnamese source string. A few compact variants necessarily simplify details (e.g. subject references or shades), **so actual emulator/editorial acceptance remains pending**.

Examples: `Đừng tham`, `Có duyên!`, `Tỏ tình đi`, `Khăn tay may`, `Rút quẻ nữa`, `Dần thành`, `Thi cử hên!`. Some extra-long or awkwardly-sized original labels are intentionally NOT compressed into misleading gibberish.

## Real exact-ROM test that completed

The current container includes:

- **Exact clean original 2MiB Japanese ROM** SHA256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`.
- Verified old complete 043 IPS inside the archived checkpoint043 ZIP. Independently applying it reconstructs exact 043 ROM SHA256 `45ffca7db5db83bc2734e885ee90c77f33746e2c4a54d1c99f1502f3e992a6ae`.
- Original existing V2 `0x84xx` codepage; actual source data length and glyph table pointer `0x9A74` were checked.

A local builder iterated the **103 exact original Fortune physical fields**, decoded raw Japanese CP932, calculated physical **byte width** rather than naively counting Japanese characters (some original lines use *two single-byte ASCII spaces*), required the unchanged original `81 6F` line terminator, checked all translated Unicode characters map to a **nonzero existing V2 glyph ID**, filled only each approved physical source span, and prohibited any edits outside those spans.

| Static byte-level result | Actual measured result |
|---|---|
| Additional Fortune fields | **103** |
| Original editable two-byte glyph source bytes | **2,002** |
| Actual byte positions changed relative to exact 043 | **1,997** |
| Previously localized Fortune entries (040+047) | **48**, no offset overlap with any of 103 |
| Text-only IPS delta (NO checksum writes) | **2,545 bytes / 108 IPS records** |
| Text-only source-overlay IPS SHA256 | `3eb7dcc55d0c0b585beb4b27d6d2ca08c5facd39196042756eae0cf0dc68379c` |
| Exact 043 + 103 overlay **preview ROM** SHA256 | `4f461333d171fc21c3541ae29393056f0c9234ea0f5c4de46f97589afd20378b` |
| Check that no original Japanese `816F` marker was moved | **PASS** |
| IPS decoded and reapplied independently to the actual 043 ROM | **PASS, exact preview SHA256** |
| Existing ROM title/graphics and font data overwritten | **NO** |
| 047 + 103 **full integrated merged ROM** | **NOT YET BUILT** |
| Actual SNES emulator/gameplay | **NOT TESTED** |

**Critical honesty:** The existing source tree documents an exact 047 full combined ROM SHA256 `1f6430064b70671a4f3ba94f0fd256764db54690950519c22d9e03ec74230dd9`, but that exact **binary is absent from this session's mounted files**. Rather than pretend a full 048 integrated ROM exists, this round built and verified the **103 text edits over actual physical 043** and committed the source data and a **fail-closed merge script**. Text-only preview ROM uses the old checksum deliberately and IS NOT A PLAYABLE RELEASE OR VALID 048 CHECKSUM. It is only a byte/overlay QA specimen. Do not send it to the user.

## Reproducible source now on GitHub

- `translation/runtime/fortune_content_first_103_048.json`: all 103 verified Japanese file offsets and Japanese source, entire canonical Vietnamese meaning reference, compact runtime Vietnamese, physical two-byte unit capacity, original source CSV identity and review state. All 103 were compared against the live canonical Fortune CSV rows, and offset intersections with the prior 040 and 047 Fortune runtime lists were zero.
- `tools/build_content_first_048_fortune_103.py`: exact SHA-pinned clean original + exact **047 full ROM** merge tool. Reads canonical Fortune sources, verifies all original source bytes/816F controls, Unicode/codepage, 103 immutable capacity contracts and no existing 047 edits at those offsets. Creates a text-only overlay first and SHA-matches the actual 043-based preview proof. For a true 047 ROM input, additionally recomputes SNES checksum, creates a **single clean-ROM IPS** and independently replays it. It refuses mismatched/unknown 047 inputs instead of silently flattening previous translations. `--static-check-043` can recreate the already-proven 043+103 overlay but must never be mistaken for 047+048 release.
- `docs/CONTENT_FIRST_FORTUNE_103_CHECKPOINT_048.md`: this checkpoint.

Example **local technical use only after the exact 047 ROM is recreated**:

```bash
python tools/build_content_first_048_fortune_103.py clean-japanese.sfc exact-047-integrated.sfc \
  --ips merged-048-clean.ips --report merged-048-static.json --allow-untested
```

No commercial ROM/font uploaded or released. The new script has been committed but **not exercised in GitHub CI**, while the independent local 043+103 byte layer was executed against actual 2MiB ROM contents. Do not report GitHub CI or SNES emulator PASS.

## Exact remaining Fortune work

Verified against all **157 canonical Fortune source CSV rows**:

- 48 previously patched 040/047.
- **103 additional exact-source display candidates now verified and stored**, with text-only experimental ROM bytes.
- **6 original rows remain not covered** after a successful future merge: `0x2BD5E` 天の声 (“Lời trời mách”), `0x2C413` 体育が開運のカギ (Thể dục and good luck), `0x2C601` プリンを食べてみよう (pudding), `0x2C86B` また来週 (“Hẹn tuần sau”), `0x2CA7D` きいろ (yellow), `0x2CADD` しろいろ (white). These should get proper, readable display treatment rather than breaking names or using misleading abbreviations.

**Potential post-merge Fortune coverage: 151/157 (96%)**, but **physical full 047+048 integration is still blocked by the missing exact 047 binary**; it is dishonest to count the 103 as already safely committed into a fully integrated 048 ROM.

## Next real work

1. Recover/rebuild the precise 047 combined ROM from project source **without relying on missing interim binary files**, then execute this fail-closed 048 merger to produce one genuine integrated ROM and clean-ROM IPS. Verify exact checksum and ensure no Story/Quiz/visual regression.
2. Restore as much remaining **Quiz** and the six Fortune rows as safely possible, including long Japanese questions/choices via proven field relocation rather than clipped nonsense.
3. Follow up G2 actual rules and G3 results; after content is substantial, run one meaningful actual SNES emulator QA, including earlier user-reported font ugliness **after content**.

**Do not send an intermediate IPS/ZIP link or ask the user to test before a comprehensive, actual playable release candidate.**
