# G2 Full Vietnamese Font Harmonization Handoff 017

Updated: 2026-09-30 +07

## Current runtime conclusion

The direct-text path itself is no longer the blocker.

Authoritative runtime evidence:

- Probe 002: **RUNTIME FAIL** — black screen at target dialogue
- Probe 003: **RUNTIME PATH PASS** — target scene loads and Vietnamese direct text renders, but V5-thin typography is unreadable
- Probe 004: **TYPOGRAPHY FAIL** — one-sided thickening creates blocky/merged glyphs
- Probe 005: clean-dialogue redesign branch, superseded by the user's request for a thinner overall face
- Probe 006: **CURRENT BEST RUNTIME DIRECTION** — thin/clean style is broadly acceptable; user feedback: "cũng cũng oke", but `ơ` is not clear enough
- Probe 007: **REJECTED BEFORE RUNTIME** — isolated `ơ/ớ` hook patch looked malformed in preview and was correctly rejected

Do not go back to Probe 004 thickening or the old V5-thin morphology.

The text/control path proven by Probe 003 remains the frozen base for future font work:

- strict 2-byte `0x84xx` Vietnamese units
- Story separators preserved
- D038 unchanged
- scene/palette/controller logic unchanged

## Local runtime artifacts from the latest session

These artifacts were produced locally during the session but are **not committed binary ROMs**:

### Probe 006 — thin clean

`Chibi_Maruko_G2_DIRECT_TEXT_PROBE_006_THIN_CLEAN.sfc`

- base: Probe 003
- SHA-1: `1e658ec71360a1d5a8cd0437b39cea0251b41682`
- SHA-256: `0ad309c4cfede4791cd5891714e487d2c1e933965f3e5b4064be3ee66c2b1efd`
- runtime: **direction accepted with reservation**
- problem: `ơ` family shape is not clear enough

### Probe 007 — isolated O-horn patch

`Chibi_Maruko_G2_DIRECT_TEXT_PROBE_007_O_HOOK_FIX.sfc`

- SHA-1: `b6a17a3b2600bb9c644d1d02bf4f764351f4badd`
- SHA-256: `6e196c5115de189a3c0f7b129197765d3a8c2cb562c64823a51234ea4876155e`
- changed only `ơ/ớ` relative to Probe 006
- preview result: **REJECTED**
- reason: horn/base construction looks malformed and patching only two members of the family is architecturally wrong

Do not promote Probe 007.

## Direction change: stop patching individual glyphs

The next build must be a **full Vietnamese harmonization pass**, not another one-off glyph repair.

The user explicitly requested a coherent thin/clean set covering the Vietnamese families below.

### A family

- `a á à ả ã ạ`
- `ă ắ ằ ẳ ẵ ặ`
- `â ấ ầ ẩ ẫ ậ`

### E family

- `e é è ẻ ẽ ẹ`
- `ê ế ề ể ễ ệ`

### I family

- `i í ì ỉ ĩ ị`

### O family

- `o ó ò ỏ õ ọ`
- `ô ố ồ ổ ỗ ộ`
- `ơ ớ ờ ở ỡ ợ`

### U family

- `u ú ù ủ ũ ụ`
- `ư ứ ừ ử ữ ự`

### Y family

- `y ý ỳ ỷ ỹ ỵ`

### D family

- `d đ`
- also keep uppercase `D Đ` coherent with the same face

## Highest-priority accent problems

The user specifically flagged the Vietnamese **hỏi** and **ngã** marks as broadly problematic.

These families must be audited together instead of fixing one glyph at a time.

### Hỏi set

`ả ẳ ẩ ẻ ể ỉ ỏ ổ ở ủ ử ỷ`

### Ngã set

`ã ẵ ẫ ẽ ễ ĩ õ ỗ ỡ ũ ữ ỹ`

Requirements:

- one consistent hỏi silhouette across families
- one consistent ngã silhouette across families
- correct vertical placement for plain vowels versus stacked bases `ă â ê ô ơ ư`
- no collision with circumflex/breve/horn
- no accent drifting left/right between family members
- thin/clean weight, not bold
- every composite must remain recognizable at native 12x12 size

## Font style decision

Current desired direction:

**thin clean / monoline-ish 12x12**

Avoid:

- V5-thin broken/fragmented strokes
- Probe 004 dilation/thickening
- isolated manual repairs that make one family inconsistent
- mixing visibly different native/custom Latin shapes inside the same runtime line

The next implementation should define reusable construction rules:

1. base Latin body
2. breve / circumflex / horn modifier
3. acute / grave / hỏi / ngã / dot tone
4. family-specific stacking positions
5. `d/đ` bar geometry

Then generate the whole family from those rules.

## Preview-first rule

Before building Probe 008 ROM:

1. render a full 12x12 atlas for every Vietnamese family above
2. render dedicated zoomed rows for hỏi and ngã families
3. render the actual runtime sample lines:
   - `Nói thẳng nhé!`
   - `Du học chớ ngại!`
   - `Luyện phản xạ!`
   - `Tập khỏi rơi!`
   - `Rèn gu mỹ thuật!`
4. inspect `ơ / ờ / ớ / ở / ỡ / ợ` as a complete family
5. only then build the ROM

Do not build another runtime ROM from an obviously malformed preview.

## Next probe

Planned:

**Probe 008 — Full Vietnamese Harmonized Thin-Clean Set**

It should:

- inherit Probe 003's proven direct-text framing
- preserve D038 and all scene logic
- replace the full Vietnamese glyph set coherently
- prioritize hỏi/ngã correctness
- include d/đ and uppercase D/Đ consistency
- remain thin, clean and readable

Runtime claim before user test: **NO**.
