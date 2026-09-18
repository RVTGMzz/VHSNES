# UI Localization Coverage Audit 001

Updated: 2026-09-18 +07  
Branch: `chibi-maruko-bootstrap-01`

This audit tracks proven player-facing UI separately from graphics-only labels and internal debug descriptors.

## A. Direct-text UI — wording covered

### Main menu

Covered:

- Cốt truyện
- Thi đấu
- Thi đấu theo đội
- Maruko Q
- Vẽ cùng Maruko
- Bói vui cùng Maruko
- Karaoke
- Âm thanh
- Stereo
- Mono

Runtime compact candidates already exist for the rigid menu fields.

### Match / minigame setup

Covered:

- Thắng mấy ván?
- 1–5 ván
- Độ khó / CPU
- Dễ / Vừa / Khó
- Thời gian / ván
- 180 giây
- Đến khi thắng
- Người chơi 1–4
- Chơi / CPU / Nghỉ
- Không kết nối
- Tay cầm / Chuột / Super Scope
- Màn

### Minigame controls

Covered:

- Cúi
- Đi
- Ném / bóng
- Sấy
- Giữ nút / Sơn
- Ném
- Húc

### Quiz UI

Covered:

- Câu
- Chúc mừng! Hoàn thành tất cả câu hỏi!!
- Tổng câu
- Lượt trả lời
- Tỷ lệ đúng
- Đúng lần đầu
- Tiếp tục câu đố?
- Có / Không
- Bấm START nhé

### Karaoke / music start

Covered:

- Chơi có nhạc
- Chơi không nhạc

Compact candidates:

- Có nhạc
- Không nhạc

## B. Graphics-driven UI — wording frozen, asset path pending

### G0 title / intro

- Chibi Maruko-chan
- Tiến tới đảo phương Nam!!
- Việt hóa bởi VôtriValley

Original publisher/copyright attribution must remain.

### G1

- Chọn gì đây?
- Bắt đầu
- Mật khẩu

### G2

- Bắt đầu thôi!
- Luật chơi
- Thắng 2
- Đến khi thắng

### G3

- Thắng
- Thua
- Tiếp tục
- Thoát
- Chiến thắng cuối cùng!
- Kết thúc

`Thoát` is context-resolved from the Story Mode quit descriptor.

## C. Stage labels — meaning covered

All 15 discovered stage/title strings have Vietnamese meaning coverage.

Editorial wording has already been polished for several awkward literal names.

Runtime layout remains a separate concern.

## D. Credits — meaning covered

Credits role meanings are translated and personal names preserved.

Build 035 already carries compact Credits role-token patches.

No new source rows are needed here unless new visible credits text is discovered.

## E. Explicitly excluded

The internal QA/debug block around `0x2865E..0x287FC` is not retail UI.

Do not patch it merely because it describes Start/Password/VS/Continue/Ending screens.

## F. Current remaining UI work

The meaningful untranslated-UI bottleneck is no longer language wording.

It is now technical asset recovery:

1. reverse G0 title asset;
2. reverse G1 menu/start/password asset;
3. reverse G2 rules/banner asset;
4. reverse G3 result/continue/ending assets;
5. validate runtime layout for direct fields marked `runtime_needs_expansion`.

Do not resume broad CP932 scanning unless new runtime evidence proves another player-facing direct-text bank.
