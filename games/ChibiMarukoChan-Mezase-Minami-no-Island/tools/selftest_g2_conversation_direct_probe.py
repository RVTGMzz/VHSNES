#!/usr/bin/env python3
from __future__ import annotations

from build_g2_conversation_direct_probe import (
    FIELD_BYTES,
    FIELDS,
    LINE_BYTES,
    build_payload,
    required_chars,
)


def main() -> int:
    chars = required_chars()
    fake = {ch: bytes((0x84, 0x40 + i)) for i, ch in enumerate(sorted(chars))}
    for _off, _sha, lines in FIELDS:
        payload = build_payload(lines, fake)
        assert len(payload) == FIELD_BYTES
        assert payload.count(bytes.fromhex("816F")) == 3
    assert LINE_BYTES == (32, 34, 34)
    assert "!" not in chars
    assert " " not in chars
    print("g2_conversation_direct_probe_selftest=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
