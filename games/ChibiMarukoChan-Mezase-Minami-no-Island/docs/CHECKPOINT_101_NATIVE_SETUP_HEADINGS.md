# Checkpoint101 — five native selection and VS setup headings

2026-10-15. Claude's resumed session added private layer/VRAM diagnostic tools;
the source tree, remote branch and cumulative100 artifact were unchanged.
Those diagnostic files were retained. Work resumed from the exact100 ROM.

Five visible native headings are now Vietnamese:

| Native heading | Replacement | Type0 package |
| --- | --- | --- |
| どれにしようかな？ | Chọn trò chơi | 82:A239 |
| プレーヤーの設定 | Người chơi | 82:A358 |
| ルールを決めよう！ | Thiết lập luật | 82:A37E |
| だれにする？ | Chọn nhân vật | 82:A294 |
| チームを決めよう！ | Chia đội | 82:A332 |

`build_native_setup_headings_101.py` replaces only these package owners. One
private C706F OBJ copy hides the native heading glyphs. Private BG1 assets
retain original banner/frame pixels and composite 15px Tahoma Bold ink onto
the banner; a transparent replacement would punch holes in the ribbon.
New BG1 tiles start at256, beyond all native map references. Existing BG1
bytes and all original OBJ resources are retained. Native character/team
packages reload D1782, preserving their portrait/marker sprite pages.

Palette7 slots14/15 supply white/black. The original palettes MUST remain
unchanged: the minigame intro reuses one palette and uses those colors.
Private 514-byte palette tables and native bank81 job scripts are selected
only at the five verified initializer sites. C47D categorizes scripts by
address; relocating a script requires its C4EB low-range initialization path,
which sets the opcode, original-script pointer and operand pointer. Merely
changing the job type is incorrect. The emitted wrapper uses the native
allocator, checks carry, then invokes C4EB. Exact native code is guarded.

Native Snes9x execution boots from the main menu and passes through game
selection, intro, player/rule/character/team selection. A stable PPU audit
against the same checkpoint100 input sequence verifies all seven screens:
BG1 tilemap and referenced tiles outside the heading are identical; every
live nonheading OBJ cell is identical; only CGRAM126/127 change in the five
target screens. Main menu and intro palette remain identical. Background
scroll phase can differ because the new resources take longer to load.
Visual review is still required in addition to byte comparisons.

Rebuild from the original ROM + historical043 ZIP with
`tools/build_cumulative_101.py`, local `--font-bold`/`--font-regular`, `--ips`
and `--report`. It rebuilds087–101 and emits one clean-ROM-relative IPS.

Final IPS:124,016 bytes, SHA256
`9cc673b08d2097b1733bff6f6d21e047f1403dc2c5ae28f4003ec80b90c949bb`.
Patched ROM SHA256:
`6fa7654443c23db2275487c7f32c0d4efb3bb71d51021b1d6fbc2715194d459e`.

Whole-game completion remains FALSE. Japanese art still includes minigame
names on balloons and their intro titles, character nameplates, team labels
on the selection screen, victory/final-victory/ending and unreviewed modes.
The result board's TWO Đội labels remain fixed by099. Source aliases and
natural complete playthrough QA remain pending; historic Quiz counts are
still279/381. Do not claim complete localization from this heading checkpoint.
