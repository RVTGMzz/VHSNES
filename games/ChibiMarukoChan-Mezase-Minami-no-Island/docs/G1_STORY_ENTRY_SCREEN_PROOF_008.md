# G1 Story Entry Screen Proof 008

Updated: 2026-09-19 +07

This checkpoint records the first reproducible execution proof for the retail Story-mode Start/Password screen.

The exact source of the visible Japanese labels is still unresolved. Therefore this document separates **screen execution identity** from **label asset identity**.

## Repository

Current repository:

`RVTGMzz/VHSNES`

Branch:

`chibi-maruko-bootstrap-01`

## Clean-ROM contract

- size: `0x200000`
- SHA-1: `08a2415362f69788ec76b1a36044dc1f1a5f2ea1`
- SHA-256: `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`

## Main-menu Story execution path

The retail main menu initializer in bank `$84` opens the bank-`$85` menu text script at:

`$85:8814`

This script begins immediately before the visible `ストーリーモード` entry.

The main-menu selection variable is:

`$7E:2010`

Story is selection index:

`0`

After the menu returns, the core router indexes table:

`$80:D60B`

Entry 0 is:

`0x00A0`

The sequence setter at:

`$80:D717`

begins with:

`STA $70`

Therefore selecting Story produces:

`$70 = $00A0`

The sequence dispatch table at:

`$80:D184`

maps entry `$A0` to:

`$80:D328`

Handler `$80:D328` calls:

`JSL $88:F5F1`

This is the G1 Story-entry module.

## G1 module state machine

The module uses a five-entry state table at:

`$85:E975`

Entries:

1. `$85:E97F` — initializer / screen construction
2. `$85:EA09` — intro / staged animation
3. `$85:EAB8` — two-choice input state
4. `$85:EB84` — returns selected result
5. `$85:EB8C` — alternate result 3

### Selection variable

Input state `$85:EAB8` toggles:

`$1404`

with:

`EOR #$0001`

The two selection Y positions are:

- `0x00A8`
- `0x00B8`

### Result mapping

State `$85:EB84` performs:

`$1406 = $1404 + 1`

Therefore:

- selection 0 -> result `1`
- selection 1 -> result `2`

The alternate result state `$85:EB8C` returns:

`$1406 = 3`

The Story router immediately consumes `$1406` after `$88:F5F1` completes.

This proves that the G1 module is a real two-choice screen and returns the choice to the Story flow.

## G1 initializer resource calls

Initializer `$85:E97F` loads, in order:

- `$82:AF23`
- `$82:AA30`
- `$82:AA50`
- `$82:B364`

through the proven resource interpreter `$80:E255`.

### Package `$82:AF23`

This is a type-0 resource package.

Offline reconstruction produces the retail stage-curtain background seen on the Story entry screen.

Key package records include:

- BG graphics at VRAM `0x2000/0x21C0/0x22D0`
- tilemaps at VRAM `0x0000/0x1000/0x1400/0x4000`
- additional UI/object support data

The background render reproduces the distinctive stage curtain / framed stage composition.

Therefore:

**G1 stage/background identity = STATIC PASS**

### Package `$82:AA30`

Type-0, one record:

- VRAM `0x6000`
- source `$97:8CB7`
- decompressed output `0x1000`
- post-process flag set

The decoded 4bpp tile bank contains character/object fragments, not the visible menu labels.

### Package `$82:AA50`

Type-0, one record:

- VRAM `0x7000`
- source `$91:AA47`
- decompressed output `0x0A40`
- post-process flag set

The decoded 4bpp tile bank also contains character/object fragments, not the visible menu labels.

## Multi-command script `$82:B364`

`$82:B364` is not one ordinary type-0 package.

It begins with a repeated sequence of type-FF commands. The observed command shape is:

`FF + source24 + parameter16 + 80`

Seven such commands occur before the next inline command.

These resources decode as structured metasprite/object data rather than raw pixel graphics.

After the type-FF prefix, script execution reaches an inline type-0 package at:

`$82:B395`

The inline package contains six resource records, including:

- VRAM `0x2000` <- `$97:BA23`
- VRAM `0x3000` <- `$90:8003`
- VRAM `0x4000` <- `$9B:8000`
- VRAM `0x0000` <- `$A1:C37B`
- VRAM `0x5000` <- `$A1:C262`
- VRAM `0x6000` <- `$A0:CBB3`

Offline renders from this inline package show additional stage/object/silhouette assets, but still do not establish the source span of the visible `はじめから / パスワード` labels.

## Reproducible trace tool

Added:

`tools/trace_g1_story_entry_flow.py`

Usage:

```bash
python tools/trace_g1_story_entry_flow.py clean.sfc \
  --json reports/generated/g1_story_entry_flow.json
```

The tool validates:

- exact clean-ROM identity;
- main-menu Story text initialization;
- Story route entry `A0`;
- sequence dispatch to `$80:D328`;
- call to `$88:F5F1`;
- five-state G1 module table;
- selection toggle and result mapping;
- type-0 packages `AF23/AA30/AA50`;
- type-FF prefix in `B364`;
- inline type-0 package `B395`.

## Current G1 status

- retail Story -> G1 execution path: **STATIC PASS**
- G1 module identity: **STATIC PASS**
- stage/background asset identity: **STATIC PASS**
- G1 two-choice selection logic: **STATIC PASS**
- Start result -> `$1406=1`: **STATIC PASS**
- Password result -> `$1406=2`: **STATIC PASS**
- visible `どれにする？` label source: **UNPROVEN**
- visible `はじめから` label source: **UNPROVEN**
- visible `パスワード` label source: **UNPROVEN**
- graphics ROM write: **NO**
- Runtime PASS: **NO**

## Next reverse target

Do not resume broad shape scans.

Continue inside this proven G1 module and resolve the visible-label source by tracing the dynamic BG/OAM/text output generated during states `$85:E97F..$85:EAB8`.

Once the source representation is proven, prepare Vietnamese targets:

- `どれにする？` -> **Chọn gì đây?**
- `はじめから` -> **Bắt đầu**
- `パスワード` -> **Mật khẩu**

Do not patch descriptor/debug prose at `0x286B4..0x287FC`.
