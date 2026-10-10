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
