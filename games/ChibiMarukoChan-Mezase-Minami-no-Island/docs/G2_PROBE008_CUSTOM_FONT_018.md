# Probe 008 custom font design — 2026-10-09

User rejected the first Probe 008 preview as unattractive and requested customization.

Added a separate hand-drawn rounded/wider monoline candidate. Existing candidate is retained for comparison. This is a typography preview, not a ROM build.

## Reproduce

```sh
python tools/generate_g2_probe008_font.py
python tools/preview_g2_probe008_font.py
python tools/customize_g2_probe008_font.py
```

Preview scripts require Pillow and DejaVuSans.ttf.

## Outputs

- `translation/codepage/g2_probe008_custom_round_glyphs.json`
- `docs/previews/probe008-custom/font-comparison.png`
- `docs/previews/probe008-custom/full-codepage.png`
- `docs/previews/probe008-custom/vietnamese-families.png`

Explicit Latin outlines replace the narrow first candidate. No dilation, donor font or antialiased rasterization is used. Lowercase bodies are generally six to seven pixels wide inside 12×12 cells. Tone marks share construction rules; lower accents stay above row 11. Existing runtime mapping is not changed.

## Verified locally

163 candidate entries, unique code units, 18 bytes per 12×12 1bpp glyph, distinct family members, candidate code assignments preserved. Preview comparison and Vietnamese family sheet inspected. These checks do not establish in-game quality or safe slot allocation.

The 163 entries cover the existing 160-entry map plus proposed ằ/ẵ/ỵ at 84E1/84E2/84E3. This is not a claim of all Unicode Vietnamese uppercase coverage. Those three proposed codes and every replacement glyph slot still need validation in the target ROM before installation.

## Remaining

- User visual feedback on the new candidate.
- Obtain the canonical clean ROM or verified Probe 003 baseline; no ROM present locally in this session.
- Implement/verify guarded slot allocation and independent diff validation before font insertion. No Probe 008 builder is claimed complete.
- Preserve strict two-byte text framing, D038, palette and scene/controller logic.
- Render spacing shown here assumes 12 px advance; runtime spacing remains unverified.
- Runtime typography: UNTESTED. No ROM produced or committed.
