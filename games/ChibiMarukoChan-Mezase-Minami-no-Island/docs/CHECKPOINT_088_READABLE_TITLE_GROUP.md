# Checkpoint 088 — the entire title group is readable

2026-10-14. User explicitly requested improving all three title lines after
seeing the actual 087 emulator screenshot.

The old red text had no contrasting border, and the thin credit crossed the
school fence. The new composition uses centered 20px bold red game title with
black border, 15px bold white subtitle with black border, and the exact
**“Việt hóa bởi Votri Valley”** in bold black on a small white bordered panel.
Original character art, sky/school scene and copyright lines remain.

Actual G0 palette calibration in Snes9x established index 3 black, index 5
white and index 13 red. Text uses binary masks pasted into the indexed plane;
antialiasing must not blend numerical palette indices into arbitrary colors.
The result uses 176 unique title tiles, within the 185 unshared native tiles.

`build_title_readable_088.py` repacks native resources using the exact codec,
verifies decode round trips and shared non-title tiles, merges only whitelisted
G0 asset spans into the exact integrated 087 image, preserves Quiz bank06
byte-for-byte, and replays one cumulative original-ROM-relative IPS. The new
3881-byte packed stream sits at `0x5A45A`; its old 087 allocation is restored
to original FF padding. No font file or copyrighted ROM is distributed.

| Property | Value |
|---|---|
| IPS bytes / records | 68,458 / 2,545 |
| IPS SHA256 | `a4c9b5cec15358a11b131c27e812532d2d488074d0de6ac067e5a5d16c95945d` |
| Result ROM SHA256 | `a8a6c028b2cff5d1daf3410768fae0c1309dddfb694142fcf682ca763fd4081f` |
| Checksum / complement | `DBC6` / `2439` |
| Bold Tahoma font SHA256 | `68f92341975acc275c7d4a2ec52a1569b70e992b521c42b30f29149806421674` |

Rebuild in one command: run the 088 tool with the exact original ROM, original
039–043 ZIP, locally supplied bold/regular fonts, `--ips` and `--report`.
It reconstructs 087 in memory and writes only the final 088 IPS/report. An
exact 087 IPS may alternatively be supplied as the second positional input.
The supplied local fonts were Windows `tahomabd.ttf` and `tahoma.ttf`.

The 088 title was rendered and visually inspected in Snes9x. Fresh-boot Quiz
smoke QA checks that the title resource repair does not disrupt entry/answers.
The prior 087 50-slot/150-selection sweep is retained as evidence for the
unchanged Quiz code/content; it is not relabeled as a full 088 game run.

Whole-game localization is still incomplete. Keep the 087 recorded blockers:
G1/Story graphics, Fortune overflows/artwork, Japanese Quiz counter, G3
results/ending, source-alias semantic review and natural whole-game QA.
Upstream's concurrent 087 source-wording manifest/audit commits are preserved.
