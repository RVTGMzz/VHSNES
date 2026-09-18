# Graphics Build 036 Pipeline 006

Updated: 2026-09-18 +07

This checkpoint closes the tooling gap between graphics reverse evidence and a guarded Build 036 candidate.

No commercial ROM is committed.

## Build 035 base contract

Graphics Build 036 is layered on the exact current direct-text/font candidate:

- file: `Chibi_Maruko_Build_035_QUIZ01_CREDITS_PASS_READY.sfc`
- size: `0x200000`
- SHA-1: `054380f9b452f245471e6309eb33c7486d581462`
- SHA-256: `f8fb662a9e1b8fc5a5ff689f690ceaf332055ed86983e52b476a78852e4fd58d`
- runtime status: **UNTESTED**

## 1. Reverse the remaining graphics

Preferred master command on the exact clean ROM:

```bash
python tools/run_all_graphics_reverse.py clean.sfc
```

This runs G0 through G3 and writes the master reverse summary.

Do not promote a candidate based on ranking alone.

Required proof remains:

`screen setup -> pointer/DMA/staging path -> decoded retail asset -> bounded asset span`

## 2. Build Vietnamese replacement graphics

### G1-G3 UI labels

Tool:

`tools/rasterize_vi_text_to_snes_tiles.py`

It reads the exact Build 035 Vietnamese font/codepage state and converts 12x12 Vietnamese glyphs into:

- raw SNES 2bpp or 4bpp tiles;
- sequential raw tilemap;
- PNG preview;
- JSON metadata.

This keeps labels such as:

- **Chọn gì đây?**
- **Bắt đầu**
- **Mật khẩu**
- **Luật chơi**
- **Thắng**
- **Thua**
- **Tiếp tục**
- **Thoát**

visually consistent with the existing Vietnamese font layer.

Helper:

`tools/prepare_graphics_patch_bundle.py`

Once geometry and asset span are proven, it performs:

`Vietnamese text -> tiles/tilemap -> fit check -> exact-span replacement -> guarded patch fragment`

It refuses a replacement that exceeds the proven graphics span.

Zero-padding is opt-in only.

### G0 title / intro custom artwork

The title should not be forced into the ordinary 12x12 UI font.

Tool:

`tools/encode_indexed_pnm_to_snes_tiles.py`

Supported custom artwork source:

- ASCII PBM `P1`
- ASCII indexed PGM `P2`

The pixel values become SNES palette indices for 2bpp or 4bpp graphics.

This allows a custom pixel-art treatment for:

- **Chibi Maruko-chan**
- **Tiến tới đảo phương Nam!!**
- **Việt hóa bởi VôtriValley**

while retaining the screen's proven palette/layout constraints.

Helper:

`tools/prepare_custom_graphics_patch_bundle.py`

Pipeline:

`indexed title art -> SNES tiles/tilemap -> fit gate -> guarded G0 patch fragment`

Actual palette colors are still owned by the proven retail screen palette; the encoder stores only palette indices.

## 3. Fit gate

Tool:

`tools/plan_graphics_asset_fit.py`

Possible results:

- `EXACT_FIT`
- `FITS_WITH_PADDING`
- `RELOCATION_OR_LAYOUT_CHANGE_REQUIRED`

Never silently truncate graphics to make them fit.

If replacement data is smaller than the proven span, padding is explicit and auditable.

If replacement data is larger, stop and reverse relocation/layout rather than overwriting the next asset.

## 4. Guarded patch fragments

Tool:

`tools/make_graphics_patch_entry.py`

For every proven replacement span it records:

- patch id;
- exact file offset;
- exact length;
- SHA-256 of the original Build 035 span;
- replacement file;
- replacement SHA-256;
- evidence note.

The original-span hash prevents a correct patch from being applied to the wrong ROM/span.

## 5. Assemble Build 036 manifest

Template:

`translation/runtime/graphics_patch_manifest_B036.template.json`

Assembler:

`tools/assemble_graphics_manifest.py`

The assembler:

- merges G0-G3 patch fragments;
- rejects duplicate patch IDs;
- rejects overlapping spans;
- verifies replacement files and hashes;
- rewrites replacement paths relative to the final manifest;
- sets `ready=true` only on the assembled manifest.

## 6. Guarded build and independent verification

Builder:

`tools/apply_graphics_patch_manifest.py`

It requires:

- exact manifest base hash;
- exact original-span SHA-256 for every patch;
- non-overlapping spans;
- exact replacement lengths.

Only the declared patch spans and SNES checksum bytes are permitted to change.

Independent verifier:

`tools/verify_graphics_patch_build.py`

It separately checks:

- Build 035 base contract;
- original-span hashes;
- replacement bytes in the built ROM;
- entire-ROM diff surface;
- SNES checksum/complement pair;
- computed checksum match.

Final wrapper:

`tools/build_036_graphics.py`

It requires an assembled manifest with:

`ready=true`

and then runs builder + verifier before writing the static build report.

Static PASS still does **not** mean Runtime PASS.

## 7. Intended end-to-end flow

Once the exact binaries and proven spans are available:

```text
clean ROM
  -> run_all_graphics_reverse.py
  -> prove G0/G1/G2/G3 asset spans

Build 035
  -> prepare G0 custom patch bundle
  -> prepare G1-G3 Vietnamese patch bundles
  -> assemble_graphics_manifest.py
  -> build_036_graphics.py

Build 036
  -> emulator/gameplay test by Ron
  -> screenshots for title/menu/rules/results
  -> Runtime PASS only after visual confirmation
```

## Static tooling status

Committed:

- G0-G3 reverse pipelines
- DMA/WRAM tracing
- 2bpp/4bpp graphics render probes
- Vietnamese 12x12 -> SNES graphics rasterizer
- indexed custom-art -> SNES graphics encoder
- graphics fit planner
- patch-entry generator
- patch-fragment assembler
- guarded manifest builder
- independent build verifier
- Build 036 wrapper
- ROM-free selftests for the core pieces

The GitHub Actions workflow has been expanded to exercise the ROM-free selftests.

As of this checkpoint, GitHub still returned no workflow run/status for the latest branch commit.

Therefore:

- workflow configuration: **COMMITTED**
- local/synthetic logic checks performed during development: **PASS where explicitly noted**
- GitHub CI PASS: **NOT CLAIMED**
- Build 036 ROM: **NOT BUILT**
- Runtime PASS: **NO**
