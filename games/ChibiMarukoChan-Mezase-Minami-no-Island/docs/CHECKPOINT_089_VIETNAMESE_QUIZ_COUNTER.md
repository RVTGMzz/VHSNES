# Checkpoint 089 — Vietnamese Quiz counter

2026-10-14. User flagged the residual Japanese 第1問 in actual Quiz screenshots.

`build_quiz_counter_089.py` replaces both fixed native heading records at
`0x31536` / `0x31543` with V2 **Câu**, preserving each record's byte length,
native row control and terminator. The original decimal renderer remains; its
column input is moved to follow the longer Vietnamese label. Answer pointers,
randomized ordering, grading metadata and title assets stay untouched.

Snes9x captures show the label at question counts **1, 10 and 50**, using saved
native Quiz initialization and WRAM count injection. No Japanese characters
remain in this counter. This does not certify every other game screen.

Final cumulative test IPS is 68,500 bytes / 2,550 records:

- IPS SHA256: `7ac471724c3d0867ecea1defb18844798fa647b8c325d9deb309677e6b6508ca`
- Result ROM SHA256: `9c88d9ef2d84f3794e3a8da6ef2f9bddb77c68998a6570408011536fb3274fa8`
- Checksum / complement: `DC04` / `23FB`.

Rebuild from original ROM and historical ZIP in one command with
`tools/build_title_readable_088.py`, the two local font paths, output IPS/JSON
paths, and **`--translate-quiz-counter`**. Earlier 087 binary/runtime evidence
and 088 title evidence remain separately labeled; final artifact includes all
three rounds. Apply final IPS once to the exact clean original, never to a
previously patched image. No original ROM or font files are delivered.

Whole-game completion remains false. Remaining blockers are the preexisting
G1/Story graphics defects, four Fortune overflows and Japanese Fortune artwork,
G3 results/ending, source-alias semantic review and natural full-game QA.
