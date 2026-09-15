# Reverse notes 001 — bootstrap

Date: 2026-09-16 (+07)

## Clean ROM validation

The uploaded ROM passes the exact canonical contract. Its stored checksum `0x1115` equals the computed checksum and `0x1115 + 0xEEEA = 0xFFFF`.

Header evidence:

- LoROM header candidate at file `0x7FC0` is coherent.
- HiROM candidate at `0xFFC0` is filler (`0xFF`).
- map mode byte is `0x30`, consistent with FastROM-capable LoROM.
- reset vector is `0xFF90`; the first opcode at the mapped reset location is `0x18` (`CLC`), a plausible reset entry.

## Direct Japanese text: proven

Exact CP932 encodings occur literally in ROM:

| File offset | Source | Bytes |
|---:|---|---:|
| `0x2B7C9` | `メロディーありでスタート` | 24 |
| `0x2B7EF` | `メロディーなしでスタート` | 24 |
| `0x31CFB` | `スタートをおしてね` | 18 |
| `0x2C74B` | `ちびまる子ちゃん` | 16 |
| `0x2C76A` | `フルーツを食べてみて` | 20 |
| `0x2C79E` | `北に行こう` | 10 |
| `0x2C7C0` | `南に行こう` | 10 |
| `0x2C918` | `ゲームで開運です` | 16 |
| `0x31D14` | `クイズを続けますか？` | 20 |
| `0x31D3A` | `いいえ` | 6 |

This proves direct Shift-JIS exists. It does **not** prove that all game text is uncompressed or uses one renderer.

## Candidate scanner

`scan_sjis_candidates.py` deliberately emits candidates, not translations.

Current reproducible result with default threshold:

- whole ROM: `2,274` candidate runs;
- focused file range `0x18000..0x34000`: `889` candidate runs.

False positives still exist, especially in graphics/code/data, so these counts must never be called source coverage.

## Script/control observations

Text phrases are frequently surrounded by bytes such as:

```text
00 0E xx 0F xx ...text... 81 6F 00
```

`0x816F` is a valid CP932 code unit (`｛`) but appears frequently at display-text boundaries. It may be printable, a script marker, or interpreted specially by this engine. The semantics of `00`, `0E`, `0F`, `81 6F` and nearby parameters are **UNPROVEN** and must be preserved by early probes.

## First renderer probe

Prepared diagnostic:

- exact offset: `0x2B7C9`
- exact source: `メロディーありでスタート`
- exact source span: 24 bytes
- diagnostic replacement: ASCII `BAT DAU CO NHAC`, padded with ASCII spaces to the same 24-byte span
- control bytes before/after field: untouched
- SNES checksum/complement: regenerated after write

Local static proof:

- clean-source gate: PASS
- source identity at offset: PASS
- field fit: PASS
- dry-run: PASS
- build: PASS
- diagnostic output SHA-1: `40841562bd8e3ae113ed77145a9e8d28261d710a`
- diagnostic output SHA-256: `7ed3d93e565e2d50eb09eff29b4bae174a2147ce859d9880db992aad739a7cf8`
- Runtime PASS: **NO**

If this probe displays readable ASCII in-game, the next decision is whether an ASCII/custom one-byte Vietnamese path is viable. If it does not, reverse the renderer/font path before bulk translation packing.
