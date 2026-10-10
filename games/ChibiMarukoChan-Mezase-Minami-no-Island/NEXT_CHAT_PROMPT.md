TIẾP TỤC VIỆT HÓA CHIBI MARUKO-CHAN SNES — CHECKPOINT 037 (2026-10-11)
Repo: RVTGMzz/VHSNES, branch chibi-maruko-bootstrap-01.

**USER ĐÃ RA LỆNH: HOÀN THÀNH NỘI DUNG/TEXT/ĐỒ HỌA TRƯỚC, FONT SAU. KHÔNG SA LẦY FONT 65816.**
 
ĐỌC THEO THỨ TỰ:
1. games/ChibiMarukoChan-Mezase-Minami-no-Island/HANDOFF_CURRENT.md (037 đầu file).
2. docs/G2_RULE_TEXT_ACTUAL_ROM_SOURCE_CHECKPOINT_037.md.
3. docs/G1_MAINMENU_HEADING_ACTUAL_PATCH_CHECKPOINT_036.md.
4. docs/G1_START_PASSWORD_ACTUAL_ROM_PATCH_CHECKPOINT_035.md.
5. docs/G0_ACTUAL_TITLE_ASSET_REPACK_CHECKPOINT_034.md.
6. translation/runtime/content_first_graphics_queue_032.csv.

NEW 037 — DỮ LIỆU G2 THẬT, KHÔNG CHỈ REPORT FONT:
- Exact clean game ROM ở /mnt/data/Chibi Maruko-chan - Mezase! Minami no Island!! (Japan)(1).sfc SHA256 e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956.
- Phát hiện ba dòng Nhật trên bảng luật G2 có nguồn CP932 DIRECT TEXT thật trong ROM bank83, KHÔNG PHẢI sprite source chưa rõ: ルールをせつめいするよ ở file 0x1E307, ２本先取だよ ở 0x1E325, ゲームの時間は勝つまでだよ ở 0x1E339. Control 816F giữ ở cả ba dòng, bullet 8145 ở 0x1E323 và 0x1E337.
- ĐÃ SỬA source CSV THẬT ở GitHub translation/source/rules_tutorial_vi.csv: trước ghi offset 0x1E326 = byte thứ hai của số ２ CP932 82 51; nay sửa 0x1E325. vi_full chỉnh rõ ý “Ai thắng 2 ván trước sẽ thắng / Chơi đến khi phân thắng bại”, giữ cấu trúc bullet semantically. 1 sửa offset, 1 sửa lời văn, không tăng nguồn row.
- Audit trực tiếp 35 nhãn VS/minigame UI offset ROM 0x288C2..0x28BFF, tất cả có nguồn CP932 xác thực và vi_full trong canonical minigame_ui_batch01_vi.csv. Ba câu rule 0x288C2/0x28958/0x28A1E có 2 space trước Nhật, HỢP LỆ. Tool mới tools/audit_g2_rules_direct_sources_037.py; local report /mnt/data/Chibi_G2_CP932_Source_Audit_037.json PASS. Thử phục hồi lỗi 0x1E326 và checker FAIL đúng.
- Queue các dòng G2 rule được sửa từ UNRESOLVED GRAPHICS sang DIRECT_CP932_TEXT_SOURCE_FOUND. CHƯA CHỨNG MINH RUNTIME CALLSITE VÀ CHƯA CHÈN VÀO GRAPHICS-ONLY ROM. Đừng claim đã hiển thị Vietnamese ở G2.
- Đã giải mã/nhìn 42 tài nguyên gần G2 (chibi_g2_candidate_sprite_sheet_1.png, Chibi_G2_VS_Resource_Focused_037.png) và 52 nguồn/dest Sprite VRAM0x6000/0x7000 thuộc package đã biết để tìm G3 (Chibi_G3_Result_Sprite_Atlas_037_1..3.png). CHƯA xác minh file nào chắc chắn là hình Thắng/Thua/Continue trong game, KHÔNG ĐƯỢC VÁ MÒ.
- 0x286EA 今からやるよ nằm trong debug/internal descriptor, không vá.
- KHÔNG CÓ ROM PATCH MỚI 037, vì chỉ làm source integrity & phân loại asset. Original graphics-only checkpoint036 ROM SHA 2c8beee73e985c9a2690cc36ace335f05115c1a3e81b369e09d0cfb132117090, IPS 14452B, SNES runtime UNTESTED; KHÔNG có Story/Quiz/Fortune tiếng Việt.

LỊCH SỬ:
- 036: G0 startup logo + line “Việt hóa bởi Votri Valley”, G1 story Start/Password, G1 main mode “Chọn gì đây?” đã vá PIXEL thật vào ROM G0/G1-only thử; static pass.
- 032: nhập 220 lượt chỉnh sửa trên 216 vị trí source tại 20 CSV (216/216 verified), 1.018 ordinary rows+3 G2 demo=1.021 historical known rows; KHÔNG phải game dịch hết.
- Historical direct-text Build035 SHA256 f8fb662a9e1b8fc5a5ff689f690ceaf332055ed86983e52b476a78852e4fd58d (ROM binary không có local session này); KHÔNG áp IPS đồ họa 036 lên Build035 nếu chưa kiểm tra xung đột.

ƯU TIÊN TIẾP:
1. Lần đúng đường vẽ MÀN KẾT QUẢ G3 (WIN/LOSE/CONTINUE) từ callback/control flow -> source graphics/text -> source exact file; mới vá có bằng chứng. Có atlas sprite37 để lọc candidate.
2. Kiểm tra source/render route G2 rule sau khi biết là direct CP932, rồi tích hợp bản dịch hoàn chỉnh trong direct-text build; không vá hình sai.
3. Tìm build direct-text 035 hợp lệ, nếu có kiểm xung đột nguồn ROM exact G0+G1 (đặc biệt bank86 0x36907), hợp nhất vào một bản thử lớn. Không bắt người dùng test nhiều bản nhỏ.
4. FONT ĐỂ SAU. SNES emulator vẫn chưa chạy được trong container, không nói runtime PASS.
