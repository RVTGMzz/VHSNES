TIẾP CHIBI MARUKO-CHAN SNES — CHECKPOINT 083 (2026-10-13)
Repo: https://github.com/RVTGMzz/VHSNES
Branch: chibi-maruko-bootstrap-01
Kiểm tra HEAD trước để tránh bỏ sót checkpoint mới hơn.

ĐỌC NHỮNG FILE MỚI NHẤT:
1. games/ChibiMarukoChan-Mezase-Minami-no-Island/HANDOFF_CURRENT.md (083 nằm ở ĐẦU).
2. docs/CHECKPOINT_083_FORTUNE_OVERFLOW_AND_QUIZ_NAME.md.
3. translation/runtime/quiz_sugiyama_ono_083.json.
4. translation/runtime/fortune_expansion_083.json.
5. tools/build_quiz_sugiyama_ono_083.py; tools/audit_fortune_expansion_083.py.
6. tools/recover_merge_061_81_one_ips_076.py — cumulative 061 +81 Quiz full choices +077/078 +079/080/081/082/083.

VIỆC ĐÃ LÀM THẬT 083:
- Phát hiện tên Sugiyama bị xóa trong câu giải thích giấc mơ Ono ra khơi. Đã sửa chính xác existing stage058 0x32BBE, V2 captions "Ono và bạn / cùng ra khơi" => "Sugiyama và / Ono ra khơi", 11/11 chữ trong 11/13 native cells. Source 058 pinned JSON KHÔNG đổi, code guarded 083 đã thêm cuối full cumulative IPS chain; source CI PASS.
- Bốn Fortune còn chưa in-ROM là vấn đề DÀI HƠN Ô CHỮ không phải chưa dịch: 0x2BD5E "Lời trời mách" 3->13 cells; 0x2C86B "Hẹn tuần sau" 4->12; 0x2CA7D "Vàng" 3->4; 0x2CADD "Trắng" 4->5. JSON manifest 083 và công cụ audit_083 ROM-free xác nhận bốn canonical JP/VI, đủ codepage 160 glyph; CI PASS. Không viết tắt kỳ quặc, KHÔNG patch in-place vì sẽ đè 816F. Công cụ có --original-sfc để quét địa chỉ tham chiếu giả thuyết trên ROM đúng SHA nhưng chưa chạy do KHÔNG có ROM.
- 083 source CI SUCCESS: https://github.com/RVTGMzz/VHSNES/actions/runs/38364216770 — bước Fortune + Quiz 083 cùng PASS.
- Cập nhật docs CHECKPOINT_083, living handoff, next chat, tracker.
- Exact original Japanese ROM SHA256 e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956.
- Không có file ROM/ZIP historical 039–043 trong runtime; KHÔNG xây cumulative IPS/giả lập, KHÔNG phát hành bản chơi thử. Các 81 full answers +3 native extensions mới ở mức candidate.
- Honest count Quiz 279/381 historical source offsets; 083 sửa 1 context, 0 new IDs. Fortune source-display candidates nếu khôi phục đủ sẽ 153/157; 4 expansion còn lại.

ƯU TIÊN TIẾP THEO:
1. Ưu tiên nội dung Việt hóa *thật*. Đưa bốn Fortune thành renderable bằng reverse original native pointers và giới hạn màn hình. Không ép ngắn sai nghĩa.
2. 0x31F33 vẫn thiếu chi tiết Maruko lên 9 tuổi vì 13+13 native cells; không bỏ cung Kim Ngưu/sinh nhật để nhồi "9t".
3. Khi 039–043 archived IPS/ZIP + original clean Japanese SFC thực sự truy cập được, chạy một cumulative guarded patch đến 083, kiểm thử SNES emulator title, Story, Quiz and fortune, results, đúng đáp án.
4. G3 win/loss/result/ending, title credit chính xác "Việt hóa bởi Votri Valley"; hoàn thiện font cuối. KHÔNG bắt user test micro IPS từng cái.

NHỚ USER ĐÃ RẤT MỆT VỚI CÁC CHECKPOINT NHỎ: luôn làm khối lượng meaningful, nói rõ cái gì đã vá thật, cái gì chỉ source review, ghi GitHub trước khi kết thúc phiên.
