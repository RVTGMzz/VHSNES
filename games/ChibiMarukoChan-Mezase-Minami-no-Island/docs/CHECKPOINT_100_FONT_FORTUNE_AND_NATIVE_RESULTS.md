# Checkpoint 100 — readable font, Fortune and native result screens

Current cumulative test IPS: 104,938 bytes, SHA256
`33158e9a0c1927f5dc283c3bd530d4e80c7b5388ad81a12a8304aec99dbded0b`.
Patched ROM SHA256:
`eeb16eb623568b8c28294af602726a2e9c2e2bc8a80f85a525245c908f2b5de6`.
Use `tools/build_cumulative_100.py` with the original user-owned ROM, original
043 archive, local Tahoma Bold and Tahoma font paths. It rebuilds 087–100 in
memory and produces one original-ROM-relative IPS and JSON; no ROM or font
file belongs in the repository. Rebuild matches the independently staged IPS.

090 installs readable Vietnamese glyphs and fixes native main-menu/Story option
art. Common C706F graphics have thirteen owners: restore the original stream
and redirect only the main-menu owner to a private copy. Never blank shared
result sprites globally. Font uses dedicated pages and an explicit hook shape
for ủ/ử to distinguish them from acute tones. 091–095 complete Fortune text
geometry, overflow captions, five ranks, controls, paper label and compact
Story spacing. All three renderer position consumers and wrapping agree.
Five earlier 087 editorial caption repairs are integrated into the binary.

096 translates the native play-again choice, retaining actor and cursor art.
097 translates the native result heading using BG3 and an isolated OBJ copy.
098 translates the animated Game Over title to “Hết lượt!”. 099 replaces BOTH
rabbit and cat team labels with “Đội”: native tile ranges 5D–68 and 7B–86 are
distinct. 100 translates the carved Fortune box in all four draw poses,
cloning modified sprite instances without changing original paper/control
tiles. All builders validate exact parents, allocation bounds, decoded asset
round trips, permitted writes, checksums and cumulative IPS replay.

Runtime evidence uses Snes9x/libretro (user plays Snes9x). Fresh Fortune entry,
shake/pull/result flow and native Story continue/quit branches were exercised.
Native VS was entered through the real main menu, player/rule/character/team
selection and actual minigame completion. The final result has all four
portraits, both Vietnamese team labels and no stray skin fragments. The pink
pixels in the rabbit face are original cheek artwork, not leftover lettering.

Earlier Story-to-VS diagnostic screenshots were INVALID visual acceptance:
changing only WRAM 2010 left Story portrait data in a VS map, producing stray
skin fragments. They also hid the separate cat label tiles. Do not reuse this
method for visual acceptance. Native result phase 7 in the headless harness
may require a savestate reload plus a frame to flush presentation; native
input advances correctly. This is not proof of a complete natural playthrough.

Source syntax, diff whitespace and 20 existing source checks passed. Hook
selftests passed 972 Quiz, 3,888 Fortune and 1,794 Story/fallback cases. A
50-slot/150-choice targeted Quiz sweep passed on the first 100 candidate
`ca1294f2...`; the final candidate differs only in two native scoreboard label
tile sets and checksum. Do not relabel that sweep as an exact-final-ROM run.
Final VS runtime and deterministic rebuild use the full final hash above.

Whole-game completion remains FALSE. Remaining visible Japanese includes
minigame-selection/intro and VS setup headings, victory/ending artwork and
other unreviewed modes. Remaining Quiz source aliases need semantic review;
the historic scanner staging remains 279/381. Complete these graphics and
natural gameplay QA next; do not restart title/font polishing or claim that
the entire translation is finished.
