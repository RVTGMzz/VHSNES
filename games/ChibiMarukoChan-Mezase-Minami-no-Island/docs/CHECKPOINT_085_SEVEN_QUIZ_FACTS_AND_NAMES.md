# Chibi Maruko-chan SNES — Checkpoint 085: seven Quiz facts/names reintroduced

Date: 2026-10-13 · Branch `chibi-maruko-bootstrap-01` · Parent: checkpoint084.

## Editorial and native caption fixes

Re-read original Japanese and canonical Vietnamese for seven **historically staged** Quiz explanation fragments. Fixed omissions affecting real character facts, birthday setup, dialogue coherence and item specificity, not just cosmetic wording. The historical 054/058/059 prebuilt manifests **remain unchanged**; new V2 edits overlay on cumulative stage084.

| Original source parent | Prior stage | Old V2 caption | New V2 caption | Approved physical glyph cells |
|---|---|---|---|---|
| `0x32095` | 059 | `Maru mê kem / Tiền tiêu vặt` | **`Mê burger, kem / Tiền tiêu vặt`** | 14 / 13 |
| `0x32303` | 059 | `Ông hiểu Maru / nhất nhà / thơ haiku` | **`Hiểu Maru nhất / thân lắm / làm haiku`** | 14 / 8 / 9 |
| `0x3259A` | 059 | `Bà âm thầm / mà biết đạp xe / Maru đã hay` | **`Bà lặng lẽ / mà biết đạp xe / Maru đã hay`** | 12 / 14 / 11 |
| `0x31FA6` | 059 | `Đáng lẽ vui / Hanawa, Maruo / Midori tới!` | **`Sinh nhật mà / Hanawa, Maruo / Midori nữa!`** | 12 / 13 / 13 |
| `0x3394B` | 058 | `Là Tokuzo / Nhà bán hoa / ngày nào cũng` | **`Sugiura / Tokuzo / Nhà bán hoa`** | 9 / 11 / 14 |
| `0x33C6C` | 058 | `Em Buutaro / tên Tomiko / hay đi lễ` | **`Em Buutaro / Tomita / Tomiko đi lễ`** | 11 / 12 / 12 |
| `0x350AD` | 054 | `Fuyuta tặng / Ono kẹo / nhưng lại` | **`Fuyuta tặng / sô-cô-la / cho Ono`** | 14 / 9 / 9 |

**Meaning and continuity considerations**

- Japanese `ハンバーグとアイスクリーム` specifically names two favorite foods; restores *burger* as a compact term for hamburger patty, keeps `Tiền tiêu vặt` for the immediately following record `0x32126`.
- Japanese `いちばんのりかいしゃ`, `なかよし`, `心のはいく` describes Tomozou as Maruko's closest understanding friend who sometimes makes haiku; older caption dropped their closeness and added unsupported `nhất nhà`.
- Japanese `目立たない` describes an unassuming grandmother; `Bà lặng lẽ` is an editorial approximation, still requiring visual/native language QA.
- Japanese `ウキウキのおたんじょうび` anchors the following unwanted visitors Hanawa, Maruo and Midori as a *birthday* intrusion. Crucial: **this does NOT fix the unrelated missing birthday age-nine fact** in native record `0x31F23` scanner alias `0x31F33`; that issue remains.
- Native `0x3394B` begins `杉浦とくぞうくん`, naming **Sugiura Tokuzo**. Family owns a flower shop. Separate following caption at `0x339AE` already says he brings flowers; changing `ngày nào cũng` to `Nhà bán hoa` preserves the independent flowers clue and full name after the Quiz question.
- Native `0x33C6C` names the sister of Buutaro **Tomita Tomiko** (`富田とみ子`) and her church attendance. The full name spans two original fixed-length rendered lines to avoid unsafe truncation; `đi lễ` remains.
- `チョコ` in Valentine story is **chocolate**, not unspecified candy. The next `0x3510A` caption already describes Maruko and Tomozou receiving the same chocolate, so keep its existing narrative.

## Reproducible and fail-closed code

- `translation/runtime/quiz_seven_fact_restore_085.json` contains seven previously staged parents, exact old and revised V2 captions, historical stage identity and original source Japanese and complete Vietnamese, glyph capacities, editorial justification and conservative release flags.
- `tools/build_quiz_seven_fact_restore_085.py --audit-only` reads the actual frozen canonical CSVs and frozen stage054/058/059 manifests, tests explicit Japanese fact anchors, verifies all **20** original V2 glyph frames totaling **234** existing glyph cells, checks **14** new frame values and all Unicode glyph lookups; prohibits creating new canonical source IDs.
- Optional `build(clean, baseline, root)` requires exactly SHA-locked user-owned 2MiB original Japanese SFC, genuine post084 V2 font table and all **old** caption bytes. It derives original CP932 text spans and `81 6F` controls from actual native record frames, checks native headers and original LoROM pointer-word evidence, writes **only 14 changed existing two-byte glyph frames + SNES checksum**, then builds a single clean-original-ROM IPS and verifies full IPS replay. It **was not executed** without the genuine ROM + historical archive.
- `tools/recover_merge_061_81_one_ips_076.py` now appends stage **085** AFTER stage084 in the protected cumulative reconstruction chain, returning the final 085 checksum and an audit report, never asking the player to apply four or seven separate patch snippets.
- CI `.github/workflows/chibi-snes-source-qa.yml` includes the new 085 audit and the old 082/083/084 source checks. First CI run exposed a **schema key mismatch** (`clean_sha256` vs `clean_original_sha256`) and missing explicit immutable-history flag. Both were corrected and tested. The subsequent source-and-static [run 38372615081](https://github.com/RVTGMzz/VHSNES/actions/runs/38372615081) **SUCCESS**; step “Verify 085 seven Japanese Quiz omissions repaired in existing V2 frames” **SUCCESS**. Graphics/static [run 38372615093](https://github.com/RVTGMzz/VHSNES/actions/runs/38372615093) **SUCCESS** on that checkpoint code commit.

## Honest current status

- Original historical Quiz scanner source count **279 / 381 unchanged**. Seven corrections are to **existing** original records; add **zero distinct scanner IDs**. An additional 81 choice-entry candidates and 3 independent non-answer source candidates are still not SNES emulator accepted.
- Four Fortune source translations remain **runtime overflow** cases: `Lời trời mách`, `Hẹn tuần sau`, `Vàng`, `Trắng`. Do not count them as safely in-ROM implemented.
- Original `0x31F33` still omits Maruko turning **nine** because existing 13 + 13 caption frames cannot naturally preserve zodiac plus birthdate question plus age; needs verified expansion, not “9t”.
- No exact clean original SFC, user-owned historical 039–043 ZIP/IPS or integrated playable ROM exists in the present session. **No full cumulative ROM/IPS rebuild, emulator gameplay, Quiz selection correctness or visual/font clipping proof**.
- G3 win/lose results, ending, exact title credit **Việt hóa bởi Votri Valley**, and final visual font polish still need end-to-end verification.

Project policy: deliver content-first Japanese-accurate colloquial Vietnamese, protect native control codes and original ROM provenance, stop inflating percentage with aliases, and wait for a properly rebuilt combined gameplay candidate rather than sending untested micro patches.
