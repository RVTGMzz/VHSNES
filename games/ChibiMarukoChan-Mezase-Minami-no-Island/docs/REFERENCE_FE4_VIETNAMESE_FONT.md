# Reference study — Vietnamese Fire Emblem 4 SNES font/text approach

Date: 2026-09-16
Branch: `chibi-maruko-bootstrap-01`

## Why this reference matters

A Vietnamese Fire Emblem 4 ROM supplied by the user was inspected as a reference for the current Chibi Maruko-chan SNES localization project.

The goal is NOT to copy FE4 addresses, mapping rules, or hardware assumptions into Chibi. The goal is to learn reusable architecture patterns that match evidence already observed in Chibi.

## Uploaded reference ROM facts

Supplied file: `Seiseno no Keifu Vietnamese.smc`

Observed locally:

- total file size: `4,194,816` bytes
- this equals 4 MiB ROM body + 512-byte copier header
- internal title: `FIREEMBLEM4`
- HiROM / FastROM header at headered file offset `0x101C0`
- map mode: `0x31`
- stored checksum: `0xFE43`
- stored complement: `0x01BC`
- checksum of the 4 MiB body recomputes to `0xFE43`
- full-file SHA-1: `2556860f8f51d0895c191a5f614c9088fc8fd98e`
- headerless-body SHA-1: `45d38e5d1ed1cdbc6129ad640be983fcc9a7e115`

The supplied ROM hash does NOT match the catalogued Stoneboat 1.1 hacked-ROM SHA-1 published by RetroHackers, so treat this exact ROM as a derivative/reference artifact rather than as the canonical Stoneboat 1.1 build.

## Public FE4 translation references

RetroHackers lists a Vietnamese Fire Emblem: Seisen no Keifu translation by Stoneboat, released 2012-05-02, fully playable, version 1.1.

A contemporary GameVN release thread by `asm65816` describes a completed FE4 Vietnamese project built over several years and based on earlier Vietnamese work. The thread explicitly describes broad replacement of Japanese characters with Latin/Vietnamese characters and acknowledges text-length constraints in some game fields.

Project Naga's later public FE4 build files are useful as an independent technical reference. They explicitly separate:

- dialogue text/font
- menu text/font
- graphics/textual UI

Project Naga also uses a dedicated dialogue font width table and treats many menu strings as 2bpp graphics/tilemaps rather than assuming one universal renderer.

## Same-author SNES source pattern worth learning from

A public SNES translation source repository under `stoneboat65816` for Yū Yū Hakusho Tokubetsu-hen demonstrates a robust Vietnamese architecture:

1. A custom table maps game codes directly to Vietnamese glyphs.
2. The table includes complete Vietnamese lowercase tone families such as:
   - `à ả ã ạ`
   - `â ấ ầ ẩ ẫ ậ`
   - `ă ắ ằ ẳ ẵ ặ`
   - `ê ế ề ể ễ ệ`
   - `ô ... ộ`
   - `ơ ... ợ`
   - `ư ... ự`
   - `đ / Đ`
3. Font bitmap data is stored separately from text code mapping.
4. A separate width table provides proportional/VWF widths per glyph.
5. 65816 code reads the width table and composes shifted glyph bitmap data into RAM before display.

Important: this proves a reusable design pattern, NOT that the 2012 FE4 patch uses identical addresses or identical code.

## Direct lessons for Chibi Maruko-chan

Current Chibi runtime evidence already says:

- raw 1-byte ASCII bulk replacement can crash the game (Probe 002)
- preserving 2-byte text units boots safely (Probe 003)
- standard CP932 full-width Latin identity is incomplete/custom in this renderer
- Probe 004 shows many unsupported letters collapsing to the same fallback glyph

Therefore the FE4/Stoneboat-style idea fits the evidence very well:

### Preferred architecture to investigate

`2-byte game code -> custom glyph index -> custom Vietnamese font bitmap`

Potentially add:

`glyph index -> width table`

only if Chibi proves that variable width is useful and safe.

### What NOT to do

Do not:

- assume CP932 full-width Latin codes are the final Vietnamese codepage
- switch back to raw 1-byte ASCII for this menu path
- copy FE4 HiROM addresses, font offsets, control codes, or VWF routine
- assume all Chibi menu/dialogue screens share one renderer
- implement VWF before proving the current Chibi code->glyph and glyph->bitmap paths

## Recommended next Chibi steps

1. Finish Probe 005 mapping proof.
2. Reverse the Chibi table that maps accepted 2-byte codes to glyph IDs.
3. Find the bitmap source for at least one known glyph ID (`A`, `T`, digit, fallback zero glyph).
4. Replace ONE unused/fallback glyph bitmap with a Vietnamese probe glyph such as `Đ` or `ế`.
5. Point one safe 2-byte code to that glyph ID.
6. Runtime-test one visible menu word only.
7. If successful, define a project-local Vietnamese codepage and freeze it in a `.tbl`/CSV source-of-truth.
8. Only then consider a width table/VWF layer if fixed-width text is too restrictive.

## Key guardrail

FE4 is a reference for architecture, not a hardware template.

Chibi remains evidence-first: every mapping, font format, width rule, and renderer path must be demonstrated on Chibi itself before becoming a project assumption.
