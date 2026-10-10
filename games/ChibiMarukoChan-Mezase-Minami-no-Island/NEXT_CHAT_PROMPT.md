TIẾP TỤC CHIBI MARUKO-CHAN SNES VIỆT HÓA — CHECKPOINT 027
Repo: RVTGMzz/VHSNES
Branch: chibi-maruko-bootstrap-01

ĐỌC ĐẦU TIÊN:
1. games/ChibiMarukoChan-Mezase-Minami-no-Island/HANDOFF_CURRENT.md
2. games/ChibiMarukoChan-Mezase-Minami-no-Island/docs/G2_PROBE008_V3_MEDIUM_FONT_CHECKPOINT_027.md
3. docs/G2_PROBE008_USER_RUNTIME_FAIL_CHECKPOINT_026.md
4. docs/G2_PROBE008_STACK_BANK_SAFE_CHECKPOINT_025.md (BẢN LỖI, KHÔNG LẤY LÀM BASE)

ĐÃ THỰC HIỆN:
- User đã test bản Probe008 025 trong game thật: font rời rạc, xấu, quá thưa. Screenshot trong hội thoại, 952x381, sha256 5fe322fe15746017ee1362daf9ffe0a275344f91b256bdd30732d033ceb62ee0. CHẮC CHẮN RUNTIME VISUAL FAIL. Đã quarantine script build 025.
- Mã nguồn parser đọc $1F94 tại $85:8340; renderer thực ở $85:8E7B, word lookup $85:8E0C gọi qua helper $85:8E05, shift lookup $85:90EE sau khi DBR đổi $7F. Screenshot khoảng cách ~13px có thể là fallback; chưa debugger nên không khẳng định nguồn DBR nào sai.
- Exact clean ROM sha256 e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956; Probe003 sha256 5208bec10147f478cc17955c4f262a5cde08e5b85708caa2717370f6835fbacd; Probe008 V2 FONT ONLY 13px sha256 2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd.
- 212 codepoints/210 physical bitmaps V2. Đã dựng 4 mẫu so sánh bitmap V2 13px, V2 9px, V3 medium 9px, V3 dense 9px. Preview PNG local Chibi_Probe008_V3_Font_Weight_Prototype_027.png (không phải ảnh game).
- Công cụ mới tools/propose_g2_probe008_v3_medium_font.py đã push GitHub. Dùng ROM V2 exact để sinh bản JSON font V3, KHÔNG VÁ ROM: giữ 32 glyph native, chỉ làm đậm 178 glyph custom bằng 1 điểm ảnh bên phải với y>=4 x<=8; nguyên tone y<=3 và 212 mã. 180 codepoint rows modified do 1 glyph alias 3 mã.
- Test bitmap offline: V2 3.651 điểm ảnh, V3 medium giữ native 5.055 điểm ảnh; 0 chồng nét trong 44.100 cặp glyph ở 9px. Không được nhầm 5.254 pixel all-glyph font ở ảnh minh họa với 5.055 pixel của data-only generator (native giữ nguyên).
- Không tạo ROM mới, không claim font V3 trong game ổn, không CI PASS giả.

VIỆC KẾ TIẾP:
1. Cần tìm đúng điều kiện renderer khi GAME THỰC đang hiển thị 13px: ghi trace PC $85:8E0C, $85:90EE, DBR, WRAM $1F94, stack bank và X-width bằng giả lập debugger; hoặc tìm bằng phân tích chính xác caller, không đoán rồi build tiếp.
2. Kiểm thử script font V3 medium từ repo bằng ROM chuẩn nếu có; xem dấu, chữ hoa A và tổ hợp hỏi/ngã, dấu ngoặc; kiểm tra toàn bộ bitmap pair 9px và độ rõ.
3. Chỉ tạo bản ROM thử font V3/9px khi xác nhận đường renderer 9px sẽ thật sự chạy; xin ảnh sau cùng để QA, không gửi nhiều ROM lỗi.
4. Sau font mới tiếp tục Việt hóa G0/title, G2/G3 graphics, menu và minigame. ROM thương mại không commit GitHub.

Checkpoint 025 FAIL, checkpoint 027 data-only mới đang STATIC QA. Luôn coi ảnh người dùng là sự thật, không lấy micro-65816 PASS làm RUNTIME PASS.
