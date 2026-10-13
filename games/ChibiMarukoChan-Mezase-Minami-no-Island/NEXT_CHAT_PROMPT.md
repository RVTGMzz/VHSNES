TIẾP VIỆT HÓA CHIBI MARUKO-CHAN SNES — CHECKPOINT 086 (2026-10-13)
GitHub https://github.com/RVTGMzz/VHSNES
Branch chibi-maruko-bootstrap-01
ĐỌC HEAD mới nhất trước khi làm, nếu >086 thì đọc bản mới nhất.

FILES TO READ:
1. games/ChibiMarukoChan-Mezase-Minami-no-Island/HANDOFF_CURRENT.md — checkpoint 086 nằm đầu.
2. docs/CHECKPOINT_086_SEVEN_QUIZ_STAGE057_CONTEXT_REPAIRS.md.
3. translation/runtime/quiz_context_semantics_086.json.
4. tools/build_quiz_context_semantics_086.py.
5. tools/recover_merge_061_81_one_ips_076.py (cumulative V2 061+81 choices+077+078+079→086).
6. docs/CHECKPOINT_085_SEVEN_QUIZ_FACTS_AND_NAMES.md.

086 WORK COMPLETED / SOURCE QA:
- Đã đối chiếu JP gốc từ source CSV batch02 part2/part3, 7 Quiz *đã* dịch ở stage057 nhưng bị cắt ý/nhầm nghĩa.
- 0x35AC3: "Tin thật / nên đành / nói thật" sai: JP thấy Yamada tin Maru và cảm động, rồi câu sau 0x35B16 mới biến lời nói dối thành sự thật. Sửa "Yamada / tin Maru / thật lòng" (vẫn cắt mất nét cảm động do 9x3 ô).
- 0x35B94: "Người đó là?" cụt -> "Ca sĩ tên / gì?".
- 0x35C63: "Quý người / già và / khiêm tốn": thêm khiêm tốn có ở bản JP.
- 0x35EDE: "Em tên gì? / nào" cụt -> "Em gái tên / gì?".
- 0x35F38: "Nagayama rành / cây cỏ, sâu bọ / Hanawa cũng nể": khôi phục JP Hanawa nể kiến thức sâu bọ/thế giới tự nhiên; câu tiếp 0x35FA9 vẫn có Koharu.
- 0x360FA: "Bọn quậy phá / bắt nạt bạn / Ono, Sugi cứu": rõ vai cứu bạn, không phải cặp Ono/Sugiyama bị đánh hoặc bắt nạt bạn.
- 0x36661: "Chị Maruko / đọc manga / nào?": câu hỏi hỏi về manga, không phải bất kỳ thứ gì.
- TOTAL: 7 old native Quiz parents, 19 original 2-byte glyph frames / 191 glyph cells, 16 changed Vietnamese caption frames, 0 new Quiz scanner source IDs. Stage057 historical pinned manifest không bị sửa, codepage/font V2 không bị đổi.
- Source-only CI PASS explicit 086 + previous 084/085: https://github.com/RVTGMzz/VHSNES/actions/runs/38377484960; new JSON 086, guarded Python 086 builder/audit; one cumulative IPS tool now appends 086 after 085. NO actual ROM or emulator test; absence of user-owned exact 2MiB original Japanese SFC and historical 039–043 IPS/ZIP means no actual IPS generated.
- ROM clean original SHA256 e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956.

STILL IMPORTANT:
- Historic Quiz staging 279/381 distinct source scanner IDs, plus 81 full-answer and 3 nonanswer static-only prototypes still need original ROM + emulator acceptance. Seven 086 corrections improve old translation quality, NOT raise total coverage.
- Four Fortune translations too long for original fields: 0x2BD5E Lời trời mách (3→13), 0x2C86B Hẹn tuần sau (4→12), 0x2CA7D Vàng (3→4), 0x2CADD Trắng (4→5). 083 has manifest/audit but no safe native relocation/render width proof.
- Quiz 0x31F33 age Maruko lên 9 còn thiếu do 13+13 native fields “Cung Kim Ngưu / Sinh hôm nào?”. Đã nghĩ nhiều cách viết ngắn trong 086 nhưng sẽ cụt/cứng khó hiểu nên chưa dám sửa.
- G3 win/loss/result/ending; title credit chính xác “Việt hóa bởi Votri Valley”; font visual QA and complete game run still outstanding. User wants finish actual CONTENT first; don't return to font over-polishing.

087 NEXT:
1. Đọc canonical Japanese + Vietnamese để chỉnh thêm một nhóm lớn lỗi thật; tránh lặp lại câu đã sửa 079–086.
2. Nếu có exact clean SFC+user archival IPS: ưu tiên build một original-ROM-relative cumulative 086 IPS, kiểm emulator, tránh giao riêng từng micro-patch.
3. Reverse 4 Fortune overflow, 0x31F33 age9 only with actual verified script/runtime display expansion; không viết tắt gượng.
4. QA title credit, outcomes, remaining G3 and gameplay only with correct emulator source.
5. Always write real GitHub changes and explain plainly static vs actual translated ROM state.

ATTN: user's many “tiếp” messages express fatigue at dozens of small checkpoint iterations. Prioritize meaningful content groups, robust QA; do NOT claim source CI = playable localization completion.
