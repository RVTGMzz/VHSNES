# Graphics Batch G0 — Title / Intro Screen Vietnamese Plan

Updated: 2026-09-18 +07

## Scope

This batch covers the first retail title/intro screen shown after startup.

Verified visible title artwork:

`ちびまる子ちゃん めざせ！南のアイランド！！`

Vietnamese target:

`Chibi Maruko-chan: Tiến tới đảo phương Nam!!`

Requested localization credit:

`Việt hóa bởi VôtriValley`

## Layout intent

Keep the original character/background illustration and overall cheerful title-screen composition.

Replace only the Japanese title/logo lettering with a Vietnamese/Latin treatment that preserves the visual hierarchy:

1. Main brand line:
   - **Chibi Maruko-chan**
2. Subtitle:
   - **Tiến tới đảo phương Nam!!**
3. Small localization credit:
   - **Việt hóa bởi VôtriValley**

The localization credit should be visibly separate from the original publisher/copyright lines.

## Copyright / attribution guardrail

Do not erase, replace, translate away, or impersonate the original copyright ownership text.

Preserve the original retail copyright/production attribution exactly as artwork unless an exact technical redraw is required to retain it pixel-for-pixel.

The Vietnamese credit is an additional localization credit only.

## Render strategy

This screen should be treated as a graphics asset until proven otherwise.

Do not assume the normal 12x12 direct-text renderer or the G1 heading path applies.

Reverse the actual title-screen asset and determine whether it is:

- raw SNES 2bpp/4bpp tiles;
- tilemap + reusable tiles;
- compressed graphics;
- or another screen-specific renderer.

The title may be redrawn as graphic tiles, which allows normal Vietnamese diacritics independently of the 12x12 runtime font if the asset path supports it.

## Preferred visual treatment

- keep the title playful and rounded rather than using plain UI text;
- preserve strong separation between the main title and subtitle;
- Vietnamese diacritics must be clearly readable at SNES resolution;
- do not crowd the character artwork;
- localization credit should be small, clean, and subordinate to the game title;
- do not place the credit on top of the original copyright lines.

## Build layering

When the title asset path is proven:

```
Build 035 direct-text/font baseline
        +
Graphics G0 title/intro layer
        +
Graphics G1 menu/start/password layer
```

G0 and G1 should remain separately auditable even if packaged into one larger user test build.

## G0 boot/title trace infrastructure

Added:

- `tools/trace_g0_title_boot.py`
- `docs/G0_BOOT_TITLE_TRACE_001.md`

The tracer starts from the proven reset vector `$00:FF90` / file `0x7F90`, expands boot-near call/jump candidates, and ranks routines with coherent BG / VRAM / DMA register activity.

Static validation:

- Python compile: **PASS**
- reset-vector mapping fixture: **PASS**
- synthetic boot-call expansion: **PASS**
- synthetic VRAM/DMA-site detection: **PASS**

No canonical-ROM run is claimed yet because the commercial binary was unavailable in the active runtime.

## DMA source reconstruction layer

The G0 toolchain now also includes:

- `tools/reconstruct_dma_sources.py`
- `tools/correlate_g0_dma_sources.py`
- `docs/G0_DMA_SOURCE_TRACE_002.md`

This allows the title reverse to proceed from boot-near PPU/DMA routine discovery to source pointer/size reconstruction and visual tile probing without guessing ROM offsets.

If the retail title is staged through WRAM or decompressed at runtime, the next reverse target will be the staging/decompression routine rather than a blind asset scan.

## Runtime status

- title source wording: **VERIFIED VISIBLE**
- Vietnamese wording: **FROZEN**
- localization credit wording: **FROZEN**
- actual ROM asset offset/path: **UNPROVEN**
- ROM write: **NO**
- Runtime PASS: **NO**

Do not call G0 Runtime PASS without a screenshot of the exact patched title screen.
