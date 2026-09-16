Tiếp tục Chibi Maruko-chan SNES từ `HANDOFF_CURRENT.md` trên branch `chibi-maruko-bootstrap-01` của repo `ronvotri/Viet-Hoa-SNES`.

Canonical clean ROM SHA1: `08a2415362f69788ec76b1a36044dc1f1a5f2ea1`.

Current critical milestone: Probe 006 screenshot runtime-proved the visible menu path as `2-byte game code -> 16-bit glyph ID -> custom 12x12 raw 1bpp bitmap`. The first line rendered exactly `TĐST1234`, proving a custom Vietnamese `Đ` glyph in slot `0x0963`.

Read `docs/REVERSE_FONT_001.md` before modifying font/codepage. Next task: stronger global collision audit, freeze a Chibi-specific Vietnamese codepage, generate a real Vietnamese glyph set, then build one multi-glyph real Vietnamese phrase probe. Keep graphics/tilemap text (`どれにする？`, Start/Password/Continue/ending family) separate until its render path is proven.

Meaning-first translation currently has 1,018 release-intent rows. Do not bulk-patch them yet. Use CLEAN ROM for every build, preserve source identity/control bytes, dry-run before write, update checksum, and state runtime claims narrowly. Do not call whole-game Runtime PASS from subsystem evidence.
