# Chibi Maruko-chan SNES — Checkpoint 032: content-first canonical Vietnamese source merge

Date: 2026-10-11. Repository `RVTGMzz/VHSNES`, branch `chibi-maruko-bootstrap-01`.

## User-directed priority change

The user explicitly directed: **finish the game translation content first; deal with font later**. Stop spending successive turns on 9px/65816 font probes. Checkpoints 025–031 are preserved as historical diagnostics, but no more font repair should block text/editorial progress.

This checkpoint is about **real canonical source data writes**, not font testing, new ROM builds or speculative scanner rows.

## Completed changes

Merged the existing second-pass Vietnamese editorial revisions **into the actual `translation/source/*.csv` `vi_full` cells**, matching `file_offset` and verifying the expected prior translation before altering text. No source Japanese, source offset, row count, byte budget field, status, parser control field or `notes` column was changed.

Editorial passes, applied in order:

| Pass | Editorial events |
| --- | ---: |
| Tone consistency 01 | 7 |
| Tone consistency 02 | 12 |
| Tone consistency 03 | 18 |
| Quiz naturalness 01 | 15 |
| Tone consistency 04 (early Story) | 20 |
| Tone consistency 05 (mid Story) | 32 |
| Fortune naturalness 01 | 24 |
| Quiz naturalness 02 | 36 |
| UI/menu naturalness 01 | 31 |
| Auxiliary UI 03 | **25** |
| **Total** | **220** |

IMPORTANT bookkeeping corrections:

- The earlier progress notes called auxiliary UI pass03 **24** rows, but the **actual checked-in CSV has 25 data rows**. The factual editorial total is **220** for these ten pass files.
- Multiple reviews may revise the same source offset: **220 editorial events** correspond to **216 distinct (source CSV, file_offset) identities**, with **4 historical overrides**. The later pass is the final authority.
- Across the source mutations, **209 revision applications changed the current `vi_full` string**, and **11 editorial events already matched** the current value. These are **revision events**, not 209 additional Japanese strings.
- **20 canonical source CSVs** were touched, spanning Story (7 files), Maruko Q (4), Fortune (3) and UI/minigame/stage/quiz stats (6).
- BOM (`UTF-8-SIG`) in headers of `minigame_ui_batch01_vi.csv`, `quiz_ui_misc_vi.csv`, `stage_names_batch01_vi.csv` initially produced false missed offsets. The importer was corrected to strip BOM from the header during lookup **without rewriting or deleting the source file's BOM**.
- Three editorial value conflicts were manually resolved after source comparison:
  - `story_batch03_part2a_vi.csv` `0x1D6E0`: restore **“Nâng ly”** required by Japanese `カンパーイ！`; final `Maruko! Giỏi lắm! Nâng ly mừng Maruko thắng nào!`.
  - `story_batch02_part1_vi.csv` `0x1AFB3`: winning pass05 final `Thắng rồi mà sao lòng mình vẫn nhói thế này!?`.
  - `quiz_ui_misc_vi.csv` `0x31CD8`: latest auxiliary UI/glossary final `Đúng lần đầu`.
- No mismatch remains after selecting the **latest** review per source offset.

## Post-write verification performed using live GitHub branch data

For every one of the **216 distinct edited source offsets**, fetched the current `translation/source/*.csv` from the branch, parsed CSV including quoted comma fields and BOM headers, and compared its literal `vi_full` to the final `vi_revised` in editorial-pass order.

| Area | Unique edited source rows | Final mismatches |
| --- | ---: | ---: |
| Story | 85 | 0 |
| Maruko Q | 54 | 0 |
| Fortune | 24 | 0 |
| UI/menu/minigame/stage/result | 53 | 0 |
| **TOTAL** | **216** | **0** |

Reproducible standard-library QA script added:

`tools/audit_g2_editorial_canonical_032.py`

```bash
cd games/ChibiMarukoChan-Mezase-Minami-no-Island
python tools/audit_g2_editorial_canonical_032.py --json reports/generated/editorial-canonical-032.json
```

Audits ten source editorial pass CSVs, 20 target canonical source files and later-pass precedence. A PASS means the intended Vietnamese is really present in canonical source `vi_full`, not that the game ROM uses that string.

## Canonical language coverage vs actual ROM completion

The old progress tracker counts **1,018** player-facing meaning rows excluding three G2 demo source rows. Its aggregate beginning section calls it **1,021** when including those three. Reconcile this accounting as:

- **1,018 ordinary release-intent meaning rows** already collected from the discovered Story, Q, Fortune, Minigame, Karaoke, Menu, Stage, Credits, etc. source inventories.
- **+ 3 G2 direct-text demo rows** makes **1,021 source-row records tracked** in the historical total.
- Neither number means 100% of the ROM's original Japanese text is known, extracted, rendered or playable in Vietnamese. It is **known source inventory coverage**, not whole-game percentage.
- All confirmed direct-text player-facing banks were already meaning-covered before this checkpoint; this round **improves the canonical translations for 216 of those rows**, rather than discovering additional Japanese lines.
- Graphics/tilemap words already have a separate meaning/glossary layer (`translation/source/graphics_text_targets_vi.csv`), but exact visible title/menu/minigame/ending graphics still require asset-path identification and integration. Current G0/G1/G2/G3 evidence is documented in HANDOFF_CURRENT.
- Historical Build035 direct-text candidate is still **RUNTIME UNTESTED**. The actual user screenshot of the later Probe008 025 font experiment remains **RUNTIME TYPOGRAPHY FAIL**.
- No commercial ROM was committed. No SNES emulator gameplay test, runtime text reinsertion or font work was performed in checkpoint032.

## NEW WORK ORDER — content first

1. Keep font/renderer checkpoint031 **on hold**. Do not create another font-only checkpoint.
2. Verify the remaining graphics-visible Japanese targets against their source assets and build a **translation coverage/graphics asset queue**: G0 title/intro/credit, G1 Start/Password selection, G2 rules/start banner, G3 win/lose/continue/end cards. The Vietnamese meanings are already documented; asset extraction/insertion remains pending.
3. Audit truly new proven visible Japanese content (Story/minigame UI/karaoke or unrecognized resources), add new source rows **only with reproducible ROM/source evidence**. Prior whole-ROM audit had 13 unchanged kana candidates which were largely internal/debug or binary noise; do not inflate coverage based solely on a scanner substring.
4. Integrate the content changes with a verified patch/build pipeline **without claiming they are already active in the ROM**, maintaining original control bytes and codepage constraints.
5. After all content/graphics tasks possible without runtime font are complete, return to font with real emulator screenshot QA and ship a usable Vietnamese build.

Do not report static font microtests as translation productivity. Source row counts, canonical merges, remaining untranslated verified text and actual game screenshots should be reported separately.
