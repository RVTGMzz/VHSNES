# Graphics / Tilemap Pass 001 Audit

Updated: 2026-09-18 +07

This note starts the post-direct-text graphics/tilemap reverse track for **Chibi Maruko-chan - Mezase! Minami no Island!!**.

## Current conclusion

The visible Japanese still reported by the user is **not coming from the normal direct-text path already patched**.

A contiguous CP932 block at `0x286B4..0x287FC` contains internal screen/demo descriptions which name the same visible labels, but these are **metadata / debug / review descriptors**, not the retail on-screen assets to replace.

Do not patch these descriptor strings and claim the visible graphic is translated.

## Confirmed descriptor/debug block

- `0x286B4`: `『はじめから』 / 『パスワード』の画面です。`
  - describes the Start / Password screen
- `0x286EA`: `『今からやるよ』の会話デモです。`
  - describes the conversation demo
- `0x28714`: `『ＶＳ』のデモです。`
  - describes the VS demo
- `0x28732`: `まるちゃんが、勝った時のデモです。`
  - describes the win demo
- `0x2875E`: `まるちゃんが、敗けた時のデモです。`
  - describes the lose demo
- `0x2878A`: `コンティニュー画面です。`
  - describes the Continue screen
- `0x287AC`: `ストーリーモードを やめる時の画面です。`
  - describes the quit-story screen
- `0x287E0`: `最終勝利デモです。`
  - describes the final-victory demo
- `0x287FC`: `エンディングです。`
  - describes the ending

## Added title-screen target — Batch G0

The first retail title/intro screen is now part of the localization scope.

Visible title:

`ちびまる子ちゃん めざせ！南のアイランド！！`

Vietnamese target:

`Chibi Maruko-chan: Tiến tới đảo phương Nam!!`

Additional requested credit:

`Việt hóa bởi VôtriValley`

Original copyright/publisher attribution must remain intact. See `docs/GRAPHICS_G0_TITLE_SCREEN_PLAN.md`.

## Visible graphics targets

### Batch G1

- `どれにする？` -> **Chọn gì đây?**
- `はじめから` -> **Bắt đầu**
- `パスワード` -> **Mật khẩu**

### Batch G2

- `今からやるよ` -> **Bắt đầu thôi!**
- VS / rule-panel visible text:
  - `ルールをせつめいするよ` -> **Luật chơi**
  - `２本先取だよ` -> **Thắng 2**
  - `ゲームの時間は勝つまでだよ` -> **Đến khi thắng**

### Batch G3

- `勝ち` -> **Thắng**
- lose-result graphic -> **Thua**
- `コンティニュー` -> **Tiếp tục**
- quit-story graphic -> **Hủy / Thoát** depending exact screen context
- ending / chapter / large title cards, including visible Japanese title-card text reported by the user

## Prior heading reverse

The pink main-menu heading `どれにする？` was previously checked against:

- direct CP932;
- simple full-width/variant encodings;
- proven glyph-ID sequence;
- sparse/interleaved code guesses;
- simple 16-bit tilemap/index patterns.

No exact safe storage sequence was established.

See:

- `docs/HEADING_REVERSE_001.md`
- `docs/HEADING_REVERSE_002.md`

Do not guess an offset.

## Direct-text audit boundary

After Build 035, the remaining unchanged kana-rich scanner hits are limited to:

- the descriptor/debug family above;
- likely effect/debug/noise candidates such as `ごごごごご-`;
- binary false positives.

Therefore the still-visible Japanese in user screenshots should now be treated as **graphics/tilemap/compressed-asset/alternate-renderer work**, not ordinary direct CP932 strings.

## Guardrails

- Keep graphics/tilemap edits as a separate patch layer from the direct-text runtime layer.
- Do not commit ROMs to GitHub.
- Use the exact clean-ROM contract for reproducibility.
- Build/test candidates may be layered on the latest direct-text candidate, currently Build 035, but document the dependency explicitly.
- Do not patch the descriptor/debug block and call the retail graphic translated.
- Do not claim Runtime PASS until the user tests the exact affected screen.
- Prefer one high-information graphics probe or a larger coherent batch because the user wants to minimize repeated testing.

## G1 trace infrastructure checkpoint

A new read-only helper now exists:

`tools/trace_g1_render_path.py`

It is documented in:

`docs/G1_RENDER_PATH_TRACE_003.md`

The tracer does **not** patch ROM bytes. It is intended to establish the missing evidence chain by collecting:

- xrefs to the screen/menu/descriptor anchors;
- direct calls to the proven parser and glyph renderer;
- bank-`$85` VRAM/PPU/DMA register stores and nearby fixed-size control-flow targets;
- candidate local and long ROM-pointer runs.

At the checkpoint that added the tool, no canonical ROM binary was available in the active runtime, so the tracer has not yet produced a clean-ROM report. Therefore there is still **no proven G1 asset offset** and no graphics build may be claimed from this checkpoint alone.

## G1 Shape Probe 004

The graphics reverse track now has a second independent evidence layer:

- `tools/scan_g1_shape_fingerprints.py` extracts the real 12x12 source glyph masks for all G1 Japanese characters and scans candidate raw 1bpp / SNES 2bpp / 4bpp asset layouts.
- `tools/correlate_g1_evidence.py` cross-ranks those shape clusters against pointer/DMA/xref evidence from `trace_g1_render_path.py`.

The intended promotion rule is deliberately strict: a multi-glyph bitmap cluster becomes high-priority only when a candidate pointer target lands inside it. Even then, it is still only a reverse target until the actual screen setup reaches that path and the decoded asset reproduces the visible label.

Static fixture validation for both new tools is **PASS**. No canonical-ROM execution is claimed yet because the binary was unavailable in the active runtime.

See `docs/G1_SHAPE_PROBE_004.md`.

## Next action

Reverse the **actual rendered asset path** for Batch G1:

1. `どれにする？`;
2. `はじめから`;
3. `パスワード`.

Determine whether each is:

- raw 2bpp / 4bpp tile graphics;
- a tilemap referencing reusable glyph tiles;
- compressed graphics;
- or another runtime renderer.

Once an asset path is proven, make a guarded graphics probe/build on top of the current direct-text candidate without disturbing the direct-text/font layer.
