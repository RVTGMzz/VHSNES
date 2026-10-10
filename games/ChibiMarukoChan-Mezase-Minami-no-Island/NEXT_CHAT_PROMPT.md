TIẾP TỤC CHIBI MARUKO-CHAN SNES — CHECKPOINT 031 (2026-10-11)
Repo: RVTGMzz/VHSNES | branch: chibi-maruko-bootstrap-01

ĐỌC TRƯỚC:
1. games/ChibiMarukoChan-Mezase-Minami-no-Island/HANDOFF_CURRENT.md
2. docs/G2_PROBE008_RECOVERY_CALLGRAPH_CHECKPOINT_031.md (MỚI NHẤT)
3. docs/G2_PROBE008_RENDERER_STACK_AUDIT_CHECKPOINT_030.md
4. docs/G2_PROBE008_ISOLATED_QUOTES_CHECKPOINT_029.md
5. docs/G2_PROBE008_USER_RUNTIME_FAIL_CHECKPOINT_026.md (025 ĐÃ FAIL RUNTIME)

CÔNG VIỆC MỚI CHỐT:
- Input CLEAN SHA e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956. Input 025 FAILED SHA d4bd629003812578580e7a380e791d87fdf64614441394f1261df3951b9815dc.
- ĐÃ KHÔI PHỤC được exact V2 FONT ONLY từ bản 025 FAIL đã user từng thử: SHA 2ca9b82bf09d0e4b6feeb65ba59d3c94cb22cdfcd475e68dd96af47a119f75bd; reverse 191 bytes đúng các stage, checksum 622E/9DD1. Code GitHub tools/recover_g2_probe008_v2_from_failed025.py. Không coi V2 là runtime-good.
- ĐÃ AUDIT nguyên ROM clean và V2: đúng 1 direct JSL parser tới glyph renderer $85:8E7B (file 28413), đúng 1 direct JSL glyph renderer tới helper $85:8E05 (file 28E83). Không có JSR same bank tới đó. Parser có REP #$20 trước LDA [$02],Y -> JSL renderer nên A16 ở đường thẳng này; hỗ trợ stack glyph low $0A,S nếu X8 / $0C,S nếu X16. Chưa chứng minh mọi indirect path. 7/7 mutation tests. Code tools/audit_g2_probe008_031_direct_call_graph.py. Local JSON Chibi_Probe008_031_direct_call_report.json.
- Preflight 029 trên CLEAN + V2: glyph quotes Nhật 0159/015A còn nguyên; 85 lead mã 8574/8575 chưa dùng; target cells 0A54/0A55 THẬT SỰ TRỐNG; 3x106-byte G2 records mỗi đoạn đúng 2 quotes 8175/8176 và 3 control 816F. Không có raw 8574/8575 trong Story bank; toàn ROM raw có 13/6 hits nên global safe CHƯA PROVEN. Code tools/audit_g2_probe008_031_alias_preflight.py. Local JSON Chibi_Probe008_031_alias_preflight.json.
- 029 V3 medium + renderer 9px theo glyph thật + duplicated 2 quote G2 codes: static 83.600 opcode tests PASS, alias glyph 0A54/0A55, 8175/8176 nguyên bản không bị co ngoài G2. SHA binary experimental 029 a23304cedff0eac959a6455d90b866c49543ca381425b089771b65da264e928e. NOT TESTED IN EMULATOR, no ROM on GitHub.
- 025 từng được USER chạy và chụp màn hình chữ Vỡ + giãn 13px; đây là RUNTIME FAIL, không dùng 025 nữa.
- Môi trường container thiếu Snes9x/bsnes/RetroArch, DNS không resolve github.com/deb.debian.org, không claim đã chơi thật.

NEXT:
1. Tập trung REAL SNES emulator/debugger cho 029: A M/X tại parser + renderer PHA, $0A,S/$0C,S khi JSL word hook 8E0C, DP $18/$08/$0A ở shift hook 90EE. Kiểm tra 9px, dấu, dấu ngoặc, wrap 19 cột, font V3, không crash và Nhật ngoài G2 vẫn 13px.
2. Nếu emulator chưa có, tiếp tục audit có GIỚI HẠN và cải tiến build QA; không lại phân tích lan man rồi tuyên bố runtime-pass.
3. Chỉ release khi screenshot thật OK; sau đó tiếp G0/title G2/G3/menu/minigame.
4. Không upload ROM hay hình chụp cá nhân lên GitHub; chỉ tools/QA/checkpoint.

Mốc 031 đã push, các JSON report lưu local. Đừng bắt người dùng gửi lại ROM trước khi đọc file đính kèm.
