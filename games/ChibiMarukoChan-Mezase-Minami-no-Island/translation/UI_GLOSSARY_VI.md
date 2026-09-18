# Chibi Maruko-chan — Vietnamese UI Glossary

Updated: 2026-09-18 +07  
Branch: `chibi-maruko-bootstrap-01`

This file freezes the preferred Vietnamese wording for recurring player-facing UI.

It is a language/style authority only. Runtime insertion still depends on the proven renderer, byte budget, or graphics asset path.

## Main flow

| Source | Vietnamese | Role | Layer |
|---|---|---|---|
| どれにする？ | Chọn gì đây? | selection heading | graphics |
| はじめから | Bắt đầu | new game | graphics |
| パスワード | Mật khẩu | password | graphics |
| コンティニュー | Tiếp tục | continue | graphics |
| やめる | Thoát | quit Story Mode | graphics |
| はい | Có | yes | direct text |
| いいえ | Không | no | direct text |
| スタートをおしてね | Bấm START nhé | start prompt | direct text |

## Main menu

| Source | Vietnamese |
|---|---|
| ストーリーモード | Cốt truyện |
| 対戦モード | Thi đấu |
| チーム対戦モード | Thi đấu theo đội |
| まるこＱ | Maruko Q |
| まるこペイント | Vẽ cùng Maruko |
| まるこみくじ | Bói vui cùng Maruko |
| 針切カラオケ | Karaoke |
| サウンド | Âm thanh |
| ステレオ | Stereo |
| モノラル | Mono |

Compact runtime variants may remain shorter where fixed fields are still proven rigid, e.g. `Truyện`, `Đấu`, `Đấu đội`, `M.Q`, `Bói`, `Hát`, `Âm`.

## Difficulty / match setup

| Source | Vietnamese |
|---|---|
| 何本先取？ | Thắng mấy ván? |
| １本 .. ５本 | 1 ván .. 5 ván |
| コンピュータの / つよさ | Độ khó / CPU |
| よわい | Dễ |
| ふつう | Vừa |
| つよい | Khó |
| １ゲームの時間 | Thời gian / ván |
| １８０秒 | 180 giây |
| 勝つまで | Đến khi thắng |
| プレイヤー１..４ | Người chơi 1..4 |
| 対戦するよ | Chơi |
| コンピュータ | CPU |
| おやすみだよ | Nghỉ |
| 接続なし | Không kết nối |
| ステージ | Màn |

## Controllers / control labels

| Source | Vietnamese |
|---|---|
| パッド | Tay cầm |
| マウス | Chuột |
| スコープ | Super Scope |
| しゃがむ | Cúi |
| 移動 | Đi |
| ボールを / なげる | Ném / bóng |
| ドライヤー | Sấy |
| おしている間 / ペンキをぬる | Giữ nút / Sơn |
| 投げる | Ném |
| 体当り | Húc |

## Rules / results

| Source | Vietnamese |
|---|---|
| ルールをせつめいするよ | Luật chơi |
| ２本先取だよ | Thắng 2 |
| ゲームの時間は勝つまでだよ | Đến khi thắng |
| 勝ち | Thắng |
| 敗けた | Thua |
| 最終勝利 | Chiến thắng cuối cùng! |
| エンディング | Kết thúc |

## Quiz UI

| Source | Vietnamese |
|---|---|
| 第 問 | Câu |
| 全問クリアおめでとう！！ | Chúc mừng! Hoàn thành tất cả câu hỏi!! |
| もんだい数 | Tổng câu |
| こたえた回数 | Lượt trả lời |
| せいかいりつ | Tỷ lệ đúng |
| 一発で正解したのは | Đúng lần đầu |
| クイズを続けますか？ | Tiếp tục câu đố? |
| はい / いいえ | Có / Không |

## Karaoke start options

| Source | Vietnamese |
|---|---|
| メロディーありでスタート | Chơi có nhạc |
| メロディーなしでスタート | Chơi không nhạc |

Compact option labels may use **Có nhạc / Không nhạc** if the surrounding screen already makes the action clear.

## Graphics title / intro

`ちびまる子ちゃん めざせ！南のアイランド！！`

Preferred presentation:

- **Chibi Maruko-chan**
- **Tiến tới đảo phương Nam!!**
- **Việt hóa bởi VôtriValley**

Preserve the original publisher/copyright attribution.

## Quality rules

- Never replace **Không** with `Ko` merely to satisfy a fixed field.
- Do not switch to English `No` / `Off` when Vietnamese field expansion is the cleaner solution.
- Graphics redraws should keep full Vietnamese diacritics whenever technically possible.
- `vi_full` / natural UI wording remains canonical; compact runtime labels are a separate implementation layer.
- Do not treat internal QA/debug descriptors as visible retail text.
- Do not call graphics labels Runtime PASS before the exact patched screen is tested.
