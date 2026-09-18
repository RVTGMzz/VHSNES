# G0 WRAM Staging Trace 003

Updated: 2026-09-18 +07

This checkpoint prepares the fallback path for title graphics that are not DMA'd directly from ROM.

## Why this path exists

A title screen may use:

`ROM/compressed data -> decompressor or block copy -> WRAM $7E/$7F -> VRAM DMA`

In that case, the DMA source reconstruction layer will correctly recover a WRAM source but cannot map it to a ROM file offset.

Do not treat that as failure and do not guess a ROM asset location.

## New tool

Added:

`tools/trace_wram_staging_candidates.py`

Input:

- exact canonical clean ROM;
- CSV from `tools/reconstruct_dma_sources.py`.

The tool selects DMA transfers whose source bank is:

- `$7E`
- `$7F`

and reports conservative candidates that may populate the same WRAM range:

1. exact 24-bit WRAM address literals;
2. `STA long` / `STA long,X` writes into the source span;
3. `MVN` / `MVP` block moves touching the same WRAM bank.

These are **staging/decompressor candidates**, not proven execution paths.

## Static validation

Local development checks:

- Python compile: **PASS**
- WRAM DMA source parse: **PASS**
- exact `$7E:9000` literal hit: **PASS**
- direct long-store hit: **PASS**
- block-move bank hit: **PASS**

## Intended fallback flow

If G0 DMA correlation yields a WRAM source:

```bash
python tools/trace_wram_staging_candidates.py \
  clean.sfc \
  reports/generated/g0_dma_sources.csv \
  > reports/generated/g0_wram_staging_trace.txt
```

Then inspect the highest-value candidate routines and prove:

`boot/title setup -> staging/decompressor -> WRAM source span -> VRAM DMA -> visible title`

## Limits

The tool intentionally does not claim to be a complete 65816 decompiler.

It can miss staging code that writes through:

- direct-page pointers;
- indirect indexed stores;
- complex decompressor loops;
- shared engine buffers whose start address is calculated dynamically.

If the conservative hits are weak, the next step is targeted disassembly/emulator trace around the proven WRAM DMA source rather than a broad ROM graphics scan.

## Current status

- direct-ROM G0 pipeline: **STATIC PASS**
- WRAM fallback pipeline: **STATIC PASS**
- canonical-ROM runtime execution: **NOT RUN in active runtime**
- actual title asset source: **UNPROVEN**
- G0 ROM write: **NO**
- Runtime PASS: **NO**
