#!/usr/bin/env python3
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

EXPECTED_SIZE = 0x200000
EXPECTED_SHA1 = "08a2415362f69788ec76b1a36044dc1f1a5f2ea1"
EXPECTED_SHA256 = "e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956"
LOROM_HEADER = 0x7FC0
CHECKSUM_COMPLEMENT = LOROM_HEADER + 0x1C
CHECKSUM = LOROM_HEADER + 0x1E
EXPECTED_TITLE = b"RS051 CHIBIMARUKOCHAN"
EXPECTED_MAP_MODE = 0x30


class RomContractError(RuntimeError):
    pass


@dataclass(frozen=True)
class RomIdentity:
    size: int
    sha1: str
    sha256: str


def digest_bytes(data: bytes) -> RomIdentity:
    return RomIdentity(
        size=len(data),
        sha1=hashlib.sha1(data).hexdigest(),
        sha256=hashlib.sha256(data).hexdigest(),
    )


def require_clean_rom(path: str | Path) -> bytearray:
    path = Path(path)
    data = path.read_bytes()
    ident = digest_bytes(data)
    problems: list[str] = []
    if ident.size != EXPECTED_SIZE:
        problems.append(f"size {ident.size} != expected {EXPECTED_SIZE}")
    if ident.sha1 != EXPECTED_SHA1:
        problems.append(f"SHA1 {ident.sha1} != expected {EXPECTED_SHA1}")
    if ident.sha256 != EXPECTED_SHA256:
        problems.append(f"SHA256 {ident.sha256} != expected {EXPECTED_SHA256}")
    if data[LOROM_HEADER:LOROM_HEADER + 21] != EXPECTED_TITLE:
        problems.append("internal title mismatch")
    if data[LOROM_HEADER + 0x15] != EXPECTED_MAP_MODE:
        problems.append("map mode mismatch")
    if problems:
        raise RomContractError("CLEAN ROM contract failed:\n- " + "\n- ".join(problems))
    return bytearray(data)


def read_u16le(data: bytes | bytearray, offset: int) -> int:
    return data[offset] | (data[offset + 1] << 8)


def calc_snes_checksum(data: bytes | bytearray) -> int:
    """Checksum for this proven 2 MiB power-of-two ROM.

    The four header bytes are replaced conceptually by a checksum/complement
    pair whose byte sum is always 0x1FE. This deliberately does NOT claim to
    be a generic algorithm for every exotic SNES ROM layout.
    """
    if len(data) != EXPECTED_SIZE:
        raise RomContractError("checksum helper is intentionally scoped to the exact 2 MiB clean-ROM contract")
    tmp = bytearray(data)
    tmp[CHECKSUM_COMPLEMENT:CHECKSUM + 2] = b"\x00\x00\x00\x00"
    return (sum(tmp) + 0x1FE) & 0xFFFF


def write_snes_checksum(data: bytearray) -> tuple[int, int]:
    checksum = calc_snes_checksum(data)
    complement = checksum ^ 0xFFFF
    data[CHECKSUM_COMPLEMENT:CHECKSUM_COMPLEMENT + 2] = complement.to_bytes(2, "little")
    data[CHECKSUM:CHECKSUM + 2] = checksum.to_bytes(2, "little")
    return checksum, complement


def validate_internal_header(data: bytes | bytearray) -> dict[str, int | str | bool]:
    title = bytes(data[LOROM_HEADER:LOROM_HEADER + 21]).decode("ascii", "replace")
    complement = read_u16le(data, CHECKSUM_COMPLEMENT)
    checksum = read_u16le(data, CHECKSUM)
    computed = calc_snes_checksum(data)
    return {
        "title": title,
        "map_mode": data[LOROM_HEADER + 0x15],
        "cartridge_type": data[LOROM_HEADER + 0x16],
        "rom_size_exp": data[LOROM_HEADER + 0x17],
        "ram_size_exp": data[LOROM_HEADER + 0x18],
        "region": data[LOROM_HEADER + 0x19],
        "maker": data[LOROM_HEADER + 0x1A],
        "version": data[LOROM_HEADER + 0x1B],
        "checksum": checksum,
        "complement": complement,
        "checksum_pair_valid": ((checksum + complement) & 0xFFFF) == 0xFFFF,
        "computed_checksum": computed,
        "checksum_matches": checksum == computed,
        "reset_vector": read_u16le(data, LOROM_HEADER + 0x3C),
    }
