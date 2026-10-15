# Checkpoint112: cumulative integration and remaining-text review

Date: 2026-10-15. Latest cumulative IPS SHA256 `06750e72ca6e51b6db6603ab10949be4631049b8e0988e4149231b6dec6dcfb1`.
ROM SHA256 `30aa68f493d01844ed2d421394b85879e99b9fa98a4bb4923fed591be2dbdfb0`.
Whole-game completion remains false. Source-only GitHub104 Karaoke audit is retained; binary104 character names is a separate local build stage.

The one-command builder is `tools/build_cumulative_112.py`, using the same original ROM, historical043 ZIP, Tahoma Bold and Tahoma regular as103. It applies104–112 in sequence and emits one clean-relative IPS. No ROM, IPS, emulator or font binary is committed.

Integrated four romanized character nameplates; Karaoke title/options and28 canonical lyric fields; Paint splash/help/buttons; three balloon names and introduction captions/options; three complete rules explanations;15 stage-name pointers; Quiz end statistics and No; remaining setup duration/device strings. Native music/timing tables, IDs, grading and statistics arithmetic remain unchanged.

Quiz now clears all32 bitmap columns over the original three six-row clearing steps via native85:8D8D; the old17-glyph blank records only cleared136px after compact spacing and left old text at the right. Native fixture reproduces the old condition and now shows clean statistics.

Validation: cumulative rebuild;20 existing source checks;5908 executed Karaoke spacing-hook cases; remote104 source audit executed locally. Native Snes9x50-question/150-selection sweep is a WRAM-injected test, not natural playthrough or semantic certification. Fresh final-question fixture seeded49 prior correct answers, then native answer/transition produced50/50/100%. Native VS setup through one entire match/result passed; three rules screens, character selection, balloons, Quiz18, Fortune, Paint splash and Karaoke captured. Resource audit examined162 type0 package candidates and365 unchanged decoded sources, no unexpected changes. Active507-field text audit found no unexpected native text.

## Confirmed remaining and limits

-19 original credits script records still contain Japanese roles/staff names, range1DED8..1E2D8. Translated CSV roles have not been integrated.
-Runtime Karaoke canonical line2B675 still expresses conditional desire rather than obligation. Five remote104 observations primarily concern the unused singable draft; only this canonical line is confirmed here as needing this semantic correction. Timing/singability remains unverified.
-Two Quiz39 Kazuo Kanji choices intentionally distinguish identical romanizations; original copyright owner notices are preserved.
-Ending, all15 actual stage selection screens, mouse/time-unlimited branches, Paint erase/exit dialogs need further direct runtime verification. The attempted110 stage screenshots captured gameplay and are NOT valid stage-selector evidence.
-Remaining substring candidates include inactive Fortune copies and internal debug strings; their count is not a count of visible untranslated text.

Use `audit_active_text_103.py`, `audit_remaining_text_112.py`, `audit_resource_owners_108.py` on the final IPS. Detailed local evidence and user delivery are in outputs/ChibiMaruko_112_Recheck_TEST.zip; no binary artifacts belong in the source branch.

Memory safety: do not allocate by scanning FF runs. Earlier unpublished experiments encountered FF inside live compressed rules17736 and resource68066; final builders use guarded known resource tails/retired owners and final resource audit preserves both. Native Paint requires the original768 consecutive canvas tiles and native completion side effects. Intro uses exact partial packages;17F9A is the prior Paint package terminator.
