Tiếp tục Chibi Maruko-chan SNES từ `HANDOFF_CURRENT.md` trên branch `chibi-maruko-bootstrap-01` của repo `ronvotri/Viet-Hoa-SNES`.

Canonical clean ROM SHA1: `08a2415362f69788ec76b1a36044dc1f1a5f2ea1`.

User đã tạm dừng vòng lặp typography để quay lại dịch nội dung. Font path/codepage đã được chứng minh runtime; Probe 010 là baseline đẹp nhất hiện tại. Probe 011..018 bị user loại vì nét/dấu không đồng đều; Probe 019 chỉ là thử sửa riêng `đ`, chưa phải release font PASS. Không tự ý mở lại font work nếu không cần.

Meaning-first translation hiện có 1,018 release-intent source rows. Large coherent direct-text banks đã được meaning-covered. Không dịch scanner noise để tăng số lượng.

Mới thêm `translation/source/karaoke_batch01_singable_v1_vi.csv`: second-pass cho 28 dòng karaoke, giữ nguyên `vi_full` và thêm `vi_singable_v1` ngắn/gọn/nhịp hơn. Đây chưa phải timing-fit runtime PASS và không tăng unique source-row count.

Ưu tiên tiếp theo: tiếp tục editorial translation có giá trị, locate graphics/tilemap player-facing text để dịch khi asset được chứng minh, sau đó mới chuẩn bị các runtime insertion batch nhỏ có guardrail. Giữ riêng graphics text như `どれにする？`, Start/Password/Continue/ending family.

Luôn build từ CLEAN ROM, preserve source identity/control bytes, dry-run/diff-surface/checksum gates, và không gọi whole-game Runtime PASS từ một subsystem screenshot.
