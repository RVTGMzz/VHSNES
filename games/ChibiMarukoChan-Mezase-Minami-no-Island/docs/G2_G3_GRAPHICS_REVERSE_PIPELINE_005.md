# G2/G3 Graphics Reverse Pipeline 005

Updated: 2026-09-18 +07

This checkpoint extends the one-command graphics reverse workflow to the remaining known graphics-driven UI after G0/G1.

## G2 targets

- `今からやるよ` -> **Bắt đầu thôi!**
- `ルールをせつめいするよ` -> **Luật chơi**
- `２本先取だよ` -> **Thắng 2**
- `ゲームの時間は勝つまでだよ` -> **Đến khi thắng**

## G3 targets

- `勝ち` -> **Thắng**
- `敗けた` -> **Thua**
- `コンティニュー` -> **Tiếp tục**
- `やめる` -> **Thoát**
- `最終勝利` -> **Chiến thắng cuối cùng!**
- `エンディング` -> **Kết thúc**

## New tools

### Shared target-shape scanner

`tools/scan_graphics_shape_targets.py`

The scanner reuses the proven Chibi 12x12 glyph extraction / shape-matching engine, but runs G2 and G3 as separate target batches.

Important behavior:

- extracts each unique source glyph through the proven CP932 -> glyph ID -> 12x12 bitmap path;
- gracefully reports source glyphs that cannot be extracted instead of crashing the whole batch;
- scans packed 12x12 1bpp and sequential SNES 2bpp / 4bpp 2x2 hypotheses;
- reports per-target coverage for each candidate cluster;
- keeps G2 and G3 scoring independent.

A source graphic may use a stylized redraw that does not match the normal font. Therefore a weak/no shape hit does **not** prove absence of the asset.

### One-command G2/G3 runner

`tools/run_g2_g3_graphics_reverse_pipeline.py`

Pipeline:

1. validate exact canonical clean ROM;
2. run the existing graphics render-path tracer with all known descriptor anchors;
3. run G2 shape scan;
4. correlate G2 clusters with pointer / DMA evidence;
5. write `g2_pipeline_summary.json`;
6. run G3 shape scan;
7. correlate G3 clusters independently;
8. write `g3_pipeline_summary.json`;
9. write combined `g2_g3_pipeline_summary.json`.

The descriptor/debug region `0x286B4..0x287FC` remains evidence only and must never be patched as the retail graphics source.

## ROM-free self-test

Added:

`tools/selftest_g2_g3_reverse_tools.py`

It validates:

- G2/G3 target dictionaries;
- duplicate-glyph handling;
- coverage accounting;
- generic cluster parsing;
- pointer parsing;
- DMA parsing;
- descriptor anchor parsing;
- strong-candidate ranking;
- summary generation.

The existing static workflow now includes the G2/G3 self-test.

## Intended command

Once the exact clean ROM is available:

```bash
python tools/run_g2_g3_graphics_reverse_pipeline.py clean.sfc
```

Inspect:

- `reports/generated/g2_g3_pipeline/g2_pipeline_summary.json`
- `reports/generated/g2_g3_pipeline/g3_pipeline_summary.json`
- `reports/generated/g2_g3_pipeline/g2_g3_pipeline_summary.json`

## Promotion gate

A strong shape/pointer candidate is still only a reverse priority.

Before writing:

`matching screen transition -> pointer/DMA path -> decoded source asset -> visible retail label -> bounded patch span`

Then build the Vietnamese graphics layer on top of the latest accepted direct-text/font candidate.

## Current status

- G0 one-command reverse pipeline: **COMMITTED**
- G1 one-command reverse pipeline: **COMMITTED**
- G2/G3 one-command reverse pipeline: **COMMITTED**
- ROM-free self-tests: **COMMITTED**
- GitHub CI successful run: **NOT OBSERVED**
- exact clean-ROM execution in active runtime: **NOT RUN**
- G0/G1/G2/G3 asset offsets: **UNPROVEN**
- graphics ROM write: **NO**
- Runtime PASS: **NO**
