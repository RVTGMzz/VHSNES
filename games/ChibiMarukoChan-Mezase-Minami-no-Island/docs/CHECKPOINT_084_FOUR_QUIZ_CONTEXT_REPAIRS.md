# Chibi Maruko-chan SNES — Checkpoint 084: four original Quiz contexts restored

Date: 2026-10-13 · Repository `RVTGMzz/VHSNES` · branch `chibi-maruko-bootstrap-01`.

## Genuine linguistic corrections in existing in-ROM stage source fields

Compared original Japanese scan text, unchanged full Vietnamese canonical CSVs and the **exact** historical stage054/stage058 displayed captions. Four previous on-screen captions had overly strong, semantically softened or misleading wording. The new compact strings keep existing full Vietnamese diacritics while preserving exact original two-byte glyph capacities.

| Original Quiz parent | Native caption slots | Previously staged caption | Checkpoint084 caption | Why |
|---|---|---|---|---|
| `0x34CF0` (054, Fujiki's misfortune letter) | 12/14/12 | `Fujiki từng / gửi thư rủi / cho Maruko` | **`Fujiki gửi / thư xui xẻo / cho Maruko`** | Clearer natural rendering of `不幸の手紙`, preserving the actual recipient and letter. |
| `0x34D5B` (054, Nagasawa/Fujiki relationship) | 12/7/7 | `Nagasawa hay / bắt nạt / Fujiki` | **`Nagasawa hay / dắt mũi / Fujiki`** | Japanese `ふり回される` is being led/dragged around and doesn't itself prove bullying. |
| `0x34E84` (054, island friend Pusadi) | 13/14/6 | `Pusadi hiền / làm Maruko vui / lắm!` | **`Pusadi hiền / Maru xúc động / lắm!`** | Japanese `かんどうさせられる` describes emotional movement rather than merely amusement. |
| `0x33E7D` (058, Nagasawa's father's resilience) | 13/3 | `Ông vẫn sống / tốt` | **`Ông vững vàng / lắm`** | `強く生きる` describes persevering strongly after the preceding fire, not moral goodness. |

**Counts:** four existing original parent records, **11 historical physical glyph frames**, **6 physically changed caption strings**, **113 original native two-byte glyph cells** unchanged in size, **zero newly staged canonical Quiz source IDs**. Avoid changing the frozen stage054/058 JSON or previously pinned ROM/IPS hashes; the batch is a post083 semantic overlay.

## Tools, source QA, and safe cumulative build

- `translation/runtime/quiz_semantic_context_batch_084.json` freezes source offsets, historical stages, canonical Japanese and full Vietnamese strings, old/new compact captions, reviewed capacities, and emulator/release flags.
- `tools/build_quiz_semantic_context_batch_084.py --audit-only` checks actual old 054/058 stage rows and canonical source CSV identities, all eleven original caption capacities, active V2 font/codepage coverage and six concrete edits, without requiring copyrighted game files.
- Optional **real ROM-dependent** `build()` fails closed without exactly SHA256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956` 2 MiB original Japanese SFC and an already-built post083 cumulative V2 baseline. It recovers original native frame delimiters from clean CP932 bytes, asserts corresponding JP scan narrative, checks native record headers and original 16-bit pointer-shaped references, proves real V2 baseline text/glyph table, changes only six exact existing glyph spans + four SNES checksum bytes, and independently replays the final original-ROM-relative IPS. The ROM-dependent path **was not run in this session**; its pointer-byte checks are conditional until executed with user-owned files.
- `tools/recover_merge_061_81_one_ips_076.py` now chains the checkpoint084 four-parent batch AFTER the previous 083 correction. It returns ONE clean Japanese original-relative IPS and QA report when the exact Japanese ROM and a real historical 039–043 archived patch are available; not four individual patches.
- Source GitHub Actions `chibi-snes-source-qa.yml` adds a dedicated **084** audit, protecting the source-only contract. [CI run 38368390692](https://github.com/RVTGMzz/VHSNES/actions/runs/38368390692) on `f248de0de1973a73cfcf6fd54b25aa8cd497f4f0` **SUCCESS**. Later branch runs must still be checked on HEAD.

## What isn't done

Original historical Quiz staging stays **279/381 canonical scanner IDs** — these are improvements to previous translated fields, not new source-count additions. The 81 answer and 3 independently addressable nonanswer candidates are still source/static proposals pending a correctly integrated V2 build and emulator test. Other unresolved tasks remain:

- Maruko's age nine missing from one 13+13-cell birthday/constellation caption at scanner alias `0x31F33`; do not replace natural “Kim Ngưu” or the birthdate question with unnatural “9t” shorthand.
- Four Fortune strings needing safe display expansion: `Lời trời mách` (3→13 cells), `Hẹn tuần sau` (4→12), `Vàng` (3→4), `Trắng` (4→5).
- G3 victory/defeat/result/ending, title credit exactly **“Việt hóa bởi Votri Valley”**, full Quiz choice/gameplay/emulator testing and final aesthetic font fixes.

This session's GitHub changes are JSON, Python source tools, workflow, and docs only. No original retail SFC, historical 039–043 ZIP/IPS, finished cumulative IPS or playable emulator-tested game was available/produced. Do not report source CI as SNES runtime acceptance or ask the user to download a speculative micro-patch.
