# Graphics Asset Render Probe 001

Updated: 2026-09-18 +07

This checkpoint adds a read-only renderer for candidate SNES graphics ranges after a DMA/source pointer has been identified.

Tool:

`tools/render_snes_graphics_probe.py`

## Supported raw formats

- SNES planar **2bpp**
- SNES planar **4bpp**

Two render modes are available.

### Sequential tile contact sheet

Use this when the tracer proves a graphics source span but the tilemap is not yet known.

Example:

```bash
python tools/render_snes_graphics_probe.py clean.sfc reports/generated/g0_tiles.png \
  --bpp 4 \
  --gfx-offset 0x123456 \
  --scale 3 \
  --mask \
  tiles --count 256 --cols 16
```

### Raw 16-bit SNES tilemap render

Use this when both graphics and tilemap source offsets are proven.

Example:

```bash
python tools/render_snes_graphics_probe.py clean.sfc reports/generated/g0_title_map.png \
  --bpp 4 \
  --gfx-offset 0x123456 \
  --scale 3 \
  tilemap \
  --map-offset 0x127000 \
  --width 32 \
  --height 28
```

The tilemap decoder understands:

- tile index bits `0..9`;
- horizontal flip bit;
- vertical flip bit.

Palette priority/color selection is intentionally not used for proof at this stage. Output is grayscale or a binary occupancy mask, which is enough to determine whether a candidate source reproduces the visible logo/text silhouette.

## Dependency policy

The PNG writer uses only Python standard-library modules.

No Pillow dependency is required.

## Static validation

Local development checks:

- Python compile: **PASS**
- synthetic 2bpp decode: **PASS**
- synthetic 4bpp decode: **PASS**
- horizontal flip: **PASS**
- PNG writer/signature: **PASS**

## Proof rule

A visually recognizable contact sheet is useful evidence, but **not sufficient by itself**.

For G0/G1 promotion, the candidate still needs a proven path from screen setup / DMA / pointer logic to the decoded graphics range.

Never select a ROM span only because the output happens to resemble text.

## Current status

- candidate renderer: **STATIC PASS**
- real clean-ROM candidate render: **NOT RUN**
- G0 asset offset: **UNPROVEN**
- G1 asset offset: **UNPROVEN**
- ROM write: **NO**
- Runtime PASS: **NO**
