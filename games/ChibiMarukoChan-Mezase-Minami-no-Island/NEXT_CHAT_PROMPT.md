TIẾP TỤC VIỆT HÓA CHIBI MARUKO-CHAN SNES — CHECKPOINT 026 (RUNTIME FAIL)
Repo: RVTGMzz/VHSNES
Branch: chibi-maruko-bootstrap-01

ĐỌC TRƯỚC:
1. games/ChibiMarukoChan-Mezase-Minami-no-Island/HANDOFF_CURRENT.md
2. docs/G2_PROBE008_USER_RUNTIME_FAIL_CHECKPOINT_026.md (QUAN TRỌNG NHẤT)
3. docs/G2_PROBE008_STACK_BANK_SAFE_CHECKPOINT_025.md (CHỈ LÀ LỊCH SỬ, BẢN NÀY FAILED)
4. docs/G2_PROBE008_LOCAL_STATIC_BUILDS_CHECKPOINT_022.md

TÌNH HUỐNG MỚI:
- User vừa test thật ROM Probe008 025 9px theo dòng, SHA256 d4bd629003812578580e7a380e791d87fdf64614441394f1261df3951b9815dc, gửi ảnh màn hình 952x381 (SHA256 5fe322fe15746017ee1362daf9ffe0a275344f91b256bdd30732d033ceb62ee0). CHỮ RẤT XẤU, RỜI RẠC, GIÃN XA; phải coi là RUNTIME TYPOGRAPHY FAIL.
- 3 dòng G2 đọc được từ ảnh: Nói thẳng nhé! / Du học chớ ngại! / Luyện phản xạ! Nhưng không đạt tính dễ đọc. Người dùng thất vọng, đừng hỏi họ test ROM chưa kiểm chứng khác ngay.
- Phân tích độ rộng mực đen ảnh tương ứng các dòng: 599, 672, 638px; bước tiến ước lượng ~13.73/14.37/14.62 native px, gần 13px gốc hơn 9px dự định. Nghi điều kiện chọn 9px dựa trên DBR=$83 và $1F94 trong ba records không đúng khi chạy thật; CHƯA CHẮC, cần debugger chứng minh.
- 18.696 kiểm tra micro-65816 và các static checksum/pointer PASS trước đó KHÔNG CÓ GIÁ TRỊ CHỨNG MINH runtime typography. Checkpoint 025 là FAILED, không phát hành.
- Đã QUARANTINE builder tools/build_g2_probe008_line_scoped_9px_diagnostic.py: bắt buộc --reproduce-known-runtime-fail-025 mới tái tạo ROM lỗi. Verifier cũng hiện runtime FAIL. Tạo tools/audit_g2_probe008_runtime_screenshot_025.py nhận chỉ đúng ảnh đã gửi (dựa hash) để phát hiện bề rộng chữ, KHÔNG đưa ảnh riêng lên GitHub.
- ROM clean gốc SHA256 e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956.
- Probe003 static rebuilt SHA256 5208bec10147f478cc17955c4f262a5cde08e5b85708caa2717370f6835fbacd (runtime text path pass, thin font fail).
- Probe008 V2 FONT ONLY SHA256 2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd, 212 codes/210 bitmap, page0A. Chỉ là baseline tĩnh. KHÔNG KHẲNG ĐỊNH bản này runtime đẹp.

VIỆC TIẾP THEO:
1. Ưu tiên PHÂN TÍCH NGUYÊN NHÂN renderer chọn sai pitch 9px trên máy thật: trace hoặc chứng minh DBR, $1F94 at parser $85:8340, glyph offset $85:8E0C, bit shift $85:90EE, 65816 M/X modes; không sửa mò tiếp.
2. Sau khi có 9px TRONG GAME, cải thiện font 12x12 tiếng Việt vì nét hiện giờ quá mảnh/ít mực, dấu vẫn xấu. Rà đồng thời câu nói, giãn cách, câu có dấu Nhật mở/đóng ngoặc, wrap và UI Nhật.
3. Chỉ đưa ROM thử mới cho người dùng khi có căn cứ mạnh hơn kiểm tra tĩnh, giải thích rõ trạng thái; đừng nói đã xong.
4. Tiếp tục menu/title/G2/G3 và game sau khi qua font gate. Không đưa ROM thương mại hay screenshot riêng của người dùng lên GitHub.

ĐỌC CHÍNH XÁC CHECKPOINT 026 VÀ ẢNH CHỤP TRONG HỘI THOẠI NẾU CÒN; không lấy bản 025 làm bản sạch.
