TIẾP TỤC VIỆT HÓA CHIBI MARUKO-CHAN SNES
Repo: RVTGMzz/VHSNES — branch chibi-maruko-bootstrap-01

ĐỌC TRƯỚC:
1. games/ChibiMarukoChan-Mezase-Minami-no-Island/HANDOFF_CURRENT.md
2. games/ChibiMarukoChan-Mezase-Minami-no-Island/docs/G2_PROBE008_STACK_BANK_SAFE_CHECKPOINT_025.md
3. docs/G2_PROBE008_LINE_SCOPED_9PX_CHECKPOINT_024.md (LỊCH SỬ; ĐÃ BỊ THAY THẾ)
4. docs/G2_PROBE008_SELECTIVE_SPACING_CHECKPOINT_023.md (LỊCH SỬ)
5. docs/G2_PROBE008_LOCAL_STATIC_BUILDS_CHECKPOINT_022.md

TÌNH TRẠNG THẬT:
- ROM clean SHA256 e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956; Probe003 dựng lại khớp SHA256 5208bec10147f478cc17955c4f262a5cde08e5b85708caa2717370f6835fbacd.
- Font Probe008 V2 có 212 mã, 210 bitmap; 49 hoa +3 thường mới; trang font 0x0A. Probe008 V2 FONT-ONLY 13px SHA256 2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd. Đã qua bitmap/codepage/checksum và pointer tests tĩnh, nhưng CHƯA RUNTIME PASS.
- Renderer thực tế tiến chữ 13px. Bản 9px GLOBAL có nguy cơ phá chữ Nhật. Bản 9px chọn theo glyph (checkpoint 023) bị lỗi dấu ngoặc Nhật 8176 lệch 64px, KHÔNG DÙNG.
- Checkpoint 024 đã thử 9px theo nguồn G2 (ba bản ghi 106 byte), nhưng PHÁT HIỆN LỖI QUAN TRỌNG: renderer ở 0x28E95 thực hiện PEA $7F00; PLB; PLB, đổi DBR thành $7F trước lần tra bảng dịch pixel 0x290EE, nên hook kiểm tra DBR hiện tại ở lần thứ hai là SAI. ROM 024 SHA256 feb7215a67046128ff67113fd921b6479d956df6018a3ae4e74992d03b0c978a bị loại, không được phát hành.
- CHECKPOINT 025 (MỚI NHẤT): đã sửa hook byte để lấy DBR gốc từ stack do renderer PHB đã lưu. Dựa vào bit X trong P đã lưu: X8 dùng LDA $07,S, X16 dùng LDA $09,S. Hook word trước lúc đổi bank dùng DBR hiện tại. Nguồn ba bản ghi ở bank 83: 81CE..8238, 8247..82B1, 82C0..832A đều bước 9px gồm ngoặc, ngoài G2 vẫn 13px.
- ROM diagnostic 025 build tại máy local, SHA256 d4bd629003812578580e7a380e791d87fdf64614441394f1261df3951b9815dc; 191 changed bytes vs V2, checksum 0xED96/complement 0x1269; word stub 57, byte stub 67; 18.696 test 65816 subset PASS, independent verifier PASS, 5/5 negative corruptions caught. Strict two-byte data, 816F tại 32/68/104, D038/scene/13px native tables nguyên trạng.
- Tools trên GitHub: tools/build_g2_probe008_line_scoped_9px_diagnostic.py, tools/verify_g2_probe008_line_scoped_9px_diagnostic.py. Đã sửa đúng stack X8/X16. Không đưa ROM lên GitHub.

VIỆC TIẾP THEO:
1. Cần emulator/debugger thật xem DBR nguồn có là 0x83 và $1F94 trỏ đúng bản ghi, kiểm tra saved DBR trên stack tại hook2; sau đó QA glyph trang font mới, dấu hỏi/ngã, A có dấu, ngoặc, wrap và chế độ Nhật. Môi trường hiện chưa có emulator; tuyệt đối KHÔNG CLAIM Runtime PASS.
2. Chỉ sau khi có runtime proof mới cân nhắc mở rộng 9px sang Story/UI khác theo nguồn đã chứng minh, không vá toàn cục.
3. Audit mã lead 0x85 trên những cảnh Nhật và tiếp tục G0 title, G2/G3 graphics, menu, minigame, phần Việt hóa còn thiếu theo handoff.
4. Không upload ROM thương mại lên repo. Tiến độ được cập nhật trực tiếp ở repo branch như trên.
