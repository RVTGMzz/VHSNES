TIẾP CHIBI MARUKO-CHAN SNES — CHECKPOINT 048 (2026-10-11)
GitHub: RVTGMzz/VHSNES, branch chibi-maruko-bootstrap-01

YÊU CẦU USER: ĐÃ LÂU QUÁ, ĐỪNG LÀM CHECKPOINT VỤN. CỨ LÀM NHIỀU NỘI DUNG THẬT VÀ GHI GITHUB. USER KHÔNG MUỐN LINK TẢI IPS THỬ NGHIỆM LẺ. FONT ĐỂ SAU. NHỚ GIỌNG THOẠI TỰ NHIÊN, KHÔNG ÉP CÂU DÀI THÀNH 1 TỪ.

ĐỌC NGAY:
1. games/ChibiMarukoChan-Mezase-Minami-no-Island/HANDOFF_CURRENT.md, mục 048 đầu tiên.
2. docs/CONTENT_FIRST_FORTUNE_103_CHECKPOINT_048.md.
3. translation/runtime/fortune_content_first_103_048.json (103 nguồn exact offset + full vi_full + compact, actual JP bytes capacity).
4. tools/build_content_first_048_fortune_103.py.
5. docs/CONTENT_FIRST_STORY_ALIGN_AND_QUIZ_FORTUNE_CHECKPOINT_047.md.

CÁI ĐÃ HOÀN THÀNH THẬT 048:
- Quét 3 Fortune canonical source 157 dòng; trước 040+047 đã chèn 48 dòng. Đợt 048 biên tập **103 Fortune runtime compact mới** đúng ngữ cảnh, đã đối chiếu trực tiếp all 103 với raw ROM Nhật 2MiB và cp932 byte capacity (chú ý 2 ASCII 20 trong JP chỉ là 2 byte, KHÔNG chiếm 2 fullwidth glyph units). 103/103 không quá độ dài và các glyph V2 0x84 đều hợp lệ, 103/103 original 816F intact. Full vi_full KHÔNG đổi.
- Xác nhận ZERO overlaps với 33 040 và 15 047 original Fortune file_offset. GitHub manifest 103 + builder fail-closed đã push.
- Actual cleaned ROM SHA e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956. Original local /mnt/data/Chibi Maruko-chan - Mezase! Minami no Island!! (Japan)(1).sfc (mount hiện tại đã có, nhưng lượt sau PHẢI kiểm tra). Đã extract old 043 IPS từ /mnt/data/Chibi_043_G0G1_176Fields_Story58_Content_First_UNTESTED.zip -> rebuild 043 ROM sha 45ffca7db5db83bc2734e885ee90c77f33746e2c4a54d1c99f1502f3e992a6ae.
- **THỬ ROM BYTES THẬT**: chèn 103 nguồn Fortune vào 043, 2002 original glyph bytes approved, 1997 changed bytes, no 816F modified, no V2 glyph/graphics/script touched. Build riêng TEXT-ONLY overlay IPS no checksum 2545B/108 records SHA 3eb7dcc55d0c0b585beb4b27d6d2ca08c5facd39196042756eae0cf0dc68379c. Preview (UNFIXED checksum) ROM 043 + text SHA 4f461333d171fc21c3541ae29393056f0c9234ea0f5c4de46f97589afd20378b; independent reapply IPS passed. LOCAL files: /mnt/data/chibi_048_fortune_candidates.txt, /mnt/data/chibi_048_build_local.py, /mnt/data/chibi048_source_entries.json, /mnt/data/chibi048_fortune_103_overlay_no_checksum.ips, /mnt/data/chibi048_local_qa.json.
- **LƯU Ý QUAN TRỌNG CHƯA GỘP FULL 047+048**: ROM047 published exact SHA 1f6430064b70671a4f3ba94f0fd256764db54690950519c22d9e03ec74230dd9 KHÔNG CÓ FILE NHỊ PHÂN TRONG CONTAINER. GitHub có toàn bộ manifests/tools 044 045 046 047 nhưng ROM047 không được commit. DO NOT CLAIM that a full 048 ROM has 151 Fortune installed. Local preview 043+103 has deliberately unchanged checksum, NOT playable! Bản code GitHub tools/build_content_first_048_fortune_103.py requires exact full 047 base SHA and either merges/rechecks/recalculates SNES checksum/creates clean-based IPS OR --static-check-043 for preview QA. It fails if any old 047 edit overlaps; no bypass. Github builder itself chưa GitHub CI-tested, but local equivalent physically patched 043.
- Potential Fortune after verified merge 48+103=151/157; 6 rows còn thiếu cần field expansion hoặc biên tập tử tế: offsets 2BD5E 天の声,2C413 体育...,2C601 プリン...,2C86B また来週,2CA7D きいろ,2CADD しろいろ. Không ép ra từ vô nghĩa.
- Toàn dự án previous 047 có 328 distinct Story physical records mapped từ 336 source CSV rows (8 false scanner offsets middle of CP932 two-byte number, 3 original tutorial), 38 UI,36 Quiz,48 Fortune and G0/G1 actual graphics; GAME PLAY CHƯA EMULATOR-TEST, font V2 user từng phàn nàn xấu.
- GitHub 048 file paths: translation/runtime/fortune_content_first_103_048.json; tools/build_content_first_048_fortune_103.py; docs/CONTENT_FIRST_FORTUNE_103_CHECKPOINT_048.md, HANDOFF_CURRENT.md, translation/TRANSLATION_PROGRESS.md. No downloadable patch links given to user.

LÀM TIẾP THẬT:
1. ƯU TIÊN KHÔI PHỤC CHÍNH XÁC ROM 047 từ ROM clean + available local old 043 IPS + GH manifests/tools 044,045,046,047, không dùng shortcut BỎ qua các sửa cũ; phải SHA verify 044 2312b9..., 045 7ddf449c..., 046 c10c0f..., 047 1f643006... trước khi merge.
2. RỒI chạy GH builder 048 cho exact 047 ROM, recompute checksum, static SHA report, clean-ROM IPS. Không bắt user tải/test micro patch.
3. Gom Quiz (source 381 rows), 6 Fortune còn khó, luật G2 1E307/1E325/1E339, G3 kết quả xác định từ asset thật (KHÔNG vá internal QA debug descriptor 0x2865E..287FF) vào cùng ROM; context-aware text wrapping/field expansion.
4. Sau khi nội dung đủ lớn, emulator test thật (title/credit, G1, Story, Quiz, Fortune, G2, results, font). FONT ENGINEERING SAU CONTENT theo user. Không claim game hoàn thành chỉ vì IPS checksum PASS.

GIỮ CHÍNH XÁC DÒNG: Việt hóa bởi Votri Valley.
