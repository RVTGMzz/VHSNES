# G2 School-Front Resource Collector Checkpoint 011

Updated: 2026-09-20 +07

This checkpoint extends the G2 reverse track after the proven execution handoff:

`Start -> A1 -> $80:E131 -> $80:E169 -> $88:8139 -> $88:CB4E -> group 4 -> school-front scene`

Target:

`今からやるよ` -> **Bắt đầu thôi!**

## Why this checkpoint exists

The active session could not recover the previously uploaded clean `.sfc` binary from File Library. Binary ROM content is not stored in GitHub by design.

Rather than restart broad scans or guess an asset, the repository now contains an execution-aware collector that will turn the next clean-ROM run into a narrow, reproducible resource census around the school-front scene.

## New tool

`tools/trace_g2_school_front_resources.py`

It starts from:

- `$88:8139`
- `$88:CB4E`

and performs a bounded local traversal through candidate code routines.

It records:

- nearby JSL/JML/JSR/JMP targets;
- exact proven resource-call pattern:
  `LDX #script ; JSL $80:E255`;
- routine depth / call site;
- referenced bank-`$82` resource scripts;
- type-0 package metadata;
- standalone type-FF script metadata when it matches the proven shape;
- source CPU/file offsets;
- compressed spans;
- post-process flags;
- VRAM destinations;
- decompressed sizes.

For type-0 records with tile-aligned outputs, it also exports both:

- 4bpp tile-sheet preview;
- 2bpp tile-sheet preview.

This is intentionally generous at the preview layer because the exact bpp of the target overlay is not yet proven.

## Command

```bash
python tools/trace_g2_school_front_resources.py clean.sfc \
  --out reports/generated/g2_school_front_resources
```

Primary output:

`reports/generated/g2_school_front_resources/g2_school_front_resources.json`

Preview directory:

`reports/generated/g2_school_front_resources/previews/`

## Self-test

Added:

`tools/selftest_g2_school_front_resources.py`

The synthetic test proves that the collector can:

1. begin from a known bank-`$88` root;
2. follow a same-bank child routine;
3. discover the exact resource-call byte shape in that child;
4. recover the expected bank-`$82` script pointer;
5. honor the traversal depth gate.

## CI

Workflow commit:

`3755af52f3ea7e5499afa6914143be379c3f7274`

GitHub Actions run:

**#42**

Observed successful core steps include:

- Compile reverse tools
- Run G0 reverse selftest
- Run G1 reverse selftest
- Run G2 G3 reverse selftest
- Run G2 targeted start-flow selftest
- **Run G2 school-front resource collector selftest**
- graphics patch / rasterizer / fit / manifest / PNM selftests

At observation time the job had already completed every substantive test step successfully and was only in the runner cleanup step.

## Claims

- execution-aware collector implementation: **STATIC PASS**
- collector synthetic self-test: **PASS**
- existing reverse/build static suite: **PASS through substantive steps**
- canonical clean-ROM collector run: **NOT RUN in this session**
- exact `今からやるよ` asset source: **UNPROVEN**
- G2 ROM write: **NO**
- G2 Runtime PASS: **NO**

## Guardrails

Still forbidden:

- patch descriptor `0x286EA`;
- revive rejected candidate `$9A:CB34` without new execution evidence;
- promote a visually similar preview without tying it to the executed resource path;
- claim Runtime PASS without user gameplay/screenshot confirmation.

Promotion gate remains:

`executed school-front routine -> exact resource call -> exact script/record/source -> decoded visible 今からやるよ overlay -> bounded replacement -> runtime confirmation`
