# G0 Boot / Title Trace 001

Updated: 2026-09-18 +07

Target screen:

- retail title / intro shown immediately after startup;
- visible Japanese title: `ちびまる子ちゃん めざせ！南のアイランド！！`;
- Vietnamese title target:
  - **Chibi Maruko-chan**
  - **Tiến tới đảo phương Nam!!**
- added localization credit:
  - **Việt hóa bởi VôtriValley**

This checkpoint adds reverse infrastructure only. It does **not** claim a proven title asset offset and does not modify a ROM.

## Why G0 needs its own path

The title screen is expected to be a graphics-heavy boot screen and must not be assumed to use the proven 12x12 menu text renderer.

A useful trace should start from the actual SNES reset path, then rank boot-near routines that configure:

- BG mode;
- BG tilemap base;
- BG tile-data base;
- VRAM address/data;
- DMA source/destination registers;
- MDMA trigger.

## Proven reset anchor

Existing clean-ROM reverse notes already establish:

- LoROM header: file `0x7FC0`;
- reset vector: `0xFF90`;
- mapped reset entry file offset: `0x7F90`;
- first opcode at reset entry: `CLC` / `0x18`.

## New tool

Added:

`tools/trace_g0_title_boot.py`

The tool is strictly read-only and uses the exact clean-ROM gate from `rom_common.py`.

It:

1. reads the real reset vector from the SNES header;
2. maps the reset entry to ROM;
3. expands fixed-size JSL/JML/JSR/JMP candidates in several generations;
4. retains caller/depth metadata so heuristic pattern hits are not confused with proven execution;
5. scans those boot-expanded windows for stores to:
   - `$2105` BGMODE
   - `$2107..$210A` BG tilemap bases
   - `$210B..$210C` BG tile-data bases
   - `$2115` VMAIN
   - `$2116` VMADD
   - `$2118..$2119` VRAM data
   - `$212C..$212D` main/sub-screen layer enable
   - `$420B` MDMAEN
   - DMA channel registers `$4300..$4376`;
6. scores boot-near windows by coherent BG + VRAM + DMA activity;
7. near MDMA triggers, reports LoROM-looking 24-bit literals as **source pointer candidates only**.

The control-flow expansion is deliberately a fixed-opcode pattern tracer, **not** a width-aware 65816 disassembler.

## Static validation

Local development checks:

- Python compile: **PASS**
- reset `$00:FF90 -> file 0x7F90`: **PASS**
- mirrored `$80:FF90 -> file 0x7F90`: **PASS**
- synthetic boot JSL expansion: **PASS**
- synthetic `STA $2116` detection: **PASS**
- synthetic `STA $420B` detection: **PASS**

The commercial clean ROM was not available in the active runtime, so no real G0 trace report is claimed yet.

## Intended invocation

From the game directory:

```bash
python tools/trace_g0_title_boot.py "path/to/clean.sfc" \
  --report reports/generated/g0_title_boot_trace.txt \
  --csv reports/generated/g0_title_boot_trace.csv
```

Expected gate:

```text
mode=READ_ONLY
clean_rom_contract=PASS
runtime_claim=NO
```

## Promotion gate before a G0 graphics write

A top-ranked boot routine is not enough.

Before modifying title graphics, prove:

`reset/title setup -> coherent BG/VRAM/DMA routine -> DMA source pointer -> decoded tile/tilemap asset -> visible title artwork`

Then independently bound:

- source tile span;
- tilemap span;
- palette dependencies if any;
- free/replaceable tile capacity for the Vietnamese redraw;
- safe placement for **Việt hóa bởi VôtriValley**;
- preservation of original publisher/copyright attribution.

## Current status

- G0 wording: **FROZEN**
- reset anchor: **PROVEN**
- G0 tracer static tests: **PASS**
- actual title asset path: **UNPROVEN**
- G0 ROM write: **NO**
- G0 Runtime PASS: **NO**
- Build 035 Runtime PASS: **NO**
