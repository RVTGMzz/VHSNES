# Chibi Maruko-chan SNES — Checkpoint 065: native 50-question / 150-answer Quiz atlas

Date: 2026-10-12. Branch: `chibi-maruko-bootstrap-01`.

## What the actual original SNES ROM establishes

Using the user-provided **headerless 2,097,152-byte original Japanese SFC**, exact SHA256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`, parsed the Quiz script area `0x31C00–0x36907` without modifying a byte. The previous read-only checkpoint064 found 355 ordinary, 4 extended and 50 special `816F 00` script transitions. This checkpoint aligns those 50 special transitions with the actual three-answer question blocks.

- **Exactly 50 original question blocks.**
- **Exactly 150 in-game answer text fields, three per question.** Each answer is preceded by the native `81 6F 00 0E 06 0F 12` sequence; the original answer starts immediately after these seven bytes.
- That native display-parameter pair occurs **151** times in the region, but the first occurrence is the startup confirmation `いいえ` (“No”). It is **not an answer to question #1**. Filtering it out produces exactly 3 choices in each of 50 question blocks. Crucial: never translate or count the startup “No” as a trivia answer.
- **150/150 real ROM answer addresses match canonical Quiz source CSV rows** across all eight CSVs; complete canonical Vietnamese `vi_full` is available for each.
- Cross-checking all nonduplicate Quiz runtime manifests (041, 047, 054, 057, 058, 059, 060, 061) gives **69/150 answer choices prepared as byte-scope translation candidates** and **81/150 choices remaining without runtime localization**, overwhelmingly long proper names and terms.
- The Quiz-wide count is still **279/381 canonical rows prepared, 102 unselected**. It includes descriptions, commentary, questions and answer choices. **Do not add 150 as new translations**—these are indexed existing original fields.

### Structural details relevant to safe expansion

| Native original ROM evidence | Count / location |
|---|---|
| Normal `81 6F 00 0E ?? 0F ??` transitions | 355 |
| Extended `81 6F 00 10 ?? 0E ?? 0F ??` | 4 |
| Special `81 6F 00` + paired footer records | 50 |
| `0E 06 0F 12` display prefixes | 151; 1 startup No + 150 answers |
| `0E 00 0F 0E` display prefixes | 99 |
| `0E 00 0F 08` display prefixes | 49 |
| `0E 00 0F 14` display prefixes | 48 |
| Special footer followed by next question starter `0E 00 0F 0A` | 49 |
| Final footer followed directly by unused `FF` space | 1 |
| Footer pairs identical in first six bytes | 49 |
| Footer pair with different initial six bytes | Question #37, near `0x35618` |

Each footer contains *two* eight-byte structures with `C6` and trailing zero and a two-byte secondary parameter after each. A useful preliminary association is one question block per paired-footer structure. **The semantics of these eight-byte records and the correct-answer encoding have not been reverse-engineered**; treating them as confirmed pointers or overwriting them would be unsafe.

Some verified canonical answer examples:

| Question | Choice 1 | Choice 2 | Choice 3 |
|---|---|---|---|
| #1, Momoe concert gift | `0x31DBD` かにカンとカンきり | `0x31DD6` きゅうりとツナカン | `0x31DEF` おさらとちくわ |
| #11, Kayoko's crush | `0x32D09` 杉山くん | `0x32D18` はまじ | `0x32D25` 中川くん |
| #28, a school-friend question | `0x346C3` まる子 | `0x346D0` きょう子ちゃん | `0x346E5` とし子ちゃん |
| #50, Maruko's candy shop | `0x367F3` みつや | `0x36800` ききょうや | `0x36811` まつや |

These answer addresses were derived from **real script delimiters and control pairs**, *not* guessed from ROM search text. Their canonical CSV rows were independently cross-checked against GitHub source. The full Japanese/Vietnamese pair and the source stage for each will be exported by the committed report generator.

## Reproducible read-only tooling

Committed `tools/build_quiz_answer_atlas_065.py` to do the following in a local checkout with the source SFC:

1. Validate exact clean ROM and canonical 381 CSV sources.
2. Verify the complete source-stage audit: 279 distinct offsets, no duplicate original offsets.
3. Parse 409 original `816F 00` control transitions and the 151 answer-style prefixes.
4. Infer **exactly three** answer fields in each of the 50 original blocks, explicitly skipping startup `いいえ`.
5. Assert that all 150 original answer addresses correspond to original Japanese/full Vietnamese source data, mark which 69 were prepared by previous stages and which 81 are pending.
6. Report 50 blocks with the original three Japanese choices, stable ROM offsets, complete canonical Vietnamese references, original two-byte glyph capacities and any already staged phase.
7. Fail closed if unexpected footer metadata or the special #37 footer changes.

Run:

```bash
python tools/build_quiz_answer_atlas_065.py clean.sfc --report quiz065_all_50_questions.json
```

**Validation scope:** Real original-ROM geometry/counts were calculated with independent Python and 150 canonical address matches cross-checked using live GitHub source records and all eight current staged manifests. The newly committed repo script has not yet run end-to-end inside a full clone with all files; it must be smoke-tested there before being considered a reproducible CI pass. It **does not write any game ROM, IPS or font data**.

## Why this advances the stalled localization

The remaining 102 canonical source rows are **not** 102 independent choices: this atlas shows 81 are actual still-untranslated answer alternatives, while the other 21 relate to narrative, prompts or scanner aliases. Future work can now attack all 50 question groups systematically, checking that names/answers remain distinguishable and correctly ordered.

Many alternative slots contain only 2–5 native Japanese double-byte cells, whereas full Vietnamese personal names or terms take more characters. **Do not** mark a fake shortened name as complete or arbitrarily use the adjacent 5,881-byte `FF` run. A genuinely new layout must first prove how script references and rendering work and pass emulator/selection highlight QA.

Historical clean ROM→043 IPS SHA `d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50` is still inaccessible as raw bytes, so **full integrated 061 (let alone later stages) has not been built**, and real SNES emulator testing remains pending. No unsupported “playable patch” should be offered.

**Progress remains 279/381 staged Quiz source IDs; 81 actual answer alternatives need runtime text work.** Also retain four Fortune long-text exceptions, G3 result/end graphics and later font QA. Per user: **content first, font last**, avoid tiny unplayable IPS downloads.
