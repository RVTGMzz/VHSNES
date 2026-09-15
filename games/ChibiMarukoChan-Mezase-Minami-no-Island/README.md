# Chibi Maruko-chan - Mezase! Minami no Island!! (SNES) — Việt hóa

Trạng thái: **Bootstrap / reverse-engineering 001**.

Mục tiêu là Việt hóa game theo workflow có thể tái tạo, có guardrail và có bằng chứng runtime. Dự án không lưu ROM thương mại.

## Canonical clean ROM

- File thường gặp: `Chibi Maruko-chan - Mezase! Minami no Island!! (Japan).sfc`
- Size: `2,097,152` bytes (`0x200000`)
- SHA-1: `08a2415362f69788ec76b1a36044dc1f1a5f2ea1`
- SHA-256: `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956`
- Internal title: `RS051 CHIBIMARUKOCHAN`
- Proven header: LoROM / FastROM, no 512-byte copier header

## First proven findings

1. Clean-ROM identity and SNES internal checksum are valid.
2. Plain CP932/Shift-JIS text exists directly in ROM. This is proven by exact hits such as:
   - `メロディーありでスタート` at `0x2B7C9`
   - `メロディーなしでスタート` at `0x2B7EF`
   - `スタートをおしてね` at `0x31CFB`
   - `ちびまる子ちゃん` at `0x2C74B`
3. Text is embedded among non-text/control bytes. Their semantics are **not yet frozen**.
4. A guarded one-string ASCII renderer probe is prepared, but **Runtime PASS = NO** until gameplay evidence exists.

## Tools

```bash
python tools/inspect_rom.py "path/to/clean.sfc"
python tools/scan_sjis_candidates.py "path/to/clean.sfc" --start 0x18000 --end 0x34000 --csv reports/generated/text_candidates.csv
python tools/probe_ascii_menu.py "path/to/clean.sfc" "out/chibi_ascii_probe.sfc" --dry-run
python tools/probe_ascii_menu.py "path/to/clean.sfc" "out/chibi_ascii_probe.sfc"
```

The probe changes only the exact 24-byte source field at `0x2B7C9`, pads inside that same span, then regenerates the SNES checksum/complement. It does not prove that ASCII is supported until observed in-game.

Read `HANDOFF_CURRENT.md` before continuing work.
