TIẾP CHIBI MARUKO-CHAN SNES VIỆT HÓA — CHECKPOINT 047 (2026-10-11)
Repo: RVTGMzz/VHSNES / branch: chibi-maruko-bootstrap-01

ƯU TIÊN USER: GAME SNES QUÁ LÂU, PHẢI LÀM NHIỀU NỘI DUNG THẬT, KHÔNG micro-checkpoints. KHÔNG gửi IPS/ZIP thử nghiệm lẻ trừ khi user yêu cầu; không bắt user tải/test bản chưa hoàn thiện. FONT ĐỂ SAU KHI NỘI DUNG ĐỦ. Xưng hô/ngữ cảnh Story phải tự nhiên.

ĐỌC NGAY:
1. games/ChibiMarukoChan-Mezase-Minami-no-Island/HANDOFF_CURRENT.md (047 trên cùng).
2. docs/CONTENT_FIRST_STORY_ALIGN_AND_QUIZ_FORTUNE_CHECKPOINT_047.md.
3. translation/runtime/story_special_cp932_alignment_046.json / tools/build_content_first_046_story_special.py.
4. translation/runtime/quiz_fortune_exactfit_047.json / tools/build_content_first_047_quiz_fortune_30.py.
5. docs/CONTENT_FIRST_STORY_BATCH02_03_CHECKPOINT_045.md.

ĐÃ LÀM 046/047 — ROM THẬT, KHÔNG CHỈ CSV:
- ROM Nhật gốc 2MiB không header SHA e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956; /mnt/data/Chibi Maruko-chan - Mezase! Minami no Island!! (Japan)(1).sfc.
- Source Story 7 CSV có 336 row. 045 báo 313, 23 thiếu. Điều tra phát hiện 8 scanner offset sai CP932: P/Q/R/O thật ra byte SAU của số fullwidth １/２/３/０ (82 50/51/52/4F), KHÔNG PHẢI BIẾN GAME. 4 alias đã có trong record đã vá 043/044, 4 alias được giải quyết bằng bản vá real parent mới 046. 3 tutorial đầu 181CC/18245/182BE đã Việt hóa từ cũ.
- Đã VÁ THẬT 15 original PHYSICAL Story records 046 (số record độc lập, không tính 8 scanner aliases), giữ nguyên mọi prefix xxf3 (E6F3/88F3/FAF3/92F3) đáng ngờ, không vá sai byte, giữ 30 marker 816F/81A5, 31 physical source segments, không thay mã script/các đoạn trước. Local /mnt/data/chibi046_local.sfc, /mnt/data/chibi046_local.ips.
- ROM046 SHA c10c0f444a97d6bea7f8f669d67bb6c0c5b6889b654d99d6e6dfa25e3d061624; clean-based IPS046 SHA 11abac1b8e0f48e6580822bcdcd3b1b3568ae08676020b86c819ae641f53367d, 44450 bytes,1599 records. Checksum F71E / complement 08E1. Diff 620 byte positions chỉ vùng cho phép+checksum.
- LIVE GH SET AUDIT đếm 7 Story CSV 126+42+42+42+42+21+21=336, so với manifests 042(26)+043(58)+044(87)+045(139)=310, +15 physical newly patched,+8 scanner alias,+3 tutorial =336/336 SOURCE ROW MAPPED, zero unknown. Có 328 distinct actual physical Story fields in ROM. **Không phải gameplay test hoặc bằng chứng toàn bộ chữ visible đã xong.**
- Sau Story 046, thêm THẬT 30 nhãn trực tiếp khác trong ROM047: 15 Quiz đáp án tuổi/sinh nhật/lớp/giá tiền, 15 Fortune con số/mức tiền/mẹo 'Gọi thử!', 'Văn hên!'. Không đổi vi_full, không rút gọn tên nhân vật.
- Final ROM047 SHA 1f6430064b70671a4f3ba94f0fd256764db54690950519c22d9e03ec74230dd9; CLEAN JP IPS047 SHA 725ca433dfeb919bd19bde6903a1e2e7d95cde1889980677863724007090cd6c, 44980 bytes/1671 IPS records, checksum EB53/14AC, replay độc lập từ original clean PASS.
- Tổng direct physical source 450 =328 Story + 38 UI +36 Quiz +48 Fortune, + separate graphic G0/G1 title/credit 'Việt hóa bởi Votri Valley', Chọn gì đây/Bắt đầu/Mật khẩu. **Không phải toàn game xong.**
- Source Quiz có 381 rows, Fortune có 157 (chiếm nhiều phần chưa chèn). G2 3 câu luật source CP932 at 1E307/1E325/1E339 cần chèn/wrap; G3 actual Win/Lose source chưa truy thật. Font V2 bị user phản ánh xấu, LÀM SAU khi nội dung hoàn chỉnh. SNES EMULATOR CHƯA CHẠY.
- Local 046 report /mnt/data/chibi046_story_static.json và 047 report /mnt/data/chibi047_static_qa.json. GH đã có manifests, 046/047 reproducible builder, checkpoint document, HANDOFF/PROGRESS. Chưa chạy CI GH, chỉ local binary & independent IPS parser.
- User KHÔNG muốn IPS/ZIP download lẻ, đừng gửi link sandbox. KHÔNG upload ROM thương mại hoặc font files.

HƯỚNG NEXT (LÀM NHIỀU THẬT):
1. Chèn Quiz và Fortune theo nguồn hiện có, PHẢI nghiên cứu safe pointer relocation/wrapping để dịch được full Vietnamese dài, không làm thoại cộc lốc hoặc cắt tên nhân vật. Các exact fit có thể gom 20–50+ mục/ngày thay vì microbuild. Đối chiếu CP932 Nhật, mã 816F/delimiter, codepage đúng.
2. G2 thực thi luật chơi còn Nhật: 1E307,1E325,1E339; hiểu 2-byte fullwidth bullet, field budget trước khi vá. Không được dịch 2 ván thành chỉ 2 chữ vô nghĩa.
3. G3 Win/Lose/Continue: trace actual executed scene asset, không dùng debug descriptor 0x2865E..0x287FF.
4. Khi đủ content, chạy thật SNES emulator QA nội dung/visual/font rồi phát hành bản tổng hợp 1 lần. Font typography SAU nội dung theo lệnh user.

Tiếp bằng sửa ROM/nguồn và update GitHub, không báo checkpoint lắt nhắt, không link IPS lẻ.
