Tiếp tục dự án Việt hóa **Chibi Maruko-chan SNES** từ repo `ronvotri/Viet-Hoa-SNES`, branch `chibi-maruko-bootstrap-01`.

Đọc trước:

- `games/ChibiMarukoChan-Mezase-Minami-no-Island/HANDOFF_CURRENT.md`
- `games/ChibiMarukoChan-Mezase-Minami-no-Island/docs/RUNTIME_BUILD_035_CHECKPOINT.md`
- `games/ChibiMarukoChan-Mezase-Minami-no-Island/docs/GRAPHICS_TILEMAP_PASS_001_AUDIT.md`
- `games/ChibiMarukoChan-Mezase-Minami-no-Island/docs/HEADING_REVERSE_001.md`
- `games/ChibiMarukoChan-Mezase-Minami-no-Island/docs/HEADING_REVERSE_002.md`

Canonical clean ROM SHA1: `08a2415362f69788ec76b1a36044dc1f1a5f2ea1`.

## Current checkpoint

Latest large direct-text candidate is **Build 035**:

`Chibi_Maruko_Build_035_QUIZ01_CREDITS_PASS_READY.sfc`

Static identity:

- checksum `0x6547`
- complement `0x9AB8`
- SHA-1 `054380f9b452f245471e6309eb33c7486d581462`
- SHA-256 `f8fb662a9e1b8fc5a5ff689f690ceaf332055ed86983e52b476a78852e4fd58d`
- runtime status: **UNTESTED**

Do not commit ROMs to GitHub.

Build 035 already carries the large direct-text runtime chain: compact menu, 328 Story fields, Minigame UI/rules, Fortune, large Quiz/Maruko Q insertion, stage labels, karaoke direct candidates, credits labels, story hotfixes, and current font/codepage fixes.

Meaning-first layer remains **1,018 release-intent rows**. Keep `vi_full` canonical; compact runtime text is separate.

## Font status

Do not restart font reverse.

The Golden Sun GBA donor experiment was rejected for Chibi.

Build 034 statically repaired issues reported after Build 033:

- T too thick;
- V thin;
- A/K/L thin;
- e thin/floating;
- g unclear/clipped;
- circumflex wrong orientation;
- dot-below disappearing.

These fixes are inherited by Build 035 but are **not yet runtime-release PASS**.

## Main task now: graphics/tilemap reverse

The remaining visible Japanese in screenshots is no longer a normal direct-text problem.

Important: the CP932 block around `0x286B4..0x287FC` only contains **internal screen/demo descriptors**, not the retail visible assets. Do not patch those descriptors and claim the graphics are translated.

Start with **Graphics Batch G1**:

1. `どれにする？` -> **Chọn gì đây?**
2. `はじめから` -> **Bắt đầu**
3. `パスワード` -> **Mật khẩu**

Then G2:

- `今からやるよ` -> **Bắt đầu thôi!**
- VS/rule graphics:
  - `ルールをせつめいするよ` -> **Luật chơi**
  - `２本先取だよ` -> **Thắng 2**
  - `ゲームの時間は勝つまでだよ` -> **Đến khi thắng**

Then G3:

- `勝ち` -> **Thắng**
- lose result -> **Thua**
- Continue -> **Tiếp tục**
- quit-story -> **Hủy / Thoát** after exact context check
- ending/chapter/large title cards

For G1, determine whether the actual visible asset uses raw 2bpp/4bpp tiles, tilemap composition, compressed graphics, or another renderer. Do not guess offsets.

The pink `どれにする？` heading has already failed simple CP932/glyph-ID/interleaved/tilemap sequence searches. Continue from the existing reverse docs instead of restarting.

## Workflow guardrails

- exact clean-ROM identity;
- preserve source identity before writes;
- separate direct text, compact runtime text, font/codepage, and graphics/tilemap layers;
- dry-run/diff-surface/checksum gates;
- no broad scanner-noise translation;
- no Runtime PASS without screenshot/gameplay evidence;
- user prefers **fewer, larger tests**, so use one high-information probe or one coherent graphics batch where technically safe.

Continue directly with the graphics/tilemap investigation and update `HANDOFF_CURRENT.md` when a new asset path or build checkpoint is proven.
