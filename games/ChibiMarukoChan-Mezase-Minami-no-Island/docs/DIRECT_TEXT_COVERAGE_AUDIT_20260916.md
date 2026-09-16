# Direct-text coverage audit — 2026-09-16

Branch: `chibi-maruko-bootstrap-01`

Purpose: separate proven coherent direct CP932/Shift-JIS-like text banks from scanner false positives, graphics/tilemap text, and internal/debug-only strings.

## Proven coherent direct-text banks

### Main story

- approximate range: `0x181CC .. 0x1DE81`
- meaning-first Vietnamese: translated through the currently discovered visible ending sequence
- source files: Story Batch 01–03

### Credits

- approximate range: `0x1DED8 .. 0x1E2D8`
- roles translated; personal names preserved
- file: `translation/source/credits_vi.csv`

### Rule/tutorial text

- around `0x1E2FF .. 0x1E34F`
- direct rule lines translated
- file: `translation/source/rules_tutorial_vi.csv`

### Internal QA / debug reference block

- approximate range: `0x2865E .. 0x287FC`
- translated only as reverse-engineering reference
- file: `translation/source/internal_debug_reference_vi.csv`
- **excluded from normal player-facing translation count**

This block contains a Sakura Production video-submission deadline and meta descriptions such as `this is the Start/Password screen`, `this is the VS demo`, `this is the Continue screen`, and `this is the ending`. Its wording strongly indicates an internal development/test navigation block rather than ordinary retail player text.

Useful navigation clues recovered directly from raw ROM:

- submission date `８／３１`
- `『はじめから』『パスワード』`
- `『今からやるよ』`
- `『ＶＳ』`
- Maru-chan win demo
- Maru-chan loss demo
- Continue screen
- Story Mode quit screen
- final-win demo
- ending

Do not patch these ten rows into a normal release unless runtime evidence proves the internal block is player-visible.

### Main menu and minigame setup/rules

- direct menu begins around `0x28818`
- minigame UI/rules continue through approximately `0x28C40`
- files: `main_menu_vi.csv`, `minigame_ui_batch01_vi.csv`

### Karaoke

- lyric-like bank: approximately `0x2B380 .. 0x2B76E`
- start options around `0x2B7C9` / `0x2B7EF`
- files: `karaoke_batch01_vi.csv`, `seed_known_strings.csv`
- meaning translation is done; singability/timing pass is still separate

### Maruko Fortune / まるこみくじ

- approximately `0x2BD28 .. 0x2CB92`
- headings, wish/money/romance/study fortunes, advice, lucky numbers/colors translated
- files: `fortune_batch01_part1_vi.csv` through `fortune_batch01_part3_vi.csv`

### Stage names

- approximately `0x2CBAD .. 0x2CD5F`
- 15 stage/title strings translated
- file: `stage_names_batch01_vi.csv`

### Quiz UI and Maruko Q

- misc/result UI around `0x3153A` and `0x31C52 .. 0x31D3A`
- coherent quiz banks approximately `0x31D47 .. 0x368D8`
- files: `quiz_ui_misc_vi.csv`, Maruko Q Batch 01–03

Raw-ROM recovery is mandatory for suspicious numeric/full-width fields because the conservative scanner sometimes begins inside a multibyte character.

## Current direct-text conclusion

Within the currently proven retail-facing direct-text islands, the large coherent story / menu / minigame / karaoke / fortune / stage / quiz banks have meaning-first Vietnamese coverage.

The remaining scanner clusters elsewhere in the 2 MiB ROM are dominated by binary-looking false positives or short unproven fragments. They must not be counted as untranslated dialogue merely because they decode under CP932.

This is **not** a whole-game completion claim. Important visible text may still live in:

- graphics / tilemaps;
- compressed graphics;
- alternate text renderers;
- dynamic counters / symbols;
- screen-specific assets.

## Next high-value translation/reverse targets

1. graphics/tilemap text hinted by the internal QA block: Start, Password, Continue, Story quit, final-win, ending screens;
2. the pink main-menu heading `どれにする？`, which is visible but not found in the proven direct text path;
3. font/codepage work required for real Vietnamese runtime insertion;
4. a later singability pass for karaoke after layout/font behavior is understood.

Keep source meaning, runtime-fit text, font/codepage, and graphics/tilemap work as separate layers.
