# ROM contract — canonical clean source

## Exact identity

| Field | Value |
|---|---|
| Size | `2,097,152` (`0x200000`) |
| SHA-1 | `08a2415362f69788ec76b1a36044dc1f1a5f2ea1` |
| SHA-256 | `e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956` |
| Internal title | `RS051 CHIBIMARUKOCHAN` |
| Header file offset | `0x7FC0` |
| Map mode byte | `0x30` |
| Cartridge type | `0x00` |
| ROM size exponent | `0x0B` |
| RAM size exponent | `0x00` |
| Region | `0x00` (Japan) |
| Maker byte | `0x33` |
| Version | `0x00` |
| Checksum | `0x1115` |
| Complement | `0xEEEA` |
| Reset vector | `0xFF90` |

The file size is an exact multiple of 32 KiB and the valid LoROM header begins at `0x7FC0`, so this canonical file has no 512-byte copier header.

## Guardrail

Every mutating tool must reject the input unless the exact clean-ROM contract passes. A later version/revision of the game must get a separate contract, not a relaxed hash check.

## Checksum scope

The current checksum helper is intentionally scoped to this exact 2 MiB power-of-two ROM. It must not be advertised as a universal checksum implementation for every SNES mapping/layout.

Reference for SNES header validation: SNESdev Wiki `ROM header`.
