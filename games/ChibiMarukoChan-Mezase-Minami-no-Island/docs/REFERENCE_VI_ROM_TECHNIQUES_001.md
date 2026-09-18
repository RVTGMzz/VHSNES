# Reference Vietnamese SNES ROM Techniques 001

Updated: 2026-09-18 +07

This note records reverse-engineering observations from three user-provided Vietnamese SNES ROMs used strictly as technical references for the Chibi Maruko-chan localization workflow.

No commercial ROM is committed to the repository.

## Reference ROM identities

### Rockman X2 Vietnamese

- size: `0x400000` / 4 MiB
- SHA-1: `1a09dfdeee5be3acc61241d16ae93e9a6fa072ad`
- SHA-256: `80dc4f964a452ba8826410a288381a23c5ad0921ea3300d309a7b8c607edc269`
- LoROM header: `0x7FC0`
- internal title: `Rockman X2 Vietnamese`
- map mode: `0x20`
- checksum pair: valid
- reset vector: `0x8000`

### Rockman X3 Vietnamese

- size: `0x400000` / 4 MiB
- SHA-1: `3fdb28f5a69d133396393a3c5fe2a2a7dfe32a6e`
- SHA-256: `2cf3f08780125fd05b5a786b39d58fa2351d366ad3b089d83fc6ea3336bd5296`
- LoROM header: `0x7FC0`
- internal title: `Rockman X3 Vietnamese`
- map mode: `0x20`
- checksum pair: valid
- reset vector: `0x8000`

### Stoneboat Clock Tower VN / AowVN

- size: `0x400000` / 4 MiB
- SHA-1: `e918742148c3096d9201212727e7949f3882c5cf`
- SHA-256: `d8537ac3480ad55b3aa440a2a8bc12613da7823823479ae664a3699fd6aade40`
- coherent HiROM header: `0xFFC0`
- internal title: `CLOCK TOWER SFX`
- map mode: `0x31`
- checksum pair: valid
- reset vector: `0xFFE0`

## Technique A: reset trampoline into expanded ROM

Rockman X2 and X3 begin with the exact same four bytes:

```text
5C 00 80 66
```

which is:

```asm
JML $66:8000
```

Under the observed LoROM mapping this lands at file:

`0x330000`

Both patches therefore intercept the reset path immediately and transfer control to code in the expanded ROM region.

The custom routine later returns to the original engine with:

```asm
JML $00:8006
```

Observed file locations:

- X2: approximately `0x3300F4`
- X3: approximately `0x3300FE`

This is a strong reusable architectural reference:

`original reset -> expanded-ROM localization/bootstrap code -> original game entry`

### Relevance to Chibi

If editing the original Chibi title asset becomes unnecessarily fragile, a separately auditable localization splash can be inserted before the original title without replacing original publisher/copyright artwork.

Potential content:

- **Chibi Maruko-chan**
- **Tiến tới đảo phương Nam!!**
- **Việt hóa bởi VôtriValley**

This should remain a fallback/optional strategy. Direct replacement of the proven retail title asset is still preferred if the real G0 path is clean and bounded.

## Technique B: explicit ROM-to-VRAM DMA helper

The Rockman expanded routine contains a compact DMA helper.

Representative X2 sequence around file `0x330297`:

```text
... STX $4302
    STA $4304
    STY $4305
    LDA #$18
    STA $4301
    LDA #$01
    STA $4300
    LDA #$01
    STA $420B
...
```

Interpretation:

- X -> DMA A1T source address
- A -> DMA A1B source bank
- Y -> DAS transfer size
- BBAD `$18` -> VRAM data port
- DMAP `$01`
- MDMAEN channel 0

A sister helper targets BBAD `$22`, consistent with CGRAM/palette upload.

The boot code passes source banks `$60` and `$61`, which map into the expanded region around file `0x300000..`.

This proves a practical pattern for storing new localization graphics in expanded ROM and uploading them explicitly to VRAM.

### Relevance to Chibi

If a G0/G1/G2/G3 replacement cannot fit its original asset span, a technically clean relocation strategy is possible:

`new graphics in free/expanded ROM -> controlled DMA upload -> existing screen flow`

Do not use this merely because it is available. Prefer an in-place bounded patch when it fits.

## Technique C: shared localization payload

Rockman X2 and X3 contain extremely strong common expanded-ROM data.

Measured byte identity:

- `0x310000..0x32FFFF`: **100% identical**, 128 KiB
- `0x330000..0x33FFFF`: approximately **98.5% identical**

Other large identical runs also exist inside these banks.

This strongly indicates a reusable localization/bootstrap payload rather than two unrelated one-off modifications.

### Relevance to Chibi

It validates the architecture already being built in this project:

- keep generic graphics/font/build tooling separate from game-specific asset addresses;
- relocate reusable code/data when justified;
- guard every game-specific hook/span by exact hashes.

## Technique D: raw graphics localization with Vietnamese diacritics

Visual tile probes of the Clock Tower ROM produced recognizable assets under raw SNES 4bpp decoding.

Notable observations:

- around `0x330000`, sequential 4bpp probing visibly reproduces portions of the **CLOCK TOWER** title/logo artwork;
- around `0x340000`, sequential 4bpp probing visibly reproduces Vietnamese words/sentences with diacritics.

This is particularly important because it demonstrates a real released/fan-patched SNES workflow where Vietnamese text can be represented directly as graphics rather than requiring the normal dialogue font renderer.

The exact Clock Tower tilemap/render path has not been reversed here, so these offsets are reference observations, not patch instructions.

### Relevance to Chibi

This directly supports the chosen G1-G3 strategy:

`Vietnamese string -> rasterized pixels -> SNES 2bpp/4bpp tiles -> tilemap/asset patch`

It is especially appropriate for:

- **Chọn gì đây?**
- **Bắt đầu**
- **Mật khẩu**
- **Luật chơi**
- **Thắng**
- **Thua**
- **Tiếp tục**
- **Thoát**

where the retail text appears to be graphics-driven.

## Expansion-space observations

The two Rockman patches are 4 MiB and contain large zero-filled regions plus concentrated localization payloads in higher banks.

The structure suggests deliberate use of expanded address space instead of forcing all replacement content into the original local spans.

Clock Tower remains structurally different and uses HiROM/FastROM mapping, so its absolute addresses/hook model must not be copied into Chibi.

## What should be reused for Chibi

Reuse **techniques**, not bytes/assets:

1. exact reset/entry hook only if a new splash or initialization layer is justified;
2. explicit expanded-ROM graphics storage;
3. tightly scoped DMA upload helper if original asset capacity is insufficient;
4. raw 2bpp/4bpp rendering of Vietnamese labels;
5. reusable generic tooling with game-specific guarded manifests;
6. exact return to original engine flow;
7. independent diff/checksum verification.

Do not copy:

- Rockman/Clock Tower code wholesale;
- their fonts/assets;
- hard-coded addresses;
- mapper assumptions;
- palette assumptions.

## Updated Chibi strategy

Preferred order remains:

1. reverse the genuine G0-G3 retail asset paths;
2. try bounded in-place graphics replacement;
3. if replacement does not fit, evaluate relocation to proven free/expanded space;
4. if G0 retail title replacement is fragile, consider an optional pre-title localization splash using the reset-trampoline pattern;
5. preserve original publisher/copyright attribution;
6. Runtime PASS only after user screenshots/gameplay confirmation.

## Status

These three ROMs materially increase confidence that the remaining Chibi graphics work is feasible.

They do **not** prove Chibi uses the same renderer or memory map.

No reference-ROM bytes are committed.
