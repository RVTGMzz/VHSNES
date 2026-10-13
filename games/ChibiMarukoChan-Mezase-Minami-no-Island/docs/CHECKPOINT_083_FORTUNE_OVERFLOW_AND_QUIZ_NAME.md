# Chibi Maruko-chan SNES — Checkpoint 083: four Fortune overflow strings audited; Ono Quiz friend named

Date: 2026-10-13 · branch `chibi-maruko-bootstrap-01` · previous checkpoint 082.

## Real content edits: Ono and Sugiyama

The **existing** stage058 Quiz explanation at original source scanner `0x32BBE` referred vaguely to Ono's friend. The immediately preceding question asks about Ono's dream, and the original Japanese physical record says `杉山くんと二人でいつか / 船乗りになることが大野君の`: it explicitly names **Sugiyama** as the person Ono dreams of going to sea with.

Original native physical layout:

- Original record starts at `0x32BBA`, source scanner starts `0x32BBE`.
- First source segment contains only two ASCII indentation bytes; must remain empty.
- Original first writable glyphs `0x32BCA`, **11** two-byte cells `杉山くんと二人でいつか`.
- Original second writable glyphs `0x32BE8`, **13** two-byte cells `船乗りになることが大野君の`.
- Original `81 6F` line breaks at `0x32BC0`, `0x32BE0`, `0x32C02` remain immutable.

| Caption | Historically staged stage058 | 083 corrected |
|---|---|---|
| First rendered text line, 11 cells | `Ono và bạn` | **`Sugiyama và`** (11) |
| Second rendered text line, 13 cells | `cùng ra khơi` | **`Ono ra khơi`** (11) |

Together these display **“Sugiyama và Ono ra khơi”** — restoring both names and the shared aspiration; the previous question supplies that it is a dream. The source text's exact sailor profession is still abbreviated as “ra khơi”; full meaning preserved in canonical `vi_full`. It is **not** a new source ID.

New `translation/runtime/quiz_sugiyama_ono_083.json` and `tools/build_quiz_sugiyama_ono_083.py` verify the unchanged canonical Japanese and Vietnamese source row; historical stage058 old captions and two exact original line capacities; original 16-bit native LoROM pointer, CP932 source bytes, `81 6F` frame controls, baseline V2 glyph pointer, all updated glyph lookups, no modifications outside 2 preapproved captions + native checksum and cumulative clean-ROM IPS replay. ROM-dependent checks cannot run until original SFC and exact archived 039–043 baseline are available.

`tools/recover_merge_061_81_one_ips_076.py` now appends guarded **083** after the full **082** semantic correction and reports the **final 083 checksum**. Still one combined patch, not a stack of micro patches.

## Four Fortune blockers — natural text kept intact

The four original source strings had **already** been fully translated in the source CSVs; what remained was runtime **capacity overflow**, not untranslated content. No unsafe abbreviations were introduced.

| Original ROM offset | Japanese | Natural Vietnamese, frozen | Original cells → required | Extra cells |
|---|---|---|---|---:|
| `0x2BD5E` | `天の声` | **Lời trời mách** | 3 → 13 | +10 |
| `0x2C86B` | `また来週` | **Hẹn tuần sau** | 4 → 12 | +8 |
| `0x2CA7D` | `きいろ` | **Vàng** | 3 → 4 | +1 |
| `0x2CADD` | `しろいろ` | **Trắng** | 4 → 5 | +1 |

**Do not mark these four as in-ROM localized.** Source-only coverage would be 153 of 157 canonical Fortune fields in the previously planned full merge and **4 pending extended storage/renderer fields**. The full merged 056 ROM hasn't been reconstructed in the present environment; its 153 count is still a conditional **static candidate inventory**, not completed integrated gameplay.

New `translation/runtime/fortune_expansion_083.json` fixes four precise original source identities, existing fully accented `vi_full` and display strings, true two-byte CP932 slot limits, and release/visual-proof restrictions. New `tools/audit_fortune_expansion_083.py` validates all **157** canonical Fortune source rows, their matching original-Japanese/VI translations, preserved prior 056 excluded IDs, 160 existing V2 glyph mappings and physical overflow. Its optional `--original-sfc` mode requires the exact retail 2MiB Japanese SHA256 and verifies all four original JP byte spans plus `81 6F` terminators before finding **potential 16-bit/24-bit LoROM pointer shapes**. These raw byte matches are deliberately labeled **hypotheses**, not proven execution references or safe relocations.

The original captions need **two separate proof gates**: (1) locate and validate actual native field pointer/control reachability before any relocation; (2) render/test whether longer text fits the Fortune screen, even when relocated. Do not simply shift `81 6F` or overwrite the following physical Japanese entries. One- or two-cell expansions for colors may still clip visually. The aged JP field limits should not force unnatural terms such as `Kim`, `Bạch` or a misleading `Lời` as final display strings.

## Testing and honest status

- GitHub Actions [source QA run 38364216770](https://github.com/RVTGMzz/VHSNES/actions/runs/38364216770) **SUCCESS**, including both explicit new 083 checks: 4 Fortune source/overflow rows, and named Sugiyama/Ono Quiz field exact width/semantics.
- All 083 commits are **source-only** (JSON, Python tools, CI, docs). Original historical stages and old SHA contracts remain unmodified.
- No exact original retail ROM or historical 039–043 ZIP/IPS raw bytes are mounted in this session. No cumulative real V2 ROM or IPS was rebuilt and no SNES emulator session occurred. Thus no new **playable** version is claimed.
- Official historical Quiz staging remains **279/381 source scanner IDs**. New correction fixes **one existing narrative parent**, zero new independent sources.
- `0x31F33` still omits **Maruko's ninth birthday age**. Avoid awkward compressed `9t` until safe Quiz text expansion is proven.
- Pending additional content/render acceptance: 4 Fortune overflow screens, 9-year age detail, G3 win/loss/result/ending graphics, first title credit exact **“Việt hóa bởi Votri Valley”**, full Story/Quiz/gameplay/controller tests, final font typography cleanup (last).

## Next highest-value work

Use actual native LoROM access and single user-owned 039–043 historical archive to test **one** end-to-end cumulative IPS through 083. For Fortune, first prove pointer ownership and screen-space constraints via a read-only exact-source inspection, not speculative in-place patches. Then complete the four runtime expansions only if both control and visual footprint can be established. Do not send isolated tester patches unless requested.
