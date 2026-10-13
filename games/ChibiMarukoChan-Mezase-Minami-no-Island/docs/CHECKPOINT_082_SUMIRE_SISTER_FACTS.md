# Chibi Maruko-chan SNES — Checkpoint 082: restore Sumire's discipline and the sister's gratin

Date: 2026-10-13. Branch `chibi-maruko-bootstrap-01`. Parent checkpoint: 081.

## What was genuinely improved

Cross-reading the original Japanese Quiz source with the historical stage058 displayed captions found **two additional omissions not captured by the nine remaining Quiz scanner alias keys**. These are refinements to two existing, independent native *explanation* records; **not** new Quiz source IDs or translations of unrelated scanner fragments.

| Original stage058 parent | Existing three physical captions | New three physical captions | Semantics returned |
|---|---|---|---|
| `0x328E5` — Sumire, original lines `のことを大切におもっている。 / まる子のバカげた / こうどうをおさえる` | `Mẹ luôn thương / Maruko / rất nhiều` | **`Mẹ cũng ngăn / Maruko / quậy phá`** | The previous independent `0x3288E` record already said she loves her daughters. This record must also say she restrains Maruko's foolish antics, instead of repeating affection. |
| `0x32A38` — older sister, original lines `まる子にしばしばめいわくを / かけられるおねえちゃんは / グラタンがすきな小学６年生。` | `Maruko quậy / chị phát mệt / chị học lớp 6` | **`Maru phá chị. / Chị lớp 6 / mê gratin.`** | Retains repeated sibling annoyance, grade six and her **gratin** preference, previously absent from the runtime caption. |

The exact original physical Japanese glyph capacities remain **14/8/9** and **13/12/14**: 70 glyph cells total. Only **five of six** Vietnamese glyph-frame captions change. Japanese fullwidth `６` belongs to the *same third field* as `グラタン`, even though an original text scanner reported `0x32A96` as an apparent independent start. Do not patch this alias separately.

## Technical safety and reproducibility

- New `translation/runtime/quiz_parent_semantic_restore_082.json` preserves source/stage identity, original CP932 glyphs, exact physical offsets, old-to-new captions, and explicitly disallows claims of emulator or production acceptance.
- New `tools/build_quiz_parent_semantic_restore_082.py --audit-only` enforces historical stage058 contents and current source CSV, capacities, all 160 existing V2 font mappings, six exact frame positions and five actual caption differences.
- Optional actual clean-original-ROM build **fails closed** unless source SHA256 is `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`, original native records/pointer references exist, original Japanese physical glyph bytes match, all old V2 caption bytes are present after checkpoint081, and the installed V2 font lookup is valid at `0x2975E`. Writes only changed old glyph spans + LoROM checksum, then validates cumulative original-ROM IPS replay.
- Historical 058 JSON and all pinned historical stage ROM/IPS SHA anchors are unchanged.
- Updated `tools/recover_merge_061_81_one_ips_076.py` cumulative chain: user-owned 039–043 patch archive → genuine 061 V2 font/story baseline → 81 Quiz choice candidates → 077 question → 078 two explanations → 079 → 080 → 081 → **082** semantic overlays → **one** original-SFC-relative IPS + QA JSON when all exact original files are supplied.
- GitHub Actions [source-only CI run 38362299037](https://github.com/RVTGMzz/VHSNES/actions/runs/38362299037) **SUCCESS** at commit `d9d15bef9f348039bddf8e53abde600b7b79a7d2`; its **step 18 specifically ran 082 audit: SUCCESS**. Graphics reverse/static CI run [38362299048](https://github.com/RVTGMzz/VHSNES/actions/runs/38362299048) **SUCCESS** on same commit.

## Remaining nine original Quiz scanner aliases: context review ledger

Original post081 scanner aliases are still not nine new writable native records. Reading the corresponding source captions now supports this narrower source-only disposition:

| Original scanner alias | Parent/source evidence | 082 disposition |
|---|---|---|
| `0x31E50` | stage059 `0x31E04`: `lớp 3` | key grade retained |
| `0x31F33` | stage059 `0x31F23`: `Cung Kim Ngưu / Sinh hôm nào?` | **age nine still omitted**; keep open |
| `0x32874` | stage058 `0x3288E`: `40` | mother's age retained; distinct neighboring `0x328E5` maternal behavior now restored in 082 |
| `0x32A96` | stage058 `0x32A38`: `Chị lớp 6` in **new 082** continuation | sixth grade retained and additional gratin/teasing context restored |
| `0x34A99` | stage054 `0x34A2E`: `68 tuổi` | Hideji age retained |
| `0x352AC` | stage054 `0x3528F`: `Sinh 31/12` | Maruo's Dec 31 birthday retained |
| `0x352C2` | stage054 `0x3528F`: `nên tên / là Sueo!` | year-end naming clue retained; check screen continuity later |
| `0x361A4` | stage057 `0x36165`: `Đấu ở Namiki / hai cậu / thắng!` | Namiki/two winners retained |
| `0x364B1` | stage057 `0x36498`: `Nhà Maruko / chỉ một tầng` | one-storey home retained |

Thus **eight listed key details are represented in previous/new 082 captions**, while the original `0x31F33` description that Maruko is **turning nine** remains missing from the cramped 13+13 glyph-cell Quiz birthdate line. Do **not** replace the zodiac or birthday question with unnatural abbreviated Vietnamese to inflate a completion metric. This ledger is **source-level semantic review**, not proof that every nuance of every Quiz story is translated, nor emulator/gameplay verification.

## Accurate status after 082

- Original historically staged Quiz scanner identifiers **279/381 unchanged**. Extra 81 full answer prototypes and three independent native field candidates remain source/static only.
- 082 fixes **two already-staged parent records**, five line captions, zero newly counted distinct source IDs.
- No user-owned original ROM, historical raw 039–043 ZIP/IPS, integrated V2 candidate or SNES emulator run was available **in this session**; no playable patch was produced. Source CI cannot prove runtime font clipping, answer selection, display width, title credit or grading.
- Other work still outstanding: original nine-year-old fact with a safe extended renderer, four overlong Fortune cases, G3 victory/defeat/ending graphics and **Việt hóa bởi Votri Valley** credit, full game and typography QA.

User's preference: prioritize finishing **real Vietnamese content**, preserve historical working game/font changes, avoid requests to test piles of unplayable micro-IPS, and keep every session's real code progress and handoff on GitHub.
