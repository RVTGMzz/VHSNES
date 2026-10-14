"""Free Quiz bank06 cells by moving the existing compressed title asset.

The loader already uses a 24-bit LoROM resource pointer. Preserve the packed
stream exactly, check both source and destination, then restore the original
FF bytes in bank06. This is binary validation, not runtime acceptance.
"""
import hashlib

from decompress_chibi_resource import cpu_to_file, decompress_resource

OLD = 0x36907
NEW = 0x596FE
SPAN = 3420
POINTER = 0x12095
OLD_CPU = bytes.fromhex("07 E9 86")
NEW_CPU = bytes.fromhex("FE 96 8B")
PACKED_SHA = "a2b18e1cf1631582e75e7437fb6b46508b94a44f1d9e3a6c9f58b0de50e83572"


def relocate(clean: bytes, baseline: bytes):
    if len(clean) != 0x200000 or len(baseline) != len(clean):
        raise ValueError("Title relocation requires the original 2MiB layout")
    if hashlib.sha256(clean).hexdigest() != "e62768e8c0743acca2632a500d4c8463f0f88920d71e8c3a94da4cc3e6f08956":
        raise ValueError("Unexpected original ROM")
    if baseline[POINTER:POINTER + 3] != OLD_CPU:
        raise AssertionError("Historical title resource pointer changed")
    packed = baseline[OLD:OLD + SPAN]
    if hashlib.sha256(packed).hexdigest() != PACKED_SHA:
        raise AssertionError("Historical compressed title stream changed")
    if clean[OLD:OLD + SPAN] != b"\xff" * SPAN:
        raise AssertionError("Old title allocation was not original padding")
    if (clean[NEW:NEW + SPAN] != b"\xff" * SPAN or
            baseline[NEW:NEW + SPAN] != b"\xff" * SPAN):
        raise AssertionError("New title allocation is occupied")
    if cpu_to_file(int.from_bytes(NEW_CPU, "little")) != NEW:
        raise AssertionError("New 24-bit resource pointer maps incorrectly")
    if NEW // 0x8000 != (NEW + SPAN - 1) // 0x8000:
        raise AssertionError("Compressed title crosses a LoROM bank")
    decoded, header, _ = decompress_resource(baseline, OLD)
    if header.span != SPAN:
        raise AssertionError("Historical title stream size changed")
    output = bytearray(baseline)
    output[NEW:NEW + SPAN] = packed
    output[OLD:OLD + SPAN] = clean[OLD:OLD + SPAN]
    output[POINTER:POINTER + 3] = NEW_CPU
    rebuilt, new_header, _ = decompress_resource(output, NEW)
    if rebuilt != decoded or new_header.postprocess != header.postprocess:
        raise AssertionError("Relocated title decoding changed")
    output[0x7fdc:0x7fe0] = bytes(4)
    checksum = (sum(output) + 0x1fe) & 0xffff
    output[0x7fdc:0x7fde] = (checksum ^ 0xffff).to_bytes(2, "little")
    output[0x7fde:0x7fe0] = checksum.to_bytes(2, "little")
    allowed = (set(range(OLD, OLD + SPAN)) | set(range(NEW, NEW + SPAN)) |
               set(range(POINTER, POINTER + 3)) | set(range(0x7fdc, 0x7fe0)))
    if any(a != b and i not in allowed for i, (a, b) in enumerate(zip(baseline, output))):
        raise AssertionError("Title relocation escaped approved allocations")
    return bytes(output), {
        "old_resource_ROM": hex(OLD), "new_resource_ROM": hex(NEW),
        "resource_bytes": SPAN, "packed_SHA256": PACKED_SHA,
        "decoded_SHA256": hashlib.sha256(decoded).hexdigest(),
        "packed_bytes_preserved": True, "decoder_roundtrip_passed": True,
        "emulator_tested": False,
    }
