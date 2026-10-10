BẮT BUỘC G0: người dùng yêu cầu Việt hóa ngay MÀN TITLE HIỆN KHI KHỞI ĐỘNG: dòng chính `Chibi Maruko-chan`, phụ đề `Tiến tới đảo phương Nam!!`, credit nhỏ CHÍNH XÁC `Việt hóa bởi Votri Valley`. G0 P0 ngang với G1. Giữ logo/ảnh nhân vật/bản quyền gốc; đừng vá debug descriptor thay asset retail. Chưa có source graphics chính xác và chưa tích hợp vào ROM thì KHÔNG claim đã xuất hiện trong game.

TIẾP TỤC VIỆT HÓA CHIBI MARUKO-CHAN SNES — CONTENT FIRST CHECKPOINT 032 (2026-10-11)
Repo: RVTGMzz/VHSNES
Branch: chibi-maruko-bootstrap-01

ƯU TIÊN CỦA NGƯỜI DÙNG (RẤT QUAN TRỌNG): HOÀN THÀNH VIỆT HÓA NỘI DUNG GAME TRƯỚC; FONT ĐỂ SAU. KHÔNG TIẾP TỤC 032/033/034 FONT MICROHOOK, KHÔNG ĐỂ FONT CHẶN VIỆC DỊCH THUẬT.

ĐỌC:
1. games/ChibiMarukoChan-Mezase-Minami-no-Island/HANDOFF_CURRENT.md
2. games/ChibiMarukoChan-Mezase-Minami-no-Island/docs/CONTENT_FIRST_CANONICAL_MERGE_CHECKPOINT_032.md
3. games/ChibiMarukoChan-Mezase-Minami-no-Island/translation/TRANSLATION_PROGRESS.md
4. games/ChibiMarukoChan-Mezase-Minami-no-Island/translation/runtime/content_first_graphics_queue_032.csv
5. games/ChibiMarukoChan-Mezase-Minami-no-Island/docs/UI_LOCALIZATION_COVERAGE_001.md
6. HANDOFF_CURRENT.md phần Graphics Batch G0/G1/G2/G3 và pipeline.

TIẾN ĐỘ THẬT ĐÃ LƯU GITHUB:
- 1.018 source rows dịch nghĩa thông thường đã có từ trước; +3 G2 demo = 1.021 bản ghi theo dõi. SỐ NÀY KHÔNG PHẢI % VIỆT HÓA CỦA GAME VÀ KHÔNG PHẢI CÂU MỚI DỊCH Ở PHIÊN NÀY.
- 10 file editorial chứa 220 revision events. Vừa nhập chúng TRỰC TIẾP vào canonical translation/source/*.csv ở 20 file, 209 lượt chỉnh câu thực tế, 11 lượt đã khớp. Do 4 lượt sửa đè các lời đề xuất cũ, có 216 nguồn (file, file_offset) cuối cùng.
- QA LIVE sau cập nhật GitHub: Story 85/85, Quiz 54/54, Fortune 24/24, UI 53/53 = 216/216 câu cuối ở vi_full khớp review cuối cùng; 0 conflict. Công cụ mới tools/audit_g2_editorial_canonical_032.py (chỉ kiểm tra ngôn ngữ, không đụng ROM).
- Xử lý BOM UTF8 trong các source CSV, giữ nguyên byte gốc ngoài giá trị vi_full. Ba khác biệt giữa review và source đã được rà theo JP, sửa xong.
- 16 target graphics đã có trong translation/runtime/content_first_graphics_queue_032.csv: G0 title + dòng Việt hóa bởi Votri Valley, G1 heading + Start/Password, G2 start banner/VS/rules, G3 Win/Lose/Continue/Quit/final/Ending. Trong đó 14 chữ Nhật cần xử lý đồ họa, 1 VS Latin giữ nguyên, 1 credit mới. Asset graphics thật nhiều cái CHƯA TRUY RA.
- Previous Build035 direct text candidate chưa runtime PASS; bản 025 font user test thực tế FAIL. 029 font experiment only static; 031 stack audit only static. ĐÓNG FONT TRACK CHO TỚI KHI XỬ LÝ NỘI DUNG XONG.
- Không đưa ROM thương mại lên GitHub, không claim game dịch hoàn chỉnh chỉ vì 1.021 source rows.

HÃY LÀM NGAY:
1. DÙNG ROM gốc và tool reverse G0/G1 đã có để truy các tài sản đồ họa hiển thị thật (đặc biệt G1 Chọn gì đây? / Bắt đầu / Mật khẩu). Đừng vá internal descriptor giả làm hình retail. Nếu chưa thể decode, ghi blocker theo asset nhưng tiếp tục phần khác chứ không sa lầy.
2. Tiếp tục rà các khu vực nội dung người chơi thật sự thấy (rules graphics, stage cards, ending, karaoke), nếu phát hiện JP MỚI ngoài 1.021 row thì trích nguồn có offset/evidence và DỊCH vào source. Không bổ sung scanner noise/internal QA để lấy số.
3. Xác định liệu các builder runtime có sử dụng vi_full canonical mới nhất hay vẫn dùng câu cũ; cập nhật đường build theo nguồn nếu được, nhưng KHÔNG QUAY LẠI CHỈ SỬA FONT.
4. Một đợt làm việc phải báo rõ số mục dịch mới, số source row biên tập/áp dụng, số graphics asset được chứng minh, số vẫn chờ, mã commit GitHub; phân biệt ngôn ngữ với kiểm thử ROM.

READ checkpoints 032 (active), 031 (font frozen history), 026 (user runtime fail). Không cần hỏi lại tên game hay bảo người dùng gửi ROM khi clean ROM còn có ở /mnt/data của phiên này.
