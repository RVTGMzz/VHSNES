# Checkpoint 117 — Karaoke meaning-first draft review (source-only)

Date: 2026-10-16. Baseline: checkpoint 116, single cumulative IPS SHA256 `910e77ab5da5235c8aae1c5d9d3dbf3e697728466039250e8a4f82d45069f4bd`. No ROM/IPS rebuilt.

Read `HANDOFF_CURRENT.md` and `docs/CHECKPOINT_116_GAMEPLAY_AND_CAPTION_QA.md` before making changes. The existing runtime 113 correction at original offset 0x2B675 is already integrated and must **not** be counted as a new runtime fix.

## Verified editorial proposal

Added `translation/runtime/karaoke_draft_editorial_117.json` with five proposed source-anchored replacements in the **unused, not timing-certified** singable draft, at original offsets `0x2B47D`, `0x2B4FA`, `0x2B622`, `0x2B675`, `0x2B69D`. They address unsteady footing, bliss/paradise, marathon, necessity/urgency, and idiomatic physical stamina.

Read-only verification against live branch files confirms:
- 28/28 canonical source and draft offsets, Japanese strings, and canonical Vietnamese references align.
- 5/5 proposals match existing draft values and original Japanese source text.
- All proposed Vietnamese glyphs exist in the existing 160-entry V2 codepage.
- Whitespace-delimited token counts remain unchanged for each proposed line (8/5/8/8/8). This is **not** a syllable, rhythm or timing proof.
- Runtime 113 already expresses obligation at 0x2B675. No integrated lyric, ROM byte, script, pointer, timing table, checksum or IPS changed in 117.

**Not merged:** the five replacements remain proposed only. An attempt to update the existing singable-draft CSV was blocked by the connected GitHub write safety check. An attempt to add a dedicated Python source audit was also blocked. Do not report those operations as completed or claim CI executes that audit. The source-only JSON proposal is committed and independently compared to the current branch files; existing draft CSV remains unchanged.

## Next

Once a permitted edit path is available, apply the five proposals to `translation/source/karaoke_batch01_singable_v1_vi.csv` without touching the canonical meaning-first CSV or 113 runtime override, run `tools/audit_karaoke_source_104.py`, and add a fail-closed semantic source audit to CI. Separately verify real song timing and singability before substituting any singable draft into runtime. Continue a natural complete winning Story run and real mouse-motion QA when authorized original game assets and emulator are accessible. Do not generate individual IPS fragments or commit copyrighted game binaries.

Whole-game complete: **false**. Current cumulative release candidate remains checkpoint 116.
