# G2 Group-4 D038 Disable Probe 012

Updated: 2026-09-20 +07

Target:

`今からやるよ` -> **Bắt đầu thôi!**

## New clean-ROM evidence

The user re-uploaded the canonical retail ROM and its identity was revalidated:

- size: `0x200000`
- SHA-1: `08a2415362f69788ec76b1a36044dc1f1a5f2ea1`
- SHA-256: `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`
- title: `RS051 CHIBIMARUKOCHAN`
- map mode: `0x30`

## Group-4 dispatcher proof

`$88:CB4E` is now decoded as a group-indexed dispatcher.

For **group 4**, the first table resolves to:

- `$82:AB4E`
- `$82:AE66`

through the proven resource interpreter `$80:E255`.

The second table resolves to:

- `$88:CE80`
- `$88:D038`

through `$80:C47D`.

## School-front asset identity

`$82:AB4E` parses as a type-0 package:

- VRAM `$1000` <- source `$90:D33F`, packed `0x565`, output `0x9C0`, postprocess=1
- VRAM `$0400` <- source `$90:ED19`, packed `0x16E`, output `0x800`

Offline 4bpp reconstruction of:

`tilemap VRAM $0400 + graphics VRAM $1000`

reproduces the retail **school-front scene**.

Therefore:

**group-4 school-front asset identity = STATIC PASS**

`$82:AE66` also belongs to group 4, but is not the `今からやるよ` text source.

## CE80 / D038 triage

Cross-group analysis of the second dispatcher table shows:

- `$88:D038` is reused by many different groups;
- `$88:CE80` is specific to group 4;
- the small `$82:AAB0` resource associated with the group-4 controller path contains only 9 8x8 tiles total and is therefore rejected as the complete six-character `今からやるよ` graphic.

The QA descriptor at `0x286EA` explicitly calls this screen a:

`『今からやるよ』の会話デモです。`

That is, a **conversation demo**, which increases the probability that D038 is part of a shared dialogue/controller path rather than a unique pre-rendered banner.

## High-information runtime probe

Group-4 second-list retail bytes:

file `0x044CF8`:

`80 CE 38 D0 00 00`

meaning:

`CE80 -> D038 -> end`

Probe 001 changes only the D038 word to zero:

`80 CE 00 00 00 00`

This preserves CE80 and cleanly terminates the list before D038.

Purpose:

- if `今からやるよ` disappears while the school-front scene and group-4-specific content remain, D038 is strongly implicated in the dialogue/overlay path;
- if the phrase remains, D038 is eliminated and CE80 / another downstream path becomes priority.

## Reproducible builder

Added:

`tools/build_g2_d038_disable_probe.py`

Expected local artifact:

`Chibi_Maruko_G2_D038_DISABLE_PROBE_001.sfc`

Local build facts from the canonical clean ROM:

- logical patch bytes: **2**
- total changed bytes including SNES checksum: **6**
- SHA-1: `da3cf951acd8d772df1b60a54fc0c81eb412f755`
- SHA-256: `e01ca8bd7da662fef983e144327558cf34213251056ea3d52736c5bef7b8f100`
- checksum: `0x100D`
- complement: `0xEFF2`
- checksum pair: valid

## Runtime status

- group-4 school-front execution/resource path: **STATIC PASS**
- school-front background identity: **STATIC PASS**
- D038 dialogue/overlay identity: **UNPROVEN**
- Probe 001 build: **STATIC PASS / READY FOR TEST**
- G2 Runtime PASS: **NO**

Do not promote D038 to the final asset path until Probe 001 is tested in gameplay.
