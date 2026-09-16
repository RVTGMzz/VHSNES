Tiếp tục Chibi Maruko-chan SNES từ `HANDOFF_CURRENT.md` trên branch `chibi-maruko-bootstrap-01` của repo `ronvotri/Viet-Hoa-SNES`.

Canonical clean ROM SHA1: `08a2415362f69788ec76b1a36044dc1f1a5f2ea1`.

Probe 006 đã runtime PASS với screenshot `TĐST1234`, chứng minh visible-menu path là `2-byte game code -> 16-bit glyph ID -> custom 12x12 raw 1bpp bitmap`.

Current test là **Probe 007 Vietnamese Codepage V1**. Đọc `docs/VI_CODEPAGE_V1.md`, `docs/REVERSE_FONT_001.md`, và `HANDOFF_CURRENT.md` trước khi sửa. V1 dùng dedicated lead `0x84`, 160 Unicode entries, 121 custom visual glyphs, còn 11 safe blank slots. Tool: `tools/probe_visible_menu_007_vi_codepage.py`.

Probe 007 static PASS; expected six visible rows are `ĐẦY ĐỦ!!`, `được!`, `CÓ DẤU!!`, `Việt`, `Maruko?`, `Ổn rồi`. Build checksum `0xB46C`, SHA1 `9d890f1d00af6d893dcf07174ea66f8954c30382`. Runtime screenshot still pending. Do not call V1 runtime-proven before screenshot.

Meaning-first translation remains 1,018 release-intent rows. Do not bulk-patch yet. Keep graphics/tilemap text (`どれにする？`, Start/Password/Continue/ending family) separate. Always build from CLEAN ROM, preserve source identity/control bytes, use diff-surface/checksum gates, and state runtime claims narrowly.
