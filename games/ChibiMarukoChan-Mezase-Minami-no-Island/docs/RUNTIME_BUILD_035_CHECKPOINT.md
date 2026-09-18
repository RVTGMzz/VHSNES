# Runtime Build 035 Checkpoint

Updated: 2026-09-18 +07

This document supersedes Build 027 as the **latest large direct-text candidate checkpoint**. It does not declare whole-game Runtime PASS.

## Current candidate

Artifact used locally for testing:

`Chibi_Maruko_Build_035_QUIZ01_CREDITS_PASS_READY.sfc`

Do **not** commit the ROM to GitHub.

Static identity:

- base: Build 034
- Quiz/direct entries newly patched in Build 035: **65**
- Credits role-token patches newly patched in Build 035: **22**
- changed bytes vs Build 034: **3129**
- checksum: `0x6547`
- complement: `0x9AB8`
- SHA-1: `054380f9b452f245471e6309eb33c7486d581462`
- SHA-256: `f8fb662a9e1b8fc5a5ff689f690ceaf332055ed86983e52b476a78852e4fd58d`
- runtime status: **UNTESTED**

## What the current chain already carries

Build 035 inherits the prior large runtime chain, including:

- compact Vietnamese main menu;
- 328 discovered direct Story fields through the known ending sequence;
- Minigame UI / setup / rules direct text;
- Fortune direct-text insertion;
- large Maruko Q / Quiz direct-text insertion;
- karaoke direct-text runtime candidates where prepared;
- stage labels;
- quiz misc/result UI;
- direct credits-role labels;
- targeted story wording hotfixes;
- current Vietnamese `0x84xx` codepage and custom 12x12 font layer.

Full canonical meaning remains in `translation/source/`. Runtime compact strings are not allowed to overwrite `vi_full`.

## Font status

The Golden Sun GBA donor experiment was rejected for Chibi. Do not reuse it unless the user explicitly reopens that experiment.

The accepted architectural baseline remains the pre-GBA Chibi Vietnamese font/codepage path derived from Probe 010 / Probe 019.

### Runtime evidence from user screenshots before Build 034

After Build 033 the user reported:

- `T` had become too thick;
- `V` still looked too thin;
- uppercase `A`, `K`, `L` looked too thin;
- lowercase `e` was thin and floated above the baseline;
- lowercase `g` was unclear / clipped;
- circumflex `^` looked reversed or breve-like;
- below-dot marks were effectively lost in runtime, making forms such as `bạn` / `chọn` look unaccented.

### Build 034 static font/text repairs

Build 034 attempted targeted corrections:

- medium-weight `T`;
- thicker `V`;
- thicker `A/K/L`;
- lower, thicker `e` family;
- redrawn `g` with visible descender above the clipped bottom row;
- corrected circumflex orientation;
- dot-below family moved upward so marks survive runtime clipping;
- story wording at `0x184A9` changed to:
  - **Học sinh hai nước trao đổi học tập nhau.**
- additional direct UI labels such as rules/music/quiz/credits labels.

Build 034 was not subsequently user-confirmed as a font Runtime PASS before work moved on.

Therefore Build 035 inherits these static fixes, but **font release status remains unconfirmed**.

## Build 035 direct-text additions

The 65 Quiz/direct entries cover the remaining discovered direct Quiz Batch01 region around `0x34009..0x34F3E`, including Noguchi, Hanawa, Hamaji, Hide-jii, Butaro, Fujiki and Pusadi question/answer/explanation text.

The 22 Credits token patches cover role labels such as producer/director/scenario/art/program/audio/visual/PR/cooperation/supervision in compact Vietnamese forms.

## Remaining direct-text audit

A whole-ROM audit after Build 035 found only 13 unchanged kana-rich candidates. They are not established normal player-facing text:

- internal debug/review screen descriptors at approximately `0x2865E..0x287FC`;
- likely effect/debug-like data;
- likely binary false positives.

The still-visible Japanese in screenshots is therefore now a **graphics/tilemap/asset track**, not a reason to resume broad direct-text scanning.

See `docs/GRAPHICS_TILEMAP_PASS_001_AUDIT.md`.

## Runtime claims

Do not call Build 035 Runtime PASS.

The user has provided runtime evidence for many earlier subsystems and screenshots, but Build 035 itself has not had a complete confirmation pass.

The user prefers **fewer, larger tests**. Avoid producing many tiny sequential builds unless a narrow diagnostic probe is technically necessary.

## Next work

Primary next track:

1. reverse the actual graphics/tilemap/asset path for the remaining visible Japanese;
2. first graphics batch:
   - `どれにする？` -> **Chọn gì đây?**
   - `はじめから` -> **Bắt đầu**
   - `パスワード` -> **Mật khẩu**
3. then VS/rules graphics;
4. then win/lose/continue/ending/title cards.

Keep direct-text, font/codepage, and graphics/tilemap layers independently auditable.
