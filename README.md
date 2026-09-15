# Việt Hóa SNES

Kho làm việc cho các dự án Việt hóa Super Nintendo / Super Famicom.

## Nguyên tắc chung

- Không lưu ROM thương mại trong repository.
- Mỗi game có clean-ROM contract riêng (size + hash + header facts đã kiểm chứng).
- Không kế thừa giả định kỹ thuật từ hệ máy khác nếu chưa chứng minh trên ROM đích.
- Mọi patcher phải có guarded dry-run trước build thật.
- Không gọi `Runtime PASS` nếu chưa có bằng chứng chạy game thực tế.
- Phân tách rõ: source-of-truth translation, runtime candidate, build artifact và runtime evidence.

Dự án đầu tiên: `Chibi Maruko-chan - Mezase! Minami no Island!! (Japan)`.
