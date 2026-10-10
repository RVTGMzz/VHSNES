TIẾP TỤC VIỆT HÓA CHIBI MARUKO-CHAN SNES — CHECKPOINT 038, 2026-10-11
Repo GitHub RVTGMzz/VHSNES, branch chibi-maruko-bootstrap-01

LỆNH NGƯỜI DÙNG: HOÀN THÀNH NỘI DUNG TRÒ CHƠI (STORY, MENU, ĐỒ HỌA, HƯỚNG DẪN, KẾT QUẢ, TITLE) TRƯỚC. FONT 13px/9px và renderer ĐỂ SAU. KHÔNG LẶP LẠI NHỮNG ĐỢT FONT VÔ TẬN.

BẮT BUỘC ĐỌC:
1. games/ChibiMarukoChan-Mezase-Minami-no-Island/HANDOFF_CURRENT.md (038 đầu file).
2. docs/G3_RESULT_AND_GRAPHICS_TEXT_MERGE_CHECKPOINT_038.md (MỚI).
3. docs/G2_RULE_TEXT_ACTUAL_ROM_SOURCE_CHECKPOINT_037.md.
4. docs/G1_MAINMENU_HEADING_ACTUAL_PATCH_CHECKPOINT_036.md, docs/G1_START_PASSWORD_ACTUAL_ROM_PATCH_CHECKPOINT_035.md, docs/G0_ACTUAL_TITLE_ASSET_REPACK_CHECKPOINT_034.md.
5. translation/runtime/content_first_graphics_queue_032.csv, translation/TRANSLATION_PROGRESS.md.

CHỐT TIẾN ĐỘ THẬT:
- ROM Nhật clean local file /mnt/data/Chibi Maruko-chan - Mezase! Minami no Island!! (Japan)(1).sfc SHA256 e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956.
- ĐỒ HỌA G0/G1 đã thực sự được PATCH bytes ROM thử CLEAN JAPANESE: G0 title + dòng Việt hóa bởi Votri Valley, G1 Bắt đầu / Mật khẩu, G1 Chọn gì đây?. Bản thử GRAPHICS036 ROM local /mnt/data/Chibi_G0_G1_Heading036_COMBINED_UNTESTED.sfc SHA256 2c8beee73e985c9a2690cc36ace335f05115c1a3e81b369e09d0cfb132117090, IPS 14.452 bytes trong /mnt/data. THỬ NGHIỆM GRAPHICS-ONLY, SNES EMULATOR CHƯA THỬ.
- Nội dung 1.018 source nghĩa chính +3 G2 demo=1.021 bản ghi đã có; checkpoint032 nhập 220 lượt biên tập thành 216 canonical vi_full cuối; CHƯA chắc các thay đổi 032 nằm trong binary Build035 cũ.
- G2 checkpoint037: 3 câu luật thật sự là direct CP932 ROM gốc 0x1E307,0x1E325,0x1E339; sửa CSV offset 0x1E326 -> 0x1E325 do ký tự ２ hai byte; 35 nhãn minigame khác đã kiểm tra. MỚI sửa bug expected bullet spacing trong tools/audit_g2_rules_direct_sources_037.py để khớp vi_full thực.
- G3 checkpoint038: rà toàn ROM cho 6 cụm exact tiếng Nhật. 勝ち tại 0x1C04F/0x1C25C/0x1D03A chỉ là Story dialogue. 敗けた/コンティニュー/やめる/最終勝利/エンディング chỉ match trong debug/QA descriptor tại 0x2865E..0x287FF. Không phải graphic thắng/thua đang chơi. Tool tools/audit_g3_literal_source_scope_038.py và local JSON Chibi_G3_Result_Literal_Source_Audit_038.json. Vẫn cần trace real G3 rendered callback; KHÔNG VÁ CÁC DESCRIPTOR NỘI BỘ.
- Chặn lớn của dự án: Lịch sử có DIRECT-TEXT Build035 chứa Story/Quiz/Fortune/... SHA256 f8fb662a9e1b8fc5a5ff689f690ceaf332055ed86983e52b476a78852e4fd58d, ROM có thể tên Chibi_Maruko_Build_035_QUIZ01_CREDITS_PASS_READY.sfc. BIN GỐC NÀY KHÔNG CÓ trong /mnt/data, 265 file của GitHub không có bản ROM hoặc bản IPS tương đương, search file Library/conversation cũng không ra. Không được bịa ROM Build035 rồi claim gộp.
- ĐÃ COMMIT tools/merge_graphics036_directtext035_preflight_038.py: yêu cầu 3 exact ROM SHA, xét toàn bộ vùng G0 title/tilemap/G1 sprite, đặc biệt vùng bank86 relocate 0x36907..0x37662, check loader pointers, chỉ build opt-in nếu NO CONFLICT. ĐÃ CHẠY LOCAL mô phỏng 2 edits tiếng Việt không trùng; 13.129 byte thay đổi của graphics036 nằm đúng whitelist, 0 ngoài; 5 trường hợp cố tình phá vùng graphics bị chặn; report /mnt/data/Chibi_038_Graphics_Text_Merge_Simulated_Preflight.json. Tool selftest GitHub tools/selftest_merge_graphics036_directtext035_038.py. Đây là SIMULATED TEXT, KHÔNG PHẢI direct-text Build035. Không có full Vietnamese ROM.
- User không muốn test nhiều patch nhỏ. Chỉ tạo bản test lớn sau khi gộp được thật. Font vẫn để sau.

HÃY LÀM TIẾP — NỘI DUNG THẬT:
1. Nếu tìm được exact DIRECT-TEXT Build035 binary hoặc patch tái lập, chạy 038 preflight với clean+graphic036, ghi JSON fail/pass. Nếu xung đột không được ép phủ IPS; chọn quy trình hợp nhất mới có bảo vệ. Ghi rõ hậu cập nhật vi_full chưa tích hợp.
2. Nếu Build035 vẫn không có, tiếp tục G3 RESULT thực sự: trace đúng game callback/scene -> resource loading -> decoded tile asset, xác nhận chữ Thắng/Thua/Tiếp tục/Kết thúc trong màn, mới vá. Không dùng QA descriptor 0x2865E..0x287FF.
3. Có thể rà thêm content Nhật còn user thấy nhưng chưa có trong source, chỉ tạo bản dịch với nguồn bytes chính xác. Không tạo report vô tận hay microtest font.
4. Cuối phiên update HANDOFF_CURRENT/NEXT_CHAT_PROMPT/translation/TRANSLATION_PROGRESS.md và push GitHub. Nói thẳng số câu sửa/ảnh đã vá, số còn thiếu, chưa emulator real.

Ghi công bắt buộc chính xác: Việt hóa bởi Votri Valley.
