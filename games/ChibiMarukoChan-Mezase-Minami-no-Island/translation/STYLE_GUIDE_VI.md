# Chibi Maruko-chan — Vietnamese localization style guide

## Core tone

This game is a cute school/family comedy, not a combat RPG.

Vietnamese should feel:

- playful, warm, childlike, and natural;
- appropriate for elementary-school friends, family, teachers, and light comedy;
- slightly retro/1990s in spirit without sounding stiff or archaic;
- faithful to each character's personality and recurring verbal quirks.

Avoid unnecessarily aggressive or battle-heavy wording when the scene is a school contest/minigame. Prefer `thi`, `thi đấu`, `so tài`, `chơi với nhau`, `chơi theo đội` over martial-sounding phrasing unless the original scene genuinely calls for it.

## Character voice anchors

- **Maruko**: casual, cheeky, curious, occasionally lazy; natural `tớ/cậu` with friends.
- **Tama-chan / Tamae**: gentle, supportive, earnest.
- **Maruo**: pompous, formal, dramatic. Preserve his `ズバリ` catchphrase with variants around `Nói thẳng ra!`.
- **Hanawa**: suave and theatrical; preserve `Hey` / `baby` when it is part of his joke/persona.
- **Narrator**: dry, witty, lightly teasing rather than harsh.
- **Family adults**: warm, familiar family speech; jokes should stay domestic and light.

## Naming

Preserve established character names such as `Maruko`, `Maru-chan`, `Tama-chan`, `Hanawa-kun`, `Maruo`, `Sakura-san`, `Honami-san` when context calls for the honorific. Do not over-Vietnamize names.

## Translation layers

- `vi_full` is the meaning-first Vietnamese source of truth. It may use full Vietnamese diacritics and natural phrasing regardless of current ROM/font limits.
- Runtime candidates are generated later after the font/codepage and layout are proven.
- Do not shorten `vi_full` merely to fit current byte spans.
- Do not treat scanner control-like glyphs such as `｛` or other decoded artifacts as ordinary dialogue until their semantics are proven.

## Menu direction

Prefer friendly school-game wording:

- `ストーリーモード` → `Chế độ Cốt truyện`
- `対戦モード` → `Thi đấu`
- `チーム対戦モード` → `Thi đấu theo đội`
- `まるこペイント` → `Maruko tập vẽ`
- `まるこみくじ` → `Bói vui cùng Maruko`
- `サウンド` → `Âm thanh`

Graphic/tile text and normal script text may use different render systems. Do not assume one font/layout solution covers both.
