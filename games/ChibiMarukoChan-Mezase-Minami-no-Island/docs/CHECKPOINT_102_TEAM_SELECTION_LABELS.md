# Checkpoint102 — both team-selection labels

2026-10-15. Follows101 without changing its five translated headings.
Both visible チーム labels in the native team-selection screen now read “Đội”.
This is a different screen/resource from the result board fixed in099.

Native BG1 map F82A6 and glyphs1176E9 share label strokes with mascot tiles.
102 reads the private101 copies, erases only verified text colors3/4/5 in
x25–59 of each64px group, and redraws the label using native light ink15 and
outline5. Native background-strip colors are recovered from the original
row. The rabbit/cat pixels end at x24 and remain unchanged, including cheeks.
Thirteen modified tile instances are cloned after the101 atlas; every old
glyph and header tile remains byte-identical. Existing palette/priority flags
are retained, and mirrored cells are cloned in display orientation.

The native package owner pointers12354/1234A now select two private resources
in guarded original+baseline FF gaps. No shared source asset is overwritten.
Binary guards cover exact parents, allowed spans, tile/map bounds, resource
round trips, checksum and one clean-ROM-relative IPS replay.

Snes9x native setup flow was exercised again. PPU pixel comparison to101
shows714 changed BG1 pixels, ZERO changed pixels outside the two word regions,
ZERO remaining original pink Japanese ink pixels in those regions, and an
identical complete CGRAM palette. Mascots, character boxes and header remain
intact. The VS match completes and returns to native result phase7. This
targeted check is not a full natural whole-game playthrough.

Rebuild with `tools/build_cumulative_102.py` from the original user-owned ROM,
original043 ZIP and local Tahoma Bold/Tahoma paths. One cumulative IPS:
127,601 bytes, SHA256
`08ccd04e2fc6fc8c6d8eb2855283ce5b7eab907092bc1d40219b9d578d625b6e`.
Patched ROM SHA256:
`94f7ae442b8efe8fe0bcf74fdb79c0540054374ae411774903080660e78bef34`.

Whole-game completion remains FALSE. Next visible graphics are minigame names
on balloons and intro screens, character nameplates, victory/final-victory
and ending. Continue source-alias semantic review and natural whole-game QA;
historic Quiz scanner coverage remains279/381. Do not redo title/font art.
