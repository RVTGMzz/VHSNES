Tiếp tục Chibi Maruko-chan SNES từ `HANDOFF_CURRENT.md` trên branch `chibi-maruko-bootstrap-01` của repo `ronvotri/Viet-Hoa-SNES`.

Canonical clean ROM SHA1: `08a2415362f69788ec76b1a36044dc1f1a5f2ea1`.

Probe 006 runtime PASS với screenshot `TĐST1234`, chứng minh visible-menu path là `2-byte game code -> 16-bit glyph ID -> custom 12x12 raw 1bpp bitmap`.

Probe 007 screenshot tiếp tục chứng minh dedicated Vietnamese codepage `0x84xx` và multi-glyph bank hoạt động runtime, nhưng typography V1 chưa đạt: nhiều dấu quá yếu/khó đọc. Classification: codepage semantics PASS, font quality NEEDS REVISION.

Current test là **Probe 008 Vietnamese Font V2**. Đọc `docs/VI_FONT_V2.md`, `docs/REVERSE_FONT_001.md`, và `HANDOFF_CURRENT.md` trước khi sửa. Files: `translation/codepage/vi_codepage_v2.csv`, `translation/codepage/vi_glyphs_v2.json`, `tools/generate_vi_glyphs_v2.py`, `tools/probe_visible_menu_008_font_v2.py`.

Probe 008 expected rows: `Âm thanh`, `Bói!!`, `Đấu đội!`, `Vẽ!!`, `Maruko?`, `Ổn rồi`. Static CLEAN-ROM build PASS: checksum `0x8DFC`, complement `0x7203`, SHA1 `605240bb3ca81883e6c4f06e76c642ad84be59a1`, SHA256 `7b9a447d7d3c19631699cfa9daa17124c08998f68878730ba89d5ee4fc6e31b5`. Runtime screenshot pending. Do not call Font V2 runtime PASS before screenshot.

Meaning-first translation remains 1,018 release-intent rows. Do not bulk-patch yet. Keep graphics/tilemap text (`どれにする？`, Start/Password/Continue/ending family) separate. Always build from CLEAN ROM, preserve source identity/control bytes, use diff-surface/checksum gates, and state runtime claims narrowly.