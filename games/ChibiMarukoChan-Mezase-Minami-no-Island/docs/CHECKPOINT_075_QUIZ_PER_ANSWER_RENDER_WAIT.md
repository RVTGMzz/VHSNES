# Chibi Maruko-chan SNES — Checkpoint 075: Quiz text-job completion wait REVERSES the checkpoint074 display inference

Date: 2026-10-12 · Branch `chibi-maruko-bootstrap-01` · exact original user-owned Japanese SFC SHA256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`.

## Important scientific correction

Checkpoint073 correctly discovered the native Quiz copier reads **66 bytes** per answer. Checkpoint074 correctly measured that the *three source-copy destinations in WRAM* start only 32 bytes apart (`$7E8000`, `$7E8020`, `$7E8040`) and found **29/81 complete Vietnamese records longer than 32 bytes**. But checkpoint074's claim that **18 answer choices will definitely display corrupted** assumed the program loads all three records **before** rendering any of them. That crucial ordering assumption was unsupported.

**Direct original 65c816 machine code from the real SFC disproves the assumption.** All three answer-loader functions COPY the native record, call the text handler with the corresponding WRAM buffer, then **poll until the text job is no longer active** before returning. A later choice's copy may indeed overwrite earlier WRAM bytes, but those bytes have already passed through a completed text job according to the engine's own status flag. Exactly how the engine draws or caches pixels, and whether wide names fit on screen, still require emulator testing.

### Actual original SNES execution sequence (direct byte assertions)

| Stage | Original file offset / CPU target | Verified original instructions |
|---|---|---|
| Answer 1 | `0x30740` | `JSR $8762` (copy 66 bytes to WRAM `$7E8000`) → `LDY #$8000` → `JSL $85804B` → `JSL $858160; BCC -6` (wait loop) |
| Answer 2 | `0x307BA` | `JSR $8762` (copy to `$7E8020`), add `$0200` to a position/control word at +2 → `LDY #$8020` → `JSL $85804B` → `JSL $858160; BCC -6` |
| Answer 3 | `0x3082B` | `JSR $8762` (copy to `$7E8040`), add `$0400` to a position/control word at +2 → `LDY #$8040` → `JSL $85804B` → `JSL $858160; BCC -6` |
| Text-job setup | `0x28156` / `$858156` | `LDA #$0002; STA $1F80; STY $1F94; RTL` — arm text job and store text source Y |
| Text-job poll | `0x28160` / `$858160` | `LDA $1F80; BEQ completed`; if active, runs job processing and returns **CLC**; if inactive, returns **SEC** |
| Native 66B copy | `0x30762` / `$878762` | `LDA #$0020`, 33 16-bit copy iterations from original bank06 pointer into `$7E8000+X` |

The exact bytes were verified **on the mounted original Japanese retail SFC**, including the `90 FA` (BCC -6) suffix in all three actual callers, the text-job start at `0x28156` and the carry-flag return paths at `0x28160`. `$85804B` is the actual wrapper taking Y, processing a text job and returning; the subsequent wait explicitly prevents the calling routine from ending while the engine reports an active text job.

Important limitation: polling until a job is inactive proves the program **waits for its processing job**, not that every extra glyph fits a selection box or that source relocation passes every renderer/answer-correctness edge case.

### Corrected meaning of 29 overlong records and 18 overlaps

The source-only byte geometry in 073–074 is still valid:

- **81** complete canonical Vietnamese choices are representable and fit original unused bank06 ROM source slots of 68 bytes each (maximum original copy window 66B; largest actual text record **53 bytes**).
- **29/81** record sizes exceed the 32-byte spacing of the original **WRAM destinations**; **18** are choices 1 or 2, which would have their RAM bytes overwritten *if those buffers were needed after a later choice's copy*.
- A simulated snapshot **at the immediate renderer handoff** retains **81/81 full records**.
- A deliberately hypothetical snapshot **after all three copies without allowing the jobs to finish** retains only **63/81** complete records. This *deferred-rendering* model does **not** match the original call/poll ordering.
- **None of these dataflow checks proves visually correct 81-choice gameplay**, but checkpoint074's categorical 18 visibly corrupted choices and the stated *necessity* of modifying RAM buffers were too strong.

The 52-choice <=32-byte builder from 074 remains a conservative isolated candidate, not a new approved completion count. **Do not delete any of the 29 long canonical translations** or alter their semantics to force a 32-byte cutoff.

## New source and automated regression QA

- `tools/audit_quiz_copy_render_order_075.py`: assertions pinned to original game bytes of all three choices, the `$85804B` wrapper, text-start `$858156`, text-poll `$858160`, and all three `JSL $858160; BCC -6` waits. A ROM-free comparison model uses 81 canonical Vietnamese source records and distinct byte tokens per option. It reports immediate-handoff **81/81 intact** versus hypothetical deferred-end **63/81 intact**, with clear no-emulator/no-release flags. Run `--original-rom clean.sfc` to also validate the exact retail binary.
- `tools/audit_quiz_wram_stride_074.py` and `tools/selftest_quiz_wram_layout_074.py` were corrected: 18 is now **conditional later-overwrite of still-needed RAM bytes**, not a guaranteed screen corruption claim; automatic safety flags still reject declaring the actual game done.
- `.github/workflows/chibi-snes-source-qa.yml` now runs both original source-length audit and original execution-order model, so future turns must not silently reintroduce the unsupported deferred-copy assumption.
- New `tools/build_quiz_relocated_81_jobwait_075.py` restores the complete **81-answer static original-ROM relocation candidate**, but adds a fail-closed check that the exact original game binary still contains the three render-and-wait paths. It reserves the original full 68-byte-per-choice source cells, leaves all Japanese inline originals unchanged, and allows only designated pointer/unused-bank/source/LoROM-checksum bytes to change. It pins the earlier independent in-memory source-only SHA values and cannot be called release-ready without actual emulator acceptance. It optionally merges over an exact approved stage061 V2-base IPS/QA **if and when one historical checkpoint039–043 file is available**.

One previous CI iteration revealed a test-fixture bug (all simulated records had identical filler bytes, hiding overwrites); fixed it by giving every Quiz slot a distinct byte token. The immediately following GitHub Actions run passed the regression model. For the final 075 commit, consult the live workflow result; syntax/source-only CI does not run the optional original-ROM-supplied byte builds.

## Current practical next steps

1. **Emulator validation is now the most valuable game milestone**: run the corrected *native Japanese* 073 relocation fixture; check long text appears and option selection remains correct. No 039–043 archive needed for that test.
2. To actually view Vietnamese glyphs, recover a user-owned historical IPS/ZIP from **any checkpoint039–043** using the previously committed 071 recovery script. The raw bytes of those archived ZIPs are still unavailable through existing Library connector access.
3. On that integrated V2 base, test a single fully Vietnamese long option, then test very long labels and distinguish the `(一雄)` / `(和雄)` choices. Only after visible/traversal tests attempt approval of all 81.
4. Continue unresolved 21 non-answer Quiz source rows, four long Fortune items, G3 game-result/ending graphics, and end-to-end font/menu story QA.

**Official prepared Quiz source count remains 279/381; 81 original answer alternatives are source-byte engineering candidates, not emulator-approved strings.** No original retail ROM, font files or production-claim IPS binaries committed to GitHub.
