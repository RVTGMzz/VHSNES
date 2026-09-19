# G1 Label Asset Proof 009

Updated: 2026-09-19 +07

This checkpoint records the first proven retail asset source and successful runtime replacement for the Story-mode Start/Password labels.

## Repository

- repo: `RVTGMzz/VHSNES`
- branch: `chibi-maruko-bootstrap-01`

## Proven retail route

The previously proven Story entry route remains:

`main menu Story index 0 -> route $A0 -> $70=$A0 -> $80:D328 -> $88:F5F1 -> $85:E959`

The Story entry initializer uses package:

`$82:AF23`

The visible Start/Password label graphics were isolated to **record #8** of this package.

## Exact asset

- package: `$82:AF23`
- record: **#8**
- compressed source: `$97:F95E`
- file offset: `0x0BF95E`
- destination VRAM: `$7800`
- original compressed span: `0x1B4` bytes
- decompressed output: `0x3E0` bytes

This is the retail visible asset used by the Story Start/Password screen, not QA/debug descriptor prose.

## Vietnamese replacement

Frozen labels:

- `はじめから` -> **Bắt đầu**
- `パスワード` -> **Mật khẩu**

The Vietnamese asset was reconstructed in-place through the same resource path.

Fit facts:

- original packed size: `0x1B4`
- Vietnamese packed size: `0x16A`
- in-place fit: **PASS**
- round-trip reconstruction: **PASS**

The heading `どれにする？` is a **separate target**. It was not silently folded into this asset proof and remains outside the Start/Password replacement claim.

## Runtime probe

Probe artifact:

`G1_LABEL_PROBE_001_CLEAN.sfc`

Static build facts:

- changed bytes: **360**
- SHA-1: `904435c61153fd7f41649ab25e8f50318d3ec72f`
- SHA-256: `16c2975f431edc74754b8b6ad9272b78e4cc37852df653d1581094efb5d15edb`
- checksum: `0x28CA`
- complement: `0xD735`

User gameplay/screenshot verification confirmed the visible labels render as:

- **Bắt đầu**
- **Mật khẩu**

Therefore:

- G1 exact label asset identity: **STATIC PASS**
- bounded in-place replacement: **STATIC PASS**
- Start/Password runtime render: **RUNTIME PASS**
- `どれにする？` replacement: **NOT INCLUDED**
- whole graphics track Runtime PASS: **NO**

## Important correction

Do not return to broad G1 shape scanning.

The authoritative retail source for the two visible choice labels is now:

`$82:AF23 record #8 -> $97:F95E -> VRAM $7800`

Do not patch the descriptor/debug block around `0x286B4` and claim a retail fix.

## Next target

Move to G2:

`今からやるよ` -> **Bắt đầu thôi!**

The descriptor at file `0x286EA` remains a QA/debug naming clue only. Trace the actual retail execution/resource path before any write.
