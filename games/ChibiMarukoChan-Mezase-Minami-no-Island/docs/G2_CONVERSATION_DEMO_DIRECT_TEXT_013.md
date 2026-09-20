# G2 Conversation Demo Direct Text Proof 013

Updated: 2026-09-20 +07

This checkpoint corrects the previous graphics-first interpretation of the G2 `今からやるよ` target.

## Runtime feedback from Probe 001

The D038-disable probe produced a visibly unstable/changed background palette while the screen still showed Japanese dialogue.

Important clarification:

Probe 001 was intentionally built from the **canonical clean ROM**, not from the latest Vietnamese candidate. Therefore seeing Japanese text in that probe did not mean the Vietnamese layer regressed.

The color/palette disturbance shows that removing `$88:D038` affects shared scene/controller setup. It is not safe to treat D038 as a pure text-source switch.

## Key correction: 今からやるよ is descriptor-only naming

The internal descriptor at file `0x286EA` contains:

`『今からやるよ』の会話デモです。`

This describes the sequence as a **conversation demo**. The phrase `今からやるよ` is an internal semantic label, not evidence that those exact characters are the player-facing visible text.

The actual player-facing text seen in runtime is stored directly in the normal CP932/direct-text bank.

## Newly proven direct-text records

The exact runtime screenshot text was found directly in the canonical ROM at:

### 0x181CE

106-byte payload:

`「ズバリっっ！  りゅうがくしても｛    はずかしくないよう            ｛    反射神経を  養いましょう」    ｛`

Meaning-first Vietnamese:

**Nói thẳng nhé! Để sau này có đi du học cũng không phải xấu hổ, ta hãy rèn luyện phản xạ!**

### 0x18247

106-byte payload:

`「ズバリっっ！  りゅうがくしても｛    はずかしくないよう  島から    ｛    おちない  とっくんでしょう！」｛`

Meaning-first Vietnamese:

**Nói thẳng nhé! Để sau này có đi du học cũng không phải xấu hổ, đây là bài tập để không bị rơi khỏi đảo!**

### 0x182C0

106-byte payload:

`「ズバリっっ！  りゅうがくしても｛    はずかしくないよう            ｛    芸術センスを  みがくのです」  ｛`

Meaning-first Vietnamese:

**Nói thẳng nhé! Để sau này có đi du học cũng không phải xấu hổ, hãy trau dồi cảm quan nghệ thuật!**

These three player-facing rows were not present in the previously committed Story/tutorial translation CSVs.

Therefore they are **new coverage**, not merely a rebuild of existing rows.

## Source and runtime layers

Added:

- `translation/source/g2_conversation_demo_vi.csv`
- `translation/runtime/g2_conversation_demo_compact_v1.csv`

Meaning-first rows remain full/natural in `translation/source/`.

The fixed-field runtime layout preserves the original three-line byte budgets exactly:

- line 1: 32 bytes
- line 2: 34 bytes
- line 3: 34 bytes
- three existing `0x816F` line-break markers
- total payload: 106 bytes

Compact runtime text:

Common first two lines:

- **Nói thẳng nhé!**
- **Du học chớ xấu hổ!**

Third lines:

- **Luyện phản xạ!**
- **Tập khỏi rơi!**
- **Rèn gu mỹ thuật!**

## Probe 002

Added reproducible builder:

`tools/build_g2_conversation_direct_probe.py`

The builder:

- requires the exact canonical clean ROM;
- keeps the original D038 path unchanged;
- uses canonical `vi_codepage_v4_fe4_native.csv`;
- uses `vi_glyphs_v5_fe4_thin.json`;
- installs only the Vietnamese mappings/glyphs required by these three fields;
- validates the original 106-byte source field SHA-256 values;
- preserves the NUL terminators and exact 32/34/34 layout;
- changes no graphics/palette/controller logic;
- rewrites the SNES checksum.

Local Probe 002 build:

- artifact: `Chibi_Maruko_G2_DIRECT_TEXT_PROBE_002.sfc`
- total diff bytes: **642**
- SHA-1: `60968e7dfb6f38158003cc57723569d88f66a849`
- SHA-256: `4c526be4554cbec58153e11c11afc95f42aa132466a7b631a20155fea807df9b`
- checksum: `0x4C21`
- complement: `0xB3DE`

## Claims

- school-front group-4 background identity: **STATIC PASS**
- visible runtime dialogue storage: **DIRECT-TEXT STATIC PASS**
- three newly recovered player-facing rows: **TRANSLATED / SOURCE COMMITTED**
- `今からやるよ` as a visible graphics banner: **REJECTED MODEL**
- Probe 002 build: **STATIC PASS / READY FOR TEST**
- Probe 002 runtime render: **RETEST REQUIRED**
- G2 Runtime PASS: **NO** until user gameplay/screenshot confirmation

Do not resume graphics hunting for the literal descriptor phrase unless later runtime evidence shows those exact characters visible somewhere.
