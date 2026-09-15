# HANDOFF CURRENT — Chibi Maruko-chan SNES Việt hóa

Updated: 2026-09-16 +07
Branch: `chibi-maruko-bootstrap-01`
Repo: `ronvotri/Viet-Hoa-SNES`

## Current milestone

Bootstrap / Reverse 001 is complete statically. Visible-menu renderer reverse is active.

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

Raw 1-byte ASCII across visible menu fields caused runtime freeze before the normal menu.

Conclusion: do NOT use raw 1-byte ASCII for bulk menu/text patching.

## Probe 003 — BOOT PASS / GLYPH IDENTITY FAIL

`tools/probe_visible_menu_003_2byte.py`

Changed only first menu field to CP932 full-width `ＴＥＳＴ１２３４`, preserving 8 two-byte units.

Runtime screenshot:

- game boots to menu: PASS
- framing/position preserved
- intended full-width `Ｅ` (`82 64`) displayed as a zero/circle-like glyph, not `E`

Conclusion: two-byte framing is safe for this path, but standard CP932 glyph identity is not complete.

## Probe 004 — RUNTIME PASS FOR COVERAGE MAP / INCOMPLETE LATIN FONT

`tools/probe_visible_menu_004_fullwidth_map.py`

Runtime screenshot observed the following intended A–Z/digit probe:

- intended `ＡＢＣＤＥＦＧＨ` → visible approximately `AB000000`
- intended `ＩＪＫＬＭ` → visible approximately `I0KLM`
- intended `ＮＯＰＱＲＳＴＵ` → visible approximately `00PQRST0`
- intended `ＶＷＸＹ` → visible approximately `V000`
- intended `Ｚ０１２３４５` → visible approximately `0012345`
- intended `６７８９ＡＢ` → visible `6789AB`

Here `0` means the same round glyph as the game's full-width digit zero, not a missing/blank pixel.

This proves many CP932 full-width Latin codepoints are structurally accepted but map to glyph-id zero rather than dedicated Latin glyphs.

## Major static discovery — CP932 0x82xx codepoint -> glyph-id table

A 16-bit little-endian mapping table has been identified in the CLEAN ROM.

For the `0x82xx` range used by full-width digits/Latin/hiragana:

- base entry for CP932 `0x824F` (full-width `０`) is file offset `0x29880`
- entry address formula for trail byte `t` in this range:

```text
entry = 0x29880 + (t - 0x4F) * 2
```

Examples from CLEAN ROM:

- `０` `0x824F` -> glyph-id `0x0000`
- `１` `0x8250` -> `0x0001`
- ...
- `９` `0x8258` -> `0x0009`
- `Ａ` `0x8260` -> `0x0517`
- `Ｂ` `0x8261` -> `0x0705`
- `Ｃ` `0x8262` -> `0x0000`
- `Ｅ` `0x8264` -> `0x0000`
- `Ｉ` `0x8268` -> `0x074B`
- `Ｋ` `0x826A` -> `0x0519`
- `Ｌ` `0x826B` -> `0x074C`
- `Ｍ` `0x826C` -> `0x0814`
- `Ｏ` `0x826E` -> `0x051A`
- `Ｐ` `0x826F` -> `0x0815`
- `Ｑ` `0x8270` -> `0x0216`
- `Ｒ` `0x8271` -> `0x0518`
- `Ｓ` `0x8272` -> `0x020D`
- `Ｔ` `0x8273` -> `0x0516`
- `Ｕ` `0x8274` -> `0x0000`
- `Ｖ` `0x8275` -> `0x020C`
- unsupported letters seen in Probe 004 also map to `0x0000`

Critical interpretation:

`0x0000` is not merely a generic null/failure value. Because full-width digit `０` itself maps to glyph-id `0x0000`, unsupported Latin letters resolve to the digit-zero glyph, exactly matching the Probe 004 screenshot.

This is strong static+runtime correlation, but the table-control relationship should still be proven with one targeted runtime mutation before treating it as frozen architecture.

Additional supporting pattern:

The credits string `ＴＡＲＡＫＯ` exists in source, and the table assigns its needed glyphs in a compact group:

- `Ｔ` -> `0x0516`
- `Ａ` -> `0x0517`
- `Ｒ` -> `0x0518`
- `Ｋ` -> `0x0519`
- `Ｏ` -> `0x051A`

This strongly suggests glyph IDs were allocated from the game's actual authored character inventory rather than a complete CP932 Latin font.

## Probe 005 — current next runtime test: mapping-table proof

`tools/probe_visible_menu_005_map_entry.py`

Purpose: prove that the discovered table directly controls the visible menu glyph selection without touching font bitmap data yet.

Changes from exact CLEAN ROM only:

1. first menu field at `0x28818`: `ストーリーモード` -> full-width `ＴＥＳＴ１２３４` (same 16-byte / 8-unit span)
2. mapping entry for full-width `Ｅ` at `0x298AA`: `0x0000` -> `0x0517`, which is the proven glyph-id used by full-width `Ａ`
3. normal SNES checksum/complement update

Expected runtime first line if mapping-table hypothesis is correct:

```text
TAST1234
```

The `E` position should deliberately render as `A`.

Static build gates:

- clean ROM identity: PASS
- text source identity: PASS
- A mapping identity: `0x0517` PASS
- E mapping identity before write: `0x0000` PASS
- dry-run: PASS
- checksum: PASS
- checksum `0x10ED`
- complement `0xEF12`
- SHA-1 `c2f830859ce4925acf76a7aa4c1bf22ba0b838bb`
- SHA-256 `36f106bd02022afa74a3c0329250ca7fbbf08bcc6f1081c8a7a95c90aa3ccdfc`

**Runtime PASS claim: NO until screenshot.**

## Next architecture task after Probe 005

If `TAST1234` appears exactly as predicted:

1. freeze the 0x82xx mapping-table behavior as runtime-proven for this renderer path;
2. reverse the glyph-id -> bitmap/font asset storage;
3. identify whether there are unused glyph slots or safely repurposable glyph slots;
4. create ONE custom Vietnamese glyph probe (for example `Ế` or `Đ`) using a chosen 2-byte code and mapping entry;
5. only after that works, define the Vietnamese codepage and expand translation.

Do not brute-force more alphabet tests unless needed. The missing-letter mechanism is now explained by the mapping table.

## Frozen workflow rule

Use Gaia Master-style guardrails, not Gaia Master hardware assumptions.

Do not call Runtime PASS without gameplay screenshot evidence.
