Tiếp tục Chibi Maruko trong repo RVTGMzz/VHSNES, nhánh chibi-maruko-bootstrap-01.

Đọc HANDOFF_CURRENT.md và docs/G2_PROBE008_SPACING_HANDOFF_019.md trước tiên.

Mục tiêu gần nhất: chữ đang quá thưa. Kiểm tra bước tiến chữ thật trong renderer và thử phương án 9 px bằng preview trước; chưa có bản vá khoảng cách nào. Sửa chữ A hoa có dấu bị mất nét ngang và dấu hỏi/ngã xếp tầng. Bộ font 163 mục chưa đủ chữ hoa tiếng Việt.

ROM gốc đã được xác minh đúng và đã dựng lại Probe 003 khớp hash. Preflight tìm 6 ô mới đủ điều kiện so với 161 bitmap; số này loại trừ toàn bộ ô custom cũ, nên cần audit tái sử dụng hoặc mở rộng font. Không ghi đè chữ Nhật. Giữ nguyên text/control path của Probe 003. Không coi kiểm tra cấu trúc là font đẹp hoặc runtime PASS.

Xem checkpoint để lấy hash và danh sách công cụ. ROM không nằm trong GitHub; dùng bản người dùng đã cung cấp.
