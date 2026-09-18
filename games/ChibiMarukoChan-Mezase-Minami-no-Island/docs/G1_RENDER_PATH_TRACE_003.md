# G1 Render Path Trace 003 — infrastructure checkpoint

Updated: 2026-09-18 +07

Target batch remains:

- `どれにする？` -> **Chọn gì đây?**
- `はじめから` -> **Bắt đầu**
- `パスワード` -> **Mật khẩu**

This checkpoint does **not** claim that the visible G1 asset offset has been found yet.

## Why this step exists

The previous heading audits already rejected the easy storage models:

- contiguous CP932;
- contiguous 16-bit glyph IDs;
- sparse/interleaved CP932 or glyph IDs with useful gap sizes;
- simple masked 16-bit tilemap runs;
- tiny nearby low-byte placement structures.

The descriptor/debug prose at `0x286B4..0x287FC` is still explicitly out of scope for patching. It names the screens but is not the visible retail artwork.

The next useful evidence must therefore connect the screen setup to one of these real render paths:

1. the proven text renderer at file `0x28E7B` / CPU `$85:8E7B`;
2. a VRAM/DMA graphics upload;
3. a local/long pointer table leading to a tilemap or compressed asset;
4. another renderer proven by references rather than guessed offsets.

## New read-only tool

Added:

`tools/trace_g1_render_path.py`

The tool accepts only the exact canonical clean ROM through the existing `rom_common.require_clean_rom()` gate and does not write to the ROM.

It reports:

- file/CPU LoROM addresses for the known parser, renderer, menu and descriptor anchors;
- 16-bit same-bank and 24-bit references to those anchors;
- exact CP932 occurrences for the three G1 strings, with the reminder that descriptor-prose hits are not retail asset proof;
- every direct `JSL` call to the proven parser and renderer;
- bank `$85` stores to high-value VRAM/PPU/DMA registers:
  - `$2115`
  - `$2116`
  - `$2118`
  - `$2119`
  - `$420B`
  - DMA channel registers `$4300..$4376`;
- nearby fixed-size control-flow targets around those VRAM/DMA sites;
- candidate 16-bit local pointer runs in bank `$85`;
- candidate 24-bit ROM-pointer runs in bank `$85`;
- a compact G1 triage summary.

The scanner is deliberately a pattern/xref tracer, not a full 65816 disassembler. Unknown M/X width state is therefore not guessed.

## Intended invocation

From the game directory:

```bash
python tools/trace_g1_render_path.py "path/to/clean.sfc" \
  --report reports/generated/g1_render_path_trace.txt \
  --csv reports/generated/g1_render_path_trace.csv
```

Expected first gate:

```text
mode=READ_ONLY
clean_rom_contract=PASS
runtime_claim=NO
```

## Evidence needed before a G1 write

A candidate asset path is considered strong enough to patch only when at least one of the following is established:

- screen setup xref -> routine -> VRAM/DMA source pointer -> ROM asset;
- screen setup xref -> tilemap/pointer table -> ROM asset;
- alternate renderer callsite with a proven source table that reproduces the visible label;
- a source-asset decode that visually reproduces the target text and is reached by the screen setup path.

A visually plausible byte region without a proven path is not enough.

## Current limitation of this checkpoint

The current session did not have the canonical clean ROM or Build 035 binary available in the active runtime, and ROMs are intentionally not committed to GitHub.

Therefore:

- the new tracer source is committed;
- syntax was checked locally;
- **no trace output is claimed yet**;
- **no asset offset is claimed yet**;
- **no G1 ROM write was made**;
- Build 035 remains **Runtime UNTESTED**;
- G1 remains **UNPATCHED / UNTESTED**.

## Next action

Run the tracer on the exact clean ROM, then correlate:

1. references to `descriptor_start_password` and `main_menu_text_first`;
2. direct calls to `$85:8E7B`;
3. nearest bank-`$85` VRAM/DMA setup;
4. pointer runs feeding those routines.

Only after the source asset pointer is proven should the Vietnamese G1 graphics layer be built on top of Build 035.
