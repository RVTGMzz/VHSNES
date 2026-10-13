TIẾP CHIBI MARUKO-CHAN SNES — CHECKPOINT 082 (2026-10-13)
GitHub: RVTGMzz/VHSNES, nhánh chibi-maruko-bootstrap-01

CẦN ĐỌC:
1. games/ChibiMarukoChan-Mezase-Minami-no-Island/HANDOFF_CURRENT.md — MỤC 082 MỚI NHẤT Ở ĐẦU.
2. docs/CHECKPOINT_082_SUMIRE_SISTER_FACTS.md.
3. docs/CHECKPOINT_081_QUIZ_STORY_CONTINUITY.md.
4. translation/runtime/quiz_parent_semantic_restore_082.json.
5. tools/build_quiz_parent_semantic_restore_082.py.
6. tools/recover_merge_061_81_one_ips_076.py.

YÊU CẦU CỦA NGƯỜI DÙNG:
- VIỆT HÓA NỘI DUNG THẬT, ĐỪNG TĂNG % ẢO, ĐỪNG CHỈ CHẠY TOOL/QUAY VỀ SỬA FONT MÃI.
- Ưu tiên các đoạn thoại, câu hỏi/đáp án, Fortune, giao diện và title credit.
- Không phát bản IPS lẻ thử nghiệm liên tục. Hạn chế yêu cầu người dùng test nhiều bản vụn.
- Font thẩm mỹ xử lý SAU, nhưng không được phá đường đi font V2 đã có.
- Giọng Maruko dễ thương, tự nhiên, đúng nguồn Nhật; không dùng viết tắt kỳ quặc.
- Dòng credit đúng y: Việt hóa bởi Votri Valley.

CHECKPOINT 082 ĐÃ THỰC HIỆN VÀ PUSH GITHUB:
- Sửa thêm 2 native Quiz explanation parent sẵn stage058, không gian lận là 2 new source IDs.
- 0x328E5: từ 'Mẹ luôn thương / Maruko / rất nhiều' trùng bản trước, thành 'Mẹ cũng ngăn / Maruko / quậy phá' cho sát gốc 'まる子のバカげたこうどうをおさえる'.
- 0x32A38: từ 'Maruko quậy / chị phát mệt / chị học lớp 6' thành 'Maru phá chị. / Chị lớp 6 / mê gratin.' giữ chuyện bị em quậy, lớp 6 và món gratin gốc Nhật.
- 5/6 glyph captions thay đổi trong hai bản ghi, physical capacities 14/8/9 + 13/12/14. 160 V2 glyphs đủ, không đổi source JP/control.
- Thêm JSON manifest 082 và builder fail-closed 082; CI chạy --audit-only thành công: https://github.com/RVTGMzz/VHSNES/actions/runs/38362299037 (step 18 SUCCESS) trước khi ghi tài liệu.
- tools/recover_merge_061_81_one_ips_076.py giờ có post081 -> 082 trong single original-ROM cumulative IPS chain, và checksum report lấy từ 082 cuối thay vì từ stage075 cũ.
- docs/CHECKPOINT_082_SUMIRE_SISTER_FACTS.md giải thích đầy đủ và rà lại 9 scanner alias.
- SỐ ĐÚNG: 279/381 historical staged Quiz source scanner IDs; 81 full-answer +3 genuine non-answer source-byte-only prototypes; 082 0 new IDs. Còn 9 scanner aliases được rà 8 fact đã có, 1 thiếu Maruko lên 9: 0x31F33.
- Full Japanese retail original 2,097,152 bytes SHA256 e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956.
- 039–043 historical raw ZIP/IPS (build baseline) và clean original ROM bytes KHÔNG CÓ TRONG container 082. Không thể build V2 cumulative real IPS hay emulator test; ĐỪNG NÓI ĐÃ CHƠI ĐƯỢC.

VIỆC KẾ TIẾP THỰC SỰ HỮU ÍCH:
1. Rà nguồn Nhật đối chiếu tiếp các parent Quiz *chưa* audit đầy đủ và 4 Fortune overlong, tạo patch ứng viên thật có kiểm soát.
2. Điều tra phép reflow an toàn của 0x31F33 để đủ cung Kim Ngưu, sinh nhật, lên 9, tránh viết '9t' máy móc.
3. G3 win/loss/result/ending graphics + title credit; font thẩm mỹ cuối.
4. Khi user-owned 039–043 ZIP/IPS thật khả dụng, chạy single guarded recovery builder 076 ghép tất cả đến 082 và SNES emulator QA cả story/gameplay; không ép user thử chồng IPS.

NHỚ: Trước khi làm phải check HEAD branch thực tế. Nếu đã có checkpoint >082 thì tiếp từ MỚI NHẤT. LƯU GITHUB sau mỗi phiên.
