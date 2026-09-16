# Vietnamese Font V5 — FE4 native-width thin refinement

Updated: 2026-09-16 +07

## Why V5 exists

Probe 010 proved the FE4-native-width transfer is readable in Chibi, and the user explicitly preferred it over Probe 008/009. However, the user judged the letters still too bold/heavy and asked for a lighter, thinner face without losing the clearer Vietnamese marks.

V5 is therefore a **weight refinement only**, not a new encoding or renderer experiment.

## Frozen architecture

V5 keeps all already-proven Chibi runtime architecture unchanged:

```text
2-byte game code -> 16-bit glyph ID -> 12x12 raw 1bpp bitmap
```

It also keeps the dedicated Vietnamese lead `0x84` and the same 160 Unicode code assignments. No FE4 engine/address/codepage assumption is copied into Chibi.

## Reference identity

The raster source remains the user-supplied:

`Seiseno no Keifu Vietnamese(1).smc`

Guard:

- size: `4,194,816` bytes
- SHA-1: `2556860f8f51d0895c191a5f614c9088fc8fd98e`
- 512-byte copier header
- dialogue-font body range after removing header: `0x128000 .. 0x12BBFF`

## V5 raster rule

V4/Probe 010 already changed the failed Probe 009 strategy by preserving FE4's native 8-pixel width instead of stretching it to 10 pixels. V5 starts from that same native-width 12x12 transfer and applies exactly **one conservative Zhang-Suen thinning iteration** to letter bodies.

To keep Vietnamese marks from becoming faint again, V5 restores these rows from the pre-thinned V4 raster:

- rows `0..4`: upper accents / circumflex / breve / horn material
- row `11`: below-dot material

This intentionally reduces body stroke weight while keeping diacritics assertive.

Generator:

`tools/generate_vi_glyphs_v5_fe4_thin.py`

Outputs:

- reuses `translation/codepage/vi_codepage_v3_fe4ref.csv` unchanged
- `translation/codepage/vi_glyphs_v5_fe4_thin.json`

V5 keeps 126 custom visual glyphs and the same conservative blank-slot allocation as V4.

## Probe 010 evidence

User screenshot on 2026-09-16 showed Probe 010 booting and rendering all six rows clearly:

```text
Âm thanh
Bói!!
Đấu đội!
Vẽ!!
Maruko?
Ổn rồi
```

Classification:

- codepage / runtime framing: PASS
- FE4 native-width readability: PASS
- typography weight: TOO BOLD per user preference

Do not call Probe 010 release font quality PASS.

## Probe 011

Tool:

`tools/probe_visible_menu_011_fe4_thin.py`

Rows remain identical to Probe 010 for direct A/B comparison:

```text
Âm thanh
Bói!!
Đấu đội!
Vẽ!!
Maruko?
Ổn rồi
```

Static CLEAN-ROM checkpoint:

- codepage entries: 160
- custom visual glyphs: 126
- lead pointer identity: PASS
- blank/reuse audit: PASS
- six source identities: PASS
- exact two-byte unit preservation: PASS
- diff-surface gate: PASS
- checksum: `0x38C2`
- complement: `0xC73D`
- SHA-1: `45d06514306cd6d1a0cf0c65c6339527944199d4`
- SHA-256: `11b1b8c824be60dcdad8d9f287e916a245fe5edc42cdbb33855c02f25bf8f9bd`

**Runtime status: PENDING screenshot.**

Do not freeze V5 typography until the user confirms Probe 011 is lighter than Probe 010 while keeping accents readable.
