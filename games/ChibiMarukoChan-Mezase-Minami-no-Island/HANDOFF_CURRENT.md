# HANDOFF CURRENT — Chibi Maruko-chan SNES Việt hóa

Updated: 2026-09-16 +07
Branch: `chibi-maruko-bootstrap-01`
Repo: `ronvotri/Viet-Hoa-SNES`

## Current milestone

Bootstrap / Reverse 001 is complete statically. Visible-menu reverse is now active.

### Canonical clean ROM

- size: `0x200000` (2 MiB)
- SHA-1: `08a2415362f69788ec76b1a36044dc1f1a5f2ea1`
- SHA-256: `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`
- internal title: `RS051 CHIBIMARUKOCHAN`
- header: LoROM / FastROM at file `0x7FC0`
- no copier header on canonical file
- stored/computed checksum: `0x1115`
- complement: `0xEEEA`

Never patch an unknown or already modified ROM.

## Proven text facts

Direct CP932/Shift-JIS-like text exists in ROM. Known exact examples are recorded in `translation/source/seed_known_strings.csv`.

A conservative scanner exists at `tools/scan_sjis_candidates.py`.

Reproducible candidate counts with current scanner:

- whole ROM: 2,274 candidate runs
- focused range `0x18000..0x34000`: 889 candidate runs

These are scanner candidates with false positives, NOT translation coverage.

## Unproven script facts

Frequently observed around text:

`00 0E xx 0F xx ...text... 81 6F 00`

Do not assign semantics to these control/marker bytes yet. Early writes must leave them untouched.

## Visible menu runtime target confirmed by screenshot

Direct source spans:

- `0x28818` `ストーリーモード` → `Chế độ Cốt truyện`
- `0x2882E` `対戦モード` → `Đối kháng`
- `0x2883C` `チーム対戦モード` → `Đấu đội`
- `0x28852` `まるこＱ` → `Maruko Q`
- `0x2885E` `まるこペイント` → `Vẽ cùng Maruko`
- `0x28870` `まるこみくじ` → `Bói quẻ Maruko`
- `0x28880` `針切カラオケ` → compact target `Karaoke`
- `0x28892` `サウンド` → `Âm thanh`
- `0x288A2` `ステレオ` → `Stereo`
- `0x288B2` `モノラル` → `Mono`

The pink heading `どれにする？` is visible as `Chọn gì đây?`, but has NOT been found as a direct CP932 string yet. Treat it as graphic/tilemap/other encoding until proven.

## Probe 001

`tools/probe_ascii_menu.py`

Single raw-ASCII probe at `0x2B7C9`. Static build PASS, but runtime location was inconvenient and no Runtime PASS was claimed.

## Probe 002 — RUNTIME FAIL

`tools/probe_visible_menu_002.py`

Probe 002 replaced all ten visible menu strings with raw 1-byte ASCII while preserving the original byte spans and surrounding control bytes.

Static gates passed, but runtime screenshot showed the game freezing at/after the Konami copyright screen before the normal menu.

Therefore:

**Probe 002 runtime result: FAIL.**

Do NOT use raw 1-byte ASCII for bulk menu/text patching.

## Probe 003 — BOOT PASS / GLYPH IDENTITY FAIL

`tools/probe_visible_menu_003_2byte.py`

Changed only first menu field:

- offset `0x28818`
- source `ストーリーモード`
- exact source length `16` bytes / `8` two-byte units
- replacement intended as CP932 full-width `ＴＥＳＴ１２３４`

Static build:

- checksum `0x10D1`
- complement `0xEF2E`
- SHA-1 `71c5b6369668bf3092f5e11f4202143392c68e30`
- SHA-256 `0fb8ea0791879f4d2548d7777f2664d9f0bb4285d8efc927d4072f9e876cfa4d`

Runtime screenshot evidence:

- game boots fully to the visible main menu: PASS
- the first line renders with correct field length/position and recognizable `T`, `S`, `T`, digits
- the intended full-width `Ｅ` (`CP932 82 64`) renders as an O/circle-like glyph rather than `E`

Conclusion:

- keeping the text field in 2-byte units avoids the Probe 002 crash for this path
- standard CP932 glyph identity is NOT valid for the whole full-width Latin range in this renderer/font
- do not assume `CP932 code -> expected Latin glyph` merely because the byte sequence is structurally accepted

This is not yet a final Runtime PASS for Vietnamese rendering. It is a runtime proof of safe 2-byte framing plus evidence of a custom/incomplete glyph mapping.

## Probe 004 — current next runtime test: full-width glyph map

`tools/probe_visible_menu_004_fullwidth_map.py`

Purpose: map the renderer's actual glyph results for the CP932 full-width Latin/digit code range without changing byte-unit counts.

It modifies only the first six visible menu fields, preserving exact two-byte unit counts:

- row 1 (8 units): `ＡＢＣＤＥＦＧＨ`
- row 2 (5 units): `ＩＪＫＬＭ`
- row 3 (8 units): `ＮＯＰＱＲＳＴＵ`
- row 4 (4 units): `ＶＷＸＹ`
- row 5 (7 units): `Ｚ０１２３４５`
- row 6 (6 units): `６７８９ＡＢ`

Rows 7–10 remain original Japanese.

Static gates from canonical clean ROM:

- clean source: PASS
- source identity: 6/6 PASS
- exact two-byte length preservation: PASS
- overlaps: 0
- dry-run: PASS
- post-build checksum: PASS
- checksum `0x0994`
- complement `0xF66B`
- SHA-1 `3eb93145e8243c35083cf0da9a0f79a9ed802810`
- SHA-256 `bc11554e22c8909b09e909c2508626830e94c7c791e4abb20da0d81437465d67`

**Runtime PASS claim: NO.**

Next evidence needed: one screenshot of Probe 004's same menu. Compare intended rows with displayed glyphs and record an observed code→glyph table. Then either:

1. reuse proven native glyph codes for a compact Latin base if enough letters exist, or
2. reverse/replace the font tiles and establish a Vietnamese 2-byte codepage.

Do not attempt bulk Vietnamese text until this glyph identity layer is mapped.

## Frozen workflow rule

Use Gaia Master-style guardrails, not Gaia Master hardware assumptions.

Do not call Runtime PASS without gameplay screenshot evidence.
