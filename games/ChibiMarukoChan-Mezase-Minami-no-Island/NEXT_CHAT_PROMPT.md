TIẾP TỤC VIỆT HÓA CHIBI MARUKO-CHAN SNES — CHECKPOINT 029
GitHub: RVTGMzz/VHSNES — branch chibi-maruko-bootstrap-01

ĐỌC TRƯỚC:
1. games/ChibiMarukoChan-Mezase-Minami-no-Island/HANDOFF_CURRENT.md
2. docs/G2_PROBE008_ISOLATED_QUOTES_CHECKPOINT_029.md
3. docs/G2_PROBE008_GLYPH_GEOMETRY_V3_CHECKPOINT_028.md
4. docs/G2_PROBE008_V3_MEDIUM_FONT_CHECKPOINT_027.md
5. docs/G2_PROBE008_USER_RUNTIME_FAIL_CHECKPOINT_026.md

TRẠNG THÁI:
- Bản 025 người dùng test thật FAIL: chữ bị giãn như 13px, mỏng và rời; ảnh có trong chat trước. Không gửi lại và không claim runtime pass.
- Bản 028 đã sửa logic chọn 9px dựa trên glyph thực sự từ thanh ghi A/stack khi gọi helper và geometry font trang/ô ở lookup2. 83.600 test 65816 subset PASS, nhưng native Japanese quote 8175/8176 cũng bị đổi 9px toàn game. Quét byte ROM gốc có 121 lần 8175 và 123 lần 8176 ngoài ba bản ghi G2: rủi ro lớn, KHÔNG RELEASE 028.
- Bản 029 mới tạo 2 BẢN SAO glyph dấu ngoặc cho G2, original native glyph IDs 0159/015A vẫn dùng 13px. Font page 0x0A mới có 16 ô còn trống; dùng 0A54 và 0A55. Tạo ánh xạ 8574 -> 0A54 và 8575 -> 0A55 trong bảng lead 0x85. Chỉ đổi 3 mở 8175->8574 + 3 đóng 8176->8575 ở đúng ba fields G2, những chữ khác giữ nguyên. 3×106 bytes không đổi độ dài; D038, dấu 816F ở 32/68/104, palette, 13px table, original native 8175/8176 không thay. CHÚ Ý: do đổi sáu cặp quote, GIẢ ĐỊNH 'G2 bytes toàn bộ identical' của 028 ĐƯỢC NỚI LỎNG CÓ KIỂM SOÁT. Không nói source payload unchanged hoàn toàn.
- Input 029 chính xác: ROM V3 MEDIUM GEOMETRY9 COMBINED 028 SHA256 59f4c45b14a24e6cf67de1c9c7cbe1d9b862eaa2eb4c6518bbc4bcbd6dd006fb.
- Output 029 local ROM SHA256 a23304cedff0eac959a6455d90b866c49543ca381425b089771b65da264e928e, 180 changed bytes, checksum 0x9309/complement 0x6CF6, word-hook 61B/shift-hook 86B, 83.600 tests 65816 subset PASS, source controls preserved. CHỈ STATIC, NOT EMULATOR TESTED.
- MỚI push scripts: tools/build_g2_probe008_029_isolated_quotes_diagnostic.py (bắt buộc --allow-untested-diagnostic) và tools/selftest_g2_probe008_029_isolated_quotes_opcode.py, checkpoint 029, updated HANDOFF_CURRENT. Không upload ROM.
- Môi trường container có ROM hợp lệ /mnt/data, nhưng không có snes9x/bsnes/retroarch, không có cache apt; curl GitHub không resolve host. KHÔNG TUYÊN BỐ ĐÃ CÓ EMULATOR.

BƯỚC TIẾP:
1. Tìm cách chạy SNES emulator/debugger hoặc lấy trace runtime từ máy người chơi với hướng dẫn tối giản. Ghi PC+stack+DBR/DP tại word hook $85:8E0C và shift hook $85:90EE. Kiểm tra 029 actual 9px và V3 medium, không crash, dấu, wrap, quote; nếu FAIL phải phân tích.
2. Audit lead 0x85 trước khi coi mapping 8574/8575 an toàn toàn game; ROM raw byte scan có nhiều false positives, không chứng minh được mọi render path.
3. Có Runtime PASS mới release candidate/font, tiếp tục G0 title, G2/G3 graphics, menu và minigames.
4. Không hỏi người dùng test bừa hoặc tuyên bố done khi chỉ static. Không đưa ROM lên GitHub.

Mốc 029 được cập nhật trong HANDOFF_CURRENT và docs/G2_PROBE008_ISOLATED_QUOTES_CHECKPOINT_029.md. Hãy tiếp tục từ đây, không quay lại sửa âm thầm bản 025.
