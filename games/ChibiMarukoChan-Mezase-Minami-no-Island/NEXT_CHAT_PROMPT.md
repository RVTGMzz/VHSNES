TIẾP TỤC VIỆT HÓA CHIBI MARUKO-CHAN SNES — CHECKPOINT 034 (2026-10-11)
Repo: RVTGMzz/VHSNES
Branch: chibi-maruko-bootstrap-01

LỆNH NGƯỜI DÙNG: VIỆT HÓA HOÀN CHỈNH NỘI DUNG VÀ ĐỒ HỌA TRƯỚC, FONT SAU. ĐÃ YÊU CẦU DỊCH CẢ MÀN TIÊU ĐỀ VÀ GHI CÔNG CHÍNH XÁC `Việt hóa bởi Votri Valley`.

PHẢI ĐỌC:
1. games/ChibiMarukoChan-Mezase-Minami-no-Island/HANDOFF_CURRENT.md (checkpoint 034 ĐẦU FILE)
2. docs/G0_ACTUAL_TITLE_ASSET_REPACK_CHECKPOINT_034.md (CHỨNG CỨ ROM THẬT + PATCH TITLE)
3. docs/CONTENT_FIRST_CANONICAL_MERGE_CHECKPOINT_032.md
4. translation/runtime/content_first_graphics_queue_032.csv
5. docs/G1_STORY_ENTRY_SCREEN_PROOF_008.md (để tiếp G1)

ĐÃ LÀM THẬT SỰ Ở 034:
- ROM gốc user gửi còn nằm trong /mnt/data của phiên trước, tên Chibi Maruko-chan - Mezase! Minami no Island!! (Japan)(1).sfc, SHA e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956.
- TÌM ĐƯỢC CHÍNH XÁC nguồn đồ họa title gốc! Gần 0xFEE, initializer thực thi LDX #$A087 ; JSL $80:E255, resource package $82:A087 file0x12087, có 10 bản ghi resource giải nén codec $80:E8B2. Tilemap logo $9E:9F00 file0xF1F00 2KB ở VRAM word0; gfx 4bpp logo $9E:E456 file0xF6456 8KB ở VRAM word0x2000. OFFLINE RENDER THẬT HIỆN CHỮ NHẬT ちびまる子ちゃん めざせ！南のアイランド！！.
- ĐÃ TẠO ROM THỬ G0 **CÓ THAY PIXEL THẬT**, không chỉ chốt chữ: Chibi Maruko-chan / Tiến tới đảo phương Nam!! / Việt hóa bởi Votri Valley. Mã glyph 4bpp ở title BG, 166 ô riêng.
- Bảo vệ 4 tilemap BG khác (word0x400,0x1000,0x5000,0x5800) byte-identical, 583 tile chữ 4bpp các lớp khác dùng không đổi, OBJ graphics region0xC000..0xFFFF không đổi. Đã REJECT phương án ghi toàn bộ tile bank làm hỏng nhân vật.
- Compression: title gfx0xF6456 4582B <=slot5570; map0xF1F00 506B <=slot545; gfx middle0xF5005 nguyên vẹn; gfx thứ 3 vượt ô gốc: 3420B >2712 nên relocate tới free bank86 $86:E907/file0x36907, update pointer 3 bytes at0x12095 trong package. Tất cả nén/giải nén roundtrip PASS.
- Bản G0-only clean ROM thử UNTESTED SHA 012cdfb87eae1b7c5a9feada4e1c322541e3c91ba45ba0b857e08a2465f47ce0, thay 9317 byte, checksum 20C8/complement DF37. IPS 10,415 bytes/218 records đã test apply lại -> EXACT ROM hash. Artifact local Chibi_G0_TieuDe_VotriValley_Only_UNTESTED.zip (IPS, README, QA, ảnh preview).
- Tái dựng từ chính patched ROM cho hình 256x88 Việt hóa đúng 3 dòng, ảnh Chibi_G0_VI_TITLE_ACTUAL_PATCHED_ROM_RENDER.png (KHÔNG PHẢI emulator screenshot).
- Công cụ đã lưu GitHub: tools/build_g0_first_boot_title_votri_experimental.py & tools/verify_g0_title_034_real_asset_static.py. Checkpoint/docs và HANDOFF_CURRENT đã ghi rõ nguồn asset. KHÔNG UPLOAD ROM hay font.
- QUAN TRỌNG: ROM G0 này dựng từ clean JAPANESE, không có 1.021 source meaning rows đã dịch ở các build khác! KHÔNG ĐƯỢC NÓI game Việt hóa hết, không áp IPS lên Build035 khi chưa kiểm tra xung đột vùng relocate 0x36907 và các resource. BẢN G0 CHƯA ĐƯỢC GIẢ LẬP THẬT NÊN RUNTIME UNTESTED.

ĐÃ LÀM 032:
- Hợp nhất 220 lượt chỉnh sửa editorial ở 216 vị trí độc lập vào translation/source/*.csv thật, 20 file, QA 216/216, giữ nguồn Nhật, không tăng số row. Có 1.018 row thường+3 G2 demo=1.021 đã theo dõi, không phải % hoàn thành game.

VIỆC TIẾP THEO, KHÔNG QUAY LẠI FONT:
1. Phân tích G1 Start/Password/Chọn gì đây? theo execution route đã PROVEN trong docs/G1_STORY_ENTRY_SCREEN_PROOF_008.md, bóc đúng visible asset, tạo patched graphics có nguồn thật tương tự G0.
2. Tiếp G2 rules, G3 results/end, rồi gộp nhiều nội dung thành một bản build test. Đừng bắt user test 4 bản nhỏ.
3. Khi gộp G0 với Build035, xác nhận từng byte ở nguồn resource & vùng relocate; nếu trùng thì chọn chỗ an toàn khác và update pointer/manifest. ROM G0 hiện là standalone.
4. Giả lập thật Snes9x/RetroArch: cần chụp cảnh TITLE FULL (bao gồm nhân vật, copyright, palette, Start), xác minh không bị tràn chữ; đến khi có screenshot PASS mới claim runtime.
5. Font track 025-031 tạm đóng theo lệnh user, không tạo checkpoint font tiếp.

ĐỢT KẾ TIẾP phải đo tiến độ bằng tên asset được chứng minh, số mục dịch/đồ họa đã thực sự ghi ROM, số chưa xử lý, CI/runtime riêng; không báo microtest font như kết quả Việt hóa.
