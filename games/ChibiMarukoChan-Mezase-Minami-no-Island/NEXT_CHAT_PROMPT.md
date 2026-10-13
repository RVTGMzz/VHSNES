TIẾP VIỆT HÓA CHIBI MARUKO-CHAN SNES — CHECKPOINT 085 (2026-10-13)
Repo: https://github.com/RVTGMzz/VHSNES
Branch: chibi-maruko-bootstrap-01
TRƯỚC KHI TIẾP: kiểm tra HEAD mới nhất; nếu checkpoint lớn hơn 085 thì đọc mới nhất.

TÀI LIỆU:
1. games/ChibiMarukoChan-Mezase-Minami-no-Island/HANDOFF_CURRENT.md (085 đầu tiên).
2. docs/CHECKPOINT_085_SEVEN_QUIZ_FACTS_AND_NAMES.md
3. translation/runtime/quiz_seven_fact_restore_085.json
4. tools/build_quiz_seven_fact_restore_085.py
5. tools/recover_merge_061_81_one_ips_076.py (cumulative 061 font + 81 choices + 077/078 + 079..085).
6. docs/CHECKPOINT_084_FOUR_QUIZ_CONTEXT_REPAIRS.md

085 ĐÃ LÀM THẬT / CI:
- Đối chiếu stage054/058/059 với bản Nhật gốc và canonical bản Việt; sửa 7 PARENT Quiz hiện đã có trong staged ROM: 0x32095 thêm burger bên cạnh kem; 0x32303 khôi phục ông Tomozou thân Maruko và haiku; 0x3259A bà Maruko lời Việt tự nhiên; 0x31FA6 nhấn đây là buổi SINH NHẬT Maruko; 0x3394B tên đầy đủ Sugiura Tokuzo; 0x33C6C Tomita Tomiko; 0x350AD sô-cô-la Fuyuta tặng Ono, không phải kẹo nói chung.
- 20 ô/vùng khung chữ gốc / 234 glyph cells, 14 dòng sửa; KHÔNG TĂNG số nguồn Quiz độc lập.
- File JSON audit + Python audit/build guard, stage 085 đã được nối sau 084 vào ONE-IPS recover_merge_061_81_one_ips_076.py. Source 054/058/059 trước đó và font V2 giữ nguyên.
- Lúc đầu CI 085 thất bại do tên key clean_sha256 vs clean_original_sha256 trong script và thiếu cờ immutable source; FIXED. CI PASS cuối: https://github.com/RVTGMzz/VHSNES/actions/runs/38372615081 ; graphics CI PASS: https://github.com/RVTGMzz/VHSNES/actions/runs/38372615093.
- ROM gốc user-owned SHA256 e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956 và checkpoint historic 039–043 ZIP/IPS KHÔNG HIỆN DIỆN trong phiên này. Không có IPA/IPS integrated mới, chưa chạy trình SNES; script ROM-dependent chỉ có guarded logic, chưa thể nói ROM QA.
- Mốc Quiz stage history 279/381 original scanner IDs, cộng 81 full answer candidates +3 native nonanswer candidates còn chờ thực nghiệm. Các sửa 085 cải thiện NGHĨA câu, không tăng source count.
- Bốn Fortune quá dài chưa vá được: 0x2BD5E Lời trời mách (3->13), 0x2C86B Hẹn tuần sau (4->12), 0x2CA7D Vàng (3->4), 0x2CADD Trắng (4->5) — cần nới script/render bằng cơ sở ROM, KHÔNG cắt nghĩa bừa.
- Chú ý 085 đã hồi phục nội dung SINH NHẬT ở 0x31FA6, KHÔNG đồng nghĩa đã khôi phục ý Maruko LÊN 9 TUỔI tại 0x31F33 (vẫn kẹt 13+13 glyph frames cần mở rộng nếu muốn giữ cung Kim Ngưu + câu hỏi sinh nhật).
- Credit tiêu đề chính xác "Việt hóa bởi Votri Valley"; G3 win/lose/results/ending pending test.

TÁC VỤ 086: tập trung hoàn thiện nội dung thực tế, ưu tiên các lỗi Nhật -> Việt có thể cải thiện trong native slots; hoặc nếu có ROM exact 2MiB và historical IPS thì ưu tiên dựng 1 patch hoàn chỉnh kiểm thử emulator. Có thể kiểm lại các câu Quiz xưng hô, QA named characters, các Fortune bị nén quá mức, actual text UI. Không gửi micro-IPS. User ưu tiên HOÀN TẤT NỘI DUNG trước, style font sau. KHÔNG nói 'đã vá thật ROM' khi chỉ code source + CI.
