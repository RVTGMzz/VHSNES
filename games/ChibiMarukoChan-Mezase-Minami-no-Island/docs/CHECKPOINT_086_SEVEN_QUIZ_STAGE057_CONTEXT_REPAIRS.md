# CHECKPOINT 086 — Seven Quiz scenes reviewed against original Japanese (2026-10-13)

Project: Chibi Maruko-chan SNES, `RVTGMzz/VHSNES`, branch `chibi-maruko-bootstrap-01`. Continues actual source checkpoint085.

## Seven old original stage057 Quiz records corrected

Full Japanese source and full translated Vietnamese remain in the authoritative `translation/source/quiz_batch02_part2_vi.csv` and `quiz_batch02_part3_vi.csv`. These are **post-stage057** display-layer corrections, not new Quiz records. The six historical `source`/ROM SFC facts elsewhere are not changed, and no old hash-locked stages are rewritten.

| Original scanner record | Original physical cell widths | Historically staged text | 086 revised native V2 text | Correction |
|---|---|---|---|---|
| `0x35AC3` | 9/9/9 | `Tin thật / nên đành / nói thật` | **`Yamada / tin Maru / thật lòng`** | Japanese describes Yamada believing Maruko and moving Maruko and her grandfather emotionally. Previous text wrongly says someone "told the truth", while the independent `0x35B16` clearly states they **make the lie become true**. The emotional reaction remains abbreviated due to original slot limits, recorded in the full source. |
| `0x35B94` | 11/4 | `Người đó / là?` | **`Ca sĩ tên / gì?`** | Proper complete spoken question asking who Yamane admires. Previously aborted middle of a question. |
| `0x35C63` | 9/7/9 | `Nhưng cậu / rất quý / người già` | **`Quý người / già và / khiêm tốn`** | Original `年よりにもやさしく` AND `けんきょ`: kindness to elderly and humility, both key facts. |
| `0x35EDE` | 12/4 | `Em tên gì? / nào` | **`Em gái tên / gì?`** | Removes orphan “nào”, asks Nagayama's little sister's name naturally. |
| `0x35F38` | 14/14/14 | `Nagayama rất / rành sâu bọ / em tên Koharu` | **`Nagayama rành / cây cỏ, sâu bọ / Hanawa cũng nể`** | Restores nature/insects **and Hanawa's explicit respect** (`いちもくおいて`). The following original independent `0x35FA9` narration already introduces ill younger sister **Koharu**, so she was not removed from the narrative. |
| `0x360FA` | 12/13/13 | `Bọn quậy phá / bắt nạt bạn / Ono, Sugiyama` | **`Bọn quậy phá / bắt nạt bạn / Ono, Sugi cứu`** | Clarifies the boys are **protectors of their bullied classmates**, not the bullies or victims. Earlier `0x36057` identifies full names Ono and Sugiyama, and the next `0x36165` describes the showdown at Namiki park. |
| `0x36661` | 11/11/6 | `Chị Maruko / hay đọc gì? / nhỉ?` | **`Chị Maruko / đọc manga / nào?`** | Original specifically asks the manga title, with `ribon` disclosed in the subsequent native explanation. |

**Verified immutable capacities:** seven previously prepared original Quiz parent records, **19** original native two-byte text frames, **191** original glyph cells, **16** actual changed screen-caption frames. **0 newly staged distinct Quiz scanner IDs.** One unchanged old `0x360FA` frame explains the 19/16 distinction.

## Source and cumulative patch work

- Created `translation/runtime/quiz_context_semantics_086.json`: each original Japanese fragment, exact canonical full Vietnamese, original source offsets/files, old and new V2 captions, source reason and 19 pinned frame widths.
- Created `tools/build_quiz_context_semantics_086.py`, with `--audit-only`: loads source CSV and frozen stage057 manifest, compares historical source identities, exact original Japanese fragment lengths and every prior caption, uses existing 160-glyph V2 encoding and checks all 16 corrected frames within 191 cells, asserts zero new source IDs. The script **does not claim emulator or ROM execution**.
- Optional `build(clean, baseline, root)`: only the precise user-owned unheadered 2 MiB original Japanese ROM SHA `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`; actual post085 font/IPS baseline needed. Derives original native Quiz physical frames from source ROM, asserts actual CP932 glyph spans, `81 6F` controls, original pointer-shaped references, old V2 rendered caption bytes, and glyph indices before modifying only 16 approved frames and SNES checksum. Creates **one original-ROM-relative IPS** plus replay checksum, not micro patches.
- Extended `tools/recover_merge_061_81_one_ips_076.py` to run stage086 **after** previous stages 079–085 and report final 086 checksums. Prior historical manifests, original source CSV translations and font codepage remain unchanged.
- Source workflow `.github/workflows/chibi-snes-source-qa.yml` runs new 086 audit. [CI source run 38377484960](https://github.com/RVTGMzz/VHSNES/actions/runs/38377484960) **SUCCESS**, confirmed new dedicated step “Verify 086 seven Quiz fact and dialogue repairs in original 057 Japanese frames” SUCCESS; previous 084/085 steps also SUCCESS. Subsequent commits' CI must still be checked.

## Remaining blockers — honest status

**No original Japanese SFC or user-owned 039–043 historic ZIP/IPS baseline available in this session.** The optional ROM builder, cumulative 076 builder, SNES emulator and in-game visual acceptance were **not run**. This was a real GitHub-source and future binary patch-chain improvement, not a newly generated playable translated ROM.

Historical distinct Quiz source staging remains **279 / 381** from source inventory; 81 answer and 3 native nonanswer source-only candidate fields remain pending integrated gameplay acceptance. The four already fully translated Fortune terms need longer native text/render relocation, not a blind overwrite. The Quiz age-nine fact at scanner alias `0x31F33` is **still missing**: we re-evaluated possible 13/13-cell phrasings but did **not** replace the existing `Cung Kim Ngưu / Sinh hôm nào?` with unnatural `9t` or a misleading truncated birthday question. Distinct birthday narrative `0x31FA6` was restored in 085 but does not fix age nine.

G3 result/victory/defeat/ending, title-screen credit **`Việt hóa bởi Votri Valley`** and final font aesthetics/emulator acceptance still pending. User prefers content-first, no endless isolated test files or unsupported release claims.
