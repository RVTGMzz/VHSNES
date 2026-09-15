# Workflow guardrails

This project borrows process discipline from `ronvotri/Viet-Hoa-PS1` (especially Gaia Master) and build/release ideas from `Optiroc/SuperFamicomWars-Translation`, but does not copy PS1 technical assumptions into SNES work.

## What we intentionally inherit

1. **Exact clean-source contract** before any patch.
2. **Source identity guard** before each write.
3. **Dry-run first**, real build second.
4. **Reject duplicate/overlapping writes** instead of silently resolving them.
5. **Source-of-truth translation is separate from runtime candidate text.** Do not destroy full Vietnamese merely because the current renderer has a smaller byte budget.
6. **Regression gates** are historical contracts, not proof of whole-game coverage.
7. **Generated build data is separate from authored source data.**
8. **Release a patch, not a commercial ROM.** BPS is the preferred eventual release format unless testing proves another format is materially better.
9. **Runtime claims require runtime evidence.** Static byte-fit/build success is not Runtime PASS.
10. Prefer **one high-information visible probe** over many speculative patches.

## What is explicitly NOT inherited from Gaia Master / PS1

Do not assume any of these until proven here:

- PS1 MODE2/2352 sector layout
- EDC/ECC regeneration
- BDP archives or any Gaia Master archive format
- MIPS executable hooks/code caves
- BIOS Krom font APIs
- Gaia Master 12x12/4bpp font layout
- Gaia Master token/control syntax
- PS1 pointer/endian assumptions

## SNES-specific assumptions currently proven

Only the following are frozen at bootstrap 001:

- exact 2 MiB canonical ROM
- no copier header on canonical input
- LoROM / FastROM internal header
- valid checksum/complement pair
- direct CP932/Shift-JIS text exists in ROM

Everything else, including text terminators, command bytes, pointers, font format, DMA path, tile depth and renderer ASCII behavior, remains subject to proof.

## Inspiration from Super Famicom Wars translation

Useful architectural ideas to retain:

- keep game-specific tools/source in the repository;
- generate derived assembly/data from authored sources;
- make builds deterministic and checkable;
- keep graphics/font tooling explicit;
- package delta patches rather than ROMs.

Not inherited by default:

- WLA-65816 requirement;
- custom VWF implementation;
- its compression formats;
- its code/layout addresses;
- its string decoder architecture.

Those are solutions to a different SNES game and become relevant here only if evidence points that way.
