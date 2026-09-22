# G2 Probe 004 Medium Font Checkpoint 015

Updated: 2026-09-22 +07

## Probe 003 runtime result

User screenshot confirms:

- target Story scene loads;
- Vietnamese text is rendered;
- no black-screen freeze from the Probe-003 strict 2-byte payload;
- text is extremely difficult to read because the installed V5 thin glyphs are too sparse / fragmented in this dialogue presentation.

Therefore:

- Probe 003 direct-text framing/path: **RUNTIME PATH PASS**
- Probe 003 typography: **RUNTIME FAIL**
- whole G2 Runtime PASS: **NO**

This is narrower than a release/font pass. The screenshot proves the text path works, not that the typography is acceptable.

## Root cause

Probe 003 used:

`translation/codepage/vi_glyphs_v5_fe4_thin.json`

V5 thin belongs to the old thinning experiment family that the user had already rejected as inconsistent / uglier.

The historical temporary baseline was Probe 010 native-width, later Probe 019 with a targeted lowercase-`đ` adjustment. Those exact local ROM artifacts are not currently recoverable from GitHub/File Library.

Do not silently substitute Probe 009's stretched/heavy V3 font as if it were Probe 010.

## Probe 004 strategy

Probe 004 is a deliberately narrow readability experiment built **on top of the verified Probe 003 ROM**.

It does not change:

- any direct-text payload;
- any Story separator/control byte;
- D038;
- scene/palette/controller logic;
- codepage assignments.

It modifies only the 27 custom glyph cells used by the three recovered conversation variants.

Transformation:

`existing V5-thin bitmap -> add one pixel immediately to the right of each lit pixel`

This is a one-sided 1px weight increase. It is intentionally milder than a full horizontal/vertical dilation.

Native glyphs already used by the game remain untouched.

## Local artifact

`Chibi_Maruko_G2_DIRECT_TEXT_PROBE_004_MEDIUM_FONT.sfc`

Static facts:

- base: Probe 003
- base SHA-1: `d0f7969aea3cad0a167dca3889ee9960be6415e0`
- custom glyphs changed: **27**
- font diff bytes: **215**
- total diff bytes vs Probe 003: **219**
- SHA-1: `850b3e794dbcb4e8d46d7738efc078d944b5e1f0`
- SHA-256: `00e9be78b0532f34d13bb8f352de16bbc453637d38184b9400e83bf3e36153b5`
- checksum/complement: `0x69BF / 0x9640`

## Claims

- Probe 003 text framing/path: **RUNTIME PATH PASS**
- Probe 003 typography: **FAIL**
- Probe 004 static build: **PASS / READY FOR TEST**
- Probe 004 typography: **RETEST REQUIRED**
- G2 Runtime PASS: **NO**

If Probe 004 is still hard to read, do not keep blindly dilating. The next step should be a new clean 12x12 dialogue font design or recovery of the exact Probe 010/019 baseline artifact.
