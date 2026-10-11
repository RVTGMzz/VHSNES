TIẾP CHIBI MARUKO-CHAN SNES VIỆT HÓA — CHECKPOINT 045 (2026-10-11)
Repo: RVTGMzz/VHSNES / branch: chibi-maruko-bootstrap-01.

MỆNH LỆNH USER: Việt hóa con SNES đã quá lâu, BỎ kiểu mỗi lượt 10–30 câu/checkpoint vụn; làm NHIỀU nội dung thật, không lạm dụng báo cáo; TUYỆT ĐỐI không gửi các IPS/ZIP thử nghiệm liên tục, không nhờ user test bản lẻ. Ưu tiên nội dung game đầy đủ trước, FONT SỬA SAU.

ĐỌC ĐẦU:
1. games/ChibiMarukoChan-Mezase-Minami-no-Island/HANDOFF_CURRENT.md (045 ở đầu).
2. docs/CONTENT_FIRST_STORY_BATCH02_03_CHECKPOINT_045.md (latest).
3. translation/runtime/story_batch02_03_content_first_045.json (139 bản text render, source chính vi_full preserved).
4. tools/build_content_first_045_story_139.py (exact SHA, script/segment safety).
5. docs/CONTENT_FIRST_LARGE_STORY_CHECKPOINT_044.md / tools/build_content_first_044_story_87.py.

KẾT QUẢ THẬT 045:
- Đã thực sự chèn thêm 139 hội thoại/lời dẫn Story vào ROM thí nghiệm: 58 Batch02 và 81 Batch03, gồm cả cuối thi đấu và cảnh đến đảo Nam. Đợt này có 368 physical glyph segments, 367 marker 816F/81A5 trong những records ấy giữ nguyên, mọi marker toàn Story bank 0x18000..0x1DFFF cùng vị trí; script stop opcodes không đổi, 7918 writable bytes, 7915 byte positions khác so 044 đều trong whitelist + checksum. Không thay font/graphics.
- Tổng Story static: Batch01 120/126, Batch02 112/126, Batch03 81/84 => 313/336 (23 chưa xử lý), không được nói 100%. 402 tracked actual in-ROM direct source fields (38 UI +33 Fortune +21 Quiz +310 tracked Story) +3 old prelocalized tutorial Story =405 in-ROM Vietnamese direct slots, cộng riêng đồ họa title/G0/G1. Nhiều Quiz/Fortune, kết quả G3, luật G2 chưa hoàn tất.
- Đã từng kiểm tra sơ bộ 140 rows, nhưng 1A916 mở đầu raw bytes 88F3 có thể là internal metadata; LOẠI, final đúng 139. Tương tự prefix 92F3/FAF3 không nên overwrite khi chưa trace engine. Superseded script _140.py đã delete khỏi repo.
- ROM Nhật gốc 2MiB SHA e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956, local /mnt/data/Chibi Maruko-chan - Mezase! Minami no Island!! (Japan)(1).sfc.
- ROM044 base SHA 2312b9ba52c0cf6ac491e71117d5c537ad7dc61828dc9e87d838826e5165f322. Final ROM045 SHA 7ddf449c2266838c3d55415f14aeee34fc21334c1ed0a490590647eb75e047b5. Final exact-clean-japanese-ROM IPS045 SHA 685d7e9f0146950ca030fd8469f57313a0b368be98e0a9c95999bda48cb65379, 43679 bytes/1568 records, independent original ROM replay exact, SNES checksum E4C1 complement1B3E.
- Local work files: /mnt/data/chibi043.ips extracted from previous attached 043 zip, /mnt/data/chibi044_local.sfc and chibi044_local.ips (rebuilt exact SHA from clean + 043 IPS and JSON044), /mnt/data/chibi045_local.sfc, /mnt/data/chibi045_local.ips, /mnt/data/chibi045_qa_report.json, /mnt/data/chibi045_story_candidates.txt, /mnt/data/build_chibi045.py. Files are local only, NOT uploaded as commercial ROM to GitHub; don't send IPS links to user.
- GitHub has translation/runtime/story_batch02_03_content_first_045.json (139 full canonical reference + candidate per source offset), tools/build_content_first_045_story_139.py (exact SHA and fail-closed checks). This builder accepts exact clean Japanese + exact 044 clean-ROM IPS OR --rebuild-044-from-043 for reconstructing 044 from source/043 IPS to avoid losing intermediate binaries. Document docs/CONTENT_FIRST_STORY_BATCH02_03_CHECKPOINT_045.md.
- Do not claim GitHub CI RUN or emulator PASS; neither has happened for checkpoint045. Original user previously complained about ugly font, but font repairs remain postponed until all possible content is in ROM; check in final combined emulator session. Full vi_full preserved in translation/source, current compact runtime may lose nuance and needs visual/editorial review.

CHƯA HOÀN THÀNH:
- 6 remaining Batch01, 14 Batch02, 3 Batch03 special Story rows, most have Q/R/P dynamic numerical glyph prefixes or scanner metadata 88F3/FAF3/92F3; avoid blind patch.
- Quiz, Fortune, G2 actual rules, G3 result screen graphic, other in-game user-facing labels/credits still need complete content sweep (exact source proof first).
- Need one consolidated full build, emulator smoke testing for title, first boot credit 'Việt hóa bởi Votri Valley', G1, Story and end, Quiz/Fortune, result and V2 font eventually. NEVER claim static checksum proves in-game runtime correctness.

NEXT: Attack 23 Story special rows as a group only if text renderer execution path can be proven (safe control/variable preservation), then large Quiz/Fortune/G2/G3 source/graphics integration, not documentation-only or font microtests. Update GitHub after actual source/ROM changes. User only needs to say 'tiếp'.
