# G1 Shape Probe 004 — bitmap fingerprint + evidence correlation

Updated: 2026-09-18 +07

Graphics Batch G1 remains:

- `どれにする？` -> **Chọn gì đây?**
- `はじめから` -> **Bắt đầu**
- `パスワード` -> **Mật khẩu**

This checkpoint advances the reverse tooling only. It does **not** claim a proven retail asset offset and does not create a G1 ROM patch.

## Why Probe 004

Earlier G1 work already rejected:

- direct CP932 storage for the pink heading;
- contiguous resolved glyph IDs;
- useful sparse/interleaved CP932 or glyph-ID streams;
- simple contiguous masked tilemap-ID runs;
- the internal descriptor/debug block as a visible retail asset.

The visible pink heading still resembles the already-proven 12x12 Chibi font face. Therefore Probe 004 searches by **bitmap shape**, not by source text bytes or glyph numbers.

## Tool 1 — bitmap shape fingerprint scanner

Added:

`tools/scan_g1_shape_fingerprints.py`

The scanner is read-only and requires the exact canonical clean ROM:

- size: `0x200000`
- SHA-1: `08a2415362f69788ec76b1a36044dc1f1a5f2ea1`

It derives the real 12x12 glyph bitmaps for every unique Japanese character used by all three G1 targets through the already-proven Chibi mapping/font path.

It then probes the ROM under these raw-asset hypotheses:

1. packed 12x12 1bpp, MSB-left;
2. packed 12x12 1bpp, LSB-left;
3. sequential 2x2 SNES 2bpp tile blocks, converted to a color-agnostic occupancy mask;
4. sequential 2x2 SNES 4bpp tile blocks, converted to the same occupancy mask.

Each candidate is compared as one 144-pixel fingerprint.

Default tolerance:

- max differing pixels: `14 / 144`;
- minimum similarity: approximately `90.3%`.

Results are clustered by ROM distance and report coverage against:

- heading;
- Start;
- Password.

A cluster containing several distinct G1 glyph shapes is only an **asset candidate**.

### Static validation

Local development checks for Probe 004:

- Python compile: **PASS**
- synthetic packed 1bpp fixture: **PASS**
- synthetic SNES 2bpp fixture: **PASS**
- synthetic SNES 4bpp fixture: **PASS**
- clustering fixture: **PASS**
- target-coverage fixture: **PASS**

The canonical commercial ROM was not available in the active runtime, so no clean-ROM shape report is claimed at this checkpoint.

## Tool 2 — evidence correlator

Added:

`tools/correlate_g1_evidence.py`

This tool combines:

- cluster output from `scan_g1_shape_fingerprints.py`;
- pointer/DMA/xref output from `trace_g1_render_path.py`.

It ranks candidates using:

- pointer targets landing directly inside a shape cluster;
- pointer targets near a cluster;
- number of distinct G1 glyph shapes;
- target-string coverage;
- best bitmap similarity.

A candidate enters the correlator's **strong reverse-priority** bucket only when:

1. at least one pointer target lands inside the cluster; and
2. the cluster contains at least two distinct G1 glyph shapes.

This is still **not** enough to patch.

Final proof still requires:

`screen setup -> pointer/DMA/render path -> decoded source asset -> visible G1 text`

### Static validation

Local development checks for the correlator:

- Python compile: **PASS**
- synthetic trace report parse: **PASS**
- synthetic shape report parse: **PASS**
- direct pointer-in-cluster ranking: **PASS**
- strong-candidate gate: **PASS**

## Intended run sequence

From the game directory:

```bash
python tools/trace_g1_render_path.py "path/to/clean.sfc" \
  --report reports/generated/g1_render_path_trace.txt \
  --csv reports/generated/g1_render_path_trace.csv

python tools/scan_g1_shape_fingerprints.py "path/to/clean.sfc" \
  > reports/generated/g1_shape_probe_004.txt

python tools/correlate_g1_evidence.py \
  reports/generated/g1_shape_probe_004.txt \
  reports/generated/g1_render_path_trace.txt \
  > reports/generated/g1_evidence_correlation_004.txt
```

## Proof gate before any Build 036 graphics write

Do not write a G1 asset merely because it looks plausible.

A patchable candidate needs all of:

1. multi-glyph shape evidence or a decoded asset reproducing the visible label;
2. a pointer/render/DMA path that reaches the candidate;
3. exact source-span identity before write;
4. independently bounded asset span;
5. no write to `0x286B4..0x287FC`;
6. diff-surface and checksum gates;
7. Runtime status remains **UNTESTED** until the user tests the exact screen.

## Current status

- Build 035: **Runtime UNTESTED**
- G1 actual visible asset offset: **NOT YET PROVEN**
- G1 graphics write: **NO**
- descriptor/debug block patched: **NO**
- Probe 004 tooling: **STATIC PASS**
- Runtime PASS: **NO**
