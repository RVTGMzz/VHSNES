# Chibi Maruko-chan SNES — Checkpoint 026: USER RUNTIME TYPOGRAPHY FAIL

Date: 2026-10-10. Branch: `chibi-maruko-bootstrap-01`.

## Critical status correction

The user played the **Probe008 V2 G2 line-scoped 9px X-width diagnostic checkpoint 025** and supplied a **real in-game screenshot**. The rendering is NOT acceptable. The game visibly reaches the translated text, but Vietnamese letters are far apart, their shapes look sparse/fragmented and diacritics lack coherence.

**Checkpoint 025 now has USER RUNTIME VISUAL FAIL, not emulator UNTESTED.** Static 18,696 synthetic 65816-subset checks and binary/verifier checks do NOT invalidate the screenshot. The version must not be released or recycled as a known-good build. The user should not be asked to keep testing this ROM.

- Tested diagnostic ROM: `d4bd629003812578580e7a380e791d87fdf64614441394f1261df3951b9815dc` SHA-256.
- Screenshot (held in user conversation only, NOT uploaded to repo): SHA-256 `5fe322fe15746017ee1362daf9ffe0a275344f91b256bdd30732d033ceb62ee0`, size 952×381.
- Text identifiable from the ROM and displayed image: `Nói thẳng nhé!`, `Du học chớ ngại!`, `Luyện phản xạ!`. The screenshot suggests the content decoding works, but font spacing and quality do not.

## Quantitative screenshot measurements

An image-only, fail-closed regression analysis extracted black-ink left/right extents of the three G2 text rows (not OCR). The screen has a cropped viewport; the native 256-wide scaling is **approximate**, so measurements are *evidence for a likely path*, not CPU-trace confirmation.

| Text | Screen ink span | Approx. advance per symbol (native pixels) | Nearest expected pitch |
| --- | ---: | ---: | --- |
| Nói thẳng nhé! (opening quote) | 599 px | 13.73 px | 13px (not 9px) |
| Du học chớ ngại! | 672 px | 14.37 px | 13px (not 9px) |
| Luyện phản xạ! (closing quote) | 638 px | 14.62 px | 13px (not 9px) |

**Strong working hypothesis:** the 025 source-bank/offset selector fell back to its original **13px** table at runtime; likely the assumed incoming DBR `$83` or source pointer `$1F94` is different inside the active renderer than in the incomplete static microhook model. Another possibility is a difference between screen scaling, control flow and text replay. Only a debugger trace can verify the exact reason. **Do not claim this gate condition is proven.**

**Separate real defect:** font V2 uses narrow/sparse 1px strokes and cannot be called an acceptable Vietnamese font solely because all bitmap IDs roundtrip. Need full screen legibility testing and a denser font design after spacing works.

The screenshot visibly confirms scene can render text, NOT a clean typography result. The old Probe003 screenshot had already identified V5-thin as aesthetically unusable; do not conflate static pointer or checksum PASS with legibility.

## Immediate safeguards completed

- The script `tools/build_g2_probe008_line_scoped_9px_diagnostic.py` is **quarantined**. By default it aborts rather than creating the failed ROM; historical reproduction requires explicit `--reproduce-known-runtime-fail-025`.
- `tools/verify_g2_probe008_line_scoped_9px_diagnostic.py` continues to verify its structure but labels it **RUNTIME VISUAL FAIL**, not release-ready. An intact checksum is not quality acceptance.
- Added `tools/audit_g2_probe008_runtime_screenshot_025.py`. It recognizes **only the exact 2026-10-10 screenshot** by SHA-256, computes the bounded ink spans and reports `USER_EMULATOR_TYPOGRAPHY_FAIL`. It does NOT include or upload the screenshot, infer precise CPU state, or classify arbitrary images. Requires Pillow.

Reproduce with the user's local screenshot, if accessible:

```bash
python tools/audit_g2_probe008_runtime_screenshot_025.py "user-screenshot.png" screenshot-QA-026.json
```

Report recorded locally as `Chibi_G2_025_actual_screenshot_QA_026.json`.

## Next safe development sequence

1. **Do not send another untested candidate ROM as fixed.** The current QA gate is unmet. Advise the user to keep backup of their original clean ROM.
2. Capture a **real 65816 CPU trace** at source parser `$85:8340`, glyph lookup `$85:8E0C` and shift lookup `$85:90EE` while rendering these exact G2 ROM records. Record DBR, `$001F94`, X-width and table result. The assumed bank is not proof.
3. Determine why the new 9px offsets were not visibly applied. Verify three source records, text pointer provenance and fallback path. Do not broaden patches to Japanese menus without audited source evidence.
4. Once 9px path actually works, redesign overly thin V2 font with readable Vietnamese glyph weight, vowel modifiers and tone marks. Test multiple words and actual G2 scenes, not just isolated glyph atlases.
5. Only after runtime screenshot matches accepted readability and no crash/quote/wrap regressions should a candidate be promoted. Continue G0, G2/G3 and remaining menu localization later.

## Version matrix

| Baseline | Static QA | User-visible runtime | Ship? |
| --- | --- | --- | --- |
| Probe003 strict two-byte | PASS | G2 text path PASS, V5-thin typography FAIL | NO |
| Probe008 V2 font-only 13px | PASS | Not separately confirmed here | NO |
| Probe008 023 glyph-scoped 9px | Static PASS | known modeled 64px quote layout fault | NO |
| Probe008 024 line-scoped 9px | Static PASS | invalid live DBR assumption in hook 2 | NO |
| **Probe008 025 stack-safe line-scoped 9px** | Static PASS | **USER REAL SCREENSHOT TYPOGRAPHY FAIL** | **NO** |

**GitHub content:** source, documentation and audit scripts only. **No commercial ROM, ROM patch data or unredacted user screenshot committed.**
