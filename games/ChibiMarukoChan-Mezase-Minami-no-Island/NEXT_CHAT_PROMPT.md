Tiếp tục Chibi Maruko-chan SNES từ `HANDOFF_CURRENT.md` trên branch `chibi-maruko-bootstrap-01` của repo `ronvotri/Viet-Hoa-SNES`.

Canonical clean ROM SHA1: `08a2415362f69788ec76b1a36044dc1f1a5f2ea1`.

Runtime evidence: Probe 006 proved custom glyph rendering; Probe 007 proved the `0x84xx` Vietnamese codepage; Probe 008/009 were typography failures; Probe 010 FE4-native-width was clearly readable but user asked for thinner/lighter strokes.

Current test is **Probe 011 FE4 Native Thin V5**. Read `docs/VI_FONT_V5_FE4_THIN.md`, `docs/REVERSE_FONT_001.md`, and `HANDOFF_CURRENT.md` before changes. Files: reuses `translation/codepage/vi_codepage_v3_fe4ref.csv`, plus `translation/codepage/vi_glyphs_v5_fe4_thin.json`, `tools/generate_vi_glyphs_v5_fe4_thin.py`, `tools/probe_visible_menu_011_fe4_thin.py`.

Probe 011 expected rows: `Âm thanh`, `Bói!!`, `Đấu đội!`, `Vẽ!!`, `Maruko?`, `Ổn rồi`. Static CLEAN-ROM build PASS: checksum `0x38C2`, complement `0xC73D`, SHA1 `45d06514306cd6d1a0cf0c65c6339527944199d4`, SHA256 `11b1b8c824be60dcdad8d9f287e916a245fe5edc42cdbb33855c02f25bf8f9bd`. Runtime screenshot pending.

Meaning-first translation remains 1,018 release-intent rows. Do not bulk-patch yet. Keep graphics/tilemap text (`どれにする？`, Start/Password/Continue/ending family) separate. Always build from CLEAN ROM, preserve source identity/control bytes, use dry-run/diff-surface/checksum gates, and never call whole-game Runtime PASS from a subsystem screenshot.
