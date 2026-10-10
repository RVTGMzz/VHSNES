#!/usr/bin/env python3
"""G0 first-boot title artwork experiment from exact clean Chibi SNES ROM.

Replace ONLY original title BG tilemap and unshared 4bpp logo tiles with:
  Chibi Maruko-chan
  Tiến tới đảo phương Nam!!
  Việt hóa bởi Votri Valley

This is a static graphics patch builder, NOT an emulator pass or complete
Vietnamese translation. Requires Pillow plus external TrueType fonts by path;
DO NOT commit font files or game ROMs to GitHub.

Reuses the exact game decompressor $80:E8B2 in this repository. The third
graphics stream relocates to confirmed clean ROM FF bank86 space because its
in-place compressed span would overflow. Do not reuse relocation space in
future builds without an exact-base collision check.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict, deque
from pathlib import Path

from decompress_chibi_resource import decompress_resource, reorder_flag1_blocks
from rom_common import require_clean_rom, write_snes_checksum

TITLE = ("Chibi Maruko-chan", "Tiến tới đảo phương Nam!!",
         "Việt hóa bởi Votri Valley")
SCRIPT_OFF = 0x12087
OLD_POINTER_OFF = 0x12095
OLD_POINTER = bytes.fromhex("6D C5 9E")
NEW_POINTER = bytes.fromhex("07 E9 86")
RELOCATE_FILE = 0x36907
GRAPHICS = ((0xF6456, 0x2000, 8192, 5570),
            (0xF5005, 0x3000, 8192, 5201),
            (0xF456D, 0x4000, 8192, 2712))
TITLE_MAP = (0xF1F00, 0x0000, 2048, 545)
OTHER_MAPS = (0x400, 0x1000, 0x5800, 0x5000)


def encode_chibi(data: bytes) -> bytes:
    """Shortest dynamic-programming path over retail RLE/zero/literal/LZ opcodes.

    Searches a bounded set of prior 3-byte matches (last 1 KiB). It is
    deterministic, not globally optimal over all possible 1KiB offsets.
    The decoder round-trip and source-space bound are mandatory.
    """
    n = len(data)
    prior = defaultdict(deque)
    matches = [None] * n
    for i in range(n):
        if i + 2 >= n:
            matches[i] = (0, None)
            continue
        key = data[i:i + 3]
        recent = prior[key]
        while recent and recent[0] < i - 1023:
            recent.popleft()
        best = (0, None)
        for j in reversed(recent):
            length = 0
            while (length < 33 and i + length < n
                   and data[i + length] == data[j + length]):
                length += 1
            if length > best[0]:
                best = (length, j)
            if length == 33:
                break
        recent.append(i)
        if len(recent) > 36:
            recent.popleft()
        matches[i] = best

    cost = [10**10] * (n + 1)
    choices = [None] * (n + 1)
    cost[n] = 0
    for i in range(n - 1, -1, -1):
        best_price = 10**10
        best_choice = None

        def offer(consumed: int, payload: bytes) -> None:
            nonlocal best_price, best_choice
            price = len(payload) + cost[i + consumed]
            if price < best_price:
                best_price, best_choice = price, (consumed, payload)

        for length in range(1, min(31, n - i) + 1):
            offer(length, bytes((0x80 | length,)) + data[i:i + length])
        same = 1
        while (same < 33 and i + same < n
               and data[i + same] == data[i]):
            same += 1
        for length in range(2, same + 1):
            offer(length, bytes((0xC0 + length - 2, data[i])))
        if data[i] == 0:
            zero = 1
            while zero < 257 and i + zero < n and data[i + zero] == 0:
                zero += 1
            for length in range(2, min(32, zero) + 1):
                offer(length, bytes((0xE0 + length - 2,)))
            for length in range(33, zero + 1):
                offer(length, bytes((0xFF, length - 2)))
        pairs = 0
        while (pairs < 33 and i + 2 * pairs + 1 < n
               and data[i + 2 * pairs] == 0):
            pairs += 1
        for length in range(2, pairs + 1):
            offer(length * 2,
                  bytes((0xA0 + length - 2,))
                  + data[i + 1:i + 2 * length:2])
        length, src = matches[i]
        if src is not None:
            pos = (src + 0x03DF) & 0x03FF
            for size in range(2, length + 1):
                offer(size, bytes((((size - 2) << 2) | (pos >> 8),
                                   pos & 0xFF)))
        if best_choice is None:
            raise AssertionError("no opcode path")
        choices[i], cost[i] = best_choice, best_price

    output = bytearray()
    cursor = 0
    while cursor < n:
        length, payload = choices[cursor]
        output += payload
        cursor += length
    assert len(output) == cost[0]
    return bytes(output)


def reverse_flag1(processed: bytes) -> bytes:
    if len(processed) % 16:
        raise ValueError("unaligned flag1 graphics")
    order = (0, 8, 1, 9, 2, 10, 3, 11, 4, 12, 5, 13, 6, 14, 7, 15)
    raw = bytearray(len(processed))
    for base in range(0, len(processed), 16):
        for dst, src in enumerate(order):
            raw[base + src] = processed[base + dst]
    return bytes(raw)


def tile_to_4bpp(pixels: bytes) -> bytes:
    if len(pixels) != 64 or max(pixels) > 15:
        raise ValueError("expected indexed 8x8 SNES tile")
    out = bytearray()
    for shift in (0, 2):
        for y in range(8):
            a = b = 0
            for x in range(8):
                val = pixels[y * 8 + x]
                a |= ((val >> shift) & 1) << (7 - x)
                b |= ((val >> (shift + 1)) & 1) << (7 - x)
            out.extend((a, b))
    return bytes(out)


def prepare_art(font_bold: str, font_regular: str):
    from PIL import Image, ImageDraw, ImageFont
    plane = Image.new("P", (256, 88), 0)
    draw = ImageDraw.Draw(plane)
    definitions = ((TITLE[0], font_bold, 25, 4, 246),
                   (TITLE[1], font_bold, 18, 34, 249),
                   (TITLE[2], font_regular, 11, 65, 215))
    for label, font_path, px, y, max_width in definitions:
        face = ImageFont.truetype(font_path, px)
        l, t, r, b = draw.textbbox((0, 0), label, font=face)
        if r - l > max_width or y + b - t > 88:
            raise RuntimeError(f"title glyphs exceed source geometry: {label}")
        x = (256 - (r - l)) // 2 - l
        draw.text((x, y - t), label, font=face, fill=13)
    glyphs = [bytes(64)]
    lookup = {glyphs[0]: 0}
    index_map = bytearray(2048)
    for row in range(11):
        for col in range(32):
            bitmap = bytes(plane.getpixel((col * 8 + x, row * 8 + y))
                           for y in range(8) for x in range(8))
            if bitmap not in lookup:
                lookup[bitmap] = len(glyphs)
                glyphs.append(bitmap)
            slot = row * 32 + col
            index_map[slot * 2:slot * 2 + 2] = lookup[bitmap].to_bytes(2, "little")
    return plane, glyphs, index_map


def make_ips(original: bytes, patched: bytes) -> tuple[bytes, int]:
    if len(original) != len(patched):
        raise ValueError("IPS size mismatch")
    out = bytearray(b"PATCH")
    cursor = records = 0
    while cursor < len(original):
        if original[cursor] == patched[cursor]:
            cursor += 1
            continue
        start = cursor
        changed = bytearray()
        while (cursor < len(original) and len(changed) < 65535
               and original[cursor] != patched[cursor]):
            changed.append(patched[cursor])
            cursor += 1
        out += start.to_bytes(3, "big")
        out += len(changed).to_bytes(2, "big")
        out += changed
        records += 1
    out += b"EOF"
    return bytes(out), records


def build(source: bytes, font_bold: str, font_regular: str):
    from PIL import Image
    if source[SCRIPT_OFF:SCRIPT_OFF + 2] != bytes(2):
        raise AssertionError("G0 package signature changed")
    if source[OLD_POINTER_OFF:OLD_POINTER_OFF + 3] != OLD_POINTER:
        raise AssertionError("original G0 third graphics source changed")

    plane, tiles, index_map = prepare_art(font_bold, font_regular)
    source_decoded = {}
    original = {}
    for off, dest, length, span in (*GRAPHICS, TITLE_MAP):
        raw, hdr, _ = decompress_resource(source, off)
        if hdr.span != span or len(raw) != length:
            raise AssertionError(f"G0 source contract differs: {off:#x}")
        source_decoded[off] = raw
        original[off] = (
            reorder_flag1_blocks(raw) if hdr.postprocess else raw)
    # Tile sharing is determined from the complete decoded 64-KiB VRAM
    # package, not from the title-only 2-KiB tilemap.
    vram = bytearray(0x10000)
    for off, dest, length, _span in (*GRAPHICS, TITLE_MAP):
        vram[dest * 2:dest * 2 + length] = original[off]
    # Include the remaining six untouched G0 resource records, which hold
    # other background tilemaps, character graphics and OBJ tiles.
    p = SCRIPT_OFF + 2
    references = []
    while source[p] != 0xFF:
        address = int.from_bytes(source[p + 2:p + 5], "little")
        dest = int.from_bytes(source[p:p + 2], "little")
        src = ((address >> 16) & 0x7F) * 0x8000 + (address & 0x7FFF)
        raw, hdr, _ = decompress_resource(source, src)
        decoded = reorder_flag1_blocks(raw) if hdr.postprocess else raw
        vram[dest * 2:dest * 2 + len(decoded)] = decoded
        references.append((dest, src))
        p += 5
    if len(references) != 10:
        raise AssertionError("G0 package no longer contains ten resources")
    protected = set()
    for base in OTHER_MAPS:
        for i in range(1024):
            off = base * 2 + i * 2
            protected.add(int.from_bytes(vram[off:off + 2], "little") & 0x03FF)
    free = [i for i in range(1, 768) if i not in protected]
    if len(tiles) - 1 > len(free):
        raise RuntimeError(
            f"{len(tiles)-1} Vietnamese tiles but only {len(free)} isolated tiles"
        )
    assigned = {i: free[i - 1] for i in range(1, len(tiles))}
    original_title_map = vram[0:2048]
    newmap = bytearray(original_title_map)
    for index in range(11 * 32):
        local = int.from_bytes(index_map[2 * index:2 * index + 2], "little")
        native = int.from_bytes(original_title_map[2 * index:2 * index + 2], "little")
        newmap[2 * index:2 * index + 2] = (
            (native & 0x3C00) | (assigned[local] if local else 0)
        ).to_bytes(2, "little")
    blocks = {}
    for off, dest, length, _span in GRAPHICS:
        blocks[off] = bytearray(vram[dest * 2:dest * 2 + length])
    for local, tile in enumerate(tiles):
        if local == 0:
            continue
        physical = 0x4000 + assigned[local] * 32
        for off, dest, size, _span in GRAPHICS:
            start = dest * 2
            if start <= physical < start + size:
                blocks[off][physical - start:physical - start + 32] = tile_to_4bpp(tile)
                break
        else:
            raise AssertionError("title gfx cannot be mapped into source banks")
    for native_id in protected:
        if native_id >= 768:
            continue
        addr = 0x4000 + native_id * 32
        for off, dest, size, _span in GRAPHICS:
            start = dest * 2
            if start <= addr < start + size:
                if blocks[off][addr-start:addr-start+32] != vram[addr:addr+32]:
                    raise AssertionError("non-title graphics tile changed")
                break

    output = bytearray(source)
    region_bounds = []
    asset_report = []
    for off, dest, length, span in (*GRAPHICS, TITLE_MAP):
        hdr_data = source_decoded[off]
        original_obj, hdr, _ = decompress_resource(source, off)
        desired = bytes(newmap) if off == TITLE_MAP[0] else bytes(blocks[off])
        raw = reverse_flag1(desired) if hdr.postprocess else desired
        if raw == original_obj:
            asset_report.append({"source": f"0x{off:X}", "unchanged": True})
            continue
        packed = encode_chibi(raw)
        newspan = len(packed) + 2
        if newspan > span:
            if off != 0xF456D:
                raise RuntimeError(f"in-place resource {off:#x} overflows {span}")
            target = RELOCATE_FILE
            if target + newspan > 0x38000:
                raise AssertionError("relocated resource crosses ROM bank86")
            if source[target:target+newspan] != bytes([255])*newspan:
                raise AssertionError("bank86 staging area is NOT free")
            output[OLD_POINTER_OFF:OLD_POINTER_OFF+3] = NEW_POINTER
            output[target:target+newspan] = (
                (newspan | (int(hdr.postprocess) << 15)).to_bytes(2, "little")
                + packed
            )
            region_bounds.extend(((OLD_POINTER_OFF, OLD_POINTER_OFF + 3),
                                  (target, target + newspan)))
        else:
            target = off
            replacement = ((newspan | (int(hdr.postprocess) << 15))
                           .to_bytes(2, "little")
                           + packed + bytes([255])*(span-newspan))
            output[off:off+span] = replacement
            region_bounds.append((off, off+span))
        test, test_header, _ = decompress_resource(output, target)
        if test != raw or test_header.postprocess != hdr.postprocess:
            raise AssertionError("post-write codec failed round-trip")
        asset_report.append({"source": f"0x{off:X}", "output_source": f"0x{target:X}",
                             "old_span": span, "new_span": newspan,
                             "postprocess": hdr.postprocess, "roundtrip": True})
    checksum, complement = write_snes_checksum(output)
    legal = set(range(0x7FDC,0x7FE0))
    for left, right in region_bounds:
        legal.update(range(left, right))
    changed = {i for i, (x,y) in enumerate(zip(source,output)) if x!=y}
    if changed-legal:
        raise AssertionError("title edit escaped whitelisted ROM spans")
    report = {
        "status": "G0_TITLE_STATIC_REPACK_PASS_NOT_EMULATOR",
        "source_rom_sha256": hashlib.sha256(source).hexdigest(),
        "output_rom_sha256": hashlib.sha256(output).hexdigest(),
        "title_texts": list(TITLE),
        "unique_title_tiles": len(tiles)-1,
        "protected_non_title_graphics_ids": len([i for i in protected if i<768]),
        "asset_report": asset_report, "changed_bytes": len(changed),
        "checksum": f"0x{checksum:04X}", "complement": f"0x{complement:04X}",
        "real_gameplay_verified": False, "full_game_translation": False,
        "release_ready": False,
    }
    return bytes(output), plane, report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("clean_rom", type=Path)
    parser.add_argument("output_rom", type=Path)
    parser.add_argument("--font-bold", required=True)
    parser.add_argument("--font-regular", required=True)
    parser.add_argument("--ips", type=Path)
    parser.add_argument("--preview", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--allow-untested-g0", action="store_true")
    args = parser.parse_args()
    if not args.allow_untested_g0:
        parser.error("unverified G0 diagnostic: pass --allow-untested-g0 explicitly")
    clean = bytes(require_clean_rom(args.clean_rom))
    patched, image, report = build(clean, args.font_bold, args.font_regular)
    args.output_rom.parent.mkdir(parents=True, exist_ok=True)
    args.output_rom.write_bytes(patched)
    if args.ips:
        payload, count = make_ips(clean, patched)
        args.ips.parent.mkdir(parents=True, exist_ok=True)
        args.ips.write_bytes(payload)
        report["ips_bytes"] = len(payload)
        report["ips_records"] = count
    if args.preview:
        from PIL import Image
        preview = Image.frombytes(
            "L", image.size, bytes(x*17 for x in image.get_flattened_data()))
        preview.resize((1024,352), Image.Resampling.NEAREST).save(args.preview)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
