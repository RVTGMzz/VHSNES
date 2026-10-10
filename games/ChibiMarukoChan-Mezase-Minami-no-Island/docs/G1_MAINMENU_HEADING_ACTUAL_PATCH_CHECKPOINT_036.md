# Chibi Maruko-chan SNES — Checkpoint 036: G1 main menu heading patched

Date: 2026-10-11. Repository RVTGMzz/VHSNES, branch chibi-maruko-bootstrap-01.

## Actual player-facing translation work

The original Japanese question on the MAIN MODE SELECTION screen (どれにする？ with its first line) has been identified as real SNES 4bpp sprite artwork and patched as TWO rows:

Chọn gì
đây?

The two-row split preserves the original 128 × 32 pixel sprite arrangement. The clean bold raster version was selected over an earlier heavy-shadow draft because the heavy draft made accents and letterforms too thick at SNES resolution. This is graphics replacement, NOT font codepage/renderer work.

## Proven retail execution path

On the exact 2MiB clean Japanese ROM (SHA256 e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956), the main-mode initializer at FILE 0x20047 contains opcode bytes:

A2 13 A2 22 55 E2 80

This loads package $82:A213 (file 0x12213) through JSL $80:E255. Package resource index 6 at file 0x12233 has five bytes 00 70 6F F0 98, sending source $98:F06F, ROM file 0xC706F, to VRAM word 0x7000.

This is the actual compressed retail sprite sheet; not debug prose. The original stream occupies 3,485 bytes and decodes to 8,192 bytes = 256 SNES 4bpp 8 × 8 tiles. Visual reconstruction directly shows Japanese mode labels and a selection arrow in tiles 0..191, plus the Japanese two-line heading in tiles 192..255.

Proof image in local working files: Chibi_G1_MainMode_AllSpriteTiles_036.png. This is an OFFLINE asset rendering, not an emulator screenshot.

## Real binary patch, audited

The experiment starts from exact previous GRAPHICS checkpoint 035 G0 title + Story Start/Password ROM (SHA256 77a207589857d2886059057151eaf3d47530032b726744fe739e991ff81a5b80).

- Replaced ONLY decoded tiles 192..255 (64 sprite tiles). All first 192 tiles, 6,144 decoded bytes, remain exactly byte-identical, protecting the other mode labels and arrow.
- Encoded the two-row Vietnamese heading using source palette index 2, no heavy shadow.
- New resource compresses to 2,428 bytes, down from the original 3,485, and is stored IN PLACE at file 0xC706F. The package pointer does not move.
- Original G0 title graphics and bank86 relocation, and G1 Story Start/Password sprite at file 0xBF95E, remain binary-identical.
- Allowed ROM modifications vs graphics035 are only within the heading resource span and header checksum bytes.
- New combined G0+G1+heading ROM SHA256: 2c8beee73e985c9a2690cc36ace335f05115c1a3e81b369e09d0cfb132117090.
- Checksum/complement: 0x3A35 / 0xC5CA.
- Combined IPS on exact clean Japanese ROM: 14,452 bytes, 263 records, independent replay returns the exact ROM SHA256.
- Independent source decompression and sprite tile comparison PASS.

IMPORTANT shared asset caution: this SAME source $98:F06F is loaded at VRAM word0x7000 by 13 UI resource packages. Their actual references were verified (package files 0x121F2, 0x12213, 0x12239, 0x12294, 0x122C0, 0x122E6, 0x1230C, 0x12332, 0x12358, 0x1237E, 0x123A4, 0x123F7, 0x12EE9). This establishes technical sharing, NOT that each screen displays the replaced tiles. ALL affected reachable UI screens need real emulator regression checks.

## GitHub tools and local artifacts

Tools:
- tools/build_g1_mode_heading_vietnamese_036.py — guarded clean/graphics035 exact hash, local installed TrueType raster, 4bpp sprite encoding, game codec compression, in-place overwrite, IPS generation. Requires explicit --allow-untested.
- tools/verify_g1_mode_heading_036_independent.py — independently checks exact ROM SHA, untouched first 192 tiles, 13 asset references, G0 and G1 unchanged source spans, cartridge checksum and IPS replay.

Local artifact: Chibi_G0_G1_ChonGiDay_036_UNTESTED.zip, containing IPS, Vietnamese README, sprite preview, static and independent QA JSON. No commercial ROM or font files are committed.

Local ROM and IPS are GRAPHICS-ONLY, based on CLEAN Japanese ROM, NOT the full Story/Quiz/Fortune Vietnamese content. Also beware the coincidental historical name Build035 used for a separate DIRECT-TEXT project: these are not yet safely merged.

SNES EMULATOR RUNTIME: NOT TESTED. A real title/menu screen screenshot and Japanese menus shared-sheet regression pass remain required. Do not claim the game is finished.

## Next content-first tasks

1. Identify real G2 VS/rule-panel and G3 result/ending assets by screen setup call -> package -> compressed source -> decoded visible Japanese. Apply further graphics translation; DO NOT modify internal descriptor/debug strings in 0x286B4..0x287FC as if they were retail graphics.
2. After meaningful graphics content is finished, build a single integrated graphics + canonical Story/Quiz/Fortune Vietnamese patch with exact byte and relocation collision audit against historical direct-text Build035. Do not apply graphics IPS over Build035 blindly.
3. Run one real emulator session on combined content, inspect original character graphics, startup Votri Valley credit, main menu header, Start/Password, shared UI packages, G2/G3 and line placement.
4. Dialogue font/65816 research remains postponed at user's request.

STATUS: ACTUAL G1 MAIN-MODE SPRITE PATCH STATIC PASS; 13 SHARED PACKAGES VALIDATED; GAMEPLAY NOT TESTED; NOT FULL-GAME VIETNAMESE.
