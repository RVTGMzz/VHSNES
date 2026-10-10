TIẾP TỤC VIỆT HÓA CHIBI MARUKO-CHAN SNES
Repo: RVTGMzz/VHSNES
Nhánh: chibi-maruko-bootstrap-01

ĐỌC THEO THỨ TỰ:
1. games/ChibiMarukoChan-Mezase-Minami-no-Island/HANDOFF_CURRENT.md
2. games/ChibiMarukoChan-Mezase-Minami-no-Island/docs/G2_PROBE008_LINE_SCOPED_9PX_CHECKPOINT_024.md
3. docs/G2_PROBE008_SELECTIVE_SPACING_CHECKPOINT_023.md
4. docs/G2_PROBE008_LOCAL_STATIC_BUILDS_CHECKPOINT_022.md
5. docs/G2_PROBE008_COMPLETE_FONT_CHECKPOINT_021.md

ĐÃ LÀM ĐẾN 024:
- ROM clean SHA256 e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956; Probe003 tái tạo đúng SHA256 5208bec10147f478cc17955c4f262a5cde08e5b85708caa2717370f6835fbacd.
- Probe008 V2 font-only 13px SHA256 2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd (212 Unicode, 210 bitmap, 49 chữ hoa +3 chữ thường mới, font page 0x0A).
- Renderer gốc advance 13px. Bản 9px chọn theo TỪNG GLYPH bị lỗi dấu ngoặc Nhật cuối câu cách dư 64px. KHÔNG PHÁT HÀNH kiểu đó.
- ĐÃ BUILD MỚI THỬ NGHIỆM: G2 SOURCE-RANGE-SCOPED 9PX, SHA256 feb7215a67046128ff67113fd921b6479d956df6018a3ae4e74992d03b0c978a, 181 bytes diff so với V2, checksum 0xF4D6, complement 0x0B29. Hai hook 65816 57 byte; vẫn giữ bảng 13px Nhật nguyên trạng. Chọn 9px khi DBR=$83 và nguồn $1F94 nằm trong 3 bản ghi 106byte đã xác minh: $83:81CE..8238, $83:8247..82B1, $83:82C0..832A. Tất cả ký tự trong G2, gồm ngoặc Nhật 8175/8176, bước 9px, nên mô hình không còn lệch 64px.
- Đã xác minh tĩnh qua 12.464 test micro-65816, bộ xác minh ROM ĐỘC LẬP PASS, 5 phép test làm hỏng dữ liệu đều bị từ chối. Text và dấu phân cách 816F ở 32/68/104, D038, scene/palette giữ nguyên.
- Script: tools/build_g2_probe008_line_scoped_9px_diagnostic.py và tools/verify_g2_probe008_line_scoped_9px_diagnostic.py. Checkpoint 024 và HANDOFF đã cập nhật lên GitHub. KHÔNG UPLOAD ROM.

CẦN LÀM TIẾP:
1. Kiểm thử thật trong giả lập SNES debugger. Đặc biệt quan sát DBR và WRAM $1F94 ngay lúc G2 renderer chạy để chứng minh lựa chọn đúng nguồn $83; kiểm tra màn đen/crash, font page0x0A, dấu hỏi/ngã, tiếng Việt, ngoặc 8176, wrap dòng; màn Nhật khác vẫn 13px. Phiên cũ không có SNES emulator nên CHƯA RUNTIME PASS.
2. Xác minh bộ codepage lead 0x85 mới không làm hỏng nội dung game Nhật; các ô FF mới chưa thể khẳng định an toàn trên mọi luồng.
3. Chỉ sau khi test runtime mới nâng patch G2 từ diagnostic sang candidate. Muốn 9px ở các Story/UI khác, phải lần ra nguồn chính xác rồi mở rộng các phạm vi đã chứng minh; KHÔNG tự ý toàn cục.
4. Khi font tốt, tiếp tục G0 title/credit VôtriValley, G2/G3 graphics, menu và những chỗ Nhật còn sót theo HANDOFF_CURRENT.md.

Không coi kiểm tra checksum/bitmap/micro-interpreter PASS là đã chạy được game. Không đưa ROM lên GitHub.
