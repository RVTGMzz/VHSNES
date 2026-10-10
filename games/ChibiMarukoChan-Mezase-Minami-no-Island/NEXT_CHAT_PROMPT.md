Tiếp tục Việt hóa Chibi Maruko SNES trên RVTGMzz/VHSNES, nhánh chibi-maruko-bootstrap-01.

ĐỌC TRƯỚC: HANDOFF_CURRENT.md, docs/G2_PROBE008_COMPLETE_FONT_CHECKPOINT_021.md, docs/G2_PROBE008_RENDERER_SPACING_PROOF_020.md, docs/G2_PROBE008_SPACING_HANDOFF_019.md.

ĐÃ CHỨNG MINH: renderer dùng 13 px/ký tự (hai bảng ROM 0x29670 và 0x29696), không phải 12 px như ảnh preview trước. Đã tạo so sánh 13/12/9 px và commit SVG. 9 px chưa được kiểm thử trong game, thay toàn cục sẽ ảnh hưởng chữ Nhật nên chưa thể coi là bản vá phát hành.

ĐÃ LƯU: script sửa chữ A hoa có dấu giữ nét ngang và căn giữa dấu hỏi/ngã xếp tầng; JSON font V2 212 ký tự / 210 bitmap, bổ sung 49 hoa + 3 thường, đề xuất 52 mã 0x8540..0x8573. 126 ô custom cũ được kiểm tra trống trên ROM gốc nhưng là slot đang được dành cho codepage cũ. Phương án trang font thứ 11 và bảng ánh xạ mới có đủ vùng đệm theo kiểm tra byte, song chưa xác nhận không có tham chiếu gián tiếp và chưa thử renderer với trang 0x0A.

HƯỚNG TIẾP: chạy các script mới với ROM gốc (đã có SHA256 chuẩn), kiểm thử sinh font V2; xác minh 0x85 có được game dùng theo mã riêng không, chứng minh relocate trang font; thiết kế 9 px chỉ cho tiếng Việt, sau đó build ROM từ Probe003 SHA256 5208bec10147f478cc17955c4f262a5cde08e5b85708caa2717370f6835fbacd, kiểm tra checksum+ROM diff độc lập và chạy giả lập trước khi gửi phiên bản. Tuyệt đối không commit ROM và không claim runtime PASS khi chưa test. Giữ framing 2 byte, các dấu phân cách 32/68/104, D038, palette và logic cảnh Probe003.
