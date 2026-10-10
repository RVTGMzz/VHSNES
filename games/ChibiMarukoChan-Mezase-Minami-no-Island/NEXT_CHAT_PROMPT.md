TIẾP TỤC VIỆT HÓA CHIBI MARUKO-CHAN SNES — CHECKPOINT 039 (2026-10-11)
Repo: RVTGMzz/VHSNES, branch chibi-maruko-bootstrap-01

NGƯỜI DÙNG RA LỆNH: HOÀN THÀNH NỘI DUNG/TRUYỆN/MENU/ĐỒ HỌA TRƯỚC, FONT SAU. Tránh lặp vô tận microtests font/65816 và không bắt user test nhiều bản IPS nhỏ.

ĐỌC TRƯỚC:
1. games/ChibiMarukoChan-Mezase-Minami-no-Island/HANDOFF_CURRENT.md (mục 039 đầu file).
2. docs/CONTENT_FIRST_REAL_UI_ROM_CHECKPOINT_039.md (MỚI).
3. docs/G3_RESULT_AND_GRAPHICS_TEXT_MERGE_CHECKPOINT_038.md.
4. docs/G2_RULE_TEXT_ACTUAL_ROM_SOURCE_CHECKPOINT_037.md.
5. docs/G1_MAINMENU_HEADING_ACTUAL_PATCH_CHECKPOINT_036.md.

039 THÀNH QUẢ ROM THẬT, KHÔNG CHỈ CSV:
- Nguồn game Nhật clean /mnt/data/Chibi Maruko-chan - Mezase! Minami no Island!! (Japan)(1).sfc SHA e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956.
- Đã xác minh binary existing V2 FONT ONLY (khôi phục từ 025 thất bại) /mnt/data/Chibi_Probe008_V2_FONT_ONLY_RECOVERED.sfc SHA 2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd.
- Đã xác minh GRAPHICS checkpoint036 /mnt/data/Chibi_G0_G1_Heading036_COMBINED_UNTESTED.sfc SHA 2c8beee73e985c9a2690cc36ace335f05115c1a3e81b369e09d0cfb132117090, chứa ĐÚNG G0 title Chibi Maruko-chan / Tiến tới đảo phương Nam!! / Việt hóa bởi Votri Valley, G1 Story Bắt đầu / Mật khẩu + main mode Chọn gì đây?.
- V2 và graphics036 cùng nguồn clean, SOI TỪNG BYTE: 0 collision ngoài checksum. ĐÃ GỘP THẬT HAI LAYER NÀY VÀ CHÈN THÊM 38 NHÃN TIẾNG VIỆT VÀO ROM MỚI: 10 từ translation/runtime/main_menu_compact_v1.csv + 28 exact-fit từ ui_choices_compact_v1.csv (giao diện chọn thi đấu, độ khó, thời gian, player, quiz). Sử dụng lại codepage 0x84 từ CSV vi_codepage_v4_fe4_native, không CHỈNH FONT; 38 trường gốc và dấu ngắt 816F được giữ chiều dài, ASCII/fullwidth spaces sau chữ không bị đè. Các câu dài còn lại 5 mục vẫn giữ Nhật vì cần field expansion, không dịch tắt khó hiểu.
- OUTPUT ROM local /mnt/data/Chibi_039_Integration_38UI_UNTESTED.sfc SHA **a1f4459942e3a757cc314d12c959168046b4a6dd66018d55b014c70d052e98ce**, checksum 7485/8B7A. IPS sạch /mnt/data/Chibi_039_Integration_38UI_UNTESTED.ips 21130 bytes/674 records. Thử apply IPS ngược từ clean bằng công cụ ĐỘC LẬP khớp đúng ROM output. Diff 17752 byte so clean thuộc các vùng cho phép. 38/38 original Japanese bytes đúng, padding/control giữ nguyên. Local /mnt/data/Chibi_039_Integration_38UI_StaticQA.json và /mnt/data/Chibi_039_Independent_StaticQA.json.
- ĐÃ ĐÓNG GÓI ZIP CHỈ CHỨA IPS, QA, README (KHÔNG chứa ROM hoặc font): /mnt/data/Chibi_039_G0G1_38UI_Content_First_UNTESTED.zip.
- Tool có mã nguồn trên GitHub: tools/build_content_first_g0g1_v2_38_ui_039.py — dùng exact SHA và các CSV runtime/codepage từ repo, fail-closed. Local equivalent đã chạy fixture 38 dòng từ GitHub trên ROM thật; TOOL mới GitHub CHƯA được CI test vì không có checks.
- 38 label trực tiếp KHÔNG ĐỒNG NGHĨA 38 câu Nhật MỚI dịch hôm nay: văn bản đã dịch trong source từ trước, lần này mới CHÈN THẬT VÀO ROM.
- **KHÔNG PHẢI GAME HOÀN CHỈNH, CHƯA RUNTIME TEST**: chưa có full direct-text Story/Quiz/Fortune/Credits. Historical direct-text Build035 SHA f8fb662a9e1b8fc5a5ff689f690ceaf332055ed86983e52b476a78852e4fd58d binary bị thiếu. Cả 216 canonical vi_full edits checkpoint032 chưa được đưa vào ROM. V2 typography từng có user 025 FAIL, không được claim font fixed hay runtime pass. User chưa cần thử 039.

TIẾP THEO — PHẢI LÀM NỘI DUNG THẬT, KHÔNG THỬ FONT:
1. ƯU TIÊN CAO NHẤT: phục dựng một direct-text STORY/QUIZ/FORTUNE/CREDITS BUILD TỪ translation/source/*.csv và runtime constraints (sau checkpoint032) mà không đòi historical Build035. Có thể gom các record CP932 có field exact-fit / relocate an toàn; không đè control hoặc viết tiếng Việt tự tiện tắt. Build lịch sử 035 nếu user gửi thì so khớp SHA và merge với 038 fail-closed.
2. Nối tiếp G2 rules offset 1E325 (037) và xử lý năm nhãn runtime needs_expansion còn Nhật trong 039. Không ép từ viết tắt vô nghĩa.
3. Truy G3 *actual executed result screen callbacks*, không vá source QA descriptors 0x2865E..0x287FF. Đã audit literal G3 ở 038, không có source kết quả đáng tin.
4. Khi hoàn thành nội dung có thể làm, tích hợp thành MỘT build lớn rồi chạy emulator SNES thực, check G0 title/credit, G1, rules, truyện, ending. Trước đó không claim runtime PASS.
5. FONT và glyph spacing sau; user đã phàn nàn nhiều vì 025 font lỗi và sửa vô tận.

MỌI LẦN BÁO KẾT QUẢ: tách (a) CÂU MỚI DỊCH, (b) SỐ CÂU ĐÃ CHÈN THẬT ROM, (c) ASSETS ĐỒ HỌA TRONG ROM, (d) PHẦN CÒN THIẾU / EMULATOR PASS, (e) SHA/commit GitHub.

Nghệ danh ghi công BẮT BUỘC: Việt hóa bởi Votri Valley.
