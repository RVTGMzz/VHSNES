# Checkpoint 073 — Actual SNES Quiz copier, corrected relocation, 81-bank-slot geometry

**CHECKPOINT 074 CORRECTION — ORIGINAL WRAM OVERWRITE HAZARD.** Checkpoint073's 81 disjoint 68-byte source slots prove original-ROM BANK06 safety, **not** WRAM safety. The original game writes each 66-byte copy into buffers only **32 bytes** apart (`$7E8000`, `$7E8020`, `$7E8040`). Exactly **29/81** full translated answer records are longer than 32 bytes; **18 choice #1/#2 records will have text bytes overwritten by the following copy**, and 11 choice #3 records remain a rendering/WRAM-layout risk. The bulk-81 runtime proposal is therefore **NOT SAFE FOR PRODUCTION**. Read `docs/CHECKPOINT_074_REAL_WRAM_STRIDE_GUARD_AND_52_SAFE_CHOICES.md`: it prepares the **52** full answers that fit the original WRAM stride as isolated, still untested source-ROM candidates and defers 29 long ones for engine work.


Date: 2026-10-12. Branch: `chibi-maruko-bootstrap-01`. User-owned clean Japanese 2MiB SFC SHA256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`.

## New reverse-engineering evidence: the game copies a FIXED window, not just a string

Original retail ROM at **file offset `0x30762`** contains this exact 21-byte 65c816 sequence:

```text
A9 20 00     LDA #$0020
85 08        STA $08
B9 00 00     LDA $0000,Y
9F 00 80 7E  STA $7E8000,X
E8 E8        INX / INX
C8 C8        INY / INY
C6 08        DEC $08
10 F1        BPL loop
60           RTS
```

In the verified 16-bit accumulator context, this loop makes **33 word reads = 66 bytes** from the answer source pointer. Three real call sites at `0x30730`, `0x307AA`, `0x3081B` use `LDY $92E7,X`, `LDY $927F,X`, `LDY $9217,X` (the three native answer tables) and invoke `JSR $8762` with destinations `X=#0`, `#$20`, `#$40`. These bytes were checked directly in the exact user-supplied original ROM, not inferred from CSV text. This is substantial evidence the game **actually consults the original question-answer pointer tables**, but it is still not a complete SNES emulator run.

### Previously unrecognized hazards

- The old experimental **067** relocation put a choice at `0x37FE0`. There are only **32 source bytes** left in bank06 before file offset `0x38000`. The 66-byte copy tries to read **34 bytes beyond that bank**, possibly wrapping or reading unrelated data. The old single-choice proof remains historical **byte-only**, but must not be used as proof of safe gameplay relocation.
- The first two **072** test targets `0x37000` and `0x37040` are **64 bytes apart**; the source's 66-byte fixed read windows overlap **by 2 bytes**. This does not prove the old probe will crash (the displayed text terminates earlier), but fails the strict disjoint-window condition for a clean engine test. **Replace ZIP072 with the corrected ZIP073 for testing.**
- Earlier **069** packs 81 variable-length answer records tightly in 2,431 bytes. The byte-coded strings/IPS replay remain real, but original engine reads 66 bytes from each record, possibly copying bytes from adjacent relocated strings into WRAM. Until actual game testing, its packing must **NOT** be declared production-safe.

## New 073 native Japanese diagnostic: nonoverlapping source read windows

The corrected test preserves the same original two answers and pointers, but moves the second new 17-byte record from `0x37040` to `0x37080`:

| First two original *pointer-table* slots | Native text | New record | Full 66-byte copy interval |
|---|---|---|---|
| 0, pointer at `0x31217` | `３０円` → `３０円です` | `0x37000` | `0x37000–0x37041` |
| 1, pointer at `0x31219` | `７６才` → `７６才です` | `0x37080` | `0x37080–0x370C1` |

On the exact 2MiB original Japanese ROM, an **independent local Python byte/IPS replay** confirmed that the copy windows are disjoint, remain within bank06, all original Japanese answer text stays untouched and only the two 16-bit pointers, two new records and SNES checksum bytes differ.

| Independent source-byte QA | Corrected 073 |
|---|---|
| Actual changed ROM bytes | **42** |
| IPS byte count / IPS records | **70 / 4** |
| IPS SHA256 | `d02a6c2aaf9f1f95d252d9c3c7947b142becd73f4bc7cb74d31e55de50c071cf` |
| Full image SHA256 if applied to exact Japanese ROM | `e52565fa299dfd35d15a6dc80cb778658be6f82ed44655bf7373e3ce1b3d8611` |
| SNES checksum | `0xFBEC` |
| IPS round trip on original user SFC | **PASS** |
| Runtime emulator rendering, highlight, grading, transitions | **NOT TESTED** |

New reproducible tool `tools/build_native_quiz_relocation_probe_073.py` incorporates original copier/callsite assertions and fails when source copy windows overlap or leave bank06. A **single corrected optional ZIP**, `Chibi-Quiz-Engine-Relocation-CopierSafe-PROBE073.zip`, contains IPS + exact static QA + Vietnamese README. Do not submit commercial ROM files to GitHub. This is an **engine smoke test**, not a Vietnamese localization patch.

## 81 full Vietnamese answers: disjoint 68-byte reserved slots

A new ROM-independent compiler geometry planner `tools/plan_quiz_bankcopy_slots_073.py` validates the exact original 381 source files, 279 staged items, 150 choice addresses and all **81 pending canonical full Vietnamese choices**, including the two distinct **Nagasawa Kazuo (一雄)/(和雄)** alternatives. It models the actual native copy semantics, not just the space occupied by the string:

- **68-byte cell per answer**: 66 bytes the game may copy + 2 gap bytes.
- All 81 cells start from **`0x36A00`** in original unused bank06 `FF` storage, last cell ends at `0x37F83`, end-exclusive `0x37F84`.
- Total reserved **81 × 68 = 5,508 bytes**; 124 bytes remain until `0x38000`. The original clean ROM contains `FF` throughout the whole proposed region.
- The longest full translated record consumes **53 bytes**, less than the 66-byte reserved copy scope; all 81 existing translations are representable with V2 bytes plus whitelisted native Kanji where necessary.
- Every proposed pointer stays in bank06's 16-bit LoROM addressable range, and source read windows cannot overlap.

The planner runs **without game ROM** in GitHub Actions source CI; when run locally with `--original-rom clean.sfc`, it additionally checks the actual original 65c816 copier/callsite bytes, bank06 `FF` storage, and all 81 source pointer words. It writes an optional JSON plan only — **not** a patch or a game ROM.

GitHub Actions `Chibi SNES source localization checks` now runs this source/copy-width planner. [Run 38202883789](https://github.com/RVTGMzz/VHSNES/actions/runs/38202883789) passed the new 81-cell allocation test. This is source-only CI, not SNES gameplay verification.

## Status and next gate

**Quiz remains 279/381 unique source offsets previously staged**, not 360/381. The corrected native Japanese diagnostic has **not been tried on SNES emulator**, the historical 039–043 composite IPS assets are still inaccessible as raw bytes, and font V2 mixed native-Kanji display and 81 longer lines have not been acceptance-tested. No production patch of all 81 new answers is approved.

Next: optional minimal native-Japanese 073 emulator test of the two sample choices, then repeat with an actually integrated Vietnamese-font ROM after acquiring one original 039–043 IPS/ZIP via checkpoint071 recovery. Also complete four too-long Fortune items and G3 result/ending assets. Keep the user's policy **content first, font polish last**, but do not ignore screen width or answer correctness.
