# Checkpoint116 — credits, gameplay coverage and actual stage-caption clipping

Date:2026-10-15. Latest single cumulative IPS SHA256 `910e77ab5da5235c8aae1c5d9d3dbf3e697728466039250e8a4f82d45069f4bd`.
Patched ROM SHA256 `bc381e2bc32df0ee6226d88b7ebcf50b3e8091379a67e2593df66dc3589f2d34`.
One-command builder:`tools/build_cumulative_116.py`; same original ROM, historical043 ZIP, Tahoma Bold/regular arguments as112. Full rebuild exactly matches the incremental build. Whole-game complete remains false because a natural full Story victory playthrough is not certified.

113 translates all19 credits roles/company captions, retaining original staff names and replacing a single inaccurate canonical Karaoke line via explicit runtime JSON override. Credits repack953/1063B in original83:DED4..E2FB pool;19 native pointers move, five trailing aliases and script timing stay unchanged. Credits retain native13px spacing so Japanese staff names do not overlap; helper81:F096 filters only that source range before the four existing compact selectors. Pure selectors now live in layout_contexts_109.py. Native source-only helper test executes9968 cases, including both sides of every affected range and original M/C preservation.

114 fixes the previously untested actual stage-selection Japanese heading. It reuses native BG1 tiles151..201, free outside the banner, leaves scene/palette intact, and disables only heading actor62. Each of the three native type0 packages redirects its BG1 map and repurposes the unused heading OBJ upload as a partial BG1 glyph upload. Original common OBJ sourceC706F stays intact for other owners. New data uses the guarded tail after109's complete palette, D6512..D6D45; no FF-run allocator is used.

115/116 fix the user's actual clipping screenshots. Both ordinal and full caption now live inside the paper, wrap at17 characters into at most two lines and center with the real BG3 scroll6px. Only the paper's bottom extends8px. Stage IDs/table order/native input stay unchanged. The first attempts exposed stale old row text: native stage text writes did not clear rows after multi-line captions.116 wraps only the native stage text job at84:9B92, clearing full-width rows22..27 through111's native clear-and-DMA helper before the unchanged text job/wait. The wrapper at81:F0C0 preserves A/P and the pointer in Y. Source pools remain owned by110;783/851B used. The final screenshot auditor decodes PPU BG3 pixels, applies actual scroll and rejects any caption/ordinal ink outside[58,186,202,218]. All15 pass; do not reuse earlier overflowing contact sheets.

## Native Snes9x evidence on the exact116 IPS

- Public `run_snes9x_qa_087.py --stage-sweep --full-stage-matches` enters all15 actual selectors via controller input (no WRAM stage injection), exercises each match entry and runs one complete timed match per family. End controllers35/55/79, result state7, all passed. `audit_stage_caption_runtime_116.py` validates all15 actual snapshots.
- Quiz50-slot/150-selection sweep uses WRAM question selection; it is not a natural full Quiz run or semantic grading certification. Seeded last-question fixture produces50/50/100% statistics with no stale text.
- Controller-only Story start through first minigame/loss/continue, retry branch and quit/Game Over/menu branch passed. Main menu controller is0F, not00 or07. Ending/19 credits reached via explicit native ending-dispatch/completion-flag fixture; no ROM edits by harness, not a natural full Story victory.
- Paint erase/quit confirmation and return paths tested;13 Karaoke pages reached their native text-job ends. Corrected page9 visibly tested. Fortune/Taurus question captured. Mouse/disconnected emulated device identification exercised, real mouse motion/hardware not certified.
- Resource regression:162 package candidates,364 unchanged decoded sources, no unexpected owner changes. Original68066 and17736 remain intact. Active507-field Quiz/Fortune audit passes with only intentional Kazuo Kanji alternatives.20 existing source checks and new emitted-hook checks pass; full syntax compilation passed.

## Remaining limits

Original staff names in credits, two distinguishing Quiz39 Kanji alternatives, copyright owners and some original scenery signs remain Japanese intentionally. Do not claim every pixel of Japanese has been removed. Karaoke singability/syllable timing and real SNES mouse use remain uncertified. Natural winning progression through the complete Story is still a manual acceptance task. Do not call fixture completion a natural playthrough.

User delivery:`outputs/ChibiMaruko_116_RC.zip`, one cumulative IPS plus actual screenshots and hash-bound JSON. Never commit ROM, IPS, font, core or savestate binaries to the source branch.
