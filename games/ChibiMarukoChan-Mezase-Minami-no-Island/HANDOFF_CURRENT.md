# HANDOFF CURRENT — Chibi Maruko-chan SNES Việt hóa

Updated: 2026-09-16 +07
Branch: `chibi-maruko-bootstrap-01`
Repo: `ronvotri/Viet-Hoa-SNES`

## Current milestone

Bootstrap / Reverse 001 is complete statically.

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

Direct CP932/Shift-JIS text exists in ROM. Known exact examples are recorded in `translation/source/seed_known_strings.csv`.

A conservative scanner exists at `tools/scan_sjis_candidates.py`.

Reproducible candidate counts with current scanner:

- whole ROM: 2,274 candidate runs
- focused range `0x18000..0x34000`: 889 candidate runs

These are scanner candidates with false positives, NOT translation coverage.

## Unproven script facts

Frequently observed around text:

`00 0E xx 0F xx ...text... 81 6F 00`

Do not assign semantics to these control/marker bytes yet. Early writes must leave them untouched.

## Diagnostic probe 001

Tool: `tools/probe_ascii_menu.py`

It changes only:

- offset `0x2B7C9`
- source `メロディーありでスタート`
- exact 24-byte source span
- replacement `BAT DAU CO NHAC` padded within the same span

Static gates already passed locally:

- exact clean ROM: PASS
- source identity: PASS
- field fit: PASS
- dry-run: PASS
- build: PASS
- post-build checksum: PASS

Diagnostic build hashes from the canonical clean ROM:

- SHA-1 `40841562bd8e3ae113ed77145a9e8d28261d710a`
- SHA-256 `7ed3d93e565e2d50eb09eff29b4bae174a2147ce859d9880db992aad739a7cf8`

Probe 001 was inconvenient to reach in runtime, so it is superseded as the preferred visible test by probe 002. No Runtime PASS is claimed for probe 001.

## Visible menu runtime target confirmed by user screenshot

The immediately reachable main menu contains these direct CP932 strings:

- `0x28818` `ストーリーモード` → meaning-first Vietnamese: `Chế độ Cốt truyện`
- `0x2882E` `対戦モード` → `Đối kháng`
- `0x2883C` `チーム対戦モード` → `Đấu đội`
- `0x28852` `まるこＱ` → `Maruko Q`
- `0x2885E` `まるこペイント` → `Vẽ cùng Maruko`
- `0x28870` `まるこみくじ` → `Bói quẻ Maruko`
- `0x28880` `針切カラオケ` → compact meaning target currently `Karaoke`
- `0x28892` `サウンド` → `Âm thanh`
- `0x288A2` `ステレオ` → `Stereo`
- `0x288B2` `モノラル` → `Mono`

The pink heading `どれにする？` is visible as `Chọn gì đây?`, but has NOT been found as a direct CP932 string yet. Treat it as graphic/tilemap/other encoding until proven.

## Diagnostic probe 002 — current preferred runtime test

Tool: `tools/probe_visible_menu_002.py`

It starts from the exact CLEAN ROM and changes only the 10 direct text spans above. Surrounding control/terminator bytes are untouched.

ASCII runtime candidates:

- `COT TRUYEN`
- `DOI KHANG`
- `DAU DOI`
- `MARUKO Q`
- `VE MARUKO`
- `BOI MARUKO`
- `KARAOKE`
- `AM THANH`
- `STEREO`
- `MONO`

Static gates:

- exact clean ROM: PASS
- exact source identity: 10/10 PASS
- field fit: 10/10 PASS
- overlap count: 0
- dry-run: PASS
- build: PASS
- post-build checksum: PASS

Probe 002 build:

- checksum `0xF03D`
- complement `0x0FC2`
- SHA-1 `6e4df69bd76cc2fe2942f46d4f29d3b144706d62`
- SHA-256 `098b3ab3af8857fb858e4881727d7a7382edcbf83dbca3f9dfd8ad0d6b348d42`

**Runtime PASS claim: NO.**

## Next task

User should boot probe 002 and screenshot this same menu.

Interpretation:

- If the ASCII labels render correctly: ASCII renderer support is proven for this visible menu path. Then establish width/spacing and design one Vietnamese-glyph/codepage probe with accents.
- If labels render as garbage/blank: reverse this menu renderer/font mapping before any bulk text patching.
- If only some labels work: compare the exact failing spans and nearby control bytes before generalizing.

After renderer proof, reverse pointer/field ownership and control semantics before building a bulk exact-offset overlay.

## Frozen workflow rule

Use Gaia Master-style guardrails, not Gaia Master hardware assumptions.

Do not call Runtime PASS without gameplay screenshot evidence.
