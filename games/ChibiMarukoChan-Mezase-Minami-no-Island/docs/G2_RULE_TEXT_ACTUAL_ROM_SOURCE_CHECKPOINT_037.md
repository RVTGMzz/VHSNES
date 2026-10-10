# Chibi Maruko-chan SNES — Checkpoint 037: G2 actual rule text origins + 35 VS UI source guards

Date: 2026-10-11. Branch `chibi-maruko-bootstrap-01` in `RVTGMzz/VHSNES`.

## Content-first findings

The previous G2 queue had incorrectly classified three visible rule panel phrases as *unknown graphics*. Direct examination of exact original unheadered 2MiB ROM (SHA256 `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`) now confirms the corresponding **literal CP932 rule sentences** are present in the coherent direct-text bank. This means the meaning source is already in `translation/source/rules_tutorial_vi.csv`; do not waste time painting separate bitmap labels unless runtime observation later establishes an additional graphics copy.

| Exact original Japanese phrase | Actual first byte in ROM | Existing Vietnamese source |
|---|---:|---|
| ルールをせつめいするよ | `0x1E307` | Luật chơi đây! |
| ２本先取だよ | **`0x1E325`** | Ai thắng 2 ván trước sẽ thắng |
| ゲームの時間は勝つまでだよ | `0x1E339` | Chơi đến khi phân thắng bại |

The entire first rule text record begins at **`0x1E2FF`**, with eight spaces of layout preceding the first Japanese glyph. Two original fullwidth bullet tokens `8145` appear at `0x1E323` and `0x1E337`; three `816F` delimiters terminate the three Japanese phrases. These exact source spans are confirmed in the real clean ROM.

**Important bug repaired in canonical source:** `rules_tutorial_vi.csv` had offset **`0x1E326`**, the **second byte** of original fullwidth digit `２` encoded `82 51`. This would make offset-based insertion start in the middle of a Japanese character. It now correctly references **`0x1E325`**. The Vietnamese wording was clarified from the ambiguous `Thắng trước 2 ván` to **`Ai thắng 2 ván trước sẽ thắng`**, and the second rule to **`Chơi đến khi phân thắng bại`**. Both bullets are still represented in `vi_full` semantically; no runtime replacement has yet been assembled.

## G2 VS/minigame direct UI

On original ROM, **35 source rows** in `translation/source/minigame_ui_batch01_vi.csv` were individually checked for their exact Japanese CP932 bytes and correct source offsets in `0x288C2..0x28BFF`. They include rule instructions for throwing a ball, painting, pushing into the pool, the “how many rounds” setting, 1–5 round choices, CPU difficulty, 180 seconds / until victory, player slots, controller types, and stage.

Three rule descriptions have two literal layout spaces **at their canonical source offset**, so the Japanese characters start at offset +2; that is intentional and **not** another mid-CP932 error. All 35 expected labels pass the source-byte check. This is source-validation, not 35 newly translated lines or proof of actual menu rendering.

GitHub tool: `tools/audit_g2_rules_direct_sources_037.py` — exact clean ROM SHA, 3 source text lines + delimiters and bullets, 35 direct UI positions, canonical CSV validations. Local JSON report: `Chibi_G2_CP932_Source_Audit_037.json`.

- Local code syntax check: PASS.
- Direct original-ROM source/CP932 verification: PASS.
- Deliberately reintroducing CSV offset `0x1E326`: audit **FAILS as intended**.
- Restore `0x1E325`: audit PASS again.
- A smaller, representative local CSV checkout was used in the container for execution because this runtime cannot directly materialize connector-fetched GitHub text files; exact full GitHub contents were separately reviewed through the connected GitHub action. **No GitHub CI run observed.**
- No ROM contents were modified by the 037 G2 rule audit. The previous graphics-only 036 ROM and IPS remain unchanged.

## G2/G3 resource scouting (NOT a patch)

We reused the original retail game resource format (`$80:E8B2` decompress + type-0 scripts) to inspect actual nearby transition packages. 42 distinct decompressible graphic resources near the G2 routing/VS menu candidates were reconstructed to a 4bpp contact sheet (`chibi_g2_candidate_sprite_sheet_1.png` and `Chibi_G2_VS_Resource_Focused_037.png`). Most are character art, backdrops, UI ornament or shared kana glyph sheets; none individually proves a G2 rule image ready for rewriting.

A further atlas of **52 unique `source,destination VRAM` 4bpp sprite entries** used by the known package catalog was exported (`Chibi_G3_Result_Sprite_Atlas_037_1.png` through `_3.png`). Those images help narrow possible result artwork, but no definite retail Win/Lose/Continue/Ending text source with a screen execution proof was established.

**Do not promote a visually plausible tile sheet to a G3 patch offset** merely from this atlas. The live result-screen callback/path remains untraced.

## G2 queue status changes

`translation/runtime/content_first_graphics_queue_032.csv` now marks the three G2 rules above as `DIRECT_CP932_TEXT_SOURCE_FOUND` instead of `UNRESOLVED`. That means **their Japanese bytes and canonical Vietnamese source are known**; it does **not** mean the localized text has been injected into the graphics-only 036 ROM or that the retail screen callback was executed in an emulator.

The separate `今からやるよ` (“Bắt đầu thôi!”) is still an unresolved retail asset: its exact CP932 hit at `0x286EA` is **only within internal QA/debug descriptor prose** and must never be patched as a substitute for real visible text.

## Remaining tasks — user says content first, font later

1. Trace G2 actual rendered rule block pointers and validate its bounds/line breaks against current direct-text Build035, then integrate corrected **`0x1E325`** into the direct-text build source. User wants **fewer, larger builds**, so do not ask for a separate G2 ROM test right now.
2. For G3, follow the actual Win/Lose/Continue/Ending screen setup to its final data source instead of guessing image positions from a tile atlas. Source `0x286B4..0x287FC` is internal descriptors, not retail player-facing dialogue.
3. Find/reconstruct historical direct-text Build035 candidate (SHA256 `f8fb662a9e1b8fc5a5ff689f690ceaf332055ed86983e52b476a78852e4fd58d`) if available; integrate with graphics-only 036 patch ONLY after byte-overlap and bank86 relocation checks. Do not blindly IPS-overwrite translated game.
4. Real SNES gameplay runtime is still NOT TESTED for new graphics; font remains frozen at 031 per user instruction.

**037 measurable progress:** 1 canonical CP932 offset defect fixed; 1 rule wording updated; 3 literal G2 rule sources established; 35 G2 UI source records cross-checked; 0 new on-ROM graphics labels patched; 0 fabricated G3 source addresses. GitHub is updated, clean ROM preserved.
