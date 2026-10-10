# Chibi Maruko-chan SNES — Checkpoint 033: localized first-boot title + exact Votri Valley credit

Date: 2026-10-11. Repository `RVTGMzz/VHSNES` branch `chibi-maruko-bootstrap-01`.

## Direct user instruction, confirmed

**Translate the actual title shown immediately when the game starts**, not just the Story Mode selection and not an internal text/debug descriptor. Add a small credit, spelled **exactly**:

```text
Chibi Maruko-chan
Tiến tới đảo phương Nam!!

Việt hóa bởi Votri Valley
```

This is the approved **display copy and order**, not a screenshot from the game. The name `Chibi Maruko-chan` remains recognizable, the subtitle translates `めざせ！南のアイランド！！`, and the additional Vietnamese credit is in a smaller readable style underneath. Use **Votri Valley**, with a space; the former `VôtriValley` spelling must not be used in this game.

The credit is **additional to**, not a replacement for, any original game publisher/developer/copyright notice. Do not cover Maruko character artwork or interrupt the intro/title flow. The internal LoROM cartridge-title header should not be rewritten for on-screen translation.

## Changes already committed

Canonical copy/target files and reverse-pipeline configuration now agree:

- `translation/source/graphics_text_targets_vi.csv` — approved Japanese-to-Vietnamese title and exact credit.
- `translation/runtime/content_first_graphics_queue_032.csv` — **both G0 title and G0 credit upgraded to P0**, the same urgent content-first category as G1.
- `translation/UI_GLOSSARY_VI.md` — exact three-line user-approved title and credit.
- `translation/TRANSLATION_PROGRESS.md` — title translation requirement stays in known content scope.
- `tools/run_g0_title_reverse_pipeline.py` and `tools/run_all_graphics_reverse.py` — G0 candidate report text uses **Votri Valley**.
- `docs/G0_BOOT_TITLE_TRACE_001.md`, `docs/G0_DMA_SOURCE_TRACE_002.md`, `docs/GRAPHICS_BUILD_036_PIPELINE_006.md` — instructions use exact credit.
- `HANDOFF_CURRENT.md`, `NEXT_CHAT_PROMPT.md` — active priority and limitation explicit.
- **New structured spec:** `translation/runtime/g0_startup_title_copy_v1.json` — title layers, alignment, priority and safety constraints.
- **New regression guard:** `tools/audit_g0_startup_title_copy_033.py` — checks canonical source, G0 priority, exact spelling, and no unproved asset/runtime claim.

Reproduction inside a full repository checkout:

```bash
cd games/ChibiMarukoChan-Mezase-Minami-no-Island
python tools/audit_g0_startup_title_copy_033.py --report reports/generated/g0_title_copy_033.json
```

The guard checks text copy, not emulator graphics. Do not claim this check validates visual placement.

## Required technical integration

The title is a **graphics-first SNES retail screen**. The exact bytes that render the original title/logo and subtitles have **NOT** yet been linked to a reproducible graphics/tilemap path. Therefore no title-screen ROM write was made in this checkpoint, and no playable file is claimed to already show the Vietnamese title.

Follow existing G0 title reverse steps:

1. Trace real `reset -> title setup -> graphics/tilemap/DMA` or `ROM -> decompressor -> WRAM -> VRAM` route.
2. Render actual graphic asset and establish source bounds and tilemap/palette assumptions.
3. Prepare localized title pixels and small Votri Valley credit **within verified capacity**; preserve character graphics and original copyright.
4. Integrate with guarded graphics Build036 (or separately verified G0 title graphics path), without assuming old Build035 has playable font support.
5. Run in an SNES emulator and collect actual **first-boot title screenshot**; accept only if Vietnamese letters, credit, original copyright and Start flow are correct.

No fabricated byte offsets. Never change internal developer/debug descriptor text as a substitute for the visible title artwork. Do not upload commercial game ROMs to GitHub.

## Status

- Exact Vietnamese title and requested credit wording: **APPROVED and committed**.
- Graphics priority: **G0 P0**.
- On-ROM tile graphics editing: **NOT DONE** (source asset still unresolved).
- Actual startup screenshot/gameplay QA: **NOT DONE**.
- Content-first directive: stays active; font/9px research remains deferred until translation/graphics content is handled.
