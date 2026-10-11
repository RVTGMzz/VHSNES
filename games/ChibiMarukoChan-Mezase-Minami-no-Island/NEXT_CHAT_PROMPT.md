TIẾP TỤC VIỆT HÓA CHIBI MARUKO-CHAN SNES — CHECKPOINT 042 (2026-10-11)
Repo: RVTGMzz/VHSNES | nhánh chibi-maruko-bootstrap-01.

MỆNH LỆNH CỦA USER: HOÀN THÀNH NỘI DUNG TRUYỆN/MENU/ĐỒ HỌA TRƯỚC, FONT XỬ LÝ SAU. Đừng sa lầy 65816 font 9px như trước, đừng làm người dùng test hàng chục bản IPS nhỏ. GIỮ nguyên ghi công: Việt hóa bởi Votri Valley.

ĐỌC:
1. games/ChibiMarukoChan-Mezase-Minami-no-Island/HANDOFF_CURRENT.md (checkpoint042 ĐẦU FILE).
2. docs/CONTENT_FIRST_STORY_CHECKPOINT_042.md.
3. translation/runtime/story_batch01_safe_segments_042.json.
4. tools/build_content_first_042_story_safe_segments.py.
5. docs/CONTENT_FIRST_QUIZ_CHECKPOINT_041.md.
6. docs/RUNTIME_STORY_BUILD_027.md (historical 328 Story records, builder not preserved).

KẾT QUẢ MỚI NHẤT:
- Đã chèn THẬT **26 lượt Story đầu** vào ROM thử 042, mỗi lượt ngữ cảnh giữ giọng nhân vật (đặc biệt Maruko, Tama-chan, Hanawa), không tự động cắt câu. Có 41 physical segments, 40 break marker 816F/81A5 giữ nguyên ở exact original offsets, và toàn bộ vị trí break marker trong ngân hàng Story 0x18000..0x1DFFF cũng không đổi. Mỗi segment viết bằng V2 0x84 2-byte, giữ số byte gốc/padding; không viết qua script opcode, không nén bừa. Full canonical vi_full được giữ trong story_batch01_vi.csv, compact runtime khác ở JSON42.
- Ngăn ghi nguồn chưa chắc: 0x18408 là raw ASCII P dính variable control, và một scanner-artifact 印 prefix bị bỏ. Nhiều câu dài hơn số ô chữ vẫn Nhật, cần nghiên cứu an toàn relocation/field expansion, KHÔNG nhét cụt ngữ pháp.
- ROM clean gốc không header 2MiB /mnt/data/Chibi Maruko-chan - Mezase! Minami no Island!! (Japan)(1).sfc SHA e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956.
- IPS 041 SHA 2117bc6e165f2c86263e74a637b6961a13f79257fccd9f02152a769fe1deb962, 22.100 bytes, trong zip 041. Bản ROM 041 reconstructed SHA 56c36cbc8e477d262216d3aa0f06909e09b9929ba0f6f544dccbaa3671bf48fb.
- Bản patch 042 từ CLEAN nhật SHA **3e3c3de245a9a0a6648b2e62eff44a72093ef1e2e9cfcb1cf013ff6c4cbb5035**, 23.105 bytes / 799 records. ROM sau vá SHA **901744ff2edb6bbf667e225e68478009f426a4d1358c1c35ccb34cdc29254691**. Thay đúng **794 byte** khác với ROM 041, chỉ ở 26 dòng Story và checksum, marker/thành phần khác byte-identical. Checksum 3988/C677. 2 local tools độc lập đã kiểm tra IPS replay, checksum, byte whitelist và page/line markers. Local QA files /mnt/data/Chibi_042_26Story_Exact_Source_QA.json, /mnt/data/Chibi_042_Independent_Static_QA.json.
- Local ZIP gửi người dùng /mnt/data/Chibi_042_G0G1_118Fields_Story26_Content_First_UNTESTED.zip CHỈ CÓ IPS, 2 QA json, README; KHÔNG CÓ ROM/TTF.
- Tổng patch hiện tại **118 fields** = 38 UI checkpoint039 + 33 Fortune checkpoint040 +21 Quiz checkpoint041 +26 Story checkpoint042. G0+G1 on-ROM Vietnamese graphic (title/phụ đề/Votri Valley, Chọn gì đây? / Bắt đầu / Mật khẩu) giữ nguyên. Chưa xong Story, chưa đủ Quiz, G2/G3 chưa tích hợp, chưa runtime test SNES, font V2 user cũ phàn nàn chưa sửa.
- GH mới: translation/runtime/story_batch01_safe_segments_042.json (26 full canonical reference+separate compact lines+capacities), tools/build_content_first_042_story_safe_segments.py (build ROM042 từ clean+IPS041+CSV+codepage); docs/CONTENT_FIRST_STORY_CHECKPOINT_042.md. Build script GH chưa được CI chạy, local script tương đương đã run binary thật.
- Mục tiêu tiếp là **thêm 40–100 Story thoại natural** nếu an toàn, xử lý batch01/batch02/batch03 theo source offset/physical frame capacities; không chỉ tạo checklist. Khi vượt byte cần tìm pointer/record relocation bằng game code, không chèn sai. Muốn nhiều nội dung một lượt, nhưng đừng quá sức gây crash.
- Historical Build027 chứa 328 Story theo docs nhưng ROM binary/candidate runtime CSV không có trong repo. Đừng lấy 328 làm số bản 042 đã tích hợp.
- Do chưa có giả lập thực tế, KHÔNG CLAIM RUNTIME PASS hay phát hành game chính thức. User chưa cần test bản lẻ, đợi bản lớn. Font vẫn ĐỂ SAU.

YÊU CẦU ĐẾN PHIÊN TIẾP: làm trực tiếp tăng số thoại Story/Quiz trong ROM + update GitHub. Không quay lại kiểm tra font trừ khi user yêu cầu.
