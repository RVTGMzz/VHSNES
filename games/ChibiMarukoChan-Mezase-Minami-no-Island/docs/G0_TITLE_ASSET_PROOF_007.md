# G0 Title Asset Proof 007

Updated: 2026-09-18 +07

This checkpoint records the first reproducible static proof of the retail Chibi Maruko-chan title asset path on the exact canonical clean ROM.

## Clean-ROM contract

- size: `0x200000`
- SHA-1: `08a2415362f69788ec76b1a36044dc1f1a5f2ea1`
- SHA-256: `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`

## Proven boot/title resource script

The title resource package is:

- CPU pointer: `$82:A087`
- file offset: `0x12087`
- script type: `0x00`

The package payload begins at file `0x12089` and contains ten 5-byte resource records:

`VRAM destination word + compressed source pointer 24-bit`

followed by `FF`.

This package is reached from the retail boot/title execution flow, not inferred only by pattern scanning.

## Exact package records

| # | VRAM word | source CPU | source file | postprocess | decompressed bytes |
|---|---:|---:|---:|---:|---:|
| 0 | `0x2000` | `$9E:E456` | `0x0F6456` | 0 | `0x2000` |
| 1 | `0x3000` | `$9E:D005` | `0x0F5005` | 1 | `0x2000` |
| 2 | `0x4000` | `$9E:C56D` | `0x0F456D` | 1 | `0x2000` |
| 3 | `0x0000` | `$9E:9F00` | `0x0F1F00` | 0 | `0x0800` |
| 4 | `0x0400` | `$9E:8A24` | `0x0F0A24` | 0 | `0x0800` |
| 5 | `0x1000` | `$9E:86CE` | `0x0F06CE` | 0 | `0x0800` |
| 6 | `0x5800` | `$9F:87D7` | `0x0F87D7` | 0 | `0x0800` |
| 7 | `0x5000` | `$91:A2BC` | `0x08A2BC` | 0 | `0x1000` |
| 8 | `0x6000` | `$9E:B19D` | `0x0F319D` | 1 | `0x2000` |
| 9 | `0x7000` | `$9E:A121` | `0x0F2121` | 1 | `0x2000` |

The exact decoder reaches the declared stream end on all ten records and produces VRAM-aligned output sizes without special-case hacks.

## Proven title layer

Offline reconstruction of package `$82:A087` yields the retail title graphic.

The proven title layer is:

- BG tilemap resource:
  - source CPU `$9E:9F00`
  - source file `0x0F1F00`
  - compressed span `0x221`
  - decompressed size `0x800`
  - VRAM destination `0x0000`
- BG tile graphics resource:
  - source CPU `$9E:E456`
  - source file `0x0F6456`
  - compressed span `0x15C2`
  - decompressed size `0x2000`
  - VRAM destination `0x2000`

Rendering:

- map VRAM word: `0x0000`
- graphics VRAM word: `0x2000`
- bpp: `4`
- tilemap: 32x32

reproduces the visible retail logo:

- `ちびまる子ちゃん`
- `めざせ！南のアイランド!!`

Therefore **G0 retail asset identity is statically proven**.

## Resource codec proof

The codec used by these resources is modeled by:

`tools/decompress_chibi_resource.py`

Observed command families include:

- ring-buffer back-reference with 1 KiB history;
- literal;
- pair-literal / zero-value expansion;
- RLE;
- zero-run;
- extended zero-run.

Header bit 15 selects a 16-byte post-process reorder used by several graphics resources.

The exact reorder for flag=1 is:

`0,8,1,9,2,10,3,11,4,12,5,13,6,14,7,15`

per complete 16-byte block.

## Reproducible renderer

The package is reconstructible with:

`tools/render_chibi_resource_package.py`

Canonical G0 render parameters:

```bash
python tools/render_chibi_resource_package.py clean.sfc g0_title.png \
  --script-cpu 0x82A087 \
  --map-vram 0x0000 \
  --gfx-vram 0x2000 \
  --bpp 4 \
  --width 32 \
  --height 32 \
  --metadata reports/generated/g0_title_proof.json
```

## Build implication

G0 is not a raw uncompressed ROM span.

A production Vietnamese G0 patch must therefore use one of these guarded strategies:

1. recompress the rebuilt Vietnamese title tilemap/graphics into valid Chibi resource streams and update bounded source spans; or
2. relocate new valid resource streams to proven free/expanded ROM space and update the package source pointers.

Do not overwrite `0x0F1F00` or `0x0F6456` with decompressed graphics.

The original publisher/copyright attribution must remain intact.

## G1 update

The Start/Password screen has not yet been proven as a type-0 resource package.

Current evidence:

- global state 2 is the title state;
- Start transitions through global state 3;
- state 3 behaves as a transition/controller gate;
- the title package already contains a reusable 2bpp 8x8 UI font in the VRAM region beginning at word `0x5000`;
- raw, compressed-resource, 16-bit tilemap and OBJ-bank searches have not yet identified the retail G1 label source.

G1 asset/source identity remains **UNPROVEN**.

## Status

- G0 asset identity: **STATIC PASS**
- G0 decompressor path: **STATIC PASS**
- G0 offline reconstruction: **STATIC PASS**
- G0 ROM write: **NO**
- G0 Runtime PASS: **NO**
- G1 asset identity: **UNPROVEN**
- Build 036: **NOT BUILT**
