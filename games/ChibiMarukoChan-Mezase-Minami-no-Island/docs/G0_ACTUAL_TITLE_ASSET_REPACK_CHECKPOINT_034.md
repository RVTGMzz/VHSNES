# Chibi Maruko-chan SNES — Checkpoint 034: FIRST ACTUAL G0 TITLE GRAPHICS PATCH (EXPERIMENT)

Date: 2026-10-11. Repo: `RVTGMzz/VHSNES`, branch `chibi-maruko-bootstrap-01`.

## Breakthrough: exact first-boot retail title asset identified from clean ROM

For the first time, the game title artwork is not merely a proposed translation. The exact clean SNES ROM SHA256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956` was actually inspected and the real original Japanese logo rendered offline.

The boot-near initializer around **ROM `0x000FEE`** loads `LDX #$A087` then calls the resource loader `JSL $80:E255`. This identifies the type-0 resource package **`$82:A087`** (file `0x12087`). All **10** compressed package records were decoded to the original 64 KiB VRAM image with the game codec `$80:E8B2`, including flag=1 16-byte reorder.

The original screen text **`ちびまる子ちゃん` / `めざせ！南のアイランド！！`** appears recognizably in an *actual ROM-derived render* of:

- BG title tilemap: VRAM word **`0x0000`**, compressed source **`$9E:9F00`** / file **`0x0F1F00`**, decoded 2048 bytes, original compressed span 545.
- 4bpp title graphics: VRAM word **`0x2000`**, compressed source **`$9E:E456`** / file **`0x0F6456`**, decoded 8192 bytes, original compressed span 5570.
- Related 4bpp banks at VRAM words `0x3000` and `0x4000`; background/character palettes, other BG tilemaps and OBJ sprites occupy separate G0 resources.

The original Japanese logo was visible in `Chibi_G0_82A087_asset_contact_sheet.png` on local development storage. This is **source-asset identification by actual decompression and offline visual recognition**, NOT proof of a live SNES emulator screenshot.

## New Vietnamese replacement actually inserted into an experimental SNES ROM

The title-only experimental build replaces the **G0 background artwork**, with approved three lines:

```text
Chibi Maruko-chan
Tiến tới đảo phương Nam!!
Việt hóa bởi Votri Valley
```

A 256×88 pixel native-resolution, mono-color palette-index 13 title composition was rasterized using locally installed TrueType fonts. The glyph bitmaps are encoded into SNES 4bpp tiles, and their tile IDs go into the original G0 BG tilemap. The actual title layer was independently decoded **from the patched ROM itself**, producing `Chibi_G0_VI_TITLE_ACTUAL_PATCHED_ROM_RENDER.png` with all three Vietnamese lines and accents. This PNG is an **offline render of ROM tile data, not a game screenshot**.

### Safeguard: original characters and copyright graphics not overwritten

A naive first attempt would have replaced the whole gfx page and damaged graphics shared with other title-screen BG layers. **This was rejected**.

The accepted experiment now:

1. Keeps **four other BG tilemaps** (at VRAM word `0x0400`, `0x1000`, `0x5000`, `0x5800`) exactly byte-identical.
2. Builds a set of tile IDs used by those non-title maps; **583 in-range 4bpp IDs** (and additional out-of-range/raw IDs) are left pixel-identical.
3. Allocates **166 new nonshared 4bpp tiles** from the **185** available free IDs across the G0 graphics banks, with no changes to the original shared characters.
4. Keeps the entire OBJ graphics VRAM region `0xC000..0xFFFF` byte-identical, plus all rows 11..31 of title map `0x0000`.
5. Preserves original palette/priority fields in the title map; only its title-region tile indices are replaced, with flips removed on new glyphs.
6. Keeps the original `$9E:D005` 4bpp graphics bank **completely unchanged** (it is not needed for the new title glyph tile allocation).
7. Recompresses the two in-place resources only if they fit their original compressed spans; otherwise fails closed.
8. Recompresses the modified third bank whose 3420-byte stream would exceed its original 2712-byte allocation. Places it at an original all-`FF` unused area **file `0x036907` / CPU `$86:E907`**, wholly within bank86. Redirects **only** record2's 24-bit source pointer at file `0x012095..0x012097` from `$9E:C56D` to `$86:E907`. The old third resource is left intact.
9. Allows changed ROM bytes only in the two bounded original resources, 3-byte package pointer, blank relocated stream and checksum header.

These are **static, offline structural guarantees**; live CPU/PPU behavior still needs testing.

### Exact local experimental artifact contract

The experimental ROM is built from the user's **exact clean 2MiB ROM**, NOT from historical Build035. Therefore this ROM contains **only** G0 title changes, not the full Story/Quiz/Fortune localization.

| Field | Value |
|---|---|
| Clean input SHA256 | `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956` |
| Experimental G0 output SHA256 | `012cdfb87eae1b7c5a9feada4e1c322541e3c91ba45ba0b857e08a2465f47ce0` |
| Changed bytes | 9317 |
| SNES checksum / complement | `0x20C8 / 0xDF37` |
| Original logo graphics 8192B | `0xF6456`, new compressed span **4582** (old **5570**) |
| Unchanged middle graphics 8192B | `0xF5005`, byte-identical |
| Relocated third graphics 8192B | from `0xF456D` (2712 old) to `0x36907` (3420 new) |
| Title tilemap 2048B | `0xF1F00`, new compressed span **506** (old **545**) |
| New title-only graphics tile count | **166** |
| Non-title 4bpp shared tiles verified | **583 preserved** |
| Compressed streams round-trip | **PASS** |
| Reconstructed actual title-layer image from patched ROM | **PASS** |
| SNES emulator title-screen gameplay test | **NOT RUN** |
| Full-game Vietnamese integration | **NOT DONE** |

A standalone IPS patch (**10,415 bytes / 218 IPS records**) was generated locally and independently reapplied to the exact clean ROM. Reapplication reproduced the output SHA256 byte-for-byte. The patch and experimental ROM stay outside GitHub; only source scripts and documentation belong in the repository.

## New GitHub scripts

- `tools/build_g0_first_boot_title_votri_experimental.py`: clean-ROM-guarded, opt-in, reproducible title raster/tilemap/4bpp encoder and LZ/RLE/zero compressor, source relocation and IPS writer. Requires Pillow and locally supplied fonts; **never upload font files**.
- `tools/verify_g0_title_034_real_asset_static.py`: independent ROM-based reconstruction of 10 G0 resources and checks that all other maps, the 583 referenced tiles, OBJ data and original checksum structure are valid. Exact experimental SHA256 guard.

Example rebuild with a local exact clean ROM and installed TrueType fonts:

```bash
cd games/ChibiMarukoChan-Mezase-Minami-no-Island
python tools/build_g0_first_boot_title_votri_experimental.py clean.sfc g0-title-only-untested.sfc \
    --font-bold /path/to/DejaVuSansCondensed-Bold.ttf \
    --font-regular /path/to/DejaVuSans.ttf \
    --ips g0-title-only-untested.ips --preview g0-title-offline.png \
    --report g0-title-static.json --allow-untested-g0
python tools/verify_g0_title_034_real_asset_static.py clean.sfc g0-title-only-untested.sfc \
    --report g0-title-independent-qa.json
```

Bitmap output may differ with font versions. The verifier is pinned to the exact locally staged experimental ROM SHA256. If the original file/fill slots are modified, fail closed; never silently assume that this relocation area is still free on Build035 or future translation builds.

## Next real deliverable

**Do not stall on font.** Test this *title-only* G0 ROM in a real Snes9x/RetroArch SNES emulator, verifying full-screen original Maruko characters, title colors, copyright line, credit, and Start navigation. If the screen displays incorrectly, diagnose actual BG/VRAM/PPU behavior; static correctness does not override player screenshots.

Then integrate the G0 graphics delta with the latest whole-game Vietnamese translation build by **explicit 3-way patch conflict checks** against the exact Build035 bytes. No automatic IPS overlay on Build035 is safe yet, especially because the relocation `0x36907` may have been used by other historical work.

After G0 runtime acceptance, continue G1 Start/Password, G2 rules, G3 results and ending; font work remains deferred under the user's instruction.

**STATUS: real G0 title source found + experimental SNES ROM bytes modified + offline round-trip VERIFIED; runtime still UNTESTED; whole-game title/translation not yet integrated.**
