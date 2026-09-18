# G0 DMA Source Trace 002

Updated: 2026-09-18 +07

This checkpoint extends G0 title reverse from "where is DMA happening?" to "what ROM source does that DMA appear to read?".

No ROM is modified.

## New tools

### 1. DMA source reconstruction

`tools/reconstruct_dma_sources.py`

Purpose:

- find `STA $420B` MDMA triggers;
- look backward for DMA channel setup;
- conservatively reconstruct:
  - A1T source address;
  - A1B source bank;
  - DAS transfer size;
  - BBAD destination;
  - DMAP mode;
- map reconstructed LoROM CPU sources back to file offsets.

Accumulator width is only considered proven when local `REP/SEP` evidence establishes M=8 or M=16.

Unknown-width cases are downgraded rather than silently guessed.

### 2. G0 boot/DMA correlator

`tools/correlate_g0_dma_sources.py`

Inputs:

- CSV from `trace_g0_title_boot.py`;
- CSV from `reconstruct_dma_sources.py`.

The correlator prioritizes transfers with:

1. proximity to a high-scoring boot/title setup window;
2. higher reconstruction confidence;
3. BBAD `0x18` / `0x19` consistent with VRAM data destination;
4. a source pointer that maps into the canonical ROM;
5. transfer size aligned to possible 2bpp or 4bpp tile counts.

For tile-aligned candidates it prints ready-to-run commands for:

`tools/render_snes_graphics_probe.py`

This creates a direct pipeline from boot trace to visual candidate proof.

## Static validation

Local development checks:

- `reconstruct_dma_sources.py` Python compile: **PASS**
- synthetic M-width tracking: **PASS**
- synthetic DMA0 A1T/A1B/DAS reconstruction: **PASS**
- synthetic source `$85:9000 -> file 0x29000`: **PASS**
- synthetic transfer size `0x0200`: **PASS**
- `correlate_g0_dma_sources.py` Python compile: **PASS**
- synthetic boot-window + VRAM DMA ranking: **PASS**
- synthetic 2bpp hypothesis generation: **PASS**
- synthetic 4bpp hypothesis generation: **PASS**

## Intended G0 pipeline

From the game directory:

```bash
python tools/trace_g0_title_boot.py clean.sfc \
  --report reports/generated/g0_title_boot_trace.txt \
  --csv reports/generated/g0_title_boot_trace.csv

python tools/reconstruct_dma_sources.py clean.sfc \
  --report reports/generated/g0_dma_sources.txt \
  --csv reports/generated/g0_dma_sources.csv

python tools/correlate_g0_dma_sources.py \
  reports/generated/g0_title_boot_trace.csv \
  reports/generated/g0_dma_sources.csv \
  --rom-name clean.sfc \
  > reports/generated/g0_boot_dma_correlation.txt
```

Then render only the highest-value source candidates with the generated commands.

## Important limits

This is still heuristic reverse infrastructure.

A reconstructed DMA source is not automatically the title asset because:

- DMA may upload palettes, tilemaps, unrelated boot graphics, or shared system data;
- the nearest immediate write may not be the true value source in more complex routines;
- fixed-opcode scanning is not a full width-aware 65816 disassembly;
- title graphics may be compressed into WRAM before VRAM upload.

If the top candidates do not decode into recognizable title artwork, the next branch is:

`ROM source -> decompressor / WRAM staging -> VRAM DMA`

rather than guessing another ROM offset.

## Proof gate before G0 write

Required chain:

`reset/title setup -> DMA setup -> source reconstruction -> decoded graphics/tilemap -> visible title identity`

Only after that should the project allocate/redraw:

- **Chibi Maruko-chan**
- **Tiến tới đảo phương Nam!!**
- **Việt hóa bởi VôtriValley**

while preserving original publisher/copyright attribution.

## Current status

- G0 language wording: **FROZEN**
- boot reset anchor: **PROVEN**
- boot tracer: **STATIC PASS**
- DMA source reconstruction: **STATIC PASS**
- boot/DMA correlator: **STATIC PASS**
- graphics renderer: **STATIC PASS**
- real clean-ROM execution: **NOT RUN in active runtime**
- actual G0 asset path: **UNPROVEN**
- G0 ROM write: **NO**
- Runtime PASS: **NO**
