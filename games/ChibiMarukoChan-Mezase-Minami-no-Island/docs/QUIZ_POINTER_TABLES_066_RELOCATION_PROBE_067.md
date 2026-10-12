# Chibi Maruko-chan SNES — checkpoint 066/067: recovered all Quiz pointers and byte-only long-answer relocation

**CHECKPOINT 073 SAFETY UPDATE.** The original SNES routine copies 66 bytes from the answer source. Single-option probe 067's relocation at `0x37FE0` lies only 32 bytes from end of bank06 and causes a 34-byte out-of-bank read. Its byte-level IPS replay is not evidence of safe engine execution. See `docs/CHECKPOINT_073_QUIZ_ENGINE_66_BYTE_COPY.md`.

Date: 2026-10-12 · Branch `chibi-maruko-bootstrap-01` · Original ROM SHA256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`.

## 066 — The actual 9 × 50 bank-06 LoROM pointer arrays

This is a major structural discovery on the user-supplied **exact original Japanese 2MiB ROM**, beyond the delimiter-only checkpoint 064/065. At ROM `0x310DF`, there are **nine parallel contiguous arrays of 50 little-endian 16-bit addresses**, spaced by exactly **104 bytes = 50 pointer words + 2 sentinel words**. Each 16-bit CPU address maps to the same SNES bank 06 / LoROM 32KiB area via `PC=0x30000+(pointer-0x8000)`.

| Field | Table start (PC) | Verified 50 destinations |
|---|---|---|
| Question footer metadata (not yet decoded) | `0x310DF` | 50 paired footer records |
| Main question text | `0x31147` | 50 `0E 00 0F 0A` intro slots |
| Question continuation | `0x311AF` | 50 `0E 00 0F 0E` slots |
| Choice 1 | `0x31217` | 50 `0E 06 0F 12` answer slots |
| Choice 2 | `0x3127F` | 50 `0E 06 0F 12` answer slots |
| Choice 3 | `0x312E7` | 50 `0E 06 0F 12` answer slots |
| Explanation part 1 | `0x3134F` | 49 `0E 00 0F 08`, 1 `0E 00 0F 0A` |
| Explanation part 2 | `0x313B7` | 49 `0E 00 0F 0E`, 1 `0E 00 0F 10` |
| Explanation part 3 | `0x3141F` | 49 `0E 00 0F 14`, 1 `0E 00 0F 16` |

All **450 pointer entries** are located in the original game and map into the expected **50** question groups. **Every array is a permutation of all 50 groups in exactly the same order** — it is not a random binary address coincidence. Each array has **two extra 16-bit sentinel words**, and both equal the corresponding field address for **question #50**. Total original entries including sentinels: **468** (450 + 18). Last table ends at `0x31487`. The table-array question order begins `#3,#4,#5,#10,#14,#15,...` and is not the original script's physical order.

Crucial exception: main-question #1 pointer leads to `0x31D43`, three bytes past the inferred block boundary `0x31D40`; this is expected, and the source audit pins it. All **150 answer-field pointers** land exactly four bytes before their original full Japanese source string. Examples:
- **Question #6, answer #1**: ROM pointer word at `0x3123D` is `67 A5`, addressing `0x32567` (`0E 06 0F 12`) and original Japanese answer `じてんしゃ` at `0x3256B`.
- Question #1, answer #1: pointer `0x3125F` → `0x31DB9` → source `0x31DBD`.
- Question #50, answer #1: pointer `0x31239` → `0x367EF` → source `0x367F3`.

**This positively identifies the original address references for all 150 answers.** The encoded *correct-answer index* and actual SNES UI width/selection behavior remain unverified. None of these 450 addresses have been altered in an officially approved combined ROM.

Source: `tools/audit_quiz_pointer_tables_066.py` consumes the checkpoint065 50-question/150-answer atlas and checks all 450 pointer targets and the 18 sentinel words on the exact Japanese game ROM; it exports the source ROM offset and the CPU address for each of nine per-question slots. It only emits a QA JSON, never a ROM/IPS.

## 067 — **Experimental** answer relocation with a real 16-bit pointer

Having identified the address table, ran two in-memory **source-only byte/IPS experiments** on the exact original ROM. Target is the original question #6 / choice #1, whose original five-glyph answer `じてんしゃ` is **“Xe đạp”** (six glyphs including space), formerly blocked by the old fixed-size slot.

The experiment copies a complete new string record (four native bytes `0E 06 0F 12`, longer text, and original `81 6F 00` terminator) to `0x37FE0`, inside the original end-of-bank `FF` padding. The earlier script-end filler at `0x36907` remains intact. It changes **one 16-bit pointer**, `0x3123D: 67 A5 → E0 FF` (SNES bank06 CPU address `0xFFE0`), leaves the original five-character Japanese answer at `0x3256B` byte-identical, recomputes SNES checksum and independently applies the in-memory clean-ROM IPS back to the original.

| **Unapproved** original-ROM source experiment | Longer native Japanese `じてんしゃです` | Vietnamese V2 codepage `Xe đạp` |
|---|---:|---:|
| Relocated record total bytes | 21 | 19 |
| Modified original ROM bytes | 27 | 25 |
| In-memory IPS records | 3 | 3 |
| In-memory IPS size | 50 B | 48 B |
| IPS SHA256 | `29575dfce7b27cfdad91fa1647e07f1dc8032a460fe919bcc2052d58580452a4` | `339f1426a87bba18fdd227f32e1eb32fe43c534cc722d42934efa1e40d565dc6` |
| In-memory resulting ROM SHA256 | `c014ea1aae6b36b137899687ea65b19134610623ec23fa92d8ace6df4a51f221` | `017db9ebc59190c0dd131d6b175b75c8cc98e42bb05483e4decfcfb8a740b05f` |
| SNES checksum | `0x072D` | `0x0637` |
| Source byte/IPS replay on exact 2MiB Japanese ROM | **PASS** | **PASS** |
| Vietnamese font in unmodified Japanese ROM | n/a | **ABSENT** |
| Emulator rendering/navigation QA | **NOT TESTED** | **NOT TESTED** |
| Approved for integration/release | **NO** | **NO** |

The native Japanese test uses existing Japanese glyphs. The Vietnamese test uses unchanged `vi_codepage_v4_fe4_native.csv` code values: `X=8470`, `e=8477`, `space=8440`, `đ=84A7`, `ạ=84AE`, `p=8483`. Both prove **addressable ROM bytes and IPS/checksum validity only**. Neither proves the game's executable reads a relocated record correctly, displays it, highlights the right answer, or returns to its question flow. This is **not** a playable Vietnamese localization patch. No copyrighted ROM, font, or trial IPS was distributed.

Source: `tools/probe_quiz_relocation_067.py`, dependent on the 066 verified pointers. It generates the two simulated full-ROM images in memory, recomputes checksum, validates every changed byte belongs to the approved *experimental* pointer/FF/checksum ranges, pins the exact SHA and IPS replay, then discards the binary images; optionally emits a JSON QA report.

## How to run, and what must be verified next

From the Chibi game project directory (with the user's exact original `.sfc`):

```bash
python tools/build_quiz_answer_atlas_065.py clean.sfc --report quiz065_atlas.json
python tools/audit_quiz_pointer_tables_066.py clean.sfc --report quiz066_pointers.json
python tools/probe_quiz_relocation_067.py clean.sfc --report quiz067_byte_probes.json
```

**Real next acceptance gate:** use a temporary **local, user-owned ROM** with the native-Japanese relocation candidate in an actual SNES emulator, navigate Quiz question #6, verify choice #1 is rendered with extra characters and stays navigable, test answer correctness and return flow. Then repeat on the real integrated Vietnamese V2 font ROM, and only then approve a versioned translation relocation builder that batches remaining 81 long answer strings. Until then, the stage-067 source experiments contribute **zero newly accepted translated fields**.

This does not resolve the earlier production blocker: the exact 043 clean-source IPS expected SHA256 `d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50` remains unavailable as raw bytes. The full 061 combined patch has not been rebuilt; no emulator QA can be asserted. Quiz staging remains **279/381** (69 out of 150 answer alternatives staged, 81 out of 150 pending). Four Fortune exceptions and G3 results also remain. **Content first; font visual polish last.**
