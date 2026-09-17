# Runtime Story Build 027

Updated: 2026-09-18 +07

This checkpoint is a large **runtime candidate** built on the accepted pre-GBA Chibi font/codepage state.

## Scope

- Base chain: Build 023 -> Build 024 -> Build 025 -> Build 026 -> Build 027.
- Build 024 keeps the compact Vietnamese main menu.
- Build 025 inserts Story Batch 01 compact runtime text.
- Build 026 inserts Story Batch 02 compact runtime text.
- Build 027 inserts Story Batch 03 through the currently discovered ending sequence.

Cumulative direct Story runtime rows inserted: **328**.

These runtime strings are compact fixed-field forms derived from the canonical meaning layer. They do **not** replace `vi_full` in `translation/source/`.

## Insertion method

The direct-text story path is patched conservatively in place:

1. start from the exact accepted previous build;
2. verify the target story text span still equals the clean ROM source bytes;
3. preserve known script separators/control-like pairs `81 6F` and `81 A5`;
4. preserve low control bytes after the player-text region;
5. write Vietnamese through the proven `0x84xx` codepage into the existing fixed text byte budget;
6. wrap compact Vietnamese across the existing line segments;
7. reject any overlap or unsupported glyph;
8. recalculate the exact 2 MiB LoROM checksum;
9. verify diff surface is limited to intended text spans plus checksum/complement.

No pointer relocation or field expansion is claimed.

## Build 025

- Story Batch 01 runtime rows: 123 unique non-overlapping fields
- source identity: 123/123 PASS
- overlap: 0 PASS
- diff surface: PASS
- checksum: `0x407E`
- complement: `0xBF81`
- SHA-1: `5352f6a7f068038cc7d6a2d1c624b3e1303ccc3c`
- SHA-256: `71899491e084b6b070fb1c5305b621f644c9061f7f1ef7e2e7b523302da1ac48`

## Build 026

- Story Batch 02 runtime rows: 121
- source identity: 121/121 PASS
- overlap: 0 PASS
- diff surface: PASS
- checksum: `0x4124`
- complement: `0xBEDB`
- SHA-1: `cdd4b2086a6ffe51f2f18f85924b039ebfe8d239`
- SHA-256: `958a31920a00a9bf8c793d3bd3bf4a85dbd096feac078e55a17143591368d06b`

## Build 027

Artifact name: `Chibi_Maruko_Build_027_STORY_COMPLETE_READY.sfc`

- Story Batch 03 runtime rows: 84
- cumulative Story runtime rows: **328**
- source identity: 84/84 PASS
- overlap: 0 PASS
- diff surface: PASS
- checksum: `0x87CF`
- complement: `0x7830`
- SHA-1: `9a9280d27c9e96df972e0b21f8b806bf19ef52f7`
- SHA-256: `ed815e70f1956d37e9fe3023bb651378874de32ebfbbd8544cbc087860f17b04`

## Runtime status

**UNTESTED. Do not call Runtime PASS yet.**

The user explicitly requested one large test after inserting as much Story content as possible. The next user test should prioritize:

- boot to compact Vietnamese main menu;
- enter Story mode;
- verify the first classroom dialogue renders and advances;
- continue through several scene changes / minigame transitions if practical;
- report the first broken line, freeze, overflow, or control-flow issue if any.

If the early Story sequence renders and advances correctly, keep Build 027 as the new runtime insertion baseline and continue with Quiz / Fortune / Minigame / Karaoke / Credits banks. If it fails, isolate the earliest failing Story field instead of restarting font work.
