# G2 Direct Text Probe 003 Strict 2-Byte Fix 014

Updated: 2026-09-21 +07

## Runtime result: Probe 002 FAIL

User test result:

**The game turns black when entering the target school-front dialogue screen.**

Therefore:

- Probe 002 build/static gates: PASS
- Probe 002 runtime: **FAIL**
- do not reuse Probe 002 payload framing

Probe 002 did not modify D038 or palette/controller logic, so the black-screen failure points back to direct-text encoding/framing.

## Root-cause correction

Historical Build 027 documentation states that Story runtime insertion uses the proven **0x84xx 2-byte Vietnamese codepage** inside fixed text budgets while preserving script separators.

Probe 002 violated that discipline by mixing:

- 2-byte `0x84xx` Vietnamese glyph codes;
- raw 1-byte ASCII space `0x20`;
- SJIS exclamation `0x8149`.

Even though the byte count and `0x816F` positions were correct, the mixed-width replacement is not equivalent to the Build 027 insertion model and is now rejected.

## Probe 003

Probe 003 uses only 2-byte Vietnamese codepage units for all replacement printable content:

- letters: `0x84xx`
- spaces: `8440`
- exclamation: `8441`
- padding: repeated `8440`

Original script tokens remain untouched:

- opening quote `8175`
- closing quote `8176`
- line separator `816F`

Separator offsets remain exactly:

- 32
- 68
- 104

Each field remains exactly 106 bytes and the following NUL terminator remains in place.

Compact runtime text was tightened to fit true 2-byte units:

- **Nói thẳng nhé!**
- **Du học chớ ngại!**
- **Luyện phản xạ!** / **Tập khỏi rơi!** / **Rèn gu mỹ thuật!**

## Local artifact

`Chibi_Maruko_G2_DIRECT_TEXT_PROBE_003.sfc`

Static facts:

- D038: **ORIGINAL**
- total changed bytes vs clean: **621**
- SHA-1: `d0f7969aea3cad0a167dca3889ee9960be6415e0`
- SHA-256: `5208bec10147f478cc17955c4f262a5cde08e5b85708caa2717370f6835fbacd`
- checksum: `0x4FE8`
- complement: `0xB017`

## Files

Added:

- `translation/runtime/g2_conversation_demo_compact_v2.csv`
- `tools/build_g2_conversation_direct_probe_003.py`
- `tools/selftest_g2_conversation_direct_probe_003.py`

## Claims

- Probe 002 Runtime FAIL: **CONFIRMED**
- Probe 003 strict framing: **STATIC PASS**
- Probe 003 runtime: **RETEST REQUIRED**
- G2 Runtime PASS: **NO**

If Probe 003 still black-screens, stop changing wording. The next diagnostic must compare against the exact Build 023/024/027 runtime baseline rather than continuing clean-ROM reconstruction.
