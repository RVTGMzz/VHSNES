# Chibi Maruko-chan SNES — Checkpoint 076: independently verified 81-choice bytes + one-archive composite builder

Date: 2026-10-12 · Branch `chibi-maruko-bootstrap-01`.

## Real original ROM result, independently reproduced

The user-owned headerless Japanese retail SFC is still available in the session:

- Exactly 2,097,152 bytes; SHA256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`.
- An independent local Python implementation (separate from the checkpoint075 GitHub builder) received all **81 canonical full Vietnamese Quiz answer strings** and original source offsets re-fetched from the live repository, encoded the original `0x84xx` V2 map and four native CP932 Kanji occurrences, resolved their pointers directly from the three original 50-entry answer tables, allocated 81 nonoverlapping **68-byte** cells within original bank06, wrote 66-byte zero-padded original text-engine copy records and correct native `0E 06 0F 12` / `81 6F 00` delimiters, computed checksum, created an IPS in memory and independently replayed it.
- **Independent exact match with previously documented checkpoint075 source-only fingerprints:**

| Data from exact ORIGINAL JAPANESE ROM, no Vietnamese font | Result |
|---|---|
| Unique original answer pointers rewritten in memory | **81** |
| Unaltered two distinctive Nagasawa Kanji spellings | **YES**, 4 two-byte native glyph occurrences |
| Experimental bank06 reserved span | `0x36A00–0x37F83` (end-exclusive `0x37F84`) |
| Maximum text record | **53 bytes**, within original 66-byte copy width |
| Changed original ROM bytes (including checksum) | **5,511** |
| Source-only IPS | **6,139 bytes**, 124 IPS records |
| IPS SHA256 | `58f284de922c3e44d2616c0de73918f6a2a86ee552c19cdc4e2cc51643f5f109` |
| 2MiB candidate ROM SHA256 if IPS replayed | `5b8ed66e2ed43936703b99393607c552b5e3697d59eb22e4b3cb6ee94ed23aaa` |
| SNES checksum | `0x1C5D` |
| Actual SNES emulator rendering or answer navigation | **NOT TESTED** |

The clean original Japanese ROM has **no custom Vietnamese V2 font**, so this source-only candidate is **not** a usable Vietnamese release. The experiment only proves fully reproducible addresses, bytes, encoding, checksum and IPS replay; the 075 disassembly independently proves the original game *waits for each text job to finish*, but does not prove long answer label appearance. No binary IPS or copyrighted ROM was published to GitHub.

## Important blocker found and FIXED in integration contracts

The existing 071 any-checkpoint recovery script emits a top-level QA field `final_061_ROM_sha256` plus nested `full_061_source_report.result_061_ROM_sha256`, but the checkpoint075 `--baseline-qa-json` code formerly demanded ONLY a top-level `result_061_ROM_sha256`. Thus even with a correct recovered 039–043 ZIP and a valid composite 061 ROM, the 075 builder would wrongly reject the 071 report.

**Fixed `tools/build_quiz_relocated_81_jobwait_075.py`**: `validate_061_baseline_report()` now accepts and cross-checks the direct 061, 070 original-043 ZIP, or 071 any-checkpoint ZIP format, requires all supplied nested and top-level ROM SHA fields to agree with the actual bytes, checks reported IPS SHA when present, checks source ROM provenance when present, enforces the correct report status and untested flags, and validates the expected **V2 glyph pointer value `0x9A74` at ROM `0x2975E`** in the actual staged ROM before modifying it. A fake QA file with wrong SHA cannot trick the real byte-source builder into accepting another game.

## New ONE COMMAND → ONE combined cumulative test IPS

Added `tools/recover_merge_061_81_one_ips_076.py`:

1. Open exactly one **user-owned** historical ZIP or IPS from checkpoint **039, 040, 041, 042 or 043**, selecting stage by matching the historical exact patch SHA/size (not filename).
2. Automatically rebuild each missing stage to exact **043**, then the canonical V2/G0/G1/Story/Quiz cumulative **061** chain, validating stage hashes and full source-ROM IPS replay.
3. Verify the generated 061 report format, byte-based QA SHA values and **real Vietnamese V2 font pointer**.
4. Add the **81 full Quiz answers** using the original 65c816 copy/poll guarded source builder, preserving the original Japanese script records and native graphics/font baseline; validate resulting full two-megabyte clean-original-ROM IPS playback.
5. Write **only one final cumulative clean-ROM IPS** and comprehensive JSON QA; **no intermediate copyrighted ROM images**, never mark actual emulator acceptance.

Reproduction (example historical ZIP filename is illustrative, not a file recovered in this session):

```bash
python tools/recover_merge_061_81_one_ips_076.py clean_original.sfc original_checkpoint041.zip --ips Chibi_061_plus_81_TEST_ONLY.ips --report Chibi_061_plus_81_QA.json --allow-untested
```

**No actual integrated cumulative IPS was built in this checkpoint**: the exact original 039–043 ZIP/IPS bytes are absent from active accessible file paths, even though some historical Library filenames remain visible in metadata. Passing source-code GitHub CI cannot replace original missing font/graphics binary data.

## Real automated CI and safety checks

Added `tools/selftest_merge_076.py` to GitHub Actions. It imports the actual 061/070/071/075/076 functions without needing game ROM, verifies **three supported QA-report formats** and **eight intentionally corrupted/unapproved provenance cases** (wrong ROM SHA, wrong nested SHA, wrong IPS SHA, original-ROM identity mismatch, fake checkpoint identifier, unknown status, false release approval, missing reported ROM hash).

- [Chibi SNES source localization checks — run 38217131132](https://github.com/RVTGMzz/VHSNES/actions/runs/38217131132): **SUCCESS**, including the one-archive 076 QA contract test, 381-source / 279-staged record audit, and 075 per-answer render/wait test.
- Earlier [graphics static CI](https://github.com/RVTGMzz/VHSNES/actions/runs/38217105129) also passed. None is an emulator pass.

## Exact remaining milestone

The user needs to supply or expose the raw bytes of **just ONE historical checkpoint 039–043 IPS/ZIP**. With that, the newly combined builder can attempt an integrated V2 + 81 Quiz candidate; any failed static guard must be repaired, not bypassed. A real SNES emulator must then verify long-choice visual widths, fonts, Japanese/Vietnamese mixed Kanji, correct answer selection, quiz transitions and game stability.

**Official Quiz staging remains 279/381** (the 81 choices are technical source-code prototypes, **not** accepted gameplay integration). Still pending: 21 non-answer Quiz source rows (including nested/unsafe scanner fragments), 4 longer Fortune cases, G3 win/lose/end screens, comprehensive Story/menu and final font QA. User preference: content first, typography polish last; avoid serial unplayable micro patches.
