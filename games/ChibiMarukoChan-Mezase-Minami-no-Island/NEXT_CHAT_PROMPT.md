TIẾP CHIBI MARUKO-CHAN SNES — CHECKPOINT 084 (2026-10-13)
GitHub: https://github.com/RVTGMzz/VHSNES
Branch: chibi-maruko-bootstrap-01
PHẢI kiểm tra HEAD trước; nếu có checkpoint >084 thì bắt đầu từ MỚI NHẤT.

ĐỌC:
1. games/ChibiMarukoChan-Mezase-Minami-no-Island/HANDOFF_CURRENT.md — Checkpoint 084 ở đầu.
2. docs/CHECKPOINT_084_FOUR_QUIZ_CONTEXT_REPAIRS.md.
3. translation/runtime/quiz_semantic_context_batch_084.json.
4. tools/build_quiz_semantic_context_batch_084.py.
5. tools/recover_merge_061_81_one_ips_076.py (đã nối 084 sau 083).
6. docs/CHECKPOINT_083_FORTUNE_OVERFLOW_AND_QUIZ_NAME.md.

084 ĐÃ THỰC HIỆN THẬT:
- Rà source Nhật + dịch VI gốc, sửa 4 bản ghi giải thích Quiz trong stage054/058 cũ: 0x34CF0 Fujiki gửi "thư xui xẻo"; 0x34D5B Nagasawa "dắt mũi" Fujiki, không mặc định bắt nạt; 0x34E84 Pusadi làm Maruko "xúc động" chứ không chỉ vui; 0x33E7D bố Nagasawa vững vàng sau cháy chứ không "sống tốt".
- Tổng cộng 4 parent, 11 khung chữ gốc (113 glyph cells), SỬA 6 khung caption có dấu Việt, không tăng số nguồn Quiz độc lập.
- JSON manifest 084 + script builder guarded và CI audit. CI source pass: https://github.com/RVTGMzz/VHSNES/actions/runs/38368390692. Chuỗi tạo IPS tổng hợp 076 đã nối thêm 084 sau 083 (080/081/082/083 vẫn giữ nguyên, không ghi đè hash bản cũ).
- GitHub updated docs CHECKPOINT_084, HANDOFF_CURRENT, TRANSLATION_PROGRESS, NEXT_CHAT_PROMPT.
- KHÔNG CÓ original 2MiB Japanese ROM / historical 039–043 ZIP/IPS trong runtime 084. Do đó chưa build IPS V2 tích hợp và chưa chạy giả lập; không tuyên bố release/done.
- Source original SHA256: e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956.
- Quiz historical staged 279/381 nguồn scanner IDs. 81 full answers +3 genuine native explanations chỉ mới candidate; 084 thêm 0 IDs.
- Bốn Fortune đã có bản dịch nhưng không thể nhét ô chữ gốc: 0x2BD5E Lời trời mách (3→13), 0x2C86B Hẹn tuần sau (4→12), 0x2CA7D Vàng (3→4), 0x2CADD Trắng (4→5). Có manifest expansion 083, chưa in ROM.
- 0x31F33 Quiz ngày sinh Maruko còn thiếu ý "lên 9" nếu không mở layout, không ép thành "9t".
- Credit chính xác: Việt hóa bởi Votri Valley. Title/G3 thắng-thua/results/font visual chưa được kiểm thử.

TIẾP THEO CHO 085:
1. LÀM NỘI DUNG CỤ THỂ, KHÔNG CHECKPOINT VỤN: rà 5–10 source Quiz/Fortune narrative nữa đối chiếu Nhật gốc và nội dung hiển thị, sửa có ghi lý do, tuyệt đối không giả tăng %.
2. Nếu có ROM original và IPS 039–043 thật, ưu tiên tái dựng cumulative checkpoint084 IPS + QA/emulator, không phát lẻ từng IPS.
3. Tìm cách mở rộng 4 Fortune + chi tiết Maruko 9 tuổi dựa trên pointer/path render đã chứng minh, không phá 816F hoặc chèn text vào fragment scanner sai.
4. G3 win/lose/title credit vẫn chưa done.
5. FONT THẨM MỸ ĐỂ SAU như user yêu cầu. Dịch tự nhiên, đúng nhân vật, đầy đủ dấu; không ăn gian 'done' chỉ vì source CI pass.

USER đã chán lặp đi lặp lại các checkpoint kỹ thuật. Ưu tiên sửa nội dung thật, thực hiện ngay và ghi GitHub, không gửi các tải IPS thử nghiệm nhỏ.
