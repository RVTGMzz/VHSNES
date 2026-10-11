# Chibi Maruko-chan SNES — G2 rules 055 and Quiz 054 editorial QA

Date: 2026-10-11. Branch: `chibi-maruko-bootstrap-01`.

## Actual work on user-supplied ROM

Validated exact Japanese headerless ROM (2,097,152 bytes, SHA256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`).

**Quiz 054:** edited 12 awkward, misleading or incomplete compact Vietnamese Quiz captions in the existing 54-record manifest. Corrected the Fujiki/Nagasawa relationship, Made Hideji's fatherly role clear, and joined the Maruko/Tomozo chocolate and sushi/pension stories more naturally across original SNES text frames. All 54 records are now directly tied to original Japanese scanner text and untouched complete canonical Vietnamese `vi_full` across three source CSV files; runtime variants are separate. After the changes, reran the independent clean-ROM overlay validator on the actual source:

- 54/54 original Quiz fields, 123 native physical line spans and 123 original `816F` separators verified
- 2,642 permitted text bytes / 2,636 changed text bytes
- 3,279B / 127-record text-only QA IPS SHA256 `792b0ccb6f60b77d6cc93f7ec91f87006e9d17a2c723344379df96731faf7ee9`
- Source-text overlay ROM SHA256 `6df189b94951cafc23cec6bb90fccbf4f1a66307b545f35619d708debd7aa26b`
- Independent clean-based IPS replay matched the original 2MiB experimental image exactly
- The guarded 054 builder now requires both the exact source-overlay IPS fingerprint and all 54 canonical Japanese/full Vietnamese source references before merging

**G2 rules 055:** real original Japanese content at `0x1E307`, `0x1E323` and `0x1E337` was given complete, static Vietnamese captions:

| Original Japanese | Runtime Vietnamese | Original slot |
|---|---|---|
| `ルールをせつめいするよ` | `Luật chơi!` | 11 two-byte cells |
| `・２本先取だよ` | `Thắng 2` | 7 two-byte cells |
| `・ゲームの時間は勝つまでだよ` | `Tới khi thắng` | 14 two-byte cells |

The Japanese `・` marker is normal CP932 glyph punctuation, not an engine control. Both bullet glyphs are replaced with readable Vietnamese characters, while original ASCII indentation and the three `816F` control delimiters remain *byte-identical*. The original full Vietnamese meaning is separately preserved in `translation/runtime/g2_rules_content_first_055.json`; the runtime captions are shorter due to physical on-screen slots.

Independent real-clean-ROM physical overlay QA:

- Three original G2 fields exactly match original CP932, totaling 64 writable source bytes
- 64 changed bytes, 3 native line markers unchanged
- 87-byte / 3-record text-only IPS with SHA256 `b2372df59679573167cd82f0c95b2c30de24eb088b323d91a2b4a8d72f494f04`
- Source-only translated overlay ROM SHA256 `1da12b5de13f06e1902690274709111bcfd0a510c2170a5bd0abd994ea362569`
- Independent IPS replay PASS

The two QA overlays are **not playable standalone game localization patches**. No SNES checksum is rewritten in these QA overlays and no Vietnamese font is present in original Japanese ROM. They are not distributed. The historical checkpoint043 patch is still unavailable as extractable raw bytes. A fully integrated 055 ROM **has not been constructed or tested in an emulator**.

## Source files and final build path

- `translation/runtime/quiz_content_first_54_054.json` — 54 contextual Quiz captions, source links, preserved full `vi_full` and refined editorial text
- `tools/build_content_first_054_quiz_54.py` — now pins independent clean-ROM physical overlay fingerprint and validates canonical sources
- `translation/runtime/g2_rules_content_first_055.json` — complete 3-rule source/slot/font mapping
- `tools/build_content_first_055_g2_rules.py` — guarded 054-ROM source checks, old V2 glyph assignment, immutable native `816F`, IPS/checksum replay
- `tools/rebuild_content_first_055_full_chain.py` — rebuild through 055 in one pass from clean ROM + exact 043 clean-ROM IPS, keep intermediate ROMs in memory only

Run when checkpoint043 IPS bytes are available as an *accessible attachment*:

```bash
python tools/rebuild_content_first_055_full_chain.py clean.sfc exact-043-clean.ips --ips final-055.ips --report final-055-qa.json --allow-untested
```

Never commit or redistribute Nintendo/game ROM images or font binaries. Next: verify combined patch from exact pinned source, then continue Fortune shortfall (6 physical exceptions), remaining long Quiz layout expansion and G3 end/result artwork; finish with **real in-emulator** screens, not static-only claims.
