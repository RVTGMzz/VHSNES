# Chibi Maruko-chan SNES — Checkpoint 081: Four Quiz narrative corrections, five actual glyph-line edits

Date: 2026-10-13. Repository `RVTGMzz/VHSNES`, branch `chibi-maruko-bootstrap-01`.

## Real source-content improvements

Following checkpoint080, **12 original Quiz scanner aliases** still needed a context review. Examining the actual original clean Japanese game, cross-checking native bank06 16-bit pointers, Japanese CP932 glyph sequences and earlier 054/058/059 Vietnamese stage manifests identified **three groups of real narrative issues across four already-staged physical text fields**.

| Native record & actual original pointer | Old Vietnamese | Corrected display text | Why |
|---|---|---|---|
| `0x31E69`, `0x313FF` (stage059 source `0x31E6D`), original scanner alias `0x31E7B` | `Máu A / lười! / Momoe có ăn?` | `Máu A / lười! / Món quà này?` | Original `このプレゼント、はたして` introduces **this gift**; the following separately staged script already asks whether Momoe ate it. Removes redundant question and restores the story transition |
| `0x343CE`, `0x313A3` (stage054 source `0x343D2`), scanner alias `0x34403` | `Mẹ Hanawa / mới 29 tuổi! / làm ở xa` | `Mẹ Hanawa / mới 29 tuổi! / làm xa xứ` | Original `がいこくでしごと` explicitly says mother works **overseas**, not merely a distant place |
| `0x33014`, `0x3139B` (stage058 source `0x33018`), scanner alias `0x33050` | `Lớp Maruko / là lớp 3-4 / Cả hai bạn` | `Lớp Maruko / là lớp 3-4 / Sugiyama và` | Japanese explains that Sugiyama, like Ono, is a reliable classmate; previous Vietnamese first-half did not name either boy |
| `0x3307F`, `0x31403` (stage058 source `0x33083`) | `Ai cũng tin / cậu ấy hết` | `Ono là hai / bạn đáng tin!` | Finish the preceding field naturally: **“Sugiyama và Ono là hai bạn đáng tin!”**, rather than two disconnected, unnatural sentences |

All new strings use existing Unicode-to-V2 mappings and preserve the original physical field capacities. The five genuinely edited lines are `0x31EB3` (12 cells), `0x34420` (12), `0x33062` (12), `0x33089` (11) and `0x330AB` (13). The **other six** original lines in these four records remain identical to their already-staged translations. No original Japanese script/control bytes, original pointer-table words, or historical stage 054/058/059 manifests are changed.

The natural-language adaptation uses a small number of on-screen glyph cells (for example, “Món quà này?” instead of a longer rhetorical “Món quà này, liệu...”), preserving the sense when read with the immediately following scene. Actual visual fit and full dialogue flow still need emulator review.

## Genuine original retail-ROM verification

The user-owned original 2,097,152-byte headerless Japanese SFC is SHA256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`.

The original physical records were read and checked directly in the current session:

- `0x31E6D` starts with `0E 00 0F 0E`; native pointer `0x313FF` contains `69 9E`; raw lines: `血液型はＡ型で`, `なまけもの。`, `このプレゼント、はたして`, with capacities 7/6/12.
- `0x343D2` starts with `0E 00 0F 08`; pointer `0x313A3` contains `CE C3`; raw lines: `花輪くんのママは、なんと`, `まだ２９才。がいこくでしごと`, `をしているので、いつもは`, capacities 12/14/12.
- `0x33018` starts with `0E 00 0F 08`; pointer `0x3139B` contains `14 B0`; raw lines: `杉山くんたち、すなわち`, `まる子のクラスは３年４組。`, `杉山くんは大野くんとおな`, capacities 11/13/12.
- `0x33083` starts with `0E 00 0F 0E`; pointer `0x31403` contains `7F B0`; raw lines: `じく、クラスのみんなの`, `たよれる男の子なのである。`, capacities 11/13.

These byte observations are direct source-ROM facts, not claims of a running Vietnamese game.

## Code changes and test coverage

1. `translation/runtime/quiz_parent_semantic_restore_081.json` stores original field record addresses, pointer-word offsets, 11 exact physical glyph slots, historical stage identities, old captions and new Vietnamese captions with source text/interpretation.
2. `tools/build_quiz_parent_semantic_restore_081.py` fails closed unless old stage054/058/059 manifests contain the exact old rendered captions, all target glyph widths/CP932 originals match the user-owned clean Japanese ROM, the existing cumulative Vietnamese game ROM contains the correct old **V2-encoded** bytes and valid font lookup pointer `0x2975E == 0x9A74`, and original native script/control/pointer bytes are intact. It replaces only the **five existing 2-byte glyph spans** with V2 glyphs (plus checksum), without rebuilding or changing old pinned 054–059 artifacts. Final output is one clean-original-ROM-relative IPS + report, with IPS replay check.
3. The `tools/recover_merge_061_81_one_ips_076.py` one-archive chain now invokes **079 → 080 → 081** as post-font semantic overlays, in addition to previous 061 font/story, 81 Quiz answer candidates and 077/078 three independent Quiz native text fields.
4. `.github/workflows/chibi-snes-source-qa.yml` now runs the **081 ROM-free original source/stage/codepage audit**. [Source CI run 38358209162](https://github.com/RVTGMzz/VHSNES/actions/runs/38358209162) **SUCCESS**. Earlier [graphics/static CI](https://github.com/RVTGMzz/VHSNES/actions/runs/38358181683) **SUCCESS**.

**Do not confuse source-only CI with emulator acceptance**: the missing raw historical 039–043 IPS/ZIP still prevents assembling the actual integrated V2 ROM in the current runtime. No rendered SNES game test has been run and no copyrighted ROM or font file was published. There is no playable download from this checkpoint.

## Precise remaining Quiz scanner audit

The 12 remaining original scanner offsets from checkpoint080 are reduced by **three semantic/source aliases** (`0x31E7B`, `0x33050`, `0x34403`). The nine remaining for contextual review are:

`0x31E50`, `0x31F33`, `0x32874`, `0x32A96`, `0x34A99`, `0x352AC`, `0x352C2`, `0x361A4`, `0x364B1`.

They are nested/unsafe scanner offsets, **not nine independently patchable strings**. `0x31F33` specifically contains the source detail of **Maruko being nine years old**, which is still absent in the existing cramped 13/13-cell caption `Cung Kim Ngưu / Sinh hôm nào?`. Do not discard the zodiac or birthday question just to force the age into an unsupported narrow slot. Investigate wider-field rendering or acceptable concise language with actual emulator QA. Several others are fragments of already staged parent script records. Continue an evidence-based **semantic QA**, not a fake increase to source progress.

**Official distinct source staging remains 279/381 Quiz scanner IDs**. Existing 81 complete answer candidates and three new independent native fields are still byte-level prototypes, not approved gameplay integration. More pending user-facing work: Fortune four long cases, G3 graphics win/loss screens, title credit “Việt hóa bởi Votri Valley”, font glyph clipping, full-story Quiz progression and answer selection.
