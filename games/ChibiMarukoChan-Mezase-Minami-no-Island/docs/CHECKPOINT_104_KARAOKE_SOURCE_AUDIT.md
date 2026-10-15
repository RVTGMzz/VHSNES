# Checkpoint 104 — Karaoke source identity audit (source-only)

Date: 2026-10-15. Branch: `chibi-maruko-bootstrap-01`.

## Scope and evidence

Read `HANDOFF_CURRENT.md` and `docs/CHECKPOINT_103_SCREENSHOT_REVIEW.md` first.
Checkpoint 103 remains the latest cumulative IPS build. Its IPS SHA256 is
`5a5a46ec63eea4c5aa9f876b008b112e31f4cef4ab4bd470b33e67cc9ccfc9c7`.
The 103 handoff reports that the 28 Karaoke lyric lines are translated only
in source CSVs; they are **not** integrated into the running game.

Added `tools/audit_karaoke_source_104.py` to audit the two existing files:

- `translation/source/karaoke_batch01_vi.csv` (meaning-first source).
- `translation/source/karaoke_batch01_singable_v1_vi.csv` (unverified lyric draft).

The script enforces 28 ordered canonical original offsets; one-to-one original
Japanese identity and identical meaning-first Vietnamese across both files;
valid CP932 source encoding; NFC Vietnamese; absence of untranslated Japanese
script in draft fields; preserved literal placeholder patterns; explicit draft
statuses/timing caveats; and identical translations in both repeated-refrain
groups. It neither reads nor writes game ROM/IPS or font assets.

A separate in-session CSV parser checked **28/28 matching source identities**,
28+28 rows, expected column layouts and statuses, and **2/2 repeated-refrain
groups**. It reported zero alignment issues. This is a CSV source audit, not
a ROM byte audit. The Python script itself has **not** been executed by CI
or locally in this session; avoid calling that an execution PASS.

## Editorial issues to resolve before Karaoke insertion

Five draft phrasing issues were identified by comparing the existing Japanese
source meaning against the existing Vietnamese source/draft. These are review
targets, not committed lyric rewrites:

| Source offset | Problem in current draft | Editorial target |
|---|---|---|
| `0x2B47D` | Adds arms/hands to a line about unsteady footing. | Keep backache and unsteady steps. |
| `0x2B4FA` | Replaces the original bliss/paradise nuance with generic happiness. | Preserve heightened delight/bliss. |
| `0x2B622` | Shortens a marathon reference to ordinary jogging. | Keep the marathon/running-event reference and jump rope. |
| `0x2B675` | Makes an obligation into a conditional desire to act. | Express necessity/urgency while there is still time. |
| `0x2B69D` | Draft has an unnatural collocation for physical stamina. | Use idiomatic Vietnamese about building stamina. |

These need a separate editorial pass **and** timing/syllable and visible
renderer/line-width proof before they can be considered singable runtime text.
Do not shorten the canonical `vi_full` merely to fit an unknown ROM span.
Do not change Japanese source offsets, control codes or placeholders.

## Reproducible source-only command

```bash
cd games/ChibiMarukoChan-Mezase-Minami-no-Island
python tools/audit_karaoke_source_104.py
```

Optional `--report path/to/report.json` emits a non-lyric JSON summary.
The CI workflow was **not** modified: connector write attempts to existing
files were blocked in this session. The new script is committed as an
independent audit but has not been incorporated into CI.

## What is NOT done

No original ROM, historical 043 archive, cumulative IPS or emulator was used
in this checkpoint. No lyric was inserted into game memory, no graphics/Paint
menu was changed, no song playback/timing was tested and no source text was
counted as newly translated. The prior 103 IPS and runtime screenshots are
historical evidence for **103**, not for Karaoke 104. Whole-game completion is
still false.

Next: execute 104 audit in CI when existing-file writes are available;
resolve the five editorial items; reverse and test Karaoke screen lyric storage
and timing using an authorized original ROM; insert as part of a **single**
cumulative patch rather than issuing extra small IPS files. Continue confirmed
remaining minigame, Paint and character graphics work.
