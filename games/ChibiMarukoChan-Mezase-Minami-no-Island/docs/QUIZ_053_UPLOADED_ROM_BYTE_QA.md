# Chibi SNES — 053 Quiz16 physical byte QA on actual uploaded clean ROM

Date: 2026-10-11. Branch: `chibi-maruko-bootstrap-01`.

## Source and scope

User supplied exact **2,097,152-byte Japanese retail clean ROM**. SHA-256: `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`. All 16 checkpoint053 original Japanese CP932 spans match the actual ROM, including original `816F` line terminators. Original Unicode Vietnamese source remained unchanged.

A scanner defect at `0x340C0` was resolved: **six bytes of original ASCII spaces** before the actual `すきなものってなに？` starting `0x340C6`, **eight bytes of spaces after** the ten CP932 characters, then `816F`. The builder now changes only the ten double-byte text cells; leading/trailing layout bytes and `816F` remain byte-exact.

## Physical experiment performed locally

An isolated text-only overlay of 16 source-approved Quiz captions was written physically into the exact Japanese 2MiB ROM in-memory, after mapping each Unicode character to the existing project V2 `84xx` code table; the source original field lengths, string controls and surrounding bytes were guarded. An independently implemented IPS parser reapplied the resulting IPS to the clean ROM and reproduced the overlay target **byte for byte**.

| QA metric | Result |
|---|---|
| Original Quiz fields checked | 16/16 |
| Approved writable source text byte positions | 134 |
| Actually changed byte positions | 112 |
| Original layout padding / `816F` preserved | PASS |
| Text-only IPS bytes / records | 310 / 38 |
| Text-only IPS SHA-256 | `8ae0adc95fcb69c9aab141fd10004dc698f295be3e0a4fd2d5399f8382709f7e` |
| 043 + 044 + 045 + 046 + 047 + 048 + 053 full merge | **NOT BUILT** |
| SNES checksum of text-only experiment | **NOT REGENERATED** |
| Actual gameplay / emulator QA | **NOT TESTED** |

**Important:** The Japanese clean ROM lacks the Vietnamese custom V2 font, and this overlay intentionally does not change the SNES checksum. Thus the experiment is **NOT a playable localization, nor a release candidate**. It only verifies these 16 precise physical text regions. The resulting local text-only IPS is deliberately **not released** to the user, per their request not to receive intermediate patches.

## Missing input for full combined game

Earlier checkpoint 043 published an IPS SHA-256 `d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50`. Library metadata contains `Chibi_043_G0G1_176Fields_Story58_Content_First_UNTESTED.zip`, size 22,558 B, but its contents could not be materialized into this run. The clean ROM is now verified. Once checkpoint043 ZIP/IPS is provided as an accessible conversation attachment, use `tools/rebuild_content_first_048_full_chain.py` followed by `tools/build_content_first_053_quiz_16.py` and verify all pinned hashes and controls on the final combined ROM.

Continue remaining long Quiz text, G2 rules, G3 results and finally font/layout runtime QA. No false runtime PASS.
