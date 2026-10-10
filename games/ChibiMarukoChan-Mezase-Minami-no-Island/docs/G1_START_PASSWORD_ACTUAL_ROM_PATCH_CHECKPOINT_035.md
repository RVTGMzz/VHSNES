# Chibi Maruko-chan SNES — Checkpoint 035: actual G1 Start / Password graphics patched and merged with G0 title

Date: 2026-10-11. Repository `RVTGMzz/VHSNES`, branch `chibi-maruko-bootstrap-01`.

## Following the user's content-first instruction

This checkpoint performs actual SNES graphic-byte localization of **two new on-screen Story selection labels**:

| Actual original Japanese sprite | New Vietnamese graphics |
|---|---|
| `はじめから` | **Bắt đầu** |
| `パスワード` | **Mật khẩu** |

The user-requested first-boot G0 title and **`Việt hóa bởi Votri Valley`** from checkpoint034 are preserved and independently merged. No work on the 65816 font/9px hooks was performed.

The separate pink heading **`どれにする？` → `Chọn gì đây?` is NOT YET patched**. No fake editing of metadata/debug prose in file `0x286B4..0x287FC` is claimed.

## Real G1 resource proven and decoded

This builds on the existing `tools/extract_g1_story_select_assets.py` and `docs/G1_STORY_ENTRY_SCREEN_PROOF_008.md`, reconfirmed by **direct clean-ROM decompression and image rendering** in this session.

- Actual retail G1 Story screen initializer: `$85:E97F`; main type-0 resource package **`$82:AF23`** (file `0x12F23`).
- Its 9th resource entry (index 8) at file `0x12F4D` is `00 78 5E F9 97`: VRAM destination **word `0x7800`**, compressed resource **`$97:F95E`** (file `0xBF95E`).
- Retail game codec compressed span **436 bytes**, decompresses to **992 bytes = 31 SNES 4bpp 8×8 tiles**. No postprocess flag.
- The decompressed tile sheet visually shows **`はじめから`** (first label), **`パスワード`** (second label) and a small adjacent game icon.
- Tile organization: first label tiles **0–14**, reserved spacer tile **15**, second label tiles **16–28**, icon tiles **29–30**. These positions were verified against the actual original decoded palette-index art, not guessed from the ROM text scanner.

## Actual binary patch, not just word proposals

A graphics-only 035 experiment replaces labels in **this exact original sprite resource**, preserving its 992-byte decoded layout, its original palette indices 1/2, tile15 and icon tiles29/30:

- Text is rasterized at 8px high for the game's existing 4bpp Story sprite layout. New labels are centered in their reserved original 16-tile and 13-tile spans. Vietnamese diacritics have been drawn into the graphic cells, but **real in-game legibility is NOT verified**. Avoid describing font/art quality as accepted until a screenshot.
- New compressed stream is **331 bytes**, safely under the original 436-byte allocation. It is stored **in place at file `0xBF95E`**, with the remaining slot padded `FF`. The G1 package pointer and all its other resources are unchanged.
- Compression roundtrip from the **patched ROM** recovers the exact intended 992-byte 4bpp stream.
- Changed source bytes are whitelisted to original G1 compressed slot and SNES checksum.
- Independent actual-ROM bitmap render local artifact: `Chibi_G1_Start_Password_VietHoa_035_ROM_Asset.png`.
- Local G1-only exact clean-ROM experimental SHA256 **`9a7bddb9afb7062a63c775e647c9ee04c226202bd16d23a7d5aadf091ea1bdaf`**, changed **434 ROM byte positions**, checksum **`0x3757/0xC8A8`**.

## Safely merged with *G0 graphics only* — NOT the whole-game Vietnamese build

Used exact G0 title-only 034 ROM SHA256 `012cdfb87eae1b7c5a9feada4e1c322541e3c91ba45ba0b857e08a2465f47ce0` from clean game. Patched only G1 in-place resource `0xBF95E..0xBFB11` and recomputed checksum.

- **0 G0/G1 changed-byte collisions excluding SNES checksum**.
- G0 title resource data, relocation at file **`0x36907`** and source pointer **`0x12095`** unchanged from 034.
- Joint G0+G1 ROM SHA256 **`77a207589857d2886059057151eaf3d47530032b726744fe739e991ff81a5b80`**.
- SNES checksum/complement **`0x470A / 0xB8F5`**.
- Exact CLEAN-ROM IPS patch is **10,880 bytes in 225 IPS records**. An independently written IPS applicator replayed all records onto the clean source and produced the joint SHA256 byte-for-byte.
- Local bundle `Chibi_G0_G1_Title_Start_Password_035_UNTESTED.zip` contains IPS, README and static JSON report. No ROM binary was committed to GitHub.
- **This build is GRAPHICS-ONLY based on the Japanese clean source.** It does **not** contain the prior Story/Quiz/Fortune meaning translations and is NOT the final Vietnamese game.
- Emulator/runtime QA **NOT RUN** (no supported SNES emulator installed). The 8px sprite text is a preliminary artwork fit, not a user-approved final font.

## Source code on GitHub

- `tools/build_g1_start_password_vietnamese_035.py`: exact clean source, exact G0 baseline, local font path, sprite extraction, Vietnamese 4bpp tile encode, 436-byte fail-closed compression, live resource roundtrip, hash-pinned G1 and G0+G1 output, IPS creation. Explicit `--allow-untested` required.
- `tools/verify_g0_g1_graphics_035_independent.py`: independent ROM/IPS comparison; checks original sprite icon and reserved tile integrity, G0 resource preservation, compression and header checksum.

Reproduce only in a complete repo checkout with the exact clean ROM and exact G0 034 graphics-only ROM; pass a local TTF **file path** (never check font files into GitHub):

```bash
cd games/ChibiMarukoChan-Mezase-Minami-no-Island
python tools/build_g1_start_password_vietnamese_035.py clean.sfc G0-only-034.sfc \
  G0-G1-035-untested.sfc \
  --font-bold /usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf \
  --ips G0-G1-035-untested.ips --report G1-035-report.json --allow-untested

python tools/verify_g0_g1_graphics_035_independent.py clean.sfc G0-only-034.sfc \
  G0-G1-035-untested.sfc G0-G1-035-untested.ips --report G1-035-independent.json
```

Exact binary output hashes are tied to the local raster font and version. A different font rasterizer version may correctly be rejected by the hash-pinned builder.

## Next content tasks — DO NOT RETURN TO FONT YET

1. Locate the actual source of G1 pink heading **`どれにする？`**, without confusing it with `$97:F95E` option sprite resource or the internal debug descriptors.
2. Resolve and patch actual G2 visible rule-panel graphics and G3 result/ending cards, using resource package execution and ROM bitmap proof as for G0/G1.
3. Before creating the long-awaited full-game test build, explicitly check all altered bytes against the historical Build035 direct-text source and the current editorial `vi_full`. The G0 bank86 relocation and codepage occupancy must be collision-audited. Do not overlay the G0+G1 clean-ROM IPS onto Build035 blindly.
4. Run the combined real game in an SNES emulator and check all layers, original character art, copyright, choice navigation and text legibility; ONLY then promote to accepted patch.

**Status:** actual G0/G1 binary graphics patches + clean-ROM IPS **STATIC PASS**, runtime **NOT TESTED**, story/quiz **NOT INTEGRATED**, heading **NOT PATCHED**.
