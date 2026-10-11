TIẾP TỤC VIỆT HÓA CHIBI MARUKO-CHAN SNES — CHECKPOINT 043, 2026-10-11
GitHub: RVTGMzz/VHSNES | nhánh chibi-maruko-bootstrap-01

ƯU TIÊN: HOÀN THIỆN NỘI DUNG TRUYỆN/MENU/ĐỒ HỌA TRƯỚC; FONT SỬA SAU. Không làm microtest font hoặc bắt user test nhiều ROM lẻ. Biên tập thoại tự nhiên, đúng nhân vật, không cắt máy móc.

ĐỌC:
1. games/ChibiMarukoChan-Mezase-Minami-no-Island/HANDOFF_CURRENT.md (checkpoint043 trên cùng).
2. docs/CONTENT_FIRST_STORY_CHECKPOINT_043.md.
3. translation/runtime/story_batch01_safe_segments_043.json (58 Story mới, vi_full tham chiếu chuẩn, segments & capacity).
4. tools/build_content_first_043_story_58.py (builder sạch+IPS042).
5. docs/CONTENT_FIRST_STORY_CHECKPOINT_042.md, 041, 040, 039; translation/TRANSLATION_PROGRESS.md.

MỚI Ở 043:
- Đã thật sự VÁ ROM ở 58 lượt Story Batch01 MỚI, 170 physical Japanese source text spans, 167 dấu ngắt 816F/81A5 giữ nguyên, toàn bộ vị trí dấu ngắt Story bank không đổi. Giọng Maruko, Tama-chan, Maruo (Nói thẳng ra!), Hanawa (Baby) giữ đúng ngữ cảnh. vi_full gốc không thay; compact runtime trong JSON043. Cộng 26 từ 042 = 84/123 Story Batch01 đã có mã tiếng Việt trong ROM thử, còn 39 chưa tích hợp.
- ROM SNES Nhật sạch 2MiB: /mnt/data/Chibi Maruko-chan - Mezase! Minami no Island!! (Japan)(1).sfc, SHA e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956.
- Base IPS042 sạch: trong /mnt/data/Chibi_042_G0G1_118Fields_Story26_Content_First_UNTESTED.zip, IPS SHA 3e3c3de245a9a0a6648b2e62eff44a72093ef1e2e9cfcb1cf013ff6c4cbb5035, dựng ROM042 SHA 901744ff2edb6bbf667e225e68478009f426a4d1358c1c35ccb34cdc29254691.
- IPS043 sạch /mnt/data/Chibi_043_Story58_Content_First_UNTESTED.ips SHA d3cb7ea84067675a5cc12cb4a26f260194b0a6f00ff235f0129460a902a58a50, 28.135 bytes/977 records, target ROM SHA 45ffca7db5db83bc2734e885ee90c77f33746e2c4a54d1c99f1502f3e992a6ae. SNES checksum/complement E83A/17C5. QA độc lập apply IPS từ ROM sạch khớp từng byte; so ROM042 có 4144 byte thay đổi hoàn toàn thuộc 58 field và checksum, không hỏng 167 break.
- Tổng hiện tại 176 direct text fields =38 UI(039)+33 Fortune(040)+21 Quiz(041)+26 Story(042)+58 Story(043). Cộng riêng G0/G1 logo/phụ đề/Việt hóa bởi Votri Valley, Chọn gì đây?, Bắt đầu/Mật khẩu.
- Local ZIP patch-only IPS+QA+CSV: /mnt/data/Chibi_043_G0G1_176Fields_Story58_Content_First_UNTESTED.zip. KHÔNG upload ROM hoặc font có bản quyền. GitHub đã có JSON043, builder043, docs043, handoff, progress.
- Chưa phải bản hoàn chỉnh: 39 Story Batch01 còn lại, Story Batch02/03 (historical Build027 báo 328 Story nhưng builder/binary không còn), G2/G3 và Quiz còn nhiều. Cần layout expansion nếu quá giới hạn; không cắt cụt. Font V2 cũ còn xấu, user dặn làm nội dung trước. Chưa chạy SNES emulator, không claim Runtime PASS.

NHIỆM VỤ NEXT:
1. Tiếp tục hàng chục Story Batch01 còn lại nếu an toàn, sau đó Story Batch02/03 với canonical vi_full và đúng CP932 source offsets. Nếu source_jp_scanner chứa ký hiệu ｛, ▼ hoặc metadata, phải xác minh ROM/callsite trước khi chèn.
2. Phát triển pointer/field relocation an toàn hoặc rewrap cho thoại dài. KHÔNG ghi đè script byte.
3. Khi đã có bản lớn, gom 1 IPS full-game và chạy 1 phiên SNES emulator QA gồm title/Story/Quiz/result/font; không bắt user test lắt nhắt.
4. Giữ G0/G1, checksum, offset và Votri Valley nhất quán, push code/checkpoint GitHub.

FONT ĐỂ SAU.
