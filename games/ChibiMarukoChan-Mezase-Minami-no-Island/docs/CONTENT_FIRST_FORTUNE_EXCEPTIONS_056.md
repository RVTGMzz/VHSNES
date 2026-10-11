# Chibi Maruko-chan SNES — Checkpoint 056: two safe Fortune exceptions

Date: 2026-10-11. Branch `chibi-maruko-bootstrap-01`.

## Physical work verified on actual clean Japanese ROM

Original unheadered ROM: **2,097,152 bytes**, SHA256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`.

The 048 Fortune batch had six intentionally excluded source offsets. Checking their exact original CP932 string bytes and `816F` script markers on the uploaded ROM showed:

| Offset | Original | Canonical full Vietnamese | Resolution |
|---|---|---|---|
| `0x2BD5E` | `天の声` | Lời trời mách | Pending larger than three original glyph cells; don't shorten to ambiguous `Lời` |
| **`0x2C413`** | `体育が開運のカギ` | Môn Thể dục là chìa khóa may mắn | **Added: `Vận động`**, eight cells |
| **`0x2C601`** | `プリンを食べてみよう` | Thử ăn pudding xem | **Added: `Ăn pudding`**, ten cells |
| `0x2C86B` | `また来週` | Hẹn tuần sau | Pending larger than four original glyph cells |
| `0x2CA7D` | `きいろ` | Vàng | Pending four letters in a three-cell slot |
| `0x2CADD` | `しろいろ` | Trắng | Pending five letters in a four-cell slot |

The two accepted original field windows were located and replaced with their existing `0x84xx` Vietnamese codepage equivalents **on the actual clean-ROM source byte array**, without changing adjacent native script metadata or the two original `81 6F` line boundaries. An independent IPS decoder reapplied the resulting text-only patch to the original 2MiB ROM and reproduced the target bytes exactly.

| Static source-only proof | Value |
|---|---|
| New reviewed Fortune original fields | **2** |
| Writable / actually changed source bytes | **36 / 36** |
| Original `816F` line separators retained | **2** |
| Text-only IPS | **54 bytes, 2 records** |
| Text-only IPS SHA256 | `84e30fe4f1bad5621934de99dcc9e0c3a11efd64152f36af676b42e56eca31be` |
| Text-only overlay ROM SHA256 | `d308a8a4b9b87a2c496fda3409398df6803c98381424a2a3a253f274d0491071` |
| Independently replayed IPS on clean ROM | **PASS** |
| Fully integrated 055+056 Vietnamese ROM | **NOT BUILT** |
| Emulator runtime QA | **NOT TESTED** |

**Important:** The above text-only overlay is **NOT playable**; the clean original ROM lacks the custom Vietnamese font and no SNES checksum was rewritten for this experiment. It was not distributed or uploaded.

The earlier G2 055 builder contained a concrete guard bug: it checked only two ASCII indentation bytes before its last two lines, whereas the original ROM physically has **four** bytes on each. Corrected `tools/build_content_first_055_g2_rules.py` to enforce the real **8 / 4 / 4 ASCII space** layout. The previous guard would have incorrectly failed in the combined build despite correct translations.

## Source, build and actual blockers

- `translation/runtime/fortune_exceptions_2_056.json` — original/full Vietnamese references, reviewed compact forms, exact physical QA hashes, and the four remaining genuine expansion-only cases.
- `tools/build_content_first_056_fortune_2.py` — guarded merge into exact 055 ROM. Rechecks Japanese bytes, unchanged original full Vietnamese CSV references, active V2 Unicode glyph assignments, original `816F`, checksum, diff whitelist, and full clean-ROM IPS replay.
- `tools/rebuild_content_first_056_full_chain.py` — single command to combine user-owned clean Japanese ROM plus original checkpoint043 IPS through stages 044/045/046/047/048/054/055/056.

From the game directory, **only after the exact historical checkpoint043 clean IPS is accessible**:

```bash
python tools/rebuild_content_first_056_full_chain.py clean.sfc checkpoint043.ips --ips final056.ips --report final056_qa.json --allow-untested
```

Original 043 IPS SHA256 must be `d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50`. Historical ZIP `Chibi_043_G0G1_176Fields_Story58_Content_First_UNTESTED.zip` remains visible as Library metadata only; attempts to materialize it and a previous Probe008 ROM in the active runtime were denied. Their bytes **have not** been read/extracted. The user's new clean ROM **is** mounted and verified.

After successful combined binary output, the project would have **153/157 Fortune canonical source entries physically represented** (33 checkpoint040 +15 checkpoint047 +103 checkpoint048 +2 checkpoint056) — but this is **conditional** until full 048/056 rebuild is executed, **not a current playable completion claim**. Quiz still has many entries unpatched, plus G3 outcome art and visual/emulator QA.

Do not ship test overlays or copyrighted ROMs; retain complete canonical full text for four pending Fortune layout expansions. Font work last per user's priority.
