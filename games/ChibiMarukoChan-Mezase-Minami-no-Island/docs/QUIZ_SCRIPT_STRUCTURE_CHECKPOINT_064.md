# Checkpoint 064 — Quiz native script structure, read-only

Date: 2026-10-12. Branch: `chibi-maruko-bootstrap-01`.

This checkpoint **does not add translated Quiz entries**; it researches a previously unresolved safety blocker: the original native Quiz script format must be understood before anyone moves answer text into spare ROM space.

## Verified exact original Japanese ROM

The user-supplied `Chibi Maruko-chan - Mezase! Minami no Island!! (Japan)(1).sfc` is 2,097,152 bytes; SHA256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`.

Read-only scan of the original Quiz-script window `0x31C00–0x36907` (end-exclusive), counting native three-byte text break / script header sequences `81 6F 00`, gave:

| Verified native transition immediately following `81 6F 00` | Count |
|---|---:|
| Normal parameters starting `0E ?? 0F ??` | **355** |
| Longer introductory command `10 ?? 0E ?? 0F ??` | **4** |
| Special seven-byte record footer (sixth byte `C6`, eighth byte `00`) | **50** |
| Unrecognized transitions | **0** |
| **Total recognized script-end transitions** | **409** |

This explains why simply concatenating translated answer glyphs into the `FF` padding is **not proven safe**: the original byte stream contains command headers and 50 distinct special record-footer transitions, not merely a flat list of text strings. The semantics of these trailers and any relocation entrypoint/pointer table remain unknown. **Do not rename these seven-byte trailers "pointers" or alter them before proving what they mean.** This is structural/byte evidence, not disassembly or emulator acceptance.

A separate exact clean-ROM comparison reconfirmed **5,881 bytes of `0xFF`** between `0x36907` and `0x38000` (exclusive). That region is still an **unapproved relocation candidate**, not a guaranteed unused section. The earlier full Quiz slot audit remains valid: 279 distinct staged source offsets, 546 independently scanned original glyph spans and no overlapping staged writable glyph ranges; 102 unstaged canonical source records, of which 82 are independent parseable text starts after excluding physically nested/unsafe fragments.

## Deliverable and safe next step

Created `tools/probe_quiz_script_grammar_064.py`. It:

- requires the exact 2MiB clean Japanese SFC SHA;
- classifies all **409** native `81 6F 00` transitions by their observed surrounding bytes, with an immutable expected-count assertion;
- asserts the intact bank-end `FF` span and exposes it as unapproved;
- emits a read-only JSON report, never an IPS or edited ROM.

Example from the game project root:

```bash
python tools/probe_quiz_script_grammar_064.py clean-japanese.sfc --report quiz064_script_grammar.json
```

Static category totals above were independently reproduced by local raw-ROM analysis. The source file was committed to GitHub, but **no fully integrated 061 Vietnamese game build, runtime menu navigation or SNES emulation was performed**. Avoid calling this a complete pointer-tracing or relocation implementation.

To proceed with *genuine* full-name expansion: inspect game code that enters/advances these records; establish exact command semantics for ordinary, intro and special footer types; identify and test any actual pointer/branch table; then perform a reversible relocated-text experiment in an emulator, including selected answer highlighting. Leave `Rolls-Royce`, `Hanawa Kazuhiko` and other long proper names intact in canonical translation meanwhile.

**Main build blocker remains the same:** original checkpoint043 clean-ROM IPS (SHA256 `d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50`) is still unavailable as readable raw bytes. Library ZIP metadata alone cannot supply it. The safe plan is to combine future complete patches **only when exact 043 bytes and emulator test path are available**; no ROM or copyrighted font files are to be committed/distributed.
