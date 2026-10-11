TIẾP VIỆT HÓA CHIBI MARUKO-CHAN SNES — CHECKPOINT 044 (2026-10-11)
GitHub RVTGMzz/VHSNES, branch chibi-maruko-bootstrap-01.

USER RẤT KHÓ CHỊU VÌ 1 THÁNG CHƯA XONG, KHÔNG MUỐN ĐỢT 10–30 CÂU MICROTEST VÀ KHÔNG MUỐN LINK TẢI IPS/ZIP TRUNG GIAN. LỆNH: TỰ LÀM NHÓM LỚN, DỊCH CÓ NGỮ CẢNH, ƯU TIÊN TOÀN BỘ STORY/QUIZ/FORTUNE/G2/G3/ĐỒ HỌA TRƯỚC; FONT SAU; TỰ ĐẨY GITHUB. ĐỪNG BẮT USER TEST TỪNG BUILD, CHỈ ĐƯA FILE KHI ĐÁNG CHƠI THỬ.

PHẢI ĐỌC ĐẦU:
1. games/ChibiMarukoChan-Mezase-Minami-no-Island/HANDOFF_CURRENT.md, mục 044 trên cùng.
2. docs/CONTENT_FIRST_LARGE_STORY_CHECKPOINT_044.md.
3. translation/runtime/story_batch01_02_content_first_044.json (87 dòng VI runtime, full canonical vi_full reference).
4. tools/build_content_first_044_story_87.py (build sạch+IPS043 theo SHA bảo vệ).
5. translation/TRANSLATION_PROGRESS.md, docs/CONTENT_FIRST_STORY_CHECKPOINT_043.md.

THÀNH TÍCH THỰC SỰ 044:
- Đã chèn THẬT 87 trường thoại/lời dẫn Story (Batch01 33, Batch02 54) vào ROM thử 044 từ 043. Có 214 physical segments 2-byte glyph, 214 dấu 816F/81A5 nguyên vị trí và toàn bộ vị trí dấu ngắt trong bank Story nguyên. Full vi_full không bị ghi đè trong CSV; mỗi runtime compact của 87 dòng có source Nhật, offset và tham chiếu câu đầy đủ.
- Exact ROM Nhật sạch /mnt/data/Chibi Maruko-chan - Mezase! Minami no Island!! (Japan)(1).sfc, SHA e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956.
- Baseline ROM 043 SHA 45ffca7db5db83bc2734e885ee90c77f33746e2c4a54d1c99f1502f3e992a6ae. IPS043 /mnt/data/Chibi_043_Story58_Content_First_UNTESTED.ips SHA d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50.
- New ROM044 /mnt/data/Chibi_044_ROM_ONLY_LOCAL_UNTESTED.sfc SHA 7f0c7ef92f2c40e0cab7703326c93cf6338d9ae771fef4b43a2350bda0c643fc. CLEAN-ROM IPS044 /mnt/data/Chibi_044_Story87_Content_First_UNTESTED.ips SHA 5b4da16b00f7c38dd1de7f4bd2431479b9b75bd2441f4d122d42d8549e9d9784, 33,901 bytes / 1195 records. Diff vs ROM043 4680 byte vùng source và checksum, checksum/complement 2D86/D279. Independent IPS reapply onto CLEAN produces EXACT new ROM SHA.
- THỐNG KÊ CẦN SỬA TỪ CÁC CHECKPOINT CŨ: Story Batch01 THẬT SỰ 126 ROW, KHÔNG PHẢI 123. 042/043 track 84 rows, 044 thêm 33 =117 tracked. Ngoài ra BA tutorial offset 181CC/18245/182BE đã được dịch sẵn trong ROM043 từ lớp cũ (so byte confirmed), không ghi đè. Vậy 120/126 Batch01 thực sự có byte tiếng Việt, còn 6 là 18408,18708,1873E,189EE,1A1B0,1A334 cần manual control/script nghiên cứu. Batch02 đã 54/126, còn 72; Batch03 0/84 trong bản tích hợp mới.
- Tổng 263 tracked direct-text ROM fields =176 cũ từ checkpoint043 (38UI+33Fortune+21Quiz+84Story) +87. Ba tutorial cũ kể riêng, không double count, G0/G1 title+credit Votri Valley và UI graphics có riêng.
- KHÔNG CÓ SNES EMULATOR RUNTIME PASS, FONT V2 VẪN XẤU NHƯ USER TỪNG BÁO, FONT ĐỂ SAU. Đừng claim xong game.
- Github đã có files: translation/runtime/story_batch01_02_content_first_044.json, tools/build_content_first_044_story_87.py, docs/CONTENT_FIRST_LARGE_STORY_CHECKPOINT_044.md, HANDOFF_CURRENT.md, TRANSLATION_PROGRESS.md. No ROM/TTF uploaded, IPS044 local only.

VIỆC PHẢI LÀM TIẾP, ĐỪNG DỪNG Ở CHỈ AUDIT:
1. Batch02 còn 72, Batch03 có 84: dịch và CHÈN THẬT vào ROM theo nhóm lớn 40–100 dòng mỗi lần tùy an toàn. Xem source story_batch02_part2_vi.csv /part3_vi.csv và story_batch03_part1/part2a/part2b. Nguồn scanner đôi khi chia một byte số Q/R/P; không vá offset giữa ký tự, kiểm tra original actual ROM.
2. Thoại dài không vừa vẫn phải giữ full vi_full, thiết kế safe relocation/wrap chứ không bẻ cụt ngữ pháp. Kiểm tra ngôi nhân vật Maruko/Tama-chan, Hanawa (Baby), Maruo (Nói thẳng ra!), chuyện tranh suất đi đảo.
3. G2 nguồn text CP932 có offset sửa 0x1E325; G3 Win/Lose phải lần đúng asset real, không patch QA descriptors 0x2865E..287FF.
4. Khi đủ lượng nội dung lớn -> gộp duy nhất một IPS/ROM QA và chạy giả lập thật, không đưa user bản vá lẻ.
5. Cứ sau mỗi phiên làm nhiều thật, update GitHub và handoff. USER CHỈ CẦN NHẮN TIẾP, KHÔNG ĐƯỢC NHỜ HỌ TEST TỪNG BUILD.

TÊN CREDIT ĐÚNG: Việt hóa bởi Votri Valley. GIỮ FONT ĐỂ SAU.
