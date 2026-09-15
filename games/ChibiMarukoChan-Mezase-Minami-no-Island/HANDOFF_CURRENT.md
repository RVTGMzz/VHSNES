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

Diagnostic IPS package generated from the exact clean ROM:

- IPS contains two diff spans only: checksum/complement at `0x7FDC` (4 bytes) and text field at `0x2B7C9` (24 bytes)
- IPS SHA-256: `e071a15b3ae65cb3157da4bb4654dd79ef63043945c8501449517cda6162b021`
- applying the IPS back to the canonical clean ROM reproduces the exact diagnostic build hashes above: PASS

**Runtime PASS claim: NO.**

## Next task

Highest-information next step is runtime evidence for probe 001.

Interpretation:

- If `BAT DAU CO NHAC` renders correctly: establish ASCII width/spacing, then design the Vietnamese glyph/codepage experiment without touching unrelated text.
- If it renders as garbage/blank: reverse the text renderer/font mapping first; do not bulk-patch no-diacritic text.
- If the screen is not easily reachable: pick a more visible exact Shift-JIS phrase, but keep the one-probe rule.

After renderer proof, reverse pointer/field ownership and control semantics before building a bulk exact-offset overlay.

## Frozen workflow rule

Use Gaia Master-style guardrails, not Gaia Master hardware assumptions.

Do not call Runtime PASS without gameplay screenshot evidence.
