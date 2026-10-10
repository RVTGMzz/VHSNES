TIẾP TỤC CHIBI MARUKO-CHAN SNES VIỆT HÓA — CHECKPOINT 028
Repo: RVTGMzz/VHSNES / branch chibi-maruko-bootstrap-01

ĐỌC TRƯỚC:
1. games/ChibiMarukoChan-Mezase-Minami-no-Island/HANDOFF_CURRENT.md
2. games/ChibiMarukoChan-Mezase-Minami-no-Island/docs/G2_PROBE008_GLYPH_GEOMETRY_V3_CHECKPOINT_028.md
3. docs/G2_PROBE008_V3_MEDIUM_FONT_CHECKPOINT_027.md
4. docs/G2_PROBE008_USER_RUNTIME_FAIL_CHECKPOINT_026.md (USER SCREENSHOT FAIL, VẪN HIỆU LỰC)

NGUYÊN NHÂN KỸ THUẬT MỚI:
- Bản 025 đã bị USER TEST THẬT: font quá mảnh, chữ giãn ~13px, RUN-TIME TYPOGRAPHY FAIL. Không tiếp tục dùng 025.
- Đã tìm ra glyph ID THẬT vào renderer ở A, được lưu PHA đầu $85:8E7B. Biến $1FB2 từng được hiểu nhầm là glyph ID là một giá trị khác (write sites $85:8026/$85:8579), không dùng để chọn glyph 9px. Bản 023 dựa trên biến đó cũng không có bằng chứng đủ.
- Word lookup $85:8E0C: glyph ID thật nằm ở $0A,S nếu X8 hoặc $0C,S nếu X16. Byte lookup $85:90EE: khôi phục phân loại ID từ font page ptr DP $18 và tọa độ cell atlas DP $08/$0A có sẵn, không cần đoán DBR bank và $1F94.
- Read-only kiểm toán 1.100 ID vật lý (11 trang×100 cell) xác minh word và byte đều cùng chọn 9px cho 218 ID (bao gồm quote Nhật 0159/015A) và giữ 13px cho 882 ID khác. Cả 3 bản ghi G2 106B đều chứa 50 glyph được chọn 9px + 3 dấu 816F.
- Đã dựng 028 geometry-only chẩn đoán, SHA256 a3d2e75da5f9dac36750ef77e249fae7613ffd35f8185c50cd6f6197ca8a8688, 258 byte diff từ V2, checksum 0xC1E2/0x3E1D. 2 hook 65816 71B/120B. Giữ nguyên codepage, G2 records, 13px Nhật gốc.
- Bộ giả lập MỘT PHẦN mã lệnh 65816 đọc chính xác machine code từ stub: 83.600 trường hợp với 1.100 ID×19 cột×2 X widths×2 hook, tất cả tĩnh PASS. KHÔNG PHẢI EMULATOR THẬT.
- Thêm V3 medium weight (178 custom physical glyphs đậm hơn, 32 native không đổi) lên bản 028, local UNTESTED combined ROM SHA256 59f4c45b14a24e6cf67de1c9c7cbe1d9b862eaa2eb4c6518bbc4bcbd6dd006fb. Diff từ geometry-only 1183 bytes, checksum 0x7587/0x8A78. Kiểm 210 bitmaps và 44.100 cặp không đụng nhau, 5.055 pixels.
- Tools: tools/audit_g2_probe008_renderer_glyph_geometry_028.py, tools/build_g2_probe008_glyph_geometry9_diagnostic.py, tools/selftest_g2_probe008_geometry9_opcode_028.py, tools/build_g2_probe008_v3_medium_geometry9_experiment.py, tools/propose_g2_probe008_v3_medium_font.py. Builders mặc định TỪ CHỐI nếu không có --allow-untested-diagnostic.
- CẢNH BÁO QUAN TRỌNG: quote glyph ID 0159/015A đổi sang 9px trong MỌI đoạn text có nó, kể cả Nhật khác; cần thử để đảm bảo không bị hỏng UI. Không upload ROM lên repo.

BẮT BUỘC LÀM TIẾP:
1. Kiểm thử thật SNES emulator/debugger (môi trường trước CHƯA CÓ emulator). Xác nhận PHA glyph trên stack ở $85:8E0C, page pointer DP $18 và atlas coord $08/$0A ở $85:90EE, font page A, 9px G2, dấu hỏi/ngã, upper A, 8175/8176 quote, WRAP 19 cột và scene không crash. Không claim đã đạt khi chỉ chạy microtest.
2. Kiểm thử UI/Story Nhật, nhất là dấu ngoặc 0159/015A có bị co khoảng cách ngoài G2 không; nếu có phải giới hạn chỉ scene G2. Kiểm tra native code lead 0x85 không đụng ngữ cảnh Nhật.
3. Sau runtime font accept mới tiếp tục G0 title, G2/G3 graphics, menu và các đoạn Nhật chưa dịch.
4. Vì user từng phải test ROM lỗi, đừng gửi tiếp ROM chưa được đánh giá đủ. Chuẩn bị test matrix rõ ràng và giải thích trạng thái thực.
5. Giữ file ROM 2 MiB ngoài GitHub, source/checkpoint/QA scripts trên branch.

ROM nguồn chính xác Probe008 V2 font-only SHA256 2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd. Probe003 reconstructed 5208bec10147f478cc17955c4f262a5cde08e5b85708caa2717370f6835fbacd.

CHECKPOINT 028 STATIC ONLY. CHECKPOINT 025 GAMEPLAY FAIL. Không phát hành.
