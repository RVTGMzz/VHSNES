# Chibi Maruko-chan SNES — Checkpoint 038: G3 false-source elimination and guarded full-language merge

Date: 2026-10-11. Repo `RVTGMzz/VHSNES`, branch `chibi-maruko-bootstrap-01`.

## User priority — finish content / graphics first, font later

This round did **not** create another font, emulator-font microtest or graphics-only ROM iteration. It addressed a real obstacle to combining localized graphics with the older direct-text Vietnamese game: the two candidates **share a clean Japanese ancestor but were built separately**.

The latest **GRAPHICS-only** checkpoint036 ROM is 2MiB with SHA256:

`2c8beee73e985c9a2690cc36ace335f05115c1a3e81b369e09d0cfb132117090`

It already contains actual on-ROM pixels for G0 title `Chibi Maruko-chan / Tiến tới đảo phương Nam!! / Việt hóa bởi Votri Valley`, G1 `Bắt đầu / Mật khẩu`, and G1 mode heading `Chọn gì đây?`.

Historical **DIRECT-TEXT Build035** has a separately documented SHA256:

`f8fb662a9e1b8fc5a5ff689f690ceaf332055ed86983e52b476a78852e4fd58d`

It carries story, quiz, fortune, karaoke, minigame and some font/codepage work. **This exact Build035 ROM binary is not in the active container, not present as a ROM/patch in the 265-entry GitHub repository tree, and a filename search in available conversation/Library files yielded no match.** Therefore this round DID NOT produce or pretend to validate a real joined Vietnamese ROM. In addition, source `vi_full` editorial revisions applied after Build035 in checkpoint032 are not automatically included in that historical binary.

## New exact-asset three-way collision preflight

Committed `tools/merge_graphics036_directtext035_preflight_038.py`.

It explicitly requires **all three exact SHA-pinned 2MiB inputs**:

1. Clean original Japanese ROM (SHA256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`)
2. Historical direct-text **Build035** (SHA256 `f8fb662a9e1b8fc5a5ff689f690ceaf332055ed86983e52b476a78852e4fd58d`)
3. Graphics-only **checkpoint036** (SHA256 `2c8beee73e985c9a2690cc36ace335f05115c1a3e81b369e09d0cfb132117090`)

Unlike blindly applying an IPS, it rejects **any preexisting text-build modifications anywhere inside each reserved asset allocation**, even if the specific bytes to rewrite do not overlap:

| Graphic resource | Reserved ROM region |
|---|---|
| G0 title loader source pointer | `0x12095..0x12097` |
| G0 relocated bank86 compressed stream | `0x36907..0x37662` |
| G0 title 4bpp graphics | `0xF6456..0xF7A17` (5570 bytes) |
| G0 title BG tilemap compressed asset | `0xF1F00..0xF2120` (545 bytes) |
| G1 Story Start/Password sprite | `0xBF95E..0xBFB11` (436 bytes) |
| G1 main-mode heading sprite | `0xC706F..0xC7E0B` (3485 bytes) |

It additionally checks actual original main-menu/Story sprite asset loader call-site signatures, the whitelist for ALL graphics036 changed bytes, and keeps every Build035 byte untouched outside those guarded resources (except recalculated SNES checksum). It defaults to read-only dry-run; writing an untested merged ROM + **Build035-relative IPS** requires an explicit flag. If a region is occupied by Build035 font/codepage or anything else, it **stops without producing a merged ROM**. No fallback guess or silent relocation.

Example once an **exact historical direct-text Build035 binary** is available:

```bash
python tools/merge_graphics036_directtext035_preflight_038.py \
  clean.sfc direct_text_Build035.sfc graphics036.sfc \
  --report reports/generated/merge_038_dryrun.json

# ONLY if SAFE_TO_MERGE and when explicitly ready for another static, untested candidate:
python tools/merge_graphics036_directtext035_preflight_038.py \
  clean.sfc direct_text_Build035.sfc graphics036.sfc \
  --output-rom merged_untested.sfc --ips merged_untested_build035_base.ips \
  --report reports/generated/merge_038.json --explicit-untested-merge
```

## Validation against actual local ROM bytes

The exact clean and graphics036 ROMs exist locally and were hash-verified:

- Graphics036 differs from clean at **13,129 byte positions** in total including SNES checksum bytes.
- **Zero** of those changed positions occur outside the guarded resource allocations + checksum.
- Synthetic TWO disjoint direct-text edits were placed outside graphics assets; a local independent test showed both are preserved after a simulated merge and ROM checksum can be reconstructed.
- FIVE deliberate preexisting-resource conflicts at bank86 relocation, title graphic, G1 Story sprite, G1 mode sprite and G0 package pointer were correctly detected and blocked.
- A local JSON report `Chibi_038_Graphics_Text_Merge_Simulated_Preflight.json` records these results, explicitly naming its text base a **SIMULATED FIXTURE**, never the historical Build035.
- New reproducible selftest script `tools/selftest_merge_graphics036_directtext035_038.py` uses actual clean + graphics036 and synthetic text fixtures. The independent local simulation was run; do NOT assert that the committed script had CI validation. Current GitHub commit reports **no configured status checks**, so do not claim CI PASS.

This is valuable preparation, **not** a merged Vietnamese game and NOT emulator QA. Later revised `vi_full` wording and font legibility still need integration/testing.

## G3 victory/loss/continue — no unsupported sprite replacement

A separate exact-ROM CP932 search found:

| Phrase | ROM file offsets | Classification |
|---|---|---|
| `勝ち` | `0x1C04F`, `0x1C25C`, `0x1D03A` | Story dialogue only; not G3 result card |
| `敗けた` | `0x2876E` | Internal QA scene descriptor |
| `コンティニュー` | `0x2878C` | Internal QA scene descriptor |
| `やめる` | `0x287C4` | Internal QA scene descriptor |
| `最終勝利` | `0x287E2` | Internal QA scene descriptor |
| `エンディング` | `0x287FE` | Internal QA scene descriptor |

The descriptions are inside the non-player-facing QA bank `0x2865E..0x287FF`. Thus they cannot be overwritten to claim retail Win/Lose/Continue/Ending localization. Exact matches do not exclude other synonyms, sprite text, different renderers or code paths in the remaining ROM.

Committed `tools/audit_g3_literal_source_scope_038.py`; original-ROM phrase positions independently verified in local report `Chibi_G3_Result_Literal_Source_Audit_038.json`. The graphics queue now distinguishes *Story-only* and *QA-descriptor-only* wording from actual G3 art.

## Repair inherited from 037

The committed G2 rule-source checker `tools/audit_g2_rules_direct_sources_037.py` had a one-space typo in the hardcoded expected Vietnamese `vi_full` (an extra blank after the first `・`). Corrected this so it matches the **actual canonical CSV**. No text or ROM bytes changed by this checker fix.

## Next concrete actions

1. **Need the exact historical direct-text Build035 binary**, or a reproducible **direct-text patch** based on the exact Japanese ROM, before the three-way guarded merge can run against the real translated game. Do not invent a Build035 file, hash, or claim a combined build exists.
2. Continue G3 screen result callback tracing. Avoid all offsets `0x2865E..0x287FF` for retail graphics patches, and avoid guessing from the previous 52-entry raw sprite atlas.
3. Independently review how checkpoint032's canonical editorial `vi_full` changes are lowered into width-constrained runtime text; historical Build035 has not necessarily received those 216 final revisions.
4. Execute a **single large emulator QA pass** only after actual content + graphics are safely joined. Keep font work deferred per the user's instruction.

**038 result:** safe merge gate committed + real graphics whitelist zero outliers + five collision guards demonstrated + G3 false source paths excluded. **Zero new graphics/text inserted into combined Build035**, **NO full Vietnamese ROM**, **NO emulator gameplay PASS**.
