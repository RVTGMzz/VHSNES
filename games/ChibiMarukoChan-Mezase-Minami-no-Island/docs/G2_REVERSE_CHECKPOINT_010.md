# G2 Reverse Checkpoint 010

Updated: 2026-09-19 +07

This checkpoint records the current execution trace toward the retail `今からやるよ` overlay after G1 Start/Password reached Runtime PASS.

## Repository

- repo: `RVTGMzz/VHSNES`
- branch: `chibi-maruko-bootstrap-01`

## Target

Visible Japanese:

`今からやるよ`

Frozen Vietnamese:

**Bắt đầu thôi!**

The QA/debug descriptor at file `0x286EA` identifies this screen semantically, but is **not** the retail visible asset and must not be patched as the solution.

## Current proven execution chain

The current route has been reduced to:

`Start -> A1 -> $80:E131 -> $80:E169 -> $88:8139 -> $88:CB4E -> group 4 -> school-front scene`

This is the current authoritative handoff point.

The next reverse step is to continue from the school-front scene and identify the resource/overlay path that produces `今からやるよ`.

## Rejected candidate

Candidate:

`$9A:CB34`

was inspected and **rejected**.

Reason:

- decoded glyph/graphic content does not match the target overlay;
- therefore it must not be promoted as a G2 asset source.

## Current status

- semantic screen clue `0x286EA`: **KNOWN / DESCRIPTOR ONLY**
- Start-to-G2 execution route through `$88:CB4E`: **STATIC TRACE IN PROGRESS**
- group 4 / school-front scene: **CURRENT REVERSE ANCHOR**
- `$9A:CB34`: **REJECTED**
- exact `今からやるよ` asset source: **UNPROVEN**
- bounded G2 graphics write: **NO**
- G2 Runtime PASS: **NO**

## Guardrails

Do not:

- patch `0x286EA`;
- revive `$9A:CB34` without new execution evidence;
- call G2 asset proof from shape similarity alone;
- call Runtime PASS before the user verifies the actual game screen.

Promotion gate remains:

`matching screen transition -> actual retail resource/callback -> source asset -> decoded visible overlay -> bounded replacement -> runtime screenshot/gameplay confirmation`

## Next reverse step

Continue from:

`$88:CB4E group 4 -> school-front scene`

and trace the overlay callback/resource load that appears immediately around the `今からやるよ` presentation.

Prefer execution/resource evidence over another broad whole-ROM shape scan.
