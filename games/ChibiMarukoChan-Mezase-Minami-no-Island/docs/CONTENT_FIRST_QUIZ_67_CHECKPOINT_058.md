# Chibi Maruko-chan SNES — Checkpoint 058: 67 original-ROM-verified Quiz records

Date: 2026-10-11. Branch: `chibi-maruko-bootstrap-01`.

## New content

**67 original player-facing Quiz records** were newly edited as Vietnamese runtime display captions, covering two whole sections of the original Quiz Batch03 source:
`translation/source/quiz_batch03_part2_vi.csv` and `translation/source/quiz_batch03_part3_vi.csv`.

The questions and narrative cover Sumire and Maruko's sister, Ono/Sugiyama and the move to Tokyo, Kayoko, Hasegawa Kenta, Sekiguchi, Tama-chan / **Honami Tamae**, teacher Togawa, Toshiko, Buutaro's sister Tomiko and Nagasawa's family. Full canonical Japanese source scans and **complete `vi_full` texts** are preserved separately; every 058 runtime record carries both unchanged source references and its short edited display lines.

**Semantic QA:** The first draft incorrectly reversed Honami Tamae's name, overabbreviated names such as Utsui Ken, and misrepresented some context. The final 058 material restores `Honami Tamae`, `Utsui Ken`, a coherent Ono/Tokyo transfer, and a correctly framed Nagasawa fire aftermath. Some captions remain compressed by physical source-line width; this is **not** a claim that all original full sentences fit. Difficult full-name answer choice records are deferred to longer-layout relocation rather than clipping a name to meaningless initials.

**Duplicate-scan fix:** Several canonical scanner rows begin midway through a prior physical ROM text window (for example `0x3299F` inside `0x32971`, `0x32C15` inside `0x32C09`, `0x33050` inside `0x33018`, `0x33119` inside `0x330E9`). The final 67 records **exclude the redundant inner span offsets**, not merely checking address equality. Physically checked all selected byte ranges and confirmed no pair overlaps.

## Exact byte QA on the real user-uploaded original ROM

Japanese headerless retail original: **2,097,152 bytes**, SHA256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`.

A Python validator scanned the exact original Japanese bytes, respecting CP932 two-byte glyphs, native ASCII indentation, `816F` line controls and script-stop bytes. Vietnamese captions are NFC-normalized and encoded through the unchanged known V2 `84xx` glyph table; no unknown glyphs or overflows were accepted. Each approved text cell was physically overlaid on a copy of the exact clean Japanese ROM. Independent IPS encoding/decoding reproduced **all 2MiB output bytes exactly**.

| Source-ROM static check | Verified result |
|---|---:|
| New original Quiz logical fields | **67** |
| Original physical text frame count | **149** |
| Preserved `81 6F` line markers | **149** |
| Original writable text region bytes | **3,180** |
| Actual changed bytes in source-only overlay | **3,174** |
| Original-ROM test-only IPS size | **3,937 B** |
| Original-ROM test-only IPS records | **151** |
| Source-only IPS SHA256 | `6403b2937ac1f82e33809954c6693b196bd425a830dfb79be4f18741a15da7d7` |
| Source-only ROM SHA256 | `510f1f64a765f16f00235fa2218b9919fab1e5fb977f7ed8afc633fbf4565ff8` |
| Byte-identical independent test IPS replay | **PASS** |
| Full 057 + 058 actual combined ROM | **NOT BUILT** |
| SNES emulator runtime / screenshot QA | **NOT TESTED** |

The isolated clean-Japanese ROM overlay is **NOT playable** as Vietnamese: it lacks the integrated V2 font, startup graphics/credit and recomputed SNES checksum. Never distribute this isolated intermediate as a full localization patch.

**Separate integration smoke test:** The 058 overlay/checksum/replay logic also passed using an **in-memory synthetic font-enabled source baseline** with a V2 lookup pointer and fake nonzero table glyph IDs. This proves only consistency of source fields, IPS replay and checksum algorithm; it is **not** the real 057 integrated ROM, nor a test of the production SNES renderer. The GitHub 058 builder itself has not been executed on the real integrated baseline yet. Do not claim SNES emulator PASS.

## Repository implementation / follow-up

- `translation/runtime/quiz_content_first_67_058.json`: 67 edited runtime Quiz records, per-row canonical Japanese and unchanged full Vietnamese references, source-only IPS/ROM QA fingerprints.
- `tools/build_content_first_058_quiz_67.py`: safe 057 -> 058 integration, verifying exact clean ROM SHA, canonical source identity, 149 script controls, no physical byte collisions with preceding 057, existing V2 glyph mapping, checksum and final IPS replay.
- `tools/rebuild_content_first_058_full_chain.py`: exact clean-ROM IPS rebuild from checkpoint043 through all stages to 058. Its initial committed version had incorrect renamed variable ordering; **fixed and committed** in `3addf45`. Use fixed revision or later.
- `docs/CONTENT_FIRST_QUIZ_67_CHECKPOINT_058.md`: this report.

**Cumulative conditional Quiz inventory:** checkpoint041 21 + checkpoint047 15 + checkpoint054 54 + checkpoint057 50 + checkpoint058 67 = **207 distinct source-record targets out of the historically inventoried 381**, leaving **174**. This is planned/byte-vetted localization material **not a verified 207/381 running-game achievement**. Older checkpoint053 was redundant (15 of its 16 were already in 041), and should never be counted separately.

**Current hard blocker for merged game:** exact source-based checkpoint043 clean-ROM IPS, expected SHA256 `d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50`, exists as historical package metadata `Chibi_043_G0G1_176Fields_Story58_Content_First_UNTESTED.zip` in Library but could not be materialized as authorized raw file bytes. Do not misrepresent this as a fetched or extracted ZIP. The user's clean Japanese SFC is available and verified.

When the exact 043 IPS is accessible, from the game folder:

```bash
python tools/rebuild_content_first_058_full_chain.py clean.sfc checkpoint043.ips --ips final058.ips --report qa058.json --allow-untested
```

Continue the remaining Quiz source bank, four capacity-blocked Fortune entries, G3 result/end graphics, then real emulation/character rendering/font QA. User requested content-first, font later, and no constant intermediate patch downloads. No copyrighted commercial ROM or font files were committed.
