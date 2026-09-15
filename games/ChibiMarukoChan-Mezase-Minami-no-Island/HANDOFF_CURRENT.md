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

Static gates passed:

- clean ROM identity: PASS
- source identity: 10/10 PASS
- field fit: 10/10 PASS
- overlap: 0
- checksum: PASS

Runtime evidence from user screenshot:

- game reaches the Konami copyright screen
- game then freezes before the normal menu

Therefore:

**Probe 002 runtime result: FAIL.**

Do NOT use raw 1-byte ASCII for bulk menu/text patching.

The strongest current hypothesis is that this script/renderer path consumes text in 2-byte units or otherwise treats raw ASCII bytes differently, causing parser/renderer desynchronization. This is a hypothesis from runtime evidence, not yet a proven complete text-engine specification.

## Probe 003 — current next runtime test

`tools/probe_visible_menu_003_2byte.py`

Purpose: isolate the 1-byte-vs-2-byte hypothesis with minimum blast radius.

Changes only the first menu field:

- offset: `0x28818`
- source: `ストーリーモード`
- exact source length: 16 bytes / 8 two-byte units
- replacement: `ＴＥＳＴ１２３４`
- replacement length: 16 bytes / 8 CP932 two-byte units

No surrounding control/terminator bytes are changed. All other menu strings remain original Japanese.

Static build from canonical clean ROM:

- checksum `0x10D1`
- complement `0xEF2E`
- SHA-1 `71c5b6369668bf3092f5e11f4202143392c68e30`
- SHA-256 `0fb8ea0791879f4d2548d7777f2664d9f0bb4285d8efc927d4072f9e876cfa4d`
- changed ROM spans only: header checksum/complement and `0x28818..0x28827`
- Runtime PASS claim: NO

Interpretation:

- If Probe 003 boots and shows `ＴＥＳＴ１２３４`, the 2-byte full-width route is strongly validated for this menu path.
- If it boots but shows unexpected glyphs, reverse the game's glyph mapping/font table next.
- If it still freezes, the failure is not explained merely by raw ASCII width; inspect source ownership, parser controls, or checksum-sensitive/game logic before more text writes.

## Frozen workflow rule

Use Gaia Master-style guardrails, not Gaia Master hardware assumptions.

Do not call Runtime PASS without gameplay screenshot evidence.
