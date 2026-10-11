# Chibi Maruko-chan — Checkpoint 044: content-first LARGE Story batch (87 real insertions)

Date 2026-10-11 · Repo `RVTGMzz/VHSNES` · branch `chibi-maruko-bootstrap-01`.

## User direction and scope

The user is frustrated that SNES localization has dragged on for weeks through repeated tiny checkpoints and test files. **Stop offering intermediary IPS downloads or asking the user to test each one.** Complete actual content first, font later, and consolidate larger batches without corrupting dialogue or its in-game scripting.

This turn inserted **87 additional real Story dialogue/narrator records into one combined ROM**, not simply editing a translation spreadsheet:

| Source | Newly inserted in checkpoint044 |
|---|---:|
| Story Batch01 | **33** |
| Story Batch02 (first two canonical CSVs) | **54** |
| **Total** | **87** |

Prior checkpoint043 had 26+58 = **84 separately tracked Story Batch01 entries**. Therefore the new integrated binary has **117 tracked Batch01 Story entries**, plus **54 new Batch02 Story entries**. The first **three separate Batch01 tutorial records** at `0x181CC`, `0x18245`, `0x182BE` were already localized in the checkpoint043 baseline **from previous builds**; checkpoint044 discovered this by comparing their ROM bytes and **did not overwrite them**. The total player-facing Batch01 list is **126 canonical CSV rows**, not 123 as historical checkpoints claimed. Thus: **120/126 Batch01 fields have Vietnamese codepoint bytes at the static ROM level** (117 here tracked +3 preexisting); **6 remain untouched** because they require dynamic script controls, continuation across records, or manual audit. Batch02 source has 126 rows; **54 of its fields now have Vietnamese bytes**. Batch03 not yet rebuilt.

In terms of directly managed fields in the cumulative content-first test sequence: **263 = 176 from 039–043 +87 new in 044**, plus the three previously localized opening/tutorial fields discovered but not double-counted. This count is not the number of all Japanese lines or a declaration of completion.

## Language/editorial policy

Dialogue was edited with scene context. Maruko/Tama-chan use informal close-friend speech, Maruo keeps `Nói thẳng ra!`, Hanawa keeps his `Baby` address, and family/narrator retain distinguishable voices. The complete natural Vietnamese `vi_full` remains in canonical `translation/source/*.csv`; separately reviewed display candidates in `translation/runtime/story_batch01_02_content_first_044.json` are compact to fit **verified physical per-line ROM capacities**, not automatic truncations.

Examples: `Trao đổi là gì / vậy?`, `Toshiko cười / mừng thầm vì / khỏi đi thi!`, `Baby, lần này / tớ không tha đâu`, `Thắng rồi mà sao / lòng vẫn đau quá?`, `Nghĩ lại, tớ đã / khổ đủ điều mà / chưa biết đảo nào`. The source's original end-marker and control positions remain unchanged.

**Limitations:** Some compact wording necessarily omits full nuance in the source. It requires future in-game readability and human editorial review. Long lines and symbolic placeholder scripts must be solved with safe segment relocation/expansion, rather than claiming these fit naturally or overwriting variable bytes.

## Actual binary and independent static QA

Based on exact original unheadered 2 MiB Japanese cartridge:

- Original SHA256: `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`.
- Exact 043 experimental input ROM SHA256: `45ffca7db5db83bc2734e885ee90c77f33746e2c4a54d1c99f1502f3e992a6ae`.
- **044 experimental output ROM SHA256: `7f0c7ef92f2c40e0cab7703326c93cf6338d9ae771fef4b43a2350bda0c643fc`.**
- **044 clean-ROM IPS SHA256: `5b4da16b00f7c38dd1de7f4bd2431479b9b75bd2441f4d122d42d8549e9d9784`.**
- IPS size **33,901 bytes / 1,195 records**; independent applicator applied directly to exact clean ROM, reproduced exact output SHA256 byte-for-byte.
- **87 actual Japanese source fields**, with original 8×8/font V2 two-byte glyph layout, all patched into exactly 4,680 original writable bytes (2,340 two-byte glyph units).
- **214** original `816F` and `81A5` line/page delimiters within the new fields untouched. A scan of the **entire Story bank** `0x18000..0x1DFFF` verified every line/page delimiter stays at the same offset.
- Actual changed ROM positions vs checkpoint043 **4,680**, restricted to the 87 new Story text spans and checksum. Prior G0/G1 title/credit, 38 UI, 33 Fortune, 21 Quiz and 84 tracked Story records were not overwritten.
- Cartridge header checksum/complement: `0x2D86 / 0xD279`.
- **NO new font or codepage graphics work**; existing V2 glyphs reused.
- **SNES emulator runtime NOT TESTED**, no complete localization, no CI PASS asserted.

### Reproducibility preserved ON GITHUB

- `translation/runtime/story_batch01_02_content_first_044.json` — exact 87 source offsets, approved short-form line sequences, respective original canonical complete `vi_full` and speaker contexts.
- `tools/build_content_first_044_story_87.py` — deterministic build from exact original 2 MiB ROM plus exact checkpoint043 **clean-ROM IPS**, validates complete canonical source row identity, Vietnamese/codepage mapping, original raw Story frame boundaries, no old-field overlap, strict diff whitelist, original `816F`/`81A5` positions, cartridge checksum, output SHA and independent IPS replay. Refuses untested output without explicit opt-in.
- `docs/CONTENT_FIRST_LARGE_STORY_CHECKPOINT_044.md` — this checkpoint.
- Local exact patch-only asset: `/mnt/data/Chibi_044_Story87_Content_First_UNTESTED.ips`. The previous user explicitly asked **not to be sent repeated patch downloads**. Commercial ROM remains local, never GitHub.

To reproduce after fetching sources and providing clean 2 MiB ROM + checkpoint043 IPS:

```bash
python tools/build_content_first_044_story_87.py original-japanese.sfc checkpoint043-clean-rom.ips \
  --ips checkpoint044-clean-rom.ips --report checkpoint044.json --allow-untested
```

The physical-ROM original→043→044 chain was reconstructed and checked locally; GitHub builder code was committed but not separately run in GitHub CI.

## Next high-impact work

1. **Batch02 remaining 72 rows**, then Batch03 (84 rows): batch whole scenes instead of 10–20 rows and stop inserting full-source dialogue into fixed boxes unless readable and contextually coherent.
2. Resolve the **six Batch01 rows** still blocked by variable control or split dialogue: `0x18408`, `0x18708`, `0x1873E`, `0x189EE`, `0x1A1B0`, `0x1A334`; check actual executable script semantics before patching.
3. Audit physical remaining Story source lengths and find a safe way to support larger Vietnamese text; do not return to font engineering while content remains.
4. Continue G2 rules and G3 real results only from validated executed assets. Consolidate one future significant whole-game trial and then emulator-test.

**Status: 87 more retail Story fields actually patched and exact static binary QA PASS; full game and SNES runtime acceptance pending.**
