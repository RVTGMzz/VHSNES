# Checkpoint118 — release candidate, remaining Japanese and actual playback recheck

Date:2026-10-16. One-command source builder:`tools/build_cumulative_118.py`.
The public117 remains the separate, source-only singable-draft editorial proposal. Its two files are preserved. No pending draft CSV edits were merged. The unpublished local runtime iteration was renamed118; rename-only verification retained exactly the same ROM/IPS hashes.

IPS SHA256:`9075914cbbffb76fb7a8488a3c8530def2b37e9aa51509c947aa838f65c34b3f`.
Patched4MiB ROM SHA256:`22d02aa0ab67966e7f88c24097b434d86c79972a5ea3254ca92a5e7f9cd59f09`.
Original unheadered2MiB Japanese ROM and historical043 ZIP are unchanged inputs. Supply local Tahoma Bold/regular paths. IPS uses standard literal/RLE expansion and header size0C; the cartridge remains ordinary Fast LoROM. No FF-run allocation inside original native data.

## User-visible changes from116

- Mitsuya shop sign is Latin, tiny wine sign uses a bottle icon; native ice and octopus stall signs read Vietnamese. Edited only seven/four/twelve approved tiles, cloned streams and redirected only their exact native owners.
- Full29 staff names romanized across19 credits pages. Credits are two native footer rows23/25 at the existing compact8px pitch. Sakura Production is written in full on the copyright; its credits company label uses Sakura Prod. to retain both supervisors' full names. Readings were checked against the game-specific MobyGames staff list, cited in `credits_latin_118.json`.
- Kazuo choices now read Nhất Hùng/Hoà Hùng with Kazuo retained, preserving original table order, grading and all gameplay code. The original correct 一雄 corresponds to Nhất Hùng. The repeated short question continuation was removed. Original multi-job explanation boundaries stay intact.
- Copyright retains Konami, Sakura Production, Nippon Animation and1995, with Latin text and Vietnamese rights wording, in isolated BG3 resources.
- Runtime recheck found additional Japanese Karaoke ruby rows and stale letters from short/long VI page changes. Ruby timing copies now upload transparent tile0. A guarded hook clears the full19..26 bitmap band with one contiguous4096-byte DMA before the original native lyric job. Music, animation, timing tables and the bouncing rabbit remain unchanged. All13 actual pages were rechecked after60 settling frames; no Japanese annotation ink remains and all8 bitmap rows match WRAM.

## Credits implementation constraints

New data uses explicitly added C0 ROM space. The native renderer cannot directly use C0 as DBR because it expects low WRAM mirrors. The wrapper stages each complete credit (maximum144-byte contract) in existing inactive-Quiz scratch7E:8000..808F. The original native wait loop completes before restoring bank83; its original caller's wait remains harmless. Original four trailing table aliases still point to original rule data and retain a bank83 fallback.

Native credits already clear rows23..26. Additional clear calls on the draw frame overfilled the finite DMA queue, leaving the second line and palette absent. Those experimental clears were removed. Final validation checks both font bitmap and tilemap DMA against WRAM for every page, catching the observed truncation rather than trusting the text-job flag alone. Do not reintroduce per-row clear calls here.

## Verification and remaining scope

- Independent original/archive rebuild equals incremental IPS byte-for-byte.
-50 Quiz slots and150 native selections; native-input15-stage selection and match entry; one full timed match for each of the3 minigame families reaches results.
-Actual PPU stage caption ink, including ordinal and scroll, remains inside the paper on all15 stages.
-507 active Quiz/Fortune fields have no native Japanese glyphs, including the former Kazuo exceptions.267 manifested Story records /7,003 VI glyphs pass; seven protected046 script prefixes remain byte-identical and are not treated as printed text.
-All19 native credits pages and the ending fixture complete; all13 Karaoke pages, Paint quit/menu return and native Fortune input/result were rechecked. The angled fortune tube already reads Bói vui in all four100 poses; an initial visual suspicion was disproved by enlarged images and source review.
-162 type0 candidates:374 decoded sources unchanged, only8 newly approved resource pointers changed; original68066 and17736 are intact. Source checks, ROM-free IPS expansion/LoROM boundary tests and syntax checks pass.

No known visible Japanese remains in the reviewed screenshots and active text scope. This is not an exhaustive pixel/OCR proof of every unvisited scene. A natural full winning Story playthrough, real SNES mouse motion/hardware and Karaoke singable syllable timing remain uncertified. Do not advertise100% full-game QA or call the ending fixture a natural playthrough.

Delivery:`outputs/ChibiMaruko_118_Release.zip` (one cumulative IPS, screenshots, reports and Vietnamese release notes). A separately created local `ChibiMaruko_VietHoa_118.sfc` is for the user's direct play request and is excluded from both Git and the public release ZIP. Never publish ROM, font, emulator or savestate binaries in the source branch.
