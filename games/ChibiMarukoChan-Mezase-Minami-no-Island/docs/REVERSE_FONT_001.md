# Reverse Font 001 — Chibi Maruko-chan SNES

Updated: 2026-09-16 +07

This note records the first proven text-code -> glyph-id -> bitmap path for the visible menu renderer. It deliberately does not claim that every graphic/text system in the game uses this same path.

## 1. CP932-like two-byte parser

The relevant parser is at file `0x283D8`, CPU `$85:83D8` on the proven LoROM mapping.

Key sequence:

```text
0283E1  EB          XBA
0283E2  85 00       STA $00
0283E4  29 FF 00    AND #$00FF
0283E7  38          SEC
0283E8  E9 80 00    SBC #$0080
0283EB  0A          ASL
0283EC  AA          TAX
0283ED  BF 56 97 85 LDA $859756,X
0283F1  85 02       STA $02
...
0283FB  A5 00       LDA $00
0283FD  EB          XBA
0283FE  29 FF 00    AND #$00FF
028401  38          SEC
028402  E9 40 00    SBC #$0040
028405  0A          ASL
028406  A8          TAY
028407  B7 02       LDA [$02],Y
...
028413  22 7B 8E 85 JSL $858E7B
```

Runtime-proven interpretation for this visible menu path:

1. first byte selects a per-lead mapping table through pointer table CPU `$85:9756`, file `0x29756`;
2. second byte is normalized as `(trail - 0x40) * 2`;
3. selected table returns a 16-bit glyph ID;
4. glyph ID is passed to renderer `$85:8E7B`.

For lead byte `0x82`, the pointer resolves to CPU `$85:9862`, file `0x29862`.

For the tested full-width digit/Latin range beginning at CP932 `0x824F`:

```text
entry = 0x29880 + (trail - 0x4F) * 2
```

Examples from CLEAN ROM:

```text
０ 0x824F -> 0x0000
１ 0x8250 -> 0x0001
...
９ 0x8258 -> 0x0009
Ａ 0x8260 -> 0x0517
Ｂ 0x8261 -> 0x0705
Ｅ 0x8264 -> 0x0000
Ｉ 0x8268 -> 0x074B
Ｋ 0x826A -> 0x0519
Ｌ 0x826B -> 0x074C
Ｍ 0x826C -> 0x0814
Ｏ 0x826E -> 0x051A
Ｐ 0x826F -> 0x0815
Ｑ 0x8270 -> 0x0216
Ｒ 0x8271 -> 0x0518
Ｓ 0x8272 -> 0x020D
Ｔ 0x8273 -> 0x0516
Ｖ 0x8275 -> 0x020C
```

Probe 004 explained why unsupported full-width Latin letters became zeroes: they mapped to glyph `0x0000`, which is the actual `0` glyph.

## 2. Renderer and font page table

Glyph renderer: CPU `$85:8E7B`, file `0x28E7B`.

The renderer selects a font page through a 24-bit pointer table at CPU `$85:95EE`, file `0x295EE`.

Ten CLEAN-ROM page pointers:

```text
A5:8000
A5:8800
A5:9000
A5:9800
A5:A000
A5:A800
A5:B000
A5:B800
A5:C000
A5:C800
```

File offsets:

```text
0x128000
0x128800
0x129000
0x129800
0x12A000
0x12A800
0x12B000
0x12B800
0x12C000
0x12C800
```

Each page is exactly `0x800` bytes.

## 3. Font format

Font pages are not ordinary SNES 2bpp/4bpp tiles.

Each page is raw **1bpp 128 x 128 bitmap**:

- 128 pixels wide = 16 bytes per raster row;
- 128 rows;
- 16 * 128 = `0x800` bytes;
- logical grid = 10 x 10 cells;
- each glyph cell = 12 x 12 pixels.

Glyph ID format:

```text
high byte = page 0..9
low byte  = binary cell index 0..99
```

For low-byte index `n`:

```text
col = n % 10
row = n // 10
x = col * 12
y = row * 12
```

Lookup table at CPU `$85:960C`, file `0x2960C`, contains packed decimal-style `00,01,...09,10,...99`, used to derive coordinates.

## 4. Proven existing Latin glyphs

Native authored Latin glyphs include:

```text
A 0x0517
B 0x0705
I 0x074B
K 0x0519
L 0x074C
M 0x0814
O 0x051A
P 0x0815
Q 0x0216
R 0x0518
S 0x020D
T 0x0516
V 0x020C
```

Their decoded 12x12 bitmaps match runtime appearance.

## 5. Conservative safe-slot audit

Static audit decoded all 1,000 logical cells across ten font pages and scanned the nearby mapping-data region for glyph-ID reuse.

At this checkpoint:

- about 868 glyph IDs appear used by conservative mapping scan / glyph-zero accounting;
- about 132 cells are blank and unseen in that scan;
- glyph ID `0x0963` = page 9, cell 99 was blank;
- page 9 cell 99 is x=108, y=108;
- little-endian ID bytes `63 09` had zero hits in audit region `0x29796 .. 0x2B380`.

This is a conservative candidate, not a global theorem about every hidden subsystem, but it was suitable for a guarded runtime probe.

## 6. Probe 006 — RUNTIME PASS

Tool: `tools/probe_visible_menu_006_custom_glyph.py`

Probe 006 changed only the guarded visible-menu/font path from CLEAN ROM:

1. first menu field -> full-width `ＴＥＳＴ１２３４`, preserving 8 two-byte units;
2. full-width `Ｅ` mapping at `0x298AA` -> custom glyph ID `0x0963`;
3. formerly blank glyph `0x0963` received a diagnostic 12x12 Vietnamese uppercase `Đ` bitmap;
4. surrounding menu control bytes remained untouched;
5. checksum/complement rebuilt and static gates passed.

Expected runtime first line:

```text
TĐST1234
```

User screenshot on 2026-09-16 shows exactly **`TĐST1234`** on the visible menu and the game reaches the menu normally.

Therefore, for this renderer path, the following architecture is now **runtime-proven**:

```text
2-byte game code -> 16-bit glyph ID -> 12x12 raw 1bpp bitmap
```

This simultaneously confirms:

- mapping-table edits control the displayed glyph;
- glyph ID `0x0963` reaches the predicted page/cell;
- a custom-drawn Vietnamese glyph can be rendered successfully by the retail menu path;
- 2-byte framing remains structurally valid for this menu field.

Probe 006 is a **custom-glyph runtime PASS**, not a whole-font or whole-game Vietnamese rendering PASS.

## 7. Next font milestone

Now justified:

1. freeze a guarded Vietnamese codepage allocation from conservatively safe glyph cells;
2. generate a first real Vietnamese glyph set instead of one diagnostic glyph;
3. keep 2-byte source framing and mapping-table edits explicit/auditable;
4. build a small Vietnamese phrase probe containing multiple accented characters, preferably a real menu phrase;
5. only after that multi-glyph screenshot passes, begin bulk runtime insertion.

Need at minimum plan for Vietnamese letters/variants used by translated text, including `Đ/đ`, `Ă/ă`, `Â/â`, `Ê/ê`, `Ô/ô`, `Ơ/ơ`, `Ư/ư` and tone-marked vowels.

Before allocating dozens of slots, run a global reference/collision audit stronger than the current nearby-table scan.

## 8. What this does not prove

Do not automatically apply this architecture to:

- pink `どれにする？` heading;
- Start / Password / Continue graphics;
- logos;
- compressed/tilemap artwork;
- any alternate renderer not yet traced.

Those remain separate reverse targets until evidence connects them to this renderer.
