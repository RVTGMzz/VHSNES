# Checkpoint 040 — Fortune actual Vietnamese direct fields

Date: 2026-10-11. Branch: `chibi-maruko-bootstrap-01`. User instruction: **finish content first, font later**.

This checkpoint completed **33 actual in-ROM Fortune text replacements** on top of graphics/UI 039: 4 fortune headings, 14 short predictions, 15 lucky-color names. Every candidate is in `translation/runtime/fortune_exact_fit_040.csv`, with original Japanese, **unchanged complete** canonical Vietnamese meaning in `translation/source/fortune_batch01_part1/part2/part3_vi.csv` and an approved compact runtime variant. All 33 match the canonical source row identity, including exact CP932 bytes and original `816F` line delimiter, and preserve the original two-byte glyph width.

Examples: `ねがい事 → Ước`, `恋愛運 → Yêu`, `ちょきんが よしじゃ → Để dành`, `じぶんをしんじて！ → Tự tin đi`, color `あかいろ → Đỏ` and `むらさきいろ → Tím`. Natural full `vi_full` stays unmodified; do not force longer Story/Quiz text into the same fixed field without expansion.

**Exact ROM/patch contract:**

| Object | SHA256 / details |
|---|---|
| Exact 2MiB clean Japanese ROM | `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956` |
| 039 clean-ROM IPS | `97c0e41b354b0dda3ea7c0c292b5aef236586e279870962fd0d4f3398285008c` |
| 039 base ROM after patch | `a1f4459942e3a757cc314d12c959168046b4a6dd66018d55b014c70d052e98ce` |
| 040 experimental patched ROM | `d892c51576c103f5881f1481c65fd2746635d222b1d387f9666cd7f44b1da3ac` |
| 040 clean-ROM IPS | `2bfdcc64973bc31ce268fa7e68a6118808c633b10d1437b7f811ac290616e580` |
| 040 IPS size / records | **21,727 bytes / 707 records** |
| Checksum / complement | `41A7 / BE58` |
| Extra translated fields | **33**, on top of 38 from 039 |
| Changed bytes vs 039 | **436** |
| Static source/delimiter/IPS replay | **PASS** |
| SNES emulator gameplay | **NOT TESTED** |

Reproducible GitHub source: `tools/build_content_first_040_fortune.py` reads the exact clean Japanese ROM, 039 IPS, runtime CSV and canonical Fortune sources; it fails on source or hash drift. Example from game directory:

```bash
python tools/build_content_first_040_fortune.py clean.sfc checkpoint039.ips --ips checkpoint040.ips --report checkpoint040.json --allow-untested
```

The local package `Chibi_040_Fortune_33_Content_First_UNTESTED.zip` contains only IPS, README and QA JSON; **no commercial ROM or font files are committed**.

**Scope caveat:** This experiment contains a total of **71 direct UI/Fortune fields**, G0 startup title/credit and G1 labels, NOT the full narrative/Quiz/Fortune meaning coverage. Source translations and 216 editorial revisions exist but are not automatically active. Existing V2 font untouched; earlier typography test failed, so no runtime acceptance. Next: add safe Quiz/Story runtime fields and develop fixed-field expansion/relocation for natural full-length dialogue.
