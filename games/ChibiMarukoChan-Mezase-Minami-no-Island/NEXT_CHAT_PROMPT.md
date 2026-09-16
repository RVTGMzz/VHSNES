Tiếp tục Chibi Maruko-chan SNES từ `HANDOFF_CURRENT.md` trên branch `chibi-maruko-bootstrap-01` của repo `ronvotri/Viet-Hoa-SNES`.

Canonical clean ROM SHA1: `08a2415362f69788ec76b1a36044dc1f1a5f2ea1`.

Probe 006 runtime PASS với screenshot `TĐST1234`, chứng minh visible-menu path là `2-byte game code -> 16-bit glyph ID -> custom 12x12 raw 1bpp bitmap`.

Probe 007 chứng minh dedicated Vietnamese codepage `0x84xx` hoạt động runtime nhưng typography V1 yếu. Probe 008 tiếp tục boot/render đúng nhưng handcrafted Font V2 bị user đánh giá xấu hơn V1, nên classification là BOOT/ENCODING PASS + TYPOGRAPHY FAIL.

Current test là **Probe 009 FE4-reference Font V3**. User đã cung cấp `Seiseno no Keifu Vietnamese(1).smc`; exact reference full SHA1 `2556860f8f51d0895c191a5f614c9088fc8fd98e`. Đã reverse font dialogue FE4 trong body range `0x128000..0x12BBFF` (0x3C00 raw 2bpp), lấy raster Latin/Vietnamese 8x16 và adapt thành Chibi 12x12. Không copy renderer/address/codepage FE4.

Đọc `docs/VI_FONT_V3_FE4_REFERENCE.md` và `HANDOFF_CURRENT.md`. Files: `translation/codepage/vi_codepage_v3_fe4ref.csv`, `translation/codepage/vi_glyphs_v3_fe4ref.json`, `tools/generate_vi_glyphs_v3_fe4ref.py`, `tools/probe_visible_menu_009_fe4ref_font.py`.

Probe 009 expected rows: `Âm thanh`, `Bói!!`, `Đấu đội!`, `Vẽ!!`, `Maruko?`, `Ổn rồi`. Static CLEAN-ROM build PASS: checksum `0x04DF`, complement `0xFB20`, SHA1 `94c0c2c303dd824ee617ec765a645a4a7adefde9`, SHA256 `072abd670a2e0dca888391f74b3104ba853ac49ec6144373e820eb95a18a782b`. Runtime screenshot pending. Do not call V3 typography Runtime PASS before screenshot.

Meaning-first translation remains 1,018 release-intent rows. Do not bulk-patch yet. Keep graphics/tilemap text (`どれにする？`, Start/Password/Continue/ending family) separate. Always build from CLEAN ROM, preserve source identity/control bytes, use diff-surface/checksum gates, and state runtime claims narrowly.