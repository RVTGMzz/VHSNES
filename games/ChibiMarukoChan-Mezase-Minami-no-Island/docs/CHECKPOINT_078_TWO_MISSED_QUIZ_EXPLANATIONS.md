# Chibi SNES — Checkpoint 078: Two REAL Quiz explanation fields recovered from unsafe scanner aliases

Date: 2026-10-13 · Branch `chibi-maruko-bootstrap-01`.

## Concrete localization progress and correction to checkpoint 077

Checkpoint077 said the 21 remaining canonical non-answer Quiz scanner offsets were 10 nested, 10 unsafe and **one independently pointer-addressable native field**. That *physical-field inference was incomplete*. Directly inspecting all nine original **50 × 16-bit LoROM Quiz pointer tables** on the user's exact original unheadered Japanese retail ROM (2MiB, SHA256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`) revealed **two more independent script records within the ten unsafe scanner aliases**.

These canonical offsets are *invalid as standalone entrypoints* but their containing native physical records are accessible by real pointers, and were NOT included in any earlier staged source-glyph overlay:

| Canonical source scanner alias (not a real field boundary) | Actual original native record | Genuine original pointer-table word | Role |
|---|---|---|---|
| `0x35A69` | `0x35A58` | `0x3136B: 58 DA` → bank06 `$DA58` | Question-explanation part 1 |
| `0x33B8D` | `0x33B8A` | `0x31453: 8A BB` → bank06 `$BB8A` | Question-explanation part 3 |

As of 078, the more accurate classification of the **21 original non-answer source identifiers** is: **10 aliases nested in previous translations + eight unsafe scanner aliases requiring parent QA + three genuine independent physical text fields**. One was identified in checkpoint077 (`0x320E8`, rebuilt as the `0x320DC` continuation); the two above are newly rescued in 078.

This does NOT mean that 18 nested/unsafe offsets are translation-complete: source IDs and independent native fields are different units. Do not add 20 bogus translation records or mark all 381 done.

## Two source-content fixes using the original glyph slots (NO ROM relocation)

### 1. April Fool's Day explanation, missing at `0x35A58`

Original three explanation lines (with exact ROM source-glyph capacity):

| Original text glyph start | Japanese | Max glyphs | Vietnamese candidate | Used |
|---|---|---:|---|---:|
| `0x35A64` | `４月１日エイプリルフールに` | 13 | **Cá tháng Tư** | 11 |
| `0x35A86` | `まる子とおじいちゃんは、山田` | 14 | **Maru và ông** | 11 |
| `0x35AAA` | `くんをだまそうとす` | 9 | **lừa cậu.** | 8 |

This is the narrator explanation for a question already staged in 057 as **“Yamada sắp bị lừa!”**. The second-half explanation (already staged at `0x35AC3`) comes next. In this context, *cậu* refers to Yamada, while the newly translated first-half explanation restores the missing April Fool's timing and Maruko's grandfather. The line breaks are dictated by the original three glyph slots; do not invent or overwrite control bytes, marker `81 6F`, or neighboring scripts.

### 2. The Japanese grade-3 suffix lingering at `0x33B8A`

The original last part of a student explanation is `年生。` (three glyphs at `0x33B94`) and was never itself localized. The immediately prior explanation part (stage058 source `0x33B3B`) already contains a complete Vietnamese line **“lớp 3”**. The extra segment is therefore translated as a brief, nonrepeating narrator ending **“đó.”** (three V2 glyphs), producing a natural continuation **“…lớp 3 đó.”**, and removing the leftover Japanese from the visible path.

These are editorial candidates, so gameplay/screen review remains required.

## Actual original-ROM static byte proof

The original SFC was read locally and a fresh, independent one-off Python implementation applied **only four fixed existing glyph spans**, with unused original glyph cells filled by existing V2 space glyph code `8440`. Unmodified: both pointer-table 16-bit words, native record headers, `81 6F` line separators and terminators, initial single-byte indentation, neighboring staged scripts, all ROM executable bytes and all game data outside these glyph slots plus header checksum.

| Original Japanese SFC source-only experiment | Result |
|---|---|
| Changed original ROM bytes, incl. checksum | **82** |
| Clean-retail-source IPS size / records | **115 bytes / 5 records** |
| Original-ROM-relative IPS SHA256 | `f560fb8b326b2f4185f7c0b4da149ebe0dee576a40b4ec28d32f375de1241e97` |
| Complete candidate 2MiB original-ROM image SHA256 | `b1ae53c74a04bf69cde9c4aaa708cc6b53d20eea7a3f80c25a81a97a24daf421` |
| Recomputed native LoROM checksum | `0x0A44` |
| Every replacement fits its native physical glyph capacity | **PASS** |
| Original ROM header/true pointer-table destinations read/verified | **PASS** |
| Real V2 Vietnamese glyph font in untouched Japanese ROM | **NO** |
| Actual emulator display / semantic acceptance | **NOT DONE** |

These hashes were computed by a separate Python script on the exact user-supplied original ROM. They are **original-ROM source-only byte proofs**, NOT a playable Vietnamese font release or an in-game test. No copyrighted ROM/IPS file is committed or released.

## Code, source manifests and automated safety

- `translation/runtime/quiz_nonanswer_reanchored_078.json`: original pointers, scanner/source correction, native original lines and exact capacities, Vietnamese edited lines, stage057/058 context and untested flags.
- `tools/build_quiz_native_explanations_078.py`: strict original retail ROM SHA validation, exact header/native pointer-original bytes, staged058 context preservation, four NFC Vietnamese V2 replacement glyph strings, available original capacities with V2 space padding, changed-byte whitelist, SNES checksum and source-based IPS replay. Source-only SHA fingerprints are hard-guarded, outputs only IPS+JSON on explicitly requested `--allow-untested`.
- `tools/audit_quiz_native_fields_078.py`: verifies corrected 077 21-row classification, two 078 pointer field anchors, total 39 original glyph capacities, 33 V2 glyphs used, and optionally source-ROM binary pointer/CP932/terminator bytes via `--original-rom`. No binary outputs.
- Updated `tools/audit_quiz_nonanswers_077.py`: its old claim of exactly one native field is replaced by three across 077+078 (one + two), leaving eight other unsafe aliases for parent-text audit.
- Updated `tools/recover_merge_061_81_one_ips_076.py`: when ONE original historical 039–043 IPS/ZIP is available, safely construct cumulative **061 + 81 Quiz answer candidates + 077 daily-allowance continuation + 078 two explanations** into ONE clean-original-relative IPS/JSON. It validates intermediate 077 SHA first, then 078 output SHA as the final image SHA. Still untested with unavailable historical raw font base.
- The GitHub Actions `chibi-snes-source-qa.yml` job now runs the 078 ROM-free field/source/capacity audit. The workflow itself is source checks, *not* a SNES emulator.

## Accurate remaining work

**Official source staging remains 279/381** from historical manifests; current extra candidates are **81 answer labels + three physical non-answer fields**, all still **emulator unaccepted**. The remaining **18 original scanner IDs** are nested or unsafe and require semantic parent-script review before being counted or deleted. Real cumulative V2 ROM requires raw historical 039–043 IPS/ZIP, which is still inaccessible in this session. Fortune's four longer entries, G3 win/loss/end graphics, final title/UI/Story QA and actual emulator visual-width, menu, answer-grading and transition tests remain.

**Never claim that static IPS validity means gameplay or a completed Vietnamese translation.** Prioritize real user-visible localization and protect the user's original ROM.
