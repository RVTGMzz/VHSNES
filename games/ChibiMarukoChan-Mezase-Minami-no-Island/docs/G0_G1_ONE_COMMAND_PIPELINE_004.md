# G0/G1 One-Command Reverse Pipeline 004

Updated: 2026-09-18 +07

This checkpoint packages the current graphics reverse work into repeatable one-command runners.

## G0 title / intro

Runner:

`tools/run_g0_title_reverse_pipeline.py`

Pipeline:

1. validate exact canonical clean ROM;
2. trace reset -> boot/title candidate routines;
3. restrict DMA reconstruction to MDMAEN sites already observed by the boot/title trace;
4. reconstruct A1T/A1B/DAS/BBAD/DMAP;
5. correlate boot proximity + VRAM destination + ROM source + tile alignment;
6. automatically render top direct-ROM 2bpp/4bpp candidates to PNG;
7. always run WRAM staging trace for $7E/$7F DMA sources;
8. write `g0_pipeline_summary.json`.

Important refinement in this checkpoint:

`reconstruct_dma_sources.py` now accepts `--sites-csv` and can reconstruct only DMA sites surfaced by `trace_g0_title_boot.py`, reducing whole-ROM false positives.

## G1 menu/start/password

Runner:

`tools/run_g1_graphics_reverse_pipeline.py`

Pipeline:

1. validate exact canonical clean ROM;
2. run `trace_g1_render_path.py`;
3. run `scan_g1_shape_fingerprints.py`;
4. run `correlate_g1_evidence.py`;
5. recompute ranked evidence for machine-readable output;
6. write `g1_pipeline_summary.json`.

Targets remain:

- **Chọn gì đây?**
- **Bắt đầu**
- **Mật khẩu**

The descriptor/debug block `0x286B4..0x287FC` remains explicitly forbidden as a retail graphics patch target.

## ROM-free self-tests

Added:

- `tools/selftest_g0_reverse_tools.py`
- `tools/selftest_g1_reverse_tools.py`

A GitHub Actions workflow was also added:

`.github/workflows/chibi-g0-reverse-tools-static.yml`

It is configured to:

- compile all Python tools;
- run the G0 reverse self-test;
- run the G1 reverse self-test.

### Current CI observation

As of this checkpoint, no workflow run/status was returned for the branch commits.

Therefore:

- workflow configuration: **COMMITTED**
- ROM-free self-test scripts: **COMMITTED**
- GitHub CI execution: **NOT OBSERVED**
- CI PASS: **NOT CLAIMED**

Do not convert the existence of the workflow into a PASS statement until GitHub actually reports a completed successful run.

## Binary availability

The File Library was searched again by:

- Chibi/Build035/ROM keywords;
- recent-upload metadata from 2026-09-14 through 2026-09-18.

No Chibi `.sfc` / Build 035 binary was found.

Therefore no real-ROM G0/G1 report or PNG is claimed in this checkpoint.

## Next executable action once the clean ROM is available

From the game directory:

```bash
python tools/run_g0_title_reverse_pipeline.py clean.sfc
python tools/run_g1_graphics_reverse_pipeline.py clean.sfc
```

Then inspect:

- `reports/generated/g0_pipeline/g0_pipeline_summary.json`
- `reports/generated/g0_pipeline/renders/`
- `reports/generated/g1_pipeline/g1_pipeline_summary.json`

Promotion gate remains:

`screen setup -> proven pointer/DMA path -> decoded asset identity -> bounded patch span -> guarded write -> runtime screenshot`

## Status

- Build 035: **Runtime UNTESTED**
- G0 asset path: **UNPROVEN**
- G1 asset path: **UNPROVEN**
- graphics ROM write: **NO**
- Runtime PASS: **NO**
