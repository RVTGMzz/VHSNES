# Chibi Maruko-chan SNES — Checkpoint 072: a minimal, playable-engine hypothesis test without checkpoint043

**SUPERSEDED BY CHECKPOINT 073.** Actual 65c816 Quiz routine copies 66 bytes from each answer source; old two new addresses are 64 bytes apart and their copy windows overlap by 2 bytes. Do not use prior 072 ZIP as the preferred test; use the corrected 073 ZIP and see `docs/CHECKPOINT_073_QUIZ_ENGINE_66_BYTE_COPY.md`.

Date: 2026-10-12. Branch: `chibi-maruko-bootstrap-01`.

## Why the experiment matters

Checkpoint 069 demonstrated that the complete Vietnamese text of **81 long Quiz answer choices** could be *stored* in bank06 and its 16-bit source pointers could be rewritten, without overwriting Japanese source records. That does **not** demonstrate that the actual SNES Quiz engine follows the moved pointers correctly, fits the extra glyphs into its choice area, or grades answers properly. The historical integrated V2/G0/G1 patch 039–043 is currently unavailable as bytes. Although checkpoint 071 can rebuild from any *user-supplied* old ZIP/IPS 039–043, no such raw artifact can currently be read by the tool.

This checkpoint supplies an independent acceptance fixture **using only the original, unmodified Japanese retail ROM**. It does not require a historical 039–043 IPS, the Vietnamese font, or a reconstructed game. It is **not a Vietnamese translation release** and does not increase the staged translation count.

## Two test relocations in the original ROM

Use the original Japanese 2,097,152-byte headerless SFC:

`e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956` (SHA256).

The existing 50×3 address atlas proves that the **first two entry slots in the Quiz answer-1 pointer table** are:

| Original answer-1 pointer table slot | Pointer 16-bit word at ROM | Original Japanese text start | Original displayed choice | Experimental longer Japanese choice | New record start |
|---|---|---|---|---|---|
| 0 | `0x31217` | `0x320FB` | `３０円` | `３０円です` | `0x37000` |
| 1 | `0x31219` | `0x32273` | `７６才` | `７６才です` | `0x37040` |

**Caution:** These are first two *pointer-table* slots. The game's actual question presentation order may be shuffled or controlled by some other state. Do **not** call them the first two questions necessarily encountered in gameplay.

Both replacement choices append native Japanese `です`, two additional glyphs, without changing the identity of their multiple-choice answer. Each new complete record is `0E 06 0F 12` + 10 bytes of Japanese CP932 text + `81 6F 00` (17 bytes). The original Japanese texts at `0x320FB` and `0x32273` are preserved byte-for-byte. Both new records reside inside original all-`FF` bank06 padding. Exactly two 16-bit LoROM pointers now refer to their new native-text records. Standard SNES header checksum/complement are updated.

**There is still a genuine risk** that the Quiz interpreter does not follow this data, has limitations on pointer targets or glyph width, or uses different values for navigation/grading. This is why an actual emulator run is required before approving any Vietnamese relocation.

## Independent actual-ROM byte and IPS replay results

A standalone local Python implementation was executed against the user's exact original retail SFC, with the following measured outputs. It verified original pointer words and source CP932 glyphs before building, checked new areas are all original `FF`, allowed changes to only the two original 16-bit pointers, two new records, and four SNES checksum bytes, then decoded/applied the resulting IPS independently to confirm the entire 2MiB target image byte-for-byte.

| Actual static QA | Result |
|---|---|
| User original SFC SHA256 | `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956` |
| Original Japanese source records preserved | **PASS, both** |
| New native-Japanese answer bytes | **2 × 17 bytes** |
| Original 16-bit answer-1 pointers changed | **2** |
| All changed ROM bytes in whitelisted positions | **42 bytes** |
| IPS total size and record count | **70 bytes / 4 records** |
| Test-only IPS SHA256 | `3d29135ff3712b4d8ee74b0afb690ec852a1537b3a713ac22866a734f8cc44ea` |
| SNES checksum after patch | `0xFBAC` |
| Expected complete ROM SHA256 if exact IPS applied | `fae23a8f7744313e5977b44eaeaeaf6177bdcd7312c78b671a30851b6599e2ee` |
| Independent clean-ROM IPS replay | **PASS** |
| SNES emulator visual/interaction test | **NOT DONE** |
| Vietnamese V2 font included | **NO** |
| Full Vietnamese game patch created | **NO** |

The isolated test IPS is a genuine minimal **engine-validation artifact**, not another bulk content patch. For user convenience, the current conversation generated a single ZIP **`Chibi-Quiz-Engine-Relocation-PROBE072.zip`** with this 70-byte IPS, byte-QA JSON and a Vietnamese README. Do not commit the binary IPS or commercial ROM into the public source repository. Do not ask the user to download multiple intermediary localization patches.

The committed `tools/build_native_quiz_relocation_probe_072.py` reproduces the experiment from their exact original Japanese ROM. It outputs IPS + JSON only when explicitly passed `--allow-untested`; it refuses wrong ROM identity, changed native text, occupied FF storage, out-of-bank pointers, unexpected changed bytes, IPS replay mismatch or checksum/SHA drift.

To independently reproduce from the cloned game project root:

```bash
python tools/build_native_quiz_relocation_probe_072.py clean.sfc --ips native-quiz072-test.ips --report native-quiz072-qa.json --allow-untested
```

## One useful SNES emulator acceptance checklist

If the user is willing to test this **one** diagnostic, apply its IPS to a **copy of the original Japanese SFC** using Floating IPS/FLIPS, then open that copy in an SNES emulator and enter `まるこＱ`. Wait until either the `３０円` or `７６才` multiple-choice option appears; with the patch, it should read `３０円です` or `７６才です`. Try highlighting/selecting it, progressing the question, and check whether text runs out of its box or gameplay freezes. Since the table order might not equal gameplay order, **not encountering the affected question is inconclusive**, not a failure.

For an affirmative emulator PASS, capture the altered option visible, stable menu highlight and correct answer handling. At that point investigate whether the same address redirection works with the real V2 integrated font, and only afterwards attempt to integrate the pending 81 full Vietnamese alternatives. A clean Japanese original **does not render Vietnamese V2 glyph codes**, so this test says nothing about Vietnamese font appearance.

**Current official Quiz source progress unchanged: 279/381 nonduplicated staged source fields; 81 long answer candidates are not emulator-approved.** Four longer Fortune items and G3 game result/ending assets also remain, and the integrated G0/G1/V2 checkpoint039–043 raw binary is still unavailable in the session.