# Checkpoint 074 — Original Quiz answer read windows overlap

Independent original-ROM audit (2026-10-12): exact 2 MiB Japanese SHA256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`. All 150 answer pointers and 150 native record prefixes verified. Within the 50 question groups, all 100 adjacent answer pairs begin only 11–31 bytes apart, while the native routine copies a 66-byte window. This overlap exists in the unmodified Japanese game.

Consequently, the 2-byte read-window overlap in the historical 072 probe is not, by itself, proof of a crash. The disjoint 68-byte slots in checkpoint 073 are a conservative testing design, not an engine requirement. The older 067 bank-boundary risk remains distinct. The tightly packed 069 answer experiment is not disproven solely by overlap; text width, font rendering, pointers, answer grading and emulator behavior are still unverified.

New source-only checker: `tools/audit_quiz_native_overlap_074.py`. The existing CI compiles it; the independent original-ROM check was executed locally. No new game strings, production IPS, or emulator acceptance. Quiz staging remains 279/381; missing historical 039–043 IPS/ZIP still blocks integrated build.
