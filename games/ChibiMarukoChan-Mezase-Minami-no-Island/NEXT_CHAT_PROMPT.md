TIẾP TỤC CHIBI MARUKO-CHAN SNES — CHECKPOINT 036 (2026-10-11)
Repo: RVTGMzz/VHSNES / branch chibi-maruko-bootstrap-01

ƯU TIÊN CỦA USER: HOÀN THÀNH NỘI DUNG GAME TRƯỚC — FONT XỬ LÝ SAU. KHÔNG QUAY LẠI 65816 FONT.

ĐỌC TRƯỚC:
1. games/ChibiMarukoChan-Mezase-Minami-no-Island/HANDOFF_CURRENT.md, section 036 ở đầu.
2. docs/G1_MAINMENU_HEADING_ACTUAL_PATCH_CHECKPOINT_036.md (MỚI NHẤT).
3. docs/G1_START_PASSWORD_ACTUAL_ROM_PATCH_CHECKPOINT_035.md.
4. docs/G0_ACTUAL_TITLE_ASSET_REPACK_CHECKPOINT_034.md.
5. translation/runtime/content_first_graphics_queue_032.csv.

NEW 036 THÀNH QUẢ:
- Đã tìm ĐÚNG nguồn sprite chữ NHẬT “どれにする？” ở main mode menu, KHÔNG phải G1 Story Start/Password. Main-mode initializer ROM 0x20047 = LDX #$A213 ; JSL $80:E255. Script package $82:A213 ở ROM 0x12213, record6 ở 0x12233 = 00 70 6F F0 98, upload VRAM word 0x7000 từ CPU $98:F06F -> file0xC706F.
- Source 3485B nén -> 8192B=256 tile 4bpp 8×8. Tile0..191 chứa chữ Nhật menu khác và mũi tên; tile192..255 chứa heading 2 dòng. Hình thật đã giải mã Chibi_G1_MainMode_AllSpriteTiles_036.png.
- ĐÃ GHI THẬT VÀO ROM THỬ: “Chọn gì” / “đây?” (nghĩa Chọn gì đây?) trong tile192..255, giữ nguyên CHÍNH XÁC tile0..191 (6144B). Bỏ bản shadow quá đậm, dùng font 14px clean. Nén mới 2428B < 3485B, ghi lại ĐÚNG vị trí gốc, không đổi pointer.
- Source sprite $98:F06F được 13 type-0 package cùng load ở VRAM 0x7000. Đã kiểm tra đầy đủ 13 pointer; chưa biết có màn khác hiển thị chính vùng heading không nên BẮT BUỘC smoke test trong emulator.
- Combined graphics checkpoint036 ROM từ CLEAN Japanese gốc (không phải direct-text Build035) SHA256 2c8beee73e985c9a2690cc36ace335f05115c1a3e81b369e09d0cfb132117090; checksum/complement 3A35/C5CA. G0 title và Votri Valley credit + G1 Story Bắt đầu/Mật khẩu giữ nguyên. IPS kích thước 14452B / 263 record, replay onto CLEAN chính xác hash. Local zip Chibi_G0_G1_ChonGiDay_036_UNTESTED.zip gồm IPS/README/preview/2xQA JSON.
- GitHub tools mới: tools/build_g1_mode_heading_vietnamese_036.py, tools/verify_g1_mode_heading_036_independent.py. Doc checkpoint036. Queue G1 heading đổi sang EXPERIMENTAL_PATCH_STATIC_RECONSTRUCTED.
- RẤT QUAN TRỌNG: GRAPHICS 036 KHÔNG BAO GỒM Story/Quiz/Fortune tiếng Việt ở historical Build035/direct text. Checkpoint 032 hợp nhất 216 câu vi_full QA PASS nhưng chưa runtime. Không coi đã hoàn thiện game. Không có emulator runtime QA (không claim PASS).
- Không upload ROM hay font lên GitHub.

HÃY LÀM TIẾP:
1. CHUYỂN TỚI G2 VS / RULE PANEL, rồi G3 THẮNG/THUA/KẾT THÚC. Xem docs/G2_G3_GRAPHICS_REVERSE_PIPELINE_005.md, tools/trace_g2_school_front_resources.py và tools/run_g2_g3_graphics_reverse_pipeline.py. Phải tìm nguồn graphics thật: màn/game code -> package -> nén -> giải hình -> sửa đúng asset; KHÔNG vá debug descriptor 0x286B4..0x287FC.
2. Sau khi đồ họa G2/G3 tiến triển, đối chiếu EXACT file bytes của historical direct-text Build035 với graphics036: nhất là reloc bank86 0x36907 và font/codepage. GỘP AN TOÀN sang một ROM test có nội dung tiếng Việt thật. KHÔNG áp IPS trên bản Build035 nếu chưa kiểm tra xung đột.
3. Khi có bản lớn, chạy SNES emulator game để xác minh từ G0 tới G3 và 13 menu dùng chung asset; đừng bắt user test nhiều bản bé.
4. ĐỂ FONT SAU đúng lời user; đo tiến độ bằng chuỗi/đồ họa vá thật, không microtests renderer.

OLD NEXT PROMPT 035 archival below:
---
TIẾP TỤC VIỆT HÓA CHIBI MARUKO-CHAN SNES — CHECKPOINT 035 (2026-10-11)
Repo: RVTGMzz/VHSNES, branch chibi-maruko-bootstrap-01

YÊU CẦU ƯU TIÊN: HOÀN THÀNH NỘI DUNG/TEXT/GRAPHICS TRƯỚC, FONT LO SAU. Không quay về font 65816 025-031.

ĐỌC:
1. games/ChibiMarukoChan-Mezase-Minami-no-Island/HANDOFF_CURRENT.md (checkpoint 035 trên cùng)
2. docs/G1_START_PASSWORD_ACTUAL_ROM_PATCH_CHECKPOINT_035.md (G1 MỚI)
3. docs/G0_ACTUAL_TITLE_ASSET_REPACK_CHECKPOINT_034.md (G0 title)
4. translation/runtime/content_first_graphics_queue_032.csv
5. docs/G1_STORY_ENTRY_SCREEN_PROOF_008.md + tools/extract_g1_story_select_assets.py

THÀNH QUẢ THẬT:
- G0 checkpoint034 đã tìm được gói tài nguyên retail title $82:A087 ở file0x12087, logo+font đồ họa từ file0xF6456 và tilemap0xF1F00, đã vá 3 dòng Chibi Maruko-chan / Tiến tới đảo phương Nam!! / Việt hóa bởi Votri Valley. G0 title-only ROM SHA 012cdfb87eae1b7c5a9feada4e1c322541e3c91ba45ba0b857e08a2465f47ce0, nguồn CLEAN Japanese.
- G1 checkpoint035 (MỚI): G1 Story initializer $85:E97F gọi package $82:AF23; record8 ở file 0x12F4D ghi dest word0x7800, source $97:F95E = file0xBF95E. Giải nén thật 436B -> 992B, 31 tile 4bpp 8×8, bitmap gốc cho thấy hai nhãn はじめから / パスワード và icon.
- ĐÃ VÁ PIXEL TIẾNG VIỆT TRONG ROM THẬT (thử nghiệm): Bắt đầu / Mật khẩu vào tile 0..14 và16..28, giữ nguyên tile trống15 và tile icon29,30. Nén lại 331B < vùng436B, KHÔNG DỜI nguồn hay sửa pointer, giữ mã/tài nguyên khác. G1-only clean ROM SHA 9a7bddb9afb7062a63c775e647c9ee04c226202bd16d23a7d5aadf091ea1bdaf (434 bytes diff including checksum).
- GỘP AN TOÀN G0+G1 (chỉ graphics) từ ROM CLEAN Japanese: 0 byte overlap ngoài checksum, giữ nguyên relocation bank86 0x36907. Combined SHA 77a207589857d2886059057151eaf3d47530032b726744fe739e991ff81a5b80, checksum 470A/B8F5. IPS 10880 bytes/225 records, apply lại onto clean ROM -> SHA trùng. Local Chibi_G0_G1_Title_Start_Password_035_UNTESTED.zip (IPS/README/QA), có ROM local để kiểm tra nhưng TUYỆT ĐỐI KHÔNG PUSH ROM LÊN GITHUB.
- GitHub tools/build_g1_start_password_vietnamese_035.py (builder Pillow + dùng codec G0), tools/verify_g0_g1_graphics_035_independent.py (ROM/IPS real source QA), docs checkpoint035. Queue G1 Start/Password đã update là có ROM experiment; HÀNG G1 どれにする？ / Chọn gì đây? VẪN CHƯA VÁ.
- Giữ nguyên giới hạn: 8px sprite text tiếng Việt nhỏ, SNES emulator/runtime CHƯA CHẠY, kết quả mới chỉ STATIC PASS. ROM G0+G1 chưa có Story/Quiz/Fortune Việt hóa; KHÔNG tuyên bố done full game.

TRƯỚC ĐÓ CHECKPOINT032:
- Đã hợp nhất 220 editorial revision events thành 216 source offsets trong translation/source/*.csv thật, 20 CSV, QA 216/216; 1.018 records regular+3 G2 demo=1.021 records theo dõi KHÔNG đồng nghĩa dịch xong toàn bộ game.

LÀM TIẾP CỤ THỂ:
1. Thử truy nguồn asset của pink heading G1/ main mode `どれにする？` (có thể khác hẳn package G1 Story options). Nếu quá khó, dịch trực tiếp G2 rules và G3 result/ending graphic assets theo pipeline đã có; đừng sa lầy font.
2. Có thể xây bản test G0+G1+G2+G3 cùng text sau khi safe-integrate với Build035: cần so từng vùng clean ROM và Build035, đặc biệt G0 relocation 0x36907. KHÔNG đè IPS sạch lên Build035 bừa.
3. Đảm bảo runtime QA qua emulator chỉ sau khi có bản test lớn, user không muốn test lắt nhắt. Không upload ROM thương mại, chỉ patch, source và báo cáo.
4. Thống kê số mục có PATCH vào ROM thật khác với số câu dịch trong CSV; font sau.

Mốc 035 GitHub đã push. Không đổi lại chữ ghi công `Việt hóa bởi Votri Valley`.
