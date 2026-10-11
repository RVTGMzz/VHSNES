TIẾP CHIBI MARUKO-CHAN SNES VIỆT HÓA — CHECKPOINT 041 (2026-10-11)
Repo: RVTGMzz/VHSNES | branch: chibi-maruko-bootstrap-01
ƯU TIÊN CỦA USER: HOÀN THÀNH NỘI DUNG VÀ ĐỒ HỌA TRƯỚC, FONT LO SAU. ĐỪNG SA LẦY VÒNG LẶP KIỂM TRA FONT.

PHẢI ĐỌC TRƯỚC:
1. games/ChibiMarukoChan-Mezase-Minami-no-Island/HANDOFF_CURRENT.md (041 đầu file).
2. docs/CONTENT_FIRST_QUIZ_CHECKPOINT_041.md (bản mới nhất).
3. docs/CONTENT_FIRST_FORTUNE_CHECKPOINT_040.md.
4. docs/CONTENT_FIRST_REAL_UI_ROM_CHECKPOINT_039.md.
5. docs/RUNTIME_STORY_BUILD_027.md (328 Story segments documented in old binary, need recreate source build).
6. translation/runtime/quiz_answers_exact_fit_041.csv, tools/build_content_first_041_quiz.py.

THÀNH QUẢ THẬT 041:
- ROM gốc Nhật không header 2MB /mnt/data/Chibi Maruko-chan - Mezase! Minami no Island!! (Japan)(1).sfc SHA e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956.
- Bản 040 clean-ROM IPS SHA 2bfdcc64973bc31ce268fa7e68a6118808c633b10d1437b7f811ac290616e580, tạo lại ROM040 SHA d892c51576c103f5881f1481c65fd2746635d222b1d387f9666cd7f44b1da3ac.
- Đã thực sự THAY TRONG ROM 21 câu đáp án quiz (tuổi, ngày, lớp, nghề, tầng); mỗi trường CP932 tiếng Nhật + dấu 816F được xác nhận tại vị trí gốc, giữ đúng số ô mã 0x84 V2; không ngắt câu hay sửa font.
- Có 2 fragment quiz nguồn scanner sai so với raw byte, bị LOẠI để không vá bậy. Các tên nhân vật không đủ ô chữ cũng được giữ nguồn đầy đủ.
- Trên GitHub: translation/runtime/quiz_answers_exact_fit_041.csv (21 mục), tools/build_content_first_041_quiz.py (dựng lại từ ROM gốc + 040 IPS, dùng canonical Quiz CSV + bảng mã V2, SHA pin), docs/CONTENT_FIRST_QUIZ_CHECKPOINT_041.md.
- Bản patch thử 041 /mnt/data/Chibi_041_G0G1_38UI_33Fortune_21Quiz_UNTESTED.ips SHA 2117bc6e165f2c86263e74a637b6961a13f79257fccd9f02152a769fe1deb962 22.100 bytes, 756 record; ROM sau vá SHA 56c36cbc8e477d262216d3aa0f06909e09b9929ba0f6f544dccbaa3671bf48fb. Diff so với 040 đúng 132 byte ở 21 field + checksum (327D/CD82). Công cụ IPS đọc độc lập áp ngược từ ROM gốc ra ROM041 trùng từng byte. Local JSON /mnt/data/Chibi_041_Independent_Static_QA.json. ZIP CHỈ IPS+JSON+README /mnt/data/Chibi_041_G0G1_92UIFortuneQuiz_Content_First_UNTESTED.zip — KHÔNG có ROM hoặc TTF.
- Bản ROM thử 041 đã gộp ĐỒ HỌA G0 tên game / dòng Việt hóa bởi Votri Valley và G1 Bắt đầu/Mật khẩu/Chọn gì đây?, cùng **92 trường TEXT =38 UI checkpoint039 +33 Fortune checkpoint040 +21 Quiz checkpoint041**.
- Đây KHÔNG phải toàn bộ bản dịch Story/Quiz/Fortune. Chưa có giả lập SNES runtime. Font V2 cũ không sửa và chưa được người dùng xác nhận đọc đẹp (ảnh 025 xấu). Đừng xin user test các bản lẻ.
- Các bản tiếng Việt FULL vi_full cũ 1.018 rows+3 G2 demo đang ở translation/source/*.csv; 216 edit canonical source từ 032; CHƯA đưa hết vào ROM. Historical direct-text Build035 ROM SHA f8fb662a9e1b8fc5a5ff689f690ceaf332055ed86983e52b476a78852e4fd58d không có binary hiện tại.
- Phát hiện trên GitHub: docs/RUNTIME_STORY_BUILD_027.md chứng minh trước kia đã INSERT 328 field Story ở 3 batch (123+121+84) bằng segment-aware wrapping fixed-field codepage, nhưng GitHub KHÔNG lưu runtime compact CSV Story hay reproducible builder; đó là tác vụ PHẢI PHỤC HỒI.
- Tool GitHub tạo ở lượt041 chưa qua GitHub CI (0 checks). Local equivalent từ physical ROM chạy thành công; không claim CI.
- Nhiệm vụ tiếp: 1) PHỤC DỰNG Story runtime build theo 816F line spans + 0E/0F metadata, đúng cảnh, xưng hô/cảm xúc đủ câu, không cắt máy móc; 2) nếu vượt budget thì thiết kế relocation/an toàn trước khi patch; 3) thêm Quiz/Fortune sau khi có content; 4) G2 rule source offset 1E325 đã fix; G3 win/loss actual sprite source chưa chứng minh. 5) sau đó mới một bản test lớn trên SNES.
- FONT SAU, GIỮ CREDIT CHÍNH XÁC: Việt hóa bởi Votri Valley.
