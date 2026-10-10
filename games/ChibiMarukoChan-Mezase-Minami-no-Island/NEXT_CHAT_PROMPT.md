TIẾP TỤC VIỆT HÓA CHIBI MARUKO SNES — RVTGMzz/VHSNES, branch chibi-maruko-bootstrap-01.

ĐỌC TRƯỚC THEO THỨ TỰ:
1. games/ChibiMarukoChan-Mezase-Minami-no-Island/HANDOFF_CURRENT.md
2. games/ChibiMarukoChan-Mezase-Minami-no-Island/docs/G2_PROBE008_LOCAL_STATIC_BUILDS_CHECKPOINT_022.md
3. .../docs/G2_PROBE008_COMPLETE_FONT_CHECKPOINT_021.md
4. .../docs/G2_PROBE008_RENDERER_SPACING_PROOF_020.md
5. .../docs/G2_PROBE008_SPACING_HANDOFF_019.md

ĐÃ HOÀN THÀNH (KIỂM TRA TĨNH THẬT, KHÔNG PHẢI EMULATOR):
- ROM clean đúng SHA256 e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956.
- Probe003 dựng lại KHỚP 100% hash SHA256 5208bec10147f478cc17955c4f262a5cde08e5b85708caa2717370f6835fbacd.
- Đã build Probe008 V2 FONT ONLY tại máy local, SHA256 2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd, 4034 byte diff so với Probe003, checksum 0x622E / complement 0x9DD1.
- V2 có 212 mã Unicode, 210 bitmap thật, 49 chữ hoa tiếng Việt thêm + 3 chữ thường, 84/100 ô trang font 0x0A mới; đã phục hồi crossbar A hoa và sửa vị trí hỏi/ngã. Đã kiểm tra roundtrip tất cả font, giữ nguyên 3 text payloads và dấu phân cách 32/68/104, D038/scene.
- LỖI QUAN TRỌNG ĐÃ SỬA: relocate 2 lệnh con trỏ font ở offsets 0x28EA8 VÀ 0x28EAE (không phải 0x28EAD). Builder và verifier trên repo đã được fix.
- Renderer gốc advance 13px (2 bảng tại 0x29670/0x29696), mẫu 9px không có bitmap collision trên tất cả 44.944 cặp Unicode; script tự động test có negative-control 7px.
- Đã build riêng bản thử DIAGNOSTIC font V2 + GLOBAL 9px, SHA256 7b982dbbcd683fa981b2a20da10850d61b6f34fd9f25970baa5f32dab75440f8, 35 bytes khác V2 13px, checksum 0x60CE / 0x9F31.
- Đã tạo PNG offline 13/9 từ chính glyph ROM đã patch và atlas 212 ký tự. Có SVG so sánh trong repo.
- KHÔNG ĐƯA ROM LÊN GITHUB; đã cập nhật mã, tài liệu, JSON, công cụ, preview SVG trên nhánh.

BƯỚC TIẾP THEO: chạy builder + verifier đúng repo và Probe003; kiểm tra độ tương thích đường mapping 0x85, renderer font page0x0A, xử lý 9px CHỈ dành cho tiếng Việt/không tác động Japanese; test trên giả lập (môi trường phiên chat trước không có emulator), thu ảnh thật từ màn hội thoại/truyện, menu Nhật, dấu hỏi ngã và chữ hoa. Chưa có Runtime PASS, chưa release Probe008 hay kết luận toàn game hoàn thiện. Sau đó mới quay lại các tồn đọng phần đồ họa/title/menus theo handoff.
