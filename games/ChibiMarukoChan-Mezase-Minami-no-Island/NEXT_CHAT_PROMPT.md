TIẾP TỤC CHIBI MARUKO-CHAN SNES VIỆT HÓA
Repo: RVTGMzz/VHSNES
Nhánh: chibi-maruko-bootstrap-01

ĐỌC TRƯỚC (THEO THỨ TỰ):
1. games/ChibiMarukoChan-Mezase-Minami-no-Island/HANDOFF_CURRENT.md
2. .../docs/G2_PROBE008_SELECTIVE_SPACING_CHECKPOINT_023.md
3. .../docs/G2_PROBE008_LOCAL_STATIC_BUILDS_CHECKPOINT_022.md
4. .../docs/G2_PROBE008_COMPLETE_FONT_CHECKPOINT_021.md
5. .../docs/G2_PROBE008_RENDERER_SPACING_PROOF_020.md

MỐC 023:
- ROM clean chính xác SHA256 e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956; Probe003 rebuilt chính xác SHA256 5208bec10147f478cc17955c4f262a5cde08e5b85708caa2717370f6835fbacd.
- Probe008 V2 FONT ONLY được build/test tĩnh (chưa emulator), SHA256 2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd. 212 mã, 210 bitmap, 84 ô trang font A4:D000. Đã sửa A hoa có dấu, hỏi/ngã xếp tầng và có đủ 49 chữ hoa + 3 chữ thường.
- Mới chạy kiểm toán parser thật trên ROM: 212/212 mã 2 byte truy cập đúng bộ font qua bảng lead, glyphID, con trỏ trang và bitmap 12x12 (0 mismatches); trong đó 84 glyph ở trang font mới. Có script tools/verify_g2_probe008_codepage_pointer_chain.py.
- Renderer gốc có bước 13px. Đã thử global-9px DIAGNOSTIC, ảnh offline đẹp hơn nhưng nguy cơ ảnh hưởng Nhật. Không được release.
- Đã tạo DIAGNOSTIC 9px theo từng glyph (chỉ glyph Việt 9px, Nhật giữ 13px) bằng 2 65816 JSL hook. 4.028 phép thử microhook Việt +190 đối chứng Nhật tĩnh PASS, độc lập checksum và changed-byte whitelist PASS. SHA256 diagnostic dffdec30af4c3ef4d02c58414a25fa8312dcffdd168691ed4add755de1582328, 157 byte changed so với V2 13px, checksum 0xF9AF / complement 0x0650.
- TUY NHIÊN: selective-9px theo glyph bị LỖI BỐ CỤC. Dòng 'Rèn gu mỹ thuật!' dài 16 ký tự rồi có dấu ngoặc gốc 8176/glyph 015A. Nó được đặt ở x212 thay vì x148, lệch 64 pixel. Có PNG minh họa offline. KHÔNG ĐƯỢC release selective probe.
- Byte 0x85 nguyên bản có 32 cặp raw 85 40..73 trong bank được scan nhưng đa số là opcode/data; native 0x85 render use chưa được chứng minh an toàn. Không nói 'đã chứng minh lead mới an toàn toàn game'.
- Các công cụ mới trên GitHub: tools/build_g2_probe008_selective_9px_diagnostic.py, tools/verify_g2_probe008_selective_9px_diagnostic.py, tools/verify_g2_probe008_codepage_pointer_chain.py. Các ROM đang ở môi trường local, KHÔNG commit ROM lên GitHub.

BƯỚC TỚI CẦN GIẢI:
1. Thiết kế và kiểm thử 9px theo CẢ DÒNG hoặc theo CẢNH để dấu ngoặc Nhật 8175/8176 ở câu Việt cũng căn 9px, nhưng những câu Nhật thông thường vẫn 13px; tránh chiếm WRAM chưa xác minh. Chú ý reset trạng thái giữa dòng/cảnh. Không được thay quote/control byte của Probe003.
2. Kiểm tra độc lập đường 0x85 và quyền sở hữu các vùng FF khi di chuyển font.
3. Giả lập SNES thật để test font page A, dấu, spacing, cắt chữ, menu và input. Chưa emulator Runtime PASS. Không phát hành bản mới khi chưa test.
4. Khi font thật sự ổn mới tiếp tục G0/title, G2/G3 graphics, kiểm thử nhiều minigame, toàn bộ dịch còn lại theo HANDOFF_CURRENT.md.

Giữ nguyên strict 2-byte text, dấu phân cách ở 32/68/104, D038, palette, controller và scene logic. Không coi STATIC PASS là RUNTIME PASS.
