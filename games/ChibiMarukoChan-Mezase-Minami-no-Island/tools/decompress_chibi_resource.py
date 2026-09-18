#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from rom_common import require_clean_rom

ROM_SIZE = 0x200000


@dataclass(frozen=True)
class ResourceHeader:
    source_file: int
    span: int
    postprocess: bool
    end_file: int


@dataclass(frozen=True)
class CommandStat:
    backref: int = 0
    literal: int = 0
    pair_literal: int = 0
    rle: int = 0
    zero: int = 0
    zero_extended: int = 0


def cpu_to_file(cpu: int) -> int:
    bank = (cpu >> 16) & 0xFF
    addr = cpu & 0xFFFF
    if addr < 0x8000:
        raise ValueError(f"not a LoROM ROM address: ${cpu:06X}")
    off = (bank & 0x7F) * 0x8000 + (addr - 0x8000)
    if not 0 <= off < ROM_SIZE:
        raise ValueError(f"mapped file offset outside ROM: 0x{off:X}")
    return off


def parse_header(data: bytes | bytearray, off: int) -> ResourceHeader:
    if off < 0 or off + 2 > len(data):
        raise ValueError(f"resource header outside ROM: 0x{off:X}")
    raw = data[off] | (data[off + 1] << 8)
    span = raw & 0x7FFF
    if span < 2:
        raise ValueError(f"invalid resource span: 0x{span:X}")
    end = off + span
    if end > len(data):
        raise ValueError(
            f"resource span outside ROM: 0x{off:X}..0x{end:X}"
        )
    return ResourceHeader(off, span, bool(raw & 0x8000), end)


def reorder_flag1_blocks(data: bytes | bytearray) -> bytes:
    """Reproduce the flag=1 16-byte reorder used before VRAM upload.

    Each complete block becomes:
    0,8,1,9,2,10,3,11,...,7,15.

    A partial tail is rejected because the retail routine operates on
    complete 16-byte units for the observed graphics resources.
    """
    if len(data) % 16:
        raise ValueError(
            f"flag1 postprocess requires 16-byte alignment, got 0x{len(data):X}"
        )
    order = (0, 8, 1, 9, 2, 10, 3, 11, 4, 12, 5, 13, 6, 14, 7, 15)
    out = bytearray(len(data))
    for base in range(0, len(data), 16):
        for dst, src in enumerate(order):
            out[base + dst] = data[base + src]
    return bytes(out)


def decompress_resource(
    data: bytes | bytearray,
    off: int,
    *,
    max_output: int = 0x20000,
) -> tuple[bytes, ResourceHeader, dict[str, int]]:
    """Exact high-level model of the resource codec at $80:E8B2.

    The compressed span includes the 2-byte header. Output is maintained
    through the same 1 KiB circular history used by the retail routine.
    """
    header = parse_header(data, off)
    ip = off + 2
    end = header.end_file

    ring = bytearray(0x400)
    write_pos = 0
    output = bytearray()
    stats = {
        "backref": 0,
        "literal": 0,
        "pair_literal": 0,
        "rle": 0,
        "zero": 0,
        "zero_extended": 0,
    }

    def emit(value: int) -> None:
        nonlocal write_pos
        value &= 0xFF
        ring[write_pos] = value
        write_pos = (write_pos + 1) & 0x03FF
        output.append(value)
        if len(output) > max_output:
            raise ValueError(
                f"decompressed output exceeds max 0x{max_output:X}"
            )

    while ip < end:
        cmd = data[ip]

        if cmd < 0x80:
            if ip + 1 >= end:
                raise ValueError(f"truncated back-reference at 0x{ip:X}")
            length = (cmd >> 2) + 2
            packed = (cmd << 8) | data[ip + 1]
            read_pos = (packed - 0x03DF) & 0x03FF
            ip += 2
            for _ in range(length):
                value = ring[read_pos]
                read_pos = (read_pos + 1) & 0x03FF
                emit(value)
            stats["backref"] += 1

        elif cmd < 0xA0:
            length = cmd & 0x1F
            ip += 1
            if ip + length > end:
                raise ValueError(
                    f"truncated literal at 0x{ip - 1:X}: "
                    f"need={length} remain={end - ip}"
                )
            for value in data[ip:ip + length]:
                emit(value)
            ip += length
            stats["literal"] += 1

        elif cmd < 0xC0:
            length = (cmd & 0x1F) + 2
            ip += 1
            if ip + length > end:
                raise ValueError(
                    f"truncated pair-literal at 0x{ip - 1:X}"
                )
            for value in data[ip:ip + length]:
                emit(0)
                emit(value)
            ip += length
            stats["pair_literal"] += 1

        elif cmd < 0xE0:
            length = (cmd & 0x1F) + 2
            if ip + 1 >= end:
                raise ValueError(f"truncated RLE at 0x{ip:X}")
            value = data[ip + 1]
            ip += 2
            for _ in range(length):
                emit(value)
            stats["rle"] += 1

        elif cmd < 0xFF:
            length = (cmd & 0x1F) + 2
            ip += 1
            for _ in range(length):
                emit(0)
            stats["zero"] += 1

        else:
            if ip + 1 >= end:
                raise ValueError(f"truncated extended zero-run at 0x{ip:X}")
            length = data[ip + 1] + 2
            ip += 2
            for _ in range(length):
                emit(0)
            stats["zero_extended"] += 1

    if ip != end:
        raise ValueError(
            f"stream cursor mismatch: ip=0x{ip:X} end=0x{end:X}"
        )

    return bytes(output), header, stats


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Decompress one canonical Chibi SNES resource stream"
    )
    ap.add_argument("rom", type=Path)
    ap.add_argument("output", type=Path)
    source = ap.add_mutually_exclusive_group(required=True)
    source.add_argument("--source-file", type=lambda s: int(s, 0))
    source.add_argument("--source-cpu", type=lambda s: int(s, 0))
    ap.add_argument(
        "--apply-postprocess",
        action="store_true",
        help="apply the flag=1 16-byte graphics reorder when the header requests it",
    )
    ap.add_argument("--metadata", type=Path)
    args = ap.parse_args()

    rom = require_clean_rom(args.rom)
    off = (
        args.source_file
        if args.source_file is not None
        else cpu_to_file(args.source_cpu)
    )

    raw, header, stats = decompress_resource(rom, off)
    output = raw
    postprocess_applied = False
    if args.apply_postprocess and header.postprocess:
        output = reorder_flag1_blocks(raw)
        postprocess_applied = True

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(output)

    metadata = {
        "mode": "READ_ONLY_SOURCE_DECODE",
        "source_file": f"0x{off:06X}",
        "source_cpu": (
            f"0x{args.source_cpu:06X}"
            if args.source_cpu is not None
            else None
        ),
        "compressed_span": f"0x{header.span:X}",
        "postprocess_flag": header.postprocess,
        "postprocess_applied": postprocess_applied,
        "decompressed_bytes": len(raw),
        "output_bytes": len(output),
        "output_sha256": hashlib.sha256(output).hexdigest(),
        "command_stats": stats,
        "runtime_claim": False,
    }

    if args.metadata:
        args.metadata.parent.mkdir(parents=True, exist_ok=True)
        args.metadata.write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    print("clean_rom_contract=PASS")
    print(f"source_file=0x{off:06X}")
    print(f"compressed_span=0x{header.span:X}")
    print(f"postprocess_flag={int(header.postprocess)}")
    print(f"decompressed_bytes=0x{len(raw):X}")
    print(f"postprocess_applied={int(postprocess_applied)}")
    print(f"output={args.output}")
    if args.metadata:
        print(f"metadata={args.metadata}")
    print("runtime_claim=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
