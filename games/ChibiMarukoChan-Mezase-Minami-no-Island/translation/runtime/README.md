# Runtime candidate layer

Runtime text is renderer/byte-budget specific and must be derived from `translation/source/`.

Current proven state on the visible mode-selection menu path:

- 2-byte Vietnamese codepage via lead `0x84`: runtime proven;
- multiple accented Vietnamese glyphs: runtime proven on this menu path;
- raw 1-byte ASCII substitution: rejected by Probe 002 because that build froze;
- pointer relocation / field expansion: still UNPROVEN;
- general story/quiz control semantics outside the menu path: still UNPROVEN.

Keep `vi_full` as the source-of-truth meaning layer. Runtime labels may be shortened only in this directory and must never silently overwrite `vi_full`.

## Main menu compact V1

`main_menu_compact_v1.csv` contains exact-fit 2-byte-unit labels for the ten direct menu fields around `0x28818..0x288B9`.

These are practical runtime candidates for the fixed-width menu fields, not replacements for the fuller source translations. Examples:

- `Chế độ Cốt truyện` -> runtime `Truyện`;
- `Thi đấu theo đội` -> runtime `Đấu đội`;
- `Bói vui cùng Maruko` -> runtime `Bói`;
- `Âm thanh` -> runtime `Âm`;
- `Stereo` -> temporary runtime abbreviation `ST`.

Build 024 uses these candidates on top of Build 023 / Probe 019. It preserves the accepted pre-GBA font/codepage baseline and changes only the ten menu text spans plus SNES checksum/complement.

Do not call these compact labels final if relocation/expansion later makes the full wording fit cleanly.

## UI choices compact V1

`ui_choices_compact_v1.csv` contains compact Vietnamese candidates for the direct minigame / setup / quiz-choice fields.

Current preferred compact set includes:

- CPU difficulty: **Dễ / Vừa / Khó**
- per-round time heading: **Mỗi ván**
- player slots: **P1 / P2 / P3 / P4**
- slot states: **Chơi / CPU / Nghỉ**
- stage heading: **Màn**
- start instruction: **Bấm START**
- quiz continuation prompt: **Tiếp tục?**
- yes choice: **Có**

Do not force poor abbreviations merely to fit. Fields such as **Đến khi thắng**, **Không kết nối**, **Chuột**, and **Không** are explicitly marked `runtime_needs_expansion` when the current fixed 2-byte-unit field is too small.

This layer is a runtime candidate only. Full natural Vietnamese remains in the source/editorial layers.

## Graphics UI labels V1

`graphics_ui_labels_v1.csv` freezes full-diacritic redraw targets for the remaining graphics-driven game-flow UI.

Examples:

- **Chọn gì đây?**
- **Bắt đầu**
- **Mật khẩu**
- **Bắt đầu thôi!**
- **Luật chơi**
- **Thắng 2**
- **Đến khi thắng**
- **Thắng / Thua**
- **Tiếp tục**
- **Thoát**
- **Chiến thắng cuối cùng!**
- **Kết thúc**

These are graphics-layer wording candidates, not direct-text byte-fit strings. Preserve full Vietnamese whenever the redrawn asset path allows it.

`Thoát` is context-resolved for `やめる` from the Story Mode quit descriptor. Other descriptor-only result/ending assets still require retail-screen/path confirmation before redraw.

