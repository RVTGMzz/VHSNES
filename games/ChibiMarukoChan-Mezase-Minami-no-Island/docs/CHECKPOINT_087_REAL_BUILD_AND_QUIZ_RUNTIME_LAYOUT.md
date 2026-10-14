# Checkpoint 087 — real cumulative build and Quiz runtime layout

2026-10-14. Started from branch HEAD `4115d8fe9c2f101ef8ae667246f6ca0550433552`.

## What the supplied binaries proved

The exact user-owned clean 2MiB ROM passed the immutable SHA256 contract. The
user's historical ZIP contained the exact SHA-approved 043 IPS. Recovery rebuilt
061 successfully, but the first real 076 cumulative build FAILED: its 81 answer
cells at `0x36A00..0x37F84` overlapped the historical G0 compressed title stream
at `0x36907..0x37663`. Earlier ROM-free source CI could not detect this collision.

`relocate_title_asset_087.py` moves the exact 3420-byte G0 packed stream to
`0x596FE..0x5A45A` (24-bit LoROM `$8B:96FE`), updates its existing loader pointer
at `0x12095`, verifies the packed SHA and decoded bytes/postprocess, checks both
destinations against the actual clean and 061 ROM, and restores the old FF gap.
Historical 039–061 builders, manifests and fingerprints remain unchanged.

## Actual emulator findings and functional correction

Snes9x/libretro CPU/PPU execution first confirmed startup, title artwork/credit,
menu entry and Quiz rendering. The 13px native layout then visibly clipped long
choices and wrapped the 25-glyph allowance continuation into the answer area.
Question portraits also covered answer text.

`build_quiz_layout_087.py` runs AFTER all guarded 079–086 content integrations:

- Quiz bank06 and its `$7E:8000..808F` answer buffers use an 8px pitch, 12px left
  origin and 28-column wrap; other source banks keep original 13px/19 columns.
- Both tilemap and bitmap-destination word-table consumers AND the shift-table
  consumer are hooked. The previously overlooked `ADC.l $859670,X` at `0x291DF`
  must use the same geometry as `LDA.l $859670,X`; changing only the two old
  hooks reproduces the fragmented typography seen in earlier experiments.
- Both parser wrap comparisons are hooked (`0x28335`, `0x2841B`). The stored
  parser bank `$001F86` supplies context; transient DBR is not used.
- 150 answer headers move from column 6 to 4, nine number/highlight headers
  move from 4 to 2. Pointer ordering, grading metadata and font bitmaps are kept.
- The question-only portrait loader places that sprite offscreen at X=256.
  This deliberately prioritizes legible answer choices over decorative art.
- Four native Kazuo Kanji occurrences receive display spaces to accommodate
  their wider original ink. Canonical answer strings remain unchanged.
- Allowance continuation becomes **“Mỗi ngày được mấy yên?”**; the parent names
  Maruko. It stays in one line with an inset inside the paper.
- Age-nine question slot 18 gets a complete new bank06 main record in the freed
  `0x36907` gap: **“Maruko cung Kim Ngưu,” / “lên 9 tuổi ngày nào?”**. The original
  Japanese main record at `0x31F1F` stays intact. Native question pointer
  `0x3116B` points to the new record; the direct-ROM question renderer was
  exercised in Snes9x. Four V2 spaces indent the second line after native wrap.

The emitted-hook selftest executes 972 cases including native fallback,
source-bank boundaries, both spacing consumers, ADC carry preservation, and
wrap thresholds. All 19 previous workflow source checks passed locally with
Python UTF-8 output enabled; the new 087 selftest also passes.

## One cumulative test artifact

| Property | Value |
|---|---|
| IPS size | 67,908 bytes |
| IPS records | 2,520 |
| IPS SHA256 | `5d380dc6d4a14b38615848236ee6991f9ced0d357d7d451658c00f8866dd49ec` |
| Result ROM SHA256 | `9b4ad402d679ca9cf0b75e65b0b834467603ae91d88f41ed93a8fd2fbb71562b` |
| Checksum / complement | `77FF` / `8800` |
| Original ROM base | exact contract ROM; apply IPS once to the clean original |

The builder writes only IPS and JSON. The emulator loads the patched image in
memory. No copyrighted ROM, original font assets, emulator core or savestates
are committed or included in the delivered patch package.

Rebuild with `tools/recover_merge_061_81_one_ips_076.py` using the original ROM,
one exact historical 039–043 archive, `--ips`, `--report`, and `--allow-untested`.
That old filename now produces the complete 087 chain.

Reproduce runtime QA with a 64-bit Snes9x libretro DLL, Python, NumPy and Pillow:

```text
python tools/run_snes9x_qa_087.py ORIGINAL.sfc PATCH.ips snes9x_libretro.dll --out LOCAL_QA --sweep
```

The harness boots from reset, captures title/menu, enters Quiz, saves after
native initialization, injects each of 50 valid question-table slots into WRAM,
and exercises all three selections (150). It captures each question,
highlight, grade animation and response. This is real emulation with targeted
state injection, NOT an uninterrupted natural 50-question playthrough. The
output report pins ROM, IPS and core SHA256. Automated screen generation is
not itself a certification of all grading keys or editorial correctness.

## Remaining work and exact metrics

Historical distinct Quiz staging remains **279/381**, with the 81 answer and
three nonanswer candidates now present in a real integrated test build.
This round adds **zero new independent scanner IDs**: age-nine is a semantic
repair of a staged parent. Do not infer whole-game completion from these counts.

The targeted 50-question/150-selection sweep runs in Snes9x; question images
were visually inspected as a contact sheet, plus large allowance, age-nine,
long-name and Kanji examples. Correct/wrong animations and explanations were
observed, but all grading keys have not been independently certified.

Still NOT complete: four Fortune overflows, G3 result/ending graphics, residual
Japanese Quiz counter, all remaining source-alias semantics, natural full game
playthrough and full Story/other-mode visual QA. Runtime smoke tests expose
preexisting broken/partial G1 menu and Story Start graphics, plus Japanese
Fortune entry artwork. These are recorded defects, not approved screens.

Content and functional display stay the priority. Next work should repair the
remaining graphics/resource reuse and Fortune fields against actual execution;
do not resume unverified isolated source-only micro-patch cycles or cosmetic
font churn. This is a test candidate, not a finished Vietnamese release.
